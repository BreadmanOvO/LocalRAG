"""Publish files with the same parsing, cleaning and chunking path as asset uploads."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, action="append", help="待入库文件，可多次指定；省略则读取来源注册表")
    parser.add_argument("--registry", type=Path, default=ROOT / "data/evaluation/shared/source_registry.json")
    args = parser.parse_args(argv)
    from core.ingestion_workflow import IngestionWorkflow
    from agent_platform.capability_packs.asset_ingestion import configured_vision
    from agent_platform.integrations.model_config_store import ModelConfigStore

    entries = [{"path_or_url": str(path)} for path in args.file] if args.file else json.loads(args.registry.read_text(encoding="utf-8"))
    workflow = IngestionWorkflow(registry_path=args.registry)
    vision = configured_vision(ModelConfigStore())
    failures = completed = skipped = 0
    for entry in entries:
        path = Path(entry.get("path_or_url", ""))
        path = path if path.is_absolute() else ROOT / path
        if not path.is_file():
            print(f"Missing file: {path}")
            failures += 1
            continue
        try:
            # Existing registry IDs remain citation-stable. Do not reindex legacy rows.
            source_id = entry.get("source_id")
            if source_id and workflow.knowledge_base.chroma.get(where={"source_id": source_id}, limit=1).get("ids"):
                skipped += 1
                print(f"Already indexed: {source_id}")
                continue
            progress = lambda stage: print(f"[{path.name}] {stage}", flush=True)
            staged = workflow.stage_file(path.name, path.read_bytes(), metadata=entry, source_id=source_id, vision=vision, on_progress=progress)
            result = workflow.publish(staged, on_progress=progress)
            if result.published:
                completed += 1
            else:
                skipped += 1
            print(f"[{path.name}] {result.chunk_count} chunks, source={result.source_id}")
        except Exception as exc:
            # Model-provider exception strings can contain credentials.
            print(f"[{path.name}] failed: {type(exc).__name__}")
            failures += 1
    print(f"Published: {completed}; skipped: {skipped}; failed: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
