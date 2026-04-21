# Bailian Runtime Keys Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make LocalRAG load Bailian chat and embedding credentials only from repository-root `key.json`, wire those values explicitly into runtime clients, and add a minimal live connectivity check.

**Architecture:** Add one focused runtime config module that owns `key.json` parsing and validation, then make runtime services and standalone scripts depend on that module instead of shell environment variables. Keep the current service boundaries intact: `rag.py` and `knowledge_base.py` still build the same clients, but now receive explicit Bailian settings from the shared loader. Verification stays narrow: unit tests for loader behavior plus one standalone connectivity script for live chat and embedding checks.

**Tech Stack:** Python, json, pathlib, unittest, LangChain, langchain_openai.ChatOpenAI, langchain_community.embeddings.DashScopeEmbeddings

---

## File Structure

- `runtime_keys.py` — new shared loader for repository-root `key.json`, including validation and structured accessors
- `rag.py` — update chat and embedding client construction to use explicit Bailian runtime settings
- `knowledge_base.py` — update standalone embedding initialization to use the shared runtime loader
- `eval_ragas.py` — replace `OPENAI_API_KEY` environment checks with shared `key.json` validation
- `eval_chunking.py` — replace environment-only credential checks with shared `key.json` validation
- `test/test_runtime_keys.py` — new unit tests for missing file, malformed JSON, missing field, empty field, and successful parse
- `test/test_eval_runners.py` — update baseline runner tests to patch the shared loader instead of shell environment variables
- `test_bailian_connectivity.py` — new standalone connectivity script for one minimal chat request and one minimal embedding request
- `.gitignore` — ignore repository-root `key.json`
- `TODO.md` — update unblock instructions so they no longer tell the user to export secrets in the shell

## Task 1: Add the shared runtime key loader

**Files:**
- Create: `runtime_keys.py`
- Create: `test/test_runtime_keys.py`

- [ ] **Step 1: Write the failing loader tests**

Create `test/test_runtime_keys.py` with:

```python
import json
import tempfile
import unittest
from pathlib import Path

from runtime_keys import BailianRuntimeConfig, load_bailian_runtime_config


class RuntimeKeysTests(unittest.TestCase):
    def test_load_bailian_runtime_config_reads_required_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            key_path = Path(temp_dir) / "key.json"
            key_path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "test-key",
                        "dashscope_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                        "chat_model_name": "qwen3-max",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            config = load_bailian_runtime_config(key_path)

        self.assertEqual(
            BailianRuntimeConfig(
                dashscope_api_key="test-key",
                dashscope_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                chat_model_name="qwen3-max",
                embedding_model_name="text-embedding-v4",
            ),
            config,
        )

    def test_load_bailian_runtime_config_requires_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "key.json"

            with self.assertRaisesRegex(RuntimeError, "Missing required root key.json file"):
                load_bailian_runtime_config(missing_path)

    def test_load_bailian_runtime_config_rejects_invalid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            key_path = Path(temp_dir) / "key.json"
            key_path.write_text("{not-json}", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "Malformed key.json"):
                load_bailian_runtime_config(key_path)

    def test_load_bailian_runtime_config_rejects_missing_field(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            key_path = Path(temp_dir) / "key.json"
            key_path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "test-key",
                        "dashscope_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                        "chat_model_name": "qwen3-max",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "Missing required key.json field: embedding_model_name"):
                load_bailian_runtime_config(key_path)

    def test_load_bailian_runtime_config_rejects_empty_field(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            key_path = Path(temp_dir) / "key.json"
            key_path.write_text(
                json.dumps(
                    {
                        "dashscope_api_key": "   ",
                        "dashscope_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                        "chat_model_name": "qwen3-max",
                        "embedding_model_name": "text-embedding-v4",
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(RuntimeError, "Empty required key.json field: dashscope_api_key"):
                load_bailian_runtime_config(key_path)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the loader tests to verify they fail**

Run: `python -m unittest test.test_runtime_keys -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'runtime_keys'`

- [ ] **Step 3: Write the runtime loader implementation**

Create `runtime_keys.py` with:

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_KEY_FIELDS = (
    "dashscope_api_key",
    "dashscope_base_url",
    "chat_model_name",
    "embedding_model_name",
)


@dataclass(frozen=True)
class BailianRuntimeConfig:
    dashscope_api_key: str
    dashscope_base_url: str
    chat_model_name: str
    embedding_model_name: str


def get_root_key_path() -> Path:
    return Path(__file__).resolve().parent / "key.json"


def load_bailian_runtime_config(path: Path | None = None) -> BailianRuntimeConfig:
    key_path = path or get_root_key_path()
    if not key_path.exists():
        raise RuntimeError(f"Missing required root key.json file: {key_path}")

    try:
        payload = json.loads(key_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Malformed key.json: {key_path}") from exc

    for field in REQUIRED_KEY_FIELDS:
        if field not in payload:
            raise RuntimeError(f"Missing required key.json field: {field}")
        value = payload[field]
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"Empty required key.json field: {field}")

    return BailianRuntimeConfig(
        dashscope_api_key=payload["dashscope_api_key"].strip(),
        dashscope_base_url=payload["dashscope_base_url"].strip(),
        chat_model_name=payload["chat_model_name"].strip(),
        embedding_model_name=payload["embedding_model_name"].strip(),
    )
```

