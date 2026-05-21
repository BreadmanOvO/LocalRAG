"""Convert downloaded PDFs to markdown and register in source_registry.json."""
import json
import os
import re
import fitz  # PyMuPDF

RAW_DIR = "data/sources/raw/papers"
MD_DIR = "data/sources/papers"
REGISTRY_PATH = "data/evaluation/shared/source_registry.json"

# Topic tag mapping by filename keywords
TOPIC_MAP = {
    "BEV": ["bev_perception", "3d_detection"],
    "Mono": ["monocular_3d", "3d_detection"],
    "DETR": ["3d_detection", "transformer"],
    "Voxel": ["lidar", "3d_detection"],
    "Point": ["lidar", "3d_detection"],
    "PV-RCNN": ["lidar", "3d_detection"],
    "Center": ["lidar", "3d_detection"],
    "TransFusion": ["lidar", "camera_fusion", "3d_detection"],
    "Occ": ["occupancy_prediction"],
    "TPV": ["occupancy_prediction"],
    "Render": ["occupancy_prediction"],
    "Flash": ["occupancy_prediction"],
    "Gaussian": ["occupancy_prediction"],
    "FusionAD": ["end_to_end", "sensor_fusion"],
    "GenAD": ["end_to_end", "generation"],
    "VAD": ["end_to_end", "vectorized"],
    "AD-MLP": ["end_to_end"],
    "SparseDrive": ["end_to_end", "sparse"],
    "GameFormer": ["end_to_end", "prediction"],
    "DriveDreamer": ["world_model", "generation"],
    "MagicDrive": ["generation", "data_augmentation"],
    "Map": ["hd_map", "map_construction"],
    "HDMap": ["hd_map", "map_construction"],
    "Vector": ["hd_map", "map_construction"],
    "Stream": ["hd_map", "map_construction"],
    "Neural": ["hd_map", "map_construction"],
    "Tracking": ["tracking", "multi_object_tracking"],
    "MOTR": ["tracking", "multi_object_tracking"],
    "AB3D": ["tracking", "multi_object_tracking"],
    "Lane": ["lane_detection"],
    "CLR": ["lane_detection"],
    "Pers": ["lane_detection"],
    "Depth": ["depth_estimation"],
    "MonoDepth": ["depth_estimation"],
    "Radar": ["radar", "sensor_fusion"],
    "CRN": ["radar", "sensor_fusion"],
    "4D": ["radar", "sensor_fusion"],
    "Survey": ["survey", "review"],
    "Review": ["survey", "review"],
    "Delving": ["survey", "review"],
    "Aug": ["data_augmentation"],
    "Sim": ["simulation", "data_augmentation"],
    "SE-SSD": ["lidar", "3d_detection"],
    "Lift": ["bev_perception", "3d_detection"],
    "Cross": ["bev_perception", "segmentation"],
    "PETR": ["3d_detection", "transformer"],
    "Far3D": ["3d_detection", "surround_view"],
    "ViP3D": ["prediction", "end_to_end"],
    "UniDepth": ["depth_estimation"],
    "UniSim": ["simulation", "data_augmentation"],
}


def get_topic_tags(filename):
    """Infer topic tags from filename."""
    tags = set()
    for keyword, topic_tags in TOPIC_MAP.items():
        if keyword.lower() in filename.lower():
            tags.update(topic_tags)
    if not tags:
        tags.add("autonomous_driving")
    return sorted(list(tags))


def pdf_to_markdown(pdf_path, title):
    """Convert PDF to structured markdown."""
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    # Extract all text
    all_text = []
    for i in range(total_pages):
        text = doc[i].get_text()
        if text.strip():
            all_text.append(f"### Page {i+1}\n\n{text.strip()}")

    doc.close()

    # Build markdown
    md_parts = [
        f"# {title}\n",
        f"**Source**: arxiv PDF, {total_pages} pages\n",
        f"**Type**: Academic Paper\n",
        "---\n",
        "## Document Content\n",
    ]
    md_parts.extend(all_text)

    return "\n".join(md_parts), total_pages


def sanitize_filename(filename):
    """Remove .pdf extension and clean for use as markdown filename."""
    name = filename.replace(".pdf", "")
    # Convert to kebab-case-ish
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[\s]+', '-', name).strip('-').lower()
    return name


def main():
    # Load existing registry
    with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
        registry = json.load(f)

    # Find max paper ID
    max_id = 0
    for entry in registry:
        if entry['source_id'].startswith('paper-'):
            num = int(entry['source_id'].split('-')[1])
            max_id = max(max_id, num)

    # Get existing raw_paths to skip already registered
    existing_raw = {e.get('raw_path', '') for e in registry}

    # Get all downloaded PDFs
    pdf_files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith('.pdf')])
    print(f"Found {len(pdf_files)} PDFs in {RAW_DIR}")

    new_entries = []
    converted = 0
    skipped = 0

    for pdf_file in pdf_files:
        raw_path = f"data/sources/raw/papers/{pdf_file}"

        # Skip if already registered
        if raw_path in existing_raw:
            print(f"SKIP (registered): {pdf_file}")
            skipped += 1
            continue

        # Generate markdown filename
        md_name = sanitize_filename(pdf_file) + ".md"
        md_path = f"data/sources/papers/{md_name}"
        full_pdf_path = os.path.join(RAW_DIR, pdf_file)
        full_md_path = os.path.join(MD_DIR, md_name)

        # Extract title from filename
        title = pdf_file.replace('.pdf', '')

        # Convert PDF to markdown
        print(f"Converting: {pdf_file} ...")
        try:
            md_content, num_pages = pdf_to_markdown(full_pdf_path, title)
            with open(full_md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            # Create registry entry
            max_id += 1
            source_id = f"paper-{max_id:03d}"
            arxiv_id = pdf_file.split()[0] if pdf_file[0].isdigit() else ""

            entry = {
                "source_id": source_id,
                "title": title,
                "doc_type": "paper",
                "category": "papers",
                "language": "en",
                "path_or_url": md_path,
                "raw_path": raw_path,
                "origin_url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else "",
                "version": f"{num_pages} pages",
                "topic_tags": get_topic_tags(pdf_file),
                "notes": f"converted from arxiv PDF, {num_pages} pages"
            }
            new_entries.append(entry)
            converted += 1
            print(f"  OK -> {source_id} ({num_pages} pages)")
        except Exception as e:
            print(f"  ERROR: {e}")

    # Update registry
    registry.extend(new_entries)
    with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)

    print(f"\n=== Results ===")
    print(f"Converted: {converted}")
    print(f"Skipped (already registered): {skipped}")
    print(f"Total registry entries: {len(registry)}")


if __name__ == "__main__":
    main()
