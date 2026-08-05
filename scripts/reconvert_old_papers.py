"""Re-convert old papers (paper-001~018) from PDF using PyMuPDF."""
import json
import os
import fitz

REGISTRY_PATH = "data/evaluation/shared/source_registry.json"
MD_DIR = "data/sources/papers"

with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
    registry = json.load(f)

old_papers = [e for e in registry if e['category'] == 'papers' and int(e['source_id'].split('-')[1]) <= 18]

converted = 0
for entry in old_papers:
    raw_path = entry.get('raw_path', '')
    md_path = entry.get('path_or_url', '')

    if not raw_path or not os.path.exists(raw_path):
        print(f"SKIP (no raw PDF): {entry['source_id']} {entry['title']}")
        continue

    if not md_path:
        print(f"SKIP (no md path): {entry['source_id']} {entry['title']}")
        continue

    title = entry['title']
    print(f"Re-converting: {entry['source_id']} - {title[:50]} ...")

    try:
        doc = fitz.open(raw_path)
        total_pages = len(doc)

        all_text = []
        for i in range(total_pages):
            text = doc[i].get_text()
            if text.strip():
                all_text.append(f"### Page {i+1}\n\n{text.strip()}")

        doc.close()

        md_parts = [
            f"# {title}\n",
            f"**Source**: arxiv PDF, {total_pages} pages\n",
            "**Type**: Academic Paper\n",
            "---\n",
            "## Document Content\n",
        ]
        md_parts.extend(all_text)

        md_content = "\n".join(md_parts)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # Update version field with page count
        entry['version'] = f"{total_pages} pages"
        entry['notes'] = f"re-converted from PDF with PyMuPDF, {total_pages} pages"

        converted += 1
        print(f"  OK ({total_pages} pages, {len(md_content)} chars)")
    except Exception as e:
        print(f"  ERROR: {e}")

# Save updated registry
with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f"\nRe-converted: {converted}/{len(old_papers)}")
