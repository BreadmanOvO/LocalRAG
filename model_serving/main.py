from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn

from model_deployment.manifest import load_manifest

from .api import create_app
from .llama_cpp_backend import LlamaCppGenerationBackend
from .profiles import load_profiles
from .transformers_backend import TransformersGenerationBackend


REPO_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the LocalRAG model service.")
    parser.add_argument(
        "--profiles",
        type=Path,
        default=Path("config/model_serving_profiles.example.json"),
    )
    parser.add_argument("--profile", default="e6_1_adapter_bf16")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--api-token-env", default="LOCALRAG_MODEL_API_TOKEN")
    parser.add_argument("--active-limit", type=int, default=1)
    parser.add_argument("--waiting-limit", type=int, default=4)
    parser.add_argument("--queue-timeout-seconds", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--llama-base-url")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.workers != 1:
        raise ValueError("workers must remain 1 for a single loaded GPU model")
    if args.host not in {"127.0.0.1", "localhost"}:
        raise ValueError("host must remain loopback-only")
    if not (1 <= args.port <= 65535):
        raise ValueError("port is invalid")

    profiles_path = args.profiles
    if not profiles_path.is_absolute():
        profiles_path = REPO_ROOT / profiles_path
    profiles = load_profiles(profiles_path, repo_root=REPO_ROOT)
    profile = profiles.require(args.profile)
    manifest_path = REPO_ROOT / profile.manifest_path
    manifest = load_manifest(manifest_path)
    if profile.backend == "transformers":
        if args.llama_base_url is not None:
            raise ValueError("llama base URL is invalid for Transformers")
        backend = TransformersGenerationBackend(
            profile=profile,
            repo_root=REPO_ROOT,
            expected_manifest=manifest,
        )
    else:
        if args.llama_base_url is None:
            raise ValueError("llama base URL is required for llama.cpp")
        backend = LlamaCppGenerationBackend(
            profile=profile,
            repo_root=REPO_ROOT,
            expected_manifest=manifest,
            base_url=args.llama_base_url,
        )
    backend.warmup()
    if not backend.readiness().ready:
        raise RuntimeError("model warm-up did not reach ready state")
    api_token = (os.environ.get(args.api_token_env) or None) if args.api_token_env else None
    app = create_app(
        backend=backend,
        profile=profile,
        expected_manifest=manifest,
        api_token=api_token,
        active_limit=args.active_limit,
        waiting_limit=args.waiting_limit,
        queue_timeout_seconds=args.queue_timeout_seconds,
    )
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        workers=1,
        log_config=None,
    )


if __name__ == "__main__":
    main()