- [ ] **Step 4: Run the loader tests to verify they pass**

Run: `python -m unittest test.test_runtime_keys -v`
Expected: PASS with all five tests green

- [ ] **Step 5: Commit the loader foundation**

```bash
git add runtime_keys.py test/test_runtime_keys.py
git commit -m "feat: add bailian runtime key loader"
```

## Task 2: Wire runtime clients to explicit Bailian settings

**Files:**
- Modify: `rag.py`
- Modify: `knowledge_base.py`
- Test: `test/test_chunking.py`
- Test: `test/test_eval_chunking.py:16-60`

- [ ] **Step 1: Extend the service tests to require explicit runtime config usage**

Add this test to `test/test_chunking.py` before `if __name__ == "__main__":`:

```python
    def test_knowledge_base_service_passes_runtime_key_to_embeddings(self):
        mock_chroma = mock.Mock()
        runtime_config = mock.Mock(embedding_model_name="text-embedding-v4", dashscope_api_key="test-key")

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                mock.patch.object(knowledge_base, "Chroma", return_value=mock_chroma),
                mock.patch.object(knowledge_base, "load_bailian_runtime_config", return_value=runtime_config),
                mock.patch.object(knowledge_base, "DashScopeEmbeddings", return_value=object()) as mock_embeddings,
                mock.patch.object(config, "persist_directory", temp_dir),
            ):
                knowledge_base.KnowledgeBaseService()

        mock_embeddings.assert_called_once_with(
            model="text-embedding-v4",
            dashscope_api_key="test-key",
        )
```

Add this test to `test/test_eval_chunking.py` after `class RagEvaluationHelperTests(unittest.TestCase):` begins:

```python
    def test_rag_service_uses_runtime_keys_for_chat_and_embeddings(self):
        runtime_config = mock.Mock(
            dashscope_api_key="test-key",
            dashscope_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            chat_model_name="qwen3-max",
            embedding_model_name="text-embedding-v4",
        )
        mock_vector_service = mock.Mock()
        mock_vector_service.get_retriever.return_value = mock.Mock()

        with (
            mock.patch.object(rag, "load_bailian_runtime_config", return_value=runtime_config),
            mock.patch.object(rag, "DashScopeEmbeddings", return_value=object()) as mock_embeddings,
            mock.patch.object(rag, "VectorStoreService", return_value=mock_vector_service),
            mock.patch.object(rag, "ChatOpenAI", return_value=mock.Mock()) as mock_chat_openai,
            mock.patch.object(rag.RagService, "_RagService__get_chain", return_value=mock.Mock()),
        ):
            rag.RagService()

        mock_embeddings.assert_called_once_with(
            model="text-embedding-v4",
            dashscope_api_key="test-key",
        )
        mock_chat_openai.assert_called_once_with(
            model="qwen3-max",
            api_key="test-key",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
```

- [ ] **Step 2: Run the targeted service tests to verify they fail**

Run: `python -m unittest test.test_chunking test.test_eval_chunking -v`
Expected: FAIL because `load_bailian_runtime_config` is not imported or used yet in `knowledge_base.py` and `rag.py`

- [ ] **Step 3: Update the runtime services to use explicit config**

In `knowledge_base.py`, replace the import section and `KnowledgeBaseService.__init__` setup with:

