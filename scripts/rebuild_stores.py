"""Rebuild vector stores with new documents."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from eval.eval_chunking import build_source_documents, STRATEGY_BASELINE, STRATEGY_DOC_TYPE_AWARE, STRATEGY_SEMANTIC
from config.runtime_keys import load_runtime_config

STORES_DIR = Path("results/chunking_eval/stores/gold_set-100-20260507")
REGISTRY_PATH = Path("data/evaluation/shared/source_registry.json")

def main():
    load_runtime_config()

    baseline_path = STORES_DIR / STRATEGY_BASELINE
    doc_type_aware_path = STORES_DIR / STRATEGY_DOC_TYPE_AWARE
    semantic_path = STORES_DIR / STRATEGY_SEMANTIC

    print("Building baseline store...")
    build_source_documents(baseline_path, STRATEGY_BASELINE, REGISTRY_PATH)
    print(f"  Saved to: {baseline_path}")

    print("\nBuilding doc_type_aware store...")
    build_source_documents(doc_type_aware_path, STRATEGY_DOC_TYPE_AWARE, REGISTRY_PATH)
    print(f"  Saved to: {doc_type_aware_path}")

    print("\nBuilding semantic store...")
    build_source_documents(semantic_path, STRATEGY_SEMANTIC, REGISTRY_PATH)
    print(f"  Saved to: {semantic_path}")

    print("\nDone! All 3 stores rebuilt.")

if __name__ == "__main__":
    main()
