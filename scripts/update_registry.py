"""Update source registry with new documents."""
import json
from pathlib import Path

REGISTRY_PATH = Path("data/evaluation/shared/source_registry.json")

new_entries = [
    # Apollo docs
    {"source_id": "apollo-doc-011", "title": "Apollo Lidar Perception", "doc_type": "official_doc", "category": "apollo", "language": "zh", "path_or_url": "data/sources/apollo/apollo-lidar-perception.md", "raw_path": "", "origin_url": "", "version": "Apollo 6.0", "topic_tags": ["perception", "sensor_fusion"], "notes": "generated from knowledge"},
    {"source_id": "apollo-doc-012", "title": "Apollo Camera Perception", "doc_type": "official_doc", "category": "apollo", "language": "zh", "path_or_url": "data/sources/apollo/apollo-camera-perception.md", "raw_path": "", "origin_url": "", "version": "Apollo 6.0", "topic_tags": ["perception", "sensor_fusion"], "notes": "generated from knowledge"},
    {"source_id": "apollo-doc-013", "title": "Apollo Radar Perception", "doc_type": "official_doc", "category": "apollo", "language": "zh", "path_or_url": "data/sources/apollo/apollo-radar-perception.md", "raw_path": "", "origin_url": "", "version": "Apollo 6.0", "topic_tags": ["perception", "sensor_fusion"], "notes": "generated from knowledge"},
    {"source_id": "apollo-doc-014", "title": "Apollo Prediction Module", "doc_type": "official_doc", "category": "apollo", "language": "zh", "path_or_url": "data/sources/apollo/apollo-prediction-module.md", "raw_path": "", "origin_url": "", "version": "Apollo 6.0", "topic_tags": ["planning_control", "perception"], "notes": "generated from knowledge"},
    {"source_id": "apollo-doc-015", "title": "Apollo Planning Module", "doc_type": "official_doc", "category": "apollo", "language": "zh", "path_or_url": "data/sources/apollo/apollo-planning-module.md", "raw_path": "", "origin_url": "", "version": "Apollo 6.0", "topic_tags": ["planning_control", "system_architecture"], "notes": "generated from knowledge"},
    # Papers
    {"source_id": "paper-008", "title": "DETR3D: 3D Object Detection from Multi-view Images", "doc_type": "paper", "category": "papers", "language": "zh", "path_or_url": "data/sources/papers/detr3d.md", "raw_path": "", "origin_url": "https://arxiv.org/abs/2110.06922", "version": "DETR3D", "topic_tags": ["perception", "sensor_fusion"], "notes": "generated from knowledge"},
    {"source_id": "paper-009", "title": "PETRv2: A Unified Framework for 3D Perception", "doc_type": "paper", "category": "papers", "language": "zh", "path_or_url": "data/sources/papers/petrv2.md", "raw_path": "", "origin_url": "https://arxiv.org/abs/2206.01256", "version": "PETRv2", "topic_tags": ["perception", "sensor_fusion"], "notes": "generated from knowledge"},
    {"source_id": "paper-010", "title": "PointPillars: Fast Encoders for Object Detection from Point Clouds", "doc_type": "paper", "category": "papers", "language": "zh", "path_or_url": "data/sources/papers/pointpillars.md", "raw_path": "", "origin_url": "https://arxiv.org/abs/1812.05784", "version": "PointPillars", "topic_tags": ["perception"], "notes": "generated from knowledge"},
    {"source_id": "paper-011", "title": "CenterPoint: Center-based 3D Object Detection and Tracking", "doc_type": "paper", "category": "papers", "language": "zh", "path_or_url": "data/sources/papers/centerpoint.md", "raw_path": "", "origin_url": "https://arxiv.org/abs/2006.11275", "version": "CenterPoint", "topic_tags": ["perception"], "notes": "generated from knowledge"},
    {"source_id": "paper-012", "title": "TransFusion: Robust LiDAR-Camera Fusion for 3D Object Detection", "doc_type": "paper", "category": "papers", "language": "zh", "path_or_url": "data/sources/papers/transfusion.md", "raw_path": "", "origin_url": "https://arxiv.org/abs/2203.11496", "version": "TransFusion", "topic_tags": ["perception", "sensor_fusion"], "notes": "generated from knowledge"},
    # Standards
    {"source_id": "standard-010", "title": "ISO 26262 Functional Safety", "doc_type": "standard", "category": "standards", "language": "zh", "path_or_url": "data/sources/standards/iso-26262-functional-safety.md", "raw_path": "", "origin_url": "", "version": "ISO 26262", "topic_tags": ["safety"], "notes": "generated from knowledge"},
    {"source_id": "standard-011", "title": "ISO 21448 SOTIF Detailed Analysis", "doc_type": "standard", "category": "standards", "language": "zh", "path_or_url": "data/sources/standards/iso-21448-sotif-details.md", "raw_path": "", "origin_url": "", "version": "ISO 21448", "topic_tags": ["safety"], "notes": "generated from knowledge"},
    {"source_id": "standard-012", "title": "UL 4600 Standard for Autonomous Products", "doc_type": "standard", "category": "standards", "language": "zh", "path_or_url": "data/sources/standards/ul-4600-standard.md", "raw_path": "", "origin_url": "", "version": "UL 4600", "topic_tags": ["safety"], "notes": "generated from knowledge"},
    {"source_id": "standard-013", "title": "ANSI/ATA Standards for Autonomous Vehicles", "doc_type": "standard", "category": "standards", "language": "zh", "path_or_url": "data/sources/standards/ansi-c-ata-standards.md", "raw_path": "", "origin_url": "", "version": "ANSI/ATA", "topic_tags": ["safety", "system_architecture"], "notes": "generated from knowledge"},
    {"source_id": "standard-014", "title": "Chinese Autonomous Driving Standards Overview", "doc_type": "standard", "category": "standards", "language": "zh", "path_or_url": "data/sources/standards/china-autonomous-driving-standards.md", "raw_path": "", "origin_url": "", "version": "China Standards", "topic_tags": ["safety", "system_architecture"], "notes": "generated from knowledge"},
]

with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
    registry = json.load(f)

registry.extend(new_entries)

with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"Registry updated: {len(registry)} total entries")
print(f"  - Apollo: {len([r for r in registry if r['category'] == 'apollo'])} docs")
print(f"  - Papers: {len([r for r in registry if r['category'] == 'papers'])} docs")
print(f"  - Standards: {len([r for r in registry if r['category'] == 'standards'])} docs")