```python
import hashlib
import os
import sys
import sqlite3
import datetime

import config_data as config
from chunking import choose_chunking_strategy, chunk_text_baseline, chunk_text_doc_type_aware
from langchain_community.embeddings import DashScopeEmbeddings
from runtime_keys import load_bailian_runtime_config
```

```python
class KnowledgeBaseService(object):
    def __init__(self) -> None:
        runtime_config = load_bailian_runtime_config()
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(
                model=runtime_config.embedding_model_name,
                dashscope_api_key=runtime_config.dashscope_api_key,
            ),
            persist_directory=config.persist_directory,
        )
```

In `rag.py`, update the imports and `RagService.__init__` body to:

```python
from uuid import uuid4

import config_data as config
from chat_history_store import get_history
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from runtime_keys import load_bailian_runtime_config
from vector_stores import VectorStoreService
```

```python
class RagService(object):
    def __init__(self) -> None:
        runtime_config = load_bailian_runtime_config()
        self.vector_service = VectorStoreService(
            embedding=DashScopeEmbeddings(
                model=runtime_config.embedding_model_name,
                dashscope_api_key=runtime_config.dashscope_api_key,
            ),
        )

        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "以我提供的已知参考资料为主，简洁和专业的回答用户问题。参考资料：{context}。"),
                ("system", "并且我提供用户的对话历史记录："),
                MessagesPlaceholder("chat_history"),
                ("user", "请回答用户提问：{question}"),
            ]
        )

        self.chat_model = ChatOpenAI(
            model=runtime_config.chat_model_name,
            api_key=runtime_config.dashscope_api_key,
            base_url=runtime_config.dashscope_base_url,
        )

        self.chain = self.__get_chain()
```

- [ ] **Step 4: Run the targeted service tests to verify they pass**

Run: `python -m unittest test.test_chunking test.test_eval_chunking -v`
Expected: PASS with the new runtime-config assertions green and the existing chunking tests still green

- [ ] **Step 5: Commit the runtime wiring**

```bash
git add knowledge_base.py rag.py test/test_chunking.py test/test_eval_chunking.py
git commit -m "feat: wire bailian runtime keys into services"
```

## Task 3: Remove environment-only credential assumptions from evaluation runners

**Files:**
- Modify: `eval_ragas.py`
- Modify: `eval_chunking.py`
- Modify: `test/test_eval_runners.py`

- [ ] **Step 1: Rewrite the runner tests to require shared loader validation**

In `test/test_eval_runners.py`, update the imports to:

```python
from eval_ragas import (
    build_prediction_record,
    build_session_id,
    require_runtime_keys,
    run_baseline,
    summarize_predictions,
    write_json,
)
```

Replace `test_run_baseline_uses_distinct_session_ids_per_sample` with:

```python
    def test_run_baseline_uses_distinct_session_ids_per_sample(self):
        samples = [
            {
                "id": "sample-1",
                "question": "What is LocalRAG?",
                "reference_answer": "A local RAG project.",
                "evidence": [
                    {"quote": "LocalRAG", "source_id": "doc-1", "locator": "p1"}
                ],
                "metadata": {"difficulty": "easy", "topic": "rag", "doc_type": "guide"},
            },
            {
                "id": "sample-2",
                "question": "What does it test?",
                "reference_answer": "Baseline evaluation.",
                "evidence": [
                    {"quote": "baseline", "source_id": "doc-2", "locator": "p2"}
                ],
                "metadata": {"difficulty": "easy", "topic": "evaluation", "doc_type": "guide"},
            },
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = Path(temp_dir)
            dataset_path = temp_dir / "dataset.json"
            predictions_path = temp_dir / "predictions.json"
            metrics_path = temp_dir / "metrics.json"
            dataset_path.write_text(json.dumps(samples), encoding="utf-8")

            fake_rag_module = types.SimpleNamespace()
            fake_rag_service = mock.Mock()
            fake_rag_service.answer_once.side_effect = ["answer-1", "answer-2"]
            fake_rag_module.RagService = mock.Mock(return_value=fake_rag_service)

            with (
                mock.patch.dict(sys.modules, {"rag": fake_rag_module}),
                mock.patch("eval_ragas.load_bailian_runtime_config", return_value=mock.Mock()),
            ):
                summary = run_baseline(dataset_path, predictions_path, metrics_path)

            self.assertEqual(summary["sample_count"], 2)
            self.assertEqual(fake_rag_module.RagService.call_count, 1)
            fake_rag_service.answer_once.assert_has_calls(
                [
                    mock.call("What is LocalRAG?", session_id="eval-session-sample-1"),
                    mock.call("What does it test?", session_id="eval-session-sample-2"),
                ]
            )
            self.assertEqual(
                [call.kwargs["session_id"] for call in fake_rag_service.answer_once.call_args_list],
                ["eval-session-sample-1", "eval-session-sample-2"],
            )
            self.assertTrue(predictions_path.exists())
            self.assertTrue(metrics_path.exists())
```

