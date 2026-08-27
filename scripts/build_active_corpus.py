from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings
from config.corpus_profile import ACTIVE_CORPUS_CONTRACT_VERSION
from eval.eval_agent import build_corpus_manifest
from eval.eval_chunking import ALL_STRATEGIES, build_source_documents


REPO_ROOT = Path(__file__).resolve().parents[1]


def _relative_or_absolute(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def build_active_corpus(
    *,
    registry: Path,
    store: Path,
    strategy: str,
    profile: Path,
    collection_name: str,
    release_version: str,
) -> dict[str, object]:
    registry = registry.resolve()
    store = store.resolve()
    build_source_documents(store, strategy, registry_path=registry)
    manifest = build_corpus_manifest(
        registry_path=registry,
        persist_directory=store,
        collection_name=collection_name,
    )
    if manifest["coverage_ratio"] != 1.0:
        raise RuntimeError(
            "Corpus build did not cover every registry source: "
            + ", ".join(manifest["missing_source_ids"])
        )
    payload = {
        "contract_version": ACTIVE_CORPUS_CONTRACT_VERSION,
        "release_version": release_version,
        "persist_directory": _relative_or_absolute(store),
        "collection_name": collection_name,
        "source_count": int(manifest["registry_source_count"]),
        "chunk_count": int(manifest["chunk_count"]),
        "corpus_fingerprint": f"sha256:{manifest['corpus_fingerprint']}",
        "registry_fingerprint": f"sha256:{manifest['registry_fingerprint']}",
    }
    profile = profile.resolve()
    profile.parent.mkdir(parents=True, exist_ok=True)
    temporary = profile.with_name(f".{profile.name}.tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(profile)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build one local Chroma store and make it the active corpus."
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/evaluation/shared/source_registry.json"),
    )
    parser.add_argument(
        "--store",
        type=Path,
        default=Path("results/local_corpus/doc_type_aware"),
    )
    parser.add_argument(
        "--strategy", choices=ALL_STRATEGIES, default="doc_type_aware"
    )
    parser.add_argument(
        "--profile", type=Path, default=Path("config/active_corpus.json")
    )
    parser.add_argument("--collection-name", default=settings.collection_name)
    parser.add_argument("--release-version", default="local")
    args = parser.parse_args()
    payload = build_active_corpus(
        registry=args.registry,
        store=args.store,
        strategy=args.strategy,
        profile=args.profile,
        collection_name=args.collection_name,
        release_version=args.release_version,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
