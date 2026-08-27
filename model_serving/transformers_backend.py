from __future__ import annotations

from collections.abc import Iterator, Mapping
from pathlib import Path
from queue import SimpleQueue
from threading import Event, Lock, Thread
from typing import Any

import torch
from peft import PeftModel
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
)

from model_deployment.manifest import (
    ManifestMismatchError,
    validate_manifest,
)

from .backend import (
    BackendGenerationError,
    BackendIdentity,
    BackendIdentityError,
    BackendMessage,
    BackendOutOfMemoryError,
    BackendReadiness,
    BackendRequestError,
    GenerationChunk,
    GenerationHandle,
    GenerationRequest,
    manifest_fingerprint,
)
from .profiles import ModelServingProfile


class _CancelStoppingCriteria(StoppingCriteria):
    def __init__(self, cancel_event: Event) -> None:
        self._cancel_event = cancel_event

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        return self._cancel_event.is_set()


class _TransformersGenerationHandle(GenerationHandle):
    def __init__(
        self,
        *,
        model: Any,
        tokenizer: Any,
        model_inputs: Mapping[str, Any],
        input_tokens: int,
        request: GenerationRequest,
        mark_oom: Any,
    ) -> None:
        self._model = model
        self._tokenizer = tokenizer
        self._model_inputs = dict(model_inputs)
        self._input_tokens = input_tokens
        self._request = request
        self._mark_oom = mark_oom
        self._cancel_event = Event()
        self._iteration_lock = Lock()
        self._iterated = False
        self._errors: SimpleQueue[BaseException] = SimpleQueue()
        self._result: Any = None

    def cancel(self) -> None:
        self._cancel_event.set()

    def _generate(self, streamer: Any) -> None:
        generation_kwargs: dict[str, Any] = {
            **self._model_inputs,
            "streamer": streamer,
            "max_new_tokens": self._request.max_tokens,
            "do_sample": self._request.temperature > 0,
            "stopping_criteria": StoppingCriteriaList(
                [_CancelStoppingCriteria(self._cancel_event)]
            ),
        }
        if self._request.temperature > 0:
            generation_kwargs["temperature"] = self._request.temperature
        else:
            generation_kwargs.update(
                temperature=None,
                top_p=None,
                top_k=None,
            )
        try:
            with torch.inference_mode():
                self._result = self._model.generate(**generation_kwargs)
        except torch.cuda.OutOfMemoryError:
            self._mark_oom()
            self._errors.put(BackendOutOfMemoryError("CUDA out of memory"))
            streamer.on_finalized_text("", stream_end=True)
        except Exception:
            self._errors.put(
                BackendGenerationError("transformers generation failed", started=False)
            )
            streamer.on_finalized_text("", stream_end=True)

    def __iter__(self) -> Iterator[GenerationChunk]:
        with self._iteration_lock:
            if self._iterated:
                raise RuntimeError("generation handle can only be iterated once")
            self._iterated = True
        streamer = TextIteratorStreamer(
            self._tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        thread = Thread(
            target=self._generate,
            args=(streamer,),
            name=f"transformers-generation-{self._request.request_id}",
            daemon=True,
        )
        thread.start()
        yielded = False
        stream_exhausted = False
        try:
            for text in streamer:
                if text:
                    yielded = True
                    yield GenerationChunk(text=text)
            stream_exhausted = True
        finally:
            if not stream_exhausted:
                self._cancel_event.set()
            thread.join()
        if not self._errors.empty():
            error = self._errors.get()
            if isinstance(error, BackendGenerationError):
                raise BackendGenerationError(str(error), started=yielded) from None
            raise error

        output_tokens = 0
        shape = getattr(self._result, "shape", None)
        if isinstance(shape, tuple) and len(shape) >= 2 and type(shape[-1]) is int:
            output_tokens = max(0, shape[-1] - self._input_tokens)
        if self._cancel_event.is_set():
            finish_reason = "cancelled"
        elif output_tokens >= self._request.max_tokens:
            finish_reason = "length"
        else:
            finish_reason = "stop"
        yield GenerationChunk(
            text="",
            input_tokens=self._input_tokens,
            output_tokens=output_tokens,
            finish_reason=finish_reason,
        )


class TransformersGenerationBackend:
    def __init__(
        self,
        *,
        profile: ModelServingProfile,
        repo_root: Path,
        expected_manifest: Mapping[str, object],
        device: str = "cuda",
    ) -> None:
        if not isinstance(profile, ModelServingProfile):
            raise TypeError("profile must be a ModelServingProfile")
        if not isinstance(expected_manifest, Mapping):
            raise TypeError("expected_manifest must be a mapping")
        if not isinstance(device, str) or not device.strip():
            raise ValueError("device must be a non-empty string")
        if (
            profile.backend != "transformers"
            or profile.dtype != "bfloat16"
            or profile.quantization != "none"
            or profile.base_model_path is None
            or profile.adapter_path is None
            or profile.artifact_path is not None
            or profile.enable_thinking
        ):
            raise BackendIdentityError("profile is not a BF16 Transformers adapter identity")

        self.profile = profile
        self.repo_root = Path(repo_root).resolve()
        self.expected_manifest = dict(expected_manifest)
        self.device = device.strip()
        self._state_lock = Lock()
        self._warmed_up = False
        self._oom_latched = False
        self._detail = "loaded_not_warmed"
        self._tokenizer: Any = None
        self._model: Any = None
        self._identity = BackendIdentity(
            model_id=profile.model_id,
            backend="transformers",
            quantization="none",
            manifest_sha256=manifest_fingerprint(expected_manifest),
        )
        self._load_verified_model()

    @property
    def identity(self) -> BackendIdentity:
        return self._identity

    def _load_verified_model(self) -> None:
        validate_manifest(self.repo_root, self.expected_manifest)
        metadata = self.expected_manifest.get("metadata")
        identity = metadata.get("model_identity") if isinstance(metadata, Mapping) else None
        if (
            not isinstance(identity, Mapping)
            or identity.get("model_id") != self.profile.model_id
            or identity.get("architecture") != "Qwen3ForCausalLM"
            or identity.get("context_limit") != self.profile.context_limit
            or identity.get("base_model_path") != self.profile.base_model_path
            or identity.get("adapter_path") != self.profile.adapter_path
            or identity.get("dtype", "bfloat16") != "bfloat16"
            or identity.get("quantization", "none") != "none"
        ):
            raise ManifestMismatchError("manifest model identity does not match local inputs")

        base_path = (self.repo_root / str(self.profile.base_model_path)).resolve()
        adapter_path = (self.repo_root / str(self.profile.adapter_path)).resolve()
        chat_template_path = adapter_path / "chat_template.jinja"
        try:
            chat_template = chat_template_path.read_text(encoding="utf-8")
            tokenizer = AutoTokenizer.from_pretrained(
                base_path,
                local_files_only=True,
                trust_remote_code=False,
            )
            tokenizer.chat_template = chat_template
            base_model = AutoModelForCausalLM.from_pretrained(
                base_path,
                dtype=torch.bfloat16,
                local_files_only=True,
                trust_remote_code=False,
                low_cpu_mem_usage=True,
            )
            model = PeftModel.from_pretrained(
                base_model,
                adapter_path,
                local_files_only=True,
                is_trainable=False,
            )
            model.eval()
            model.to(self.device)
        except torch.cuda.OutOfMemoryError:
            self._mark_oom()
            raise BackendOutOfMemoryError("CUDA out of memory while loading") from None
        except OSError as exc:
            raise BackendIdentityError("verified model files could not be loaded") from exc
        self._tokenizer = tokenizer
        self._model = model

    def _mark_oom(self) -> None:
        torch.cuda.empty_cache()
        with self._state_lock:
            self._oom_latched = True
            self._warmed_up = False
            self._detail = "oom_latched"

    def readiness(self) -> BackendReadiness:
        with self._state_lock:
            return BackendReadiness(
                ready=self._warmed_up and not self._oom_latched,
                warmed_up=self._warmed_up,
                oom_latched=self._oom_latched,
                detail=self._detail,
            )

    def _prepare_inputs(
        self, request: GenerationRequest
    ) -> tuple[dict[str, Any], int]:
        if not isinstance(request, GenerationRequest):
            raise BackendRequestError("request must be a GenerationRequest")
        if request.model != self.profile.model_id:
            raise BackendRequestError("request model does not match backend")
        if (
            type(request.max_tokens) is not int
            or request.max_tokens <= 0
            or request.max_tokens > self.profile.max_new_tokens
        ):
            raise BackendRequestError("max_tokens exceeds profile")
        if not isinstance(request.temperature, (int, float)) or not (
            0 <= request.temperature <= 2
        ):
            raise BackendRequestError("temperature is invalid")
        if request.purpose not in {
            "agent_planning",
            "rag_generation",
            "conversation_summary",
        }:
            raise BackendRequestError("request purpose is invalid")
        if not request.messages or not all(
            isinstance(message, BackendMessage) for message in request.messages
        ):
            raise BackendRequestError("messages are invalid")
        messages = []
        for message in request.messages:
            value: dict[str, Any] = {
                "role": message.role,
                "content": message.content,
            }
            if message.name is not None:
                value["name"] = message.name
            if message.tool_call_id is not None:
                value["tool_call_id"] = message.tool_call_id
            if message.tool_calls:
                value["tool_calls"] = [dict(call) for call in message.tool_calls]
            messages.append(value)
        if any(
            message["role"] not in {"system", "user", "assistant", "tool"}
            or not isinstance(message["content"], str)
            or (
                not message["content"]
                and not (
                    message["role"] == "assistant" and message.get("tool_calls")
                )
            )
            for message in messages
        ):
            raise BackendRequestError("messages are invalid")
        try:
            template_options: dict[str, Any] = {
                "tokenize": False,
                "add_generation_prompt": True,
                "enable_thinking": False,
            }
            if request.tools:
                template_options["tools"] = [dict(tool) for tool in request.tools]
            prompt = self._tokenizer.apply_chat_template(messages, **template_options)
            encoded = self._tokenizer(
                prompt,
                return_tensors="pt",
                add_special_tokens=False,
            )
            if not isinstance(encoded, Mapping) or "input_ids" not in encoded:
                raise TypeError("tokenizer result is invalid")
            shape = getattr(encoded["input_ids"], "shape", None)
            if not isinstance(shape, tuple) or len(shape) < 2 or type(shape[-1]) is not int:
                raise TypeError("tokenizer input shape is invalid")
            input_tokens = shape[-1]
            if input_tokens > self.profile.context_limit - request.max_tokens:
                raise BackendRequestError("request exceeds the model context limit")
            model_inputs = {
                key: value.to(self.device) if callable(getattr(value, "to", None)) else value
                for key, value in encoded.items()
            }
        except BackendRequestError:
            raise
        except torch.cuda.OutOfMemoryError:
            self._mark_oom()
            raise BackendOutOfMemoryError("CUDA out of memory while preparing input") from None
        except Exception:
            raise BackendRequestError("request could not be tokenized") from None
        return model_inputs, input_tokens

    def start(self, request: GenerationRequest) -> GenerationHandle:
        with self._state_lock:
            if self._oom_latched:
                raise BackendOutOfMemoryError("backend restart required after OOM")
        model_inputs, input_tokens = self._prepare_inputs(request)
        return _TransformersGenerationHandle(
            model=self._model,
            tokenizer=self._tokenizer,
            model_inputs=model_inputs,
            input_tokens=input_tokens,
            request=request,
            mark_oom=self._mark_oom,
        )

    def warmup(self) -> None:
        for _ in self.start(
            GenerationRequest(
                request_id="warmup",
                model=self.profile.model_id,
                messages=(
                    BackendMessage(role="user", content="ready"),
                ),
                temperature=0.0,
                max_tokens=1,
                purpose="conversation_summary",
            )
        ):
            pass
        with self._state_lock:
            if not self._oom_latched:
                self._warmed_up = True
                self._detail = "ready"