Replace `test_run_baseline_requires_openai_api_key` with:

```python
    def test_require_runtime_keys_uses_shared_loader(self):
        with mock.patch("eval_ragas.load_bailian_runtime_config", return_value=mock.Mock()) as mock_loader:
            require_runtime_keys()

        mock_loader.assert_called_once_with()

    def test_require_runtime_keys_surfaces_loader_errors(self):
        with mock.patch(
            "eval_ragas.load_bailian_runtime_config",
            side_effect=RuntimeError("Missing required root key.json file: /tmp/key.json"),
        ):
            with self.assertRaisesRegex(RuntimeError, "Missing required root key.json file"):
                require_runtime_keys()
```

- [ ] **Step 2: Run the runner tests to verify they fail**

Run: `python -m unittest test.test_eval_runners -v`
Expected: FAIL because `require_runtime_keys` does not exist and `run_baseline` still depends on `OPENAI_API_KEY`

- [ ] **Step 3: Replace environment checks with shared loader validation**

In `eval_ragas.py`, update imports and add the shared validation helper:

```python
import argparse
import json
from pathlib import Path
from typing import Any

from data.evaluation.shared.eval_schema import validate_dataset
from runtime_keys import load_bailian_runtime_config
```

```python
def require_runtime_keys() -> None:
    load_bailian_runtime_config()
```

Then replace the environment check in `run_baseline` with:

```python
    require_runtime_keys()
```

In `eval_chunking.py`, update imports to remove `os` and add the loader:

```python
import argparse
import json
import shutil
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import config_data as config
from eval_ragas import build_session_id, load_dataset, write_json
from knowledge_base import KnowledgeBaseService
from rag import RagService
from runtime_keys import load_bailian_runtime_config
```

Replace `require_runtime_credentials()` with:

```python
def require_runtime_credentials() -> None:
    load_bailian_runtime_config()
```

- [ ] **Step 4: Run the runner tests to verify they pass**

Run: `python -m unittest test.test_eval_runners -v`
Expected: PASS with baseline runner behavior unchanged except for the new loader-based validation path

- [ ] **Step 5: Commit the runner validation change**

```bash
git add eval_ragas.py eval_chunking.py test/test_eval_runners.py
git commit -m "refactor: load bailian runtime keys in evaluation runners"
```

## Task 4: Add local-only key file protection and usage guidance

**Files:**
- Modify: `.gitignore`
- Modify: `TODO.md`

- [ ] **Step 1: Add the failing ignore/usage expectation as a manual check**

Review `.gitignore` and `TODO.md` and confirm two gaps exist before editing:

- `.gitignore` does not ignore `key.json`
- `TODO.md` still tells the user to export secrets in the shell

Expected: both gaps are present in the current repository state

- [ ] **Step 2: Update `.gitignore` to protect the local key file**

Append this line under the local secrets section in `.gitignore`:

```gitignore
key.json
```

- [ ] **Step 3: Update `TODO.md` to describe the new unblock path**

Replace the `## How to unblock` section in `TODO.md` with:

```md
## How to unblock

Create a local-only `key.json` file in the repository root before running the blocked scripts:

```json
{
  "dashscope_api_key": "...",
  "dashscope_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
  "chat_model_name": "qwen3-max",
  "embedding_model_name": "text-embedding-v4"
}
```

Do not commit this file.

Then run the blocked scripts normally.
```

- [ ] **Step 4: Verify the local-only guidance is correct**

Run: `git diff -- .gitignore TODO.md`
Expected: diff shows `key.json` ignored and shell export instructions removed in favor of local root `key.json`

- [ ] **Step 5: Commit the safety and guidance update**

```bash
git add .gitignore TODO.md
git commit -m "docs: document local bailian key configuration"
```

## Task 5: Add the minimal Bailian connectivity check

