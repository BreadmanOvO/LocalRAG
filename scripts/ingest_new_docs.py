"""Ingest new documents into the knowledge base."""
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.knowledge_base import KnowledgeBaseService
from config import settings as config


def load_registry():
    with open("data/evaluation/shared/source_registry.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_new_docs(registry):
    """Find documents in registry that haven't been ingested yet."""
    # Check MD5 file for already ingested docs
    ingested = set()
    if Path(config.md5_path).exists():
        with open(config.md5_path, "r", encoding="utf-8") as f:
            ingested = {line.strip() for line in f if line.strip()}

    new_docs = []
    for entry in registry:
        path = entry.get("path_or_url", "")
        if not path or not Path(path).exists():
            continue
        # Check if already ingested by reading file and computing MD5
        content = Path(path).read_text(encoding="utf-8")
        from core.knowledge_base import get_string_md5
        md5 = get_string_md5(content)
        if md5 not in ingested:
            new_docs.append((entry, content, md5))

    return new_docs


def main():
    registry = load_registry()
    new_docs = get_new_docs(registry)

    if not new_docs:
        print("No new documents to ingest.")
        return

    print(f"Found {len(new_docs)} new documents to ingest:")
    for entry, content, md5 in new_docs:
        print(f"  - {entry['source_id']}: {entry['title']}")

    kb = KnowledgeBaseService()

    for entry, content, md5 in new_docs:
        print(f"\nIngesting {entry['source_id']}: {entry['title']}...")
        source_metadata = {
            "source": entry["path_or_url"],
            "source_id": entry["source_id"],
            "doc_type": entry["doc_type"],
            "doc_type": entry.get("doc_type", "untyped"),
            "category": entry.get("category", ""),
            "language": entry.get("language", "zh"),
        }
        try:
            chunk_records = kb.ingest_document(content, source_metadata, chunking_strategy="doc_type_aware")
            from core.knowledge_base import save_md5
            save_md5(md5)
            print(f"  Done: {len(chunk_records)} chunks created")
        except Exception as e:
            print(f"  Error: {e}")

    print("\nIngestion complete!")


if __name__ == "__main__":
    main()