**Files:**
- Create: `test_bailian_connectivity.py`
- Test: `runtime_keys.py`

- [ ] **Step 1: Write the connectivity script contract test**

Create `test/test_bailian_connectivity_contract.py` with:

```python
import importlib.util
import unittest
from pathlib import Path


class BailianConnectivityScriptContractTests(unittest.TestCase):
    def test_connectivity_script_exists(self):
        self.assertTrue(Path("test_bailian_connectivity.py").exists())

    def test_connectivity_script_is_importable(self):
        spec = importlib.util.spec_from_file_location(
            "test_bailian_connectivity",
            Path("test_bailian_connectivity.py"),
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, "main"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract test to verify it fails**

Run: `python -m unittest test.test_bailian_connectivity_contract -v`
Expected: FAIL because `test_bailian_connectivity.py` does not exist yet

- [ ] **Step 3: Write the standalone connectivity script**

Create `test_bailian_connectivity.py` with:

```python
from __future__ import annotations

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI

from runtime_keys import load_bailian_runtime_config


def run_chat_check() -> str:
    runtime_config = load_bailian_runtime_config()
    client = ChatOpenAI(
        model=runtime_config.chat_model_name,
        api_key=runtime_config.dashscope_api_key,
        base_url=runtime_config.dashscope_base_url,
    )
    response = client.invoke("Reply with exactly: BAILIAN_CHAT_OK")
    return getattr(response, "content", str(response))


def run_embedding_check() -> int:
    runtime_config = load_bailian_runtime_config()
    client = DashScopeEmbeddings(
        model=runtime_config.embedding_model_name,
        dashscope_api_key=runtime_config.dashscope_api_key,
    )
    vector = client.embed_query("Bailian embedding connectivity check")
    return len(vector)


def main() -> int:
    try:
        chat_result = run_chat_check().strip()
        embedding_length = run_embedding_check()
    except Exception as exc:
        print(f"Bailian connectivity check failed: {exc}")
        return 1

    print(f"Bailian chat check succeeded: {chat_result}")
    print(f"Bailian embedding check succeeded: vector_length={embedding_length}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run the contract test to verify it passes**

Run: `python -m unittest test.test_bailian_connectivity_contract -v`
Expected: PASS with both tests green

- [ ] **Step 5: Run the minimal live connectivity check after the user fills `key.json`**

Run: `python test_bailian_connectivity.py`
Expected: exit code 0 with one chat success line and one embedding success line; output must not print the raw API key

- [ ] **Step 6: Commit the connectivity check**

```bash
git add test/test_bailian_connectivity_contract.py test_bailian_connectivity.py
git commit -m "test: add bailian connectivity check script"
```

## Task 6: Run the focused regression suite

**Files:**
- Test: `test/test_runtime_keys.py`
- Test: `test/test_chunking.py`
- Test: `test/test_eval_chunking.py`
- Test: `test/test_eval_runners.py`
- Test: `test/test_bailian_connectivity_contract.py`

- [ ] **Step 1: Run the focused automated regression suite**

Run: `python -m unittest test.test_runtime_keys test.test_chunking test.test_eval_chunking test.test_eval_runners test.test_bailian_connectivity_contract -v`
Expected: PASS with all targeted runtime-key and evaluation tests green

- [ ] **Step 2: Review the working tree before the final commit**

Run: `git status --short`
Expected: only the planned code, test, and doc files are modified or added; `key.json` remains untracked and ignored if present locally

- [ ] **Step 3: Commit the final integrated change if the earlier task-level commits were skipped**

```bash
git add runtime_keys.py knowledge_base.py rag.py eval_ragas.py eval_chunking.py .gitignore TODO.md test/test_runtime_keys.py test/test_chunking.py test/test_eval_chunking.py test/test_eval_runners.py test/test_bailian_connectivity_contract.py test_bailian_connectivity.py
git commit -m "feat: load bailian runtime settings from root key file"
```

## Self-Review

- **Spec coverage:** covered shared loader, explicit runtime client wiring, independent script validation, local-only `key.json` guidance, and minimal chat+embedding connectivity check
- **Placeholder scan:** no TBD/TODO placeholders remain; every code-writing step includes concrete code or exact edits
- **Type consistency:** shared loader name is `load_bailian_runtime_config`, returned type is `BailianRuntimeConfig`, and all later tasks use the same names
