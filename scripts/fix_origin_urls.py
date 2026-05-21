"""Fix missing origin_url entries in source_registry.json using arxiv ID mapping."""
import json

REGISTRY_PATH = "data/evaluation/shared/source_registry.json"

# Mapping from filename to arxiv_id (from download_papers.py)
ARXIV_MAP = {
    "BEVDet High-performance Multi-camera 3D Object Detection.pdf": "2112.11790",
    "BEVFormer v2 Adapting Modern Image Backbones.pdf": "2211.10439",
    "BEVDet4D Exploit Temporal Cues in Multi-camera 3D Detection.pdf": "2203.17054",
    "BEVStereo Enhancing Depth Estimation in Multi-view 3D Detection.pdf": "2212.03027",
    "Cross-view Transformers for Real-time Map-view Segmentation.pdf": "2205.02833",
    "Lift Splat Shoot Encoding Images from Arbitrary Camera Rigs.pdf": "2008.05711",
    "BEVFusion Multi-Task Multi-Sensor Fusion Unified BEV.pdf": "2205.13542",
    "PETR Position Embedding Transformation Multi-view 3D Detection.pdf": "2203.05625",
    "Far3D Expanding Horizon Surround-view 3D Object Detection.pdf": "2304.10592",
    "SparseDrive End-to-End Autonomous Driving Sparse Scene.pdf": "2306.12965",
    "ViP3D End-to-end Visual Trajectory Prediction via 3D Agent Queries.pdf": "2304.02643",
    "SE-SSD Self-Ensembling Single-Stage Object Detector Point Cloud.pdf": "2109.01604",
    "MonoDLE Delving into Localization Errors Monocular 3D Detection.pdf": "2211.10641",
    "MonoFlex Monocular 3D Object Detection Flexible Reconstruction.pdf": "2103.04630",
    "DD3D Depth-aware 3D Object Detection Fully Convolutional.pdf": "2104.13137",
    "DETRs3D Monocular 3D Object Detection with DETR.pdf": "2212.05998",
    "SMOKE Single-Stage Monocular 3D Object Detection Keypoint.pdf": "2108.06417",
    "MonoGround Monocular 3D Object Detection Ground-truth.pdf": "2211.14682",
    "SparseFusion Fusing Multi-modal Sparse Representations 3D Detection.pdf": "2311.08108",
    "DETR3D 3D Object Detection from Multi-view Images.pdf": "2110.06922",
    "PETRv2 A Unified Framework for 3D Perception.pdf": "2206.01256",
    "VoxelNet End-to-End Learning Point Cloud 3D Object Detection.pdf": "1711.06396",
    "SECOND Sparsely Embedded Convolutional Detection.pdf": "1803.05958",
    "Part-A2 3D Object Detection Point Cloud Part-aware Aggregation.pdf": "1907.12736",
    "PV-RCNN Point-Voxel Feature Set Abstraction 3D Detection.pdf": "1912.13192",
    "PV-RCNN++ Point-Voxel Feature Set Abstraction Local Vector.pdf": "2108.13203",
    "PointPillars Fast Encoders Object Detection Point Clouds.pdf": "1812.05784",
    "CenterPoint Center-based 3D Object Detection and Tracking.pdf": "2006.11275",
    "TransFusion Robust LiDAR-Camera Fusion 3D Object Detection.pdf": "2203.11496",
    "Occ3D A Large-Scale 3D Occupancy Prediction Benchmark.pdf": "2305.18323",
    "TPVFormer Tri-perspective View 3D Semantic Occupancy.pdf": "2304.02650",
    "RenderOcc Vision-centric 3D Occupancy Prediction 2D Rendering.pdf": "2306.09317",
    "FB-OCC Flow-based 3D Occupancy Prediction.pdf": "2312.09243",
    "GaussianOcc 3D Gaussian Splatting Occupancy Prediction.pdf": "2403.12556",
    "FlashOcc Fast Camera-Only 3D Occupancy Prediction.pdf": "2312.17118",
    "OccWorld 3D Occupancy World Model.pdf": "2308.16245",
    "UniDepth Unified Depth Estimation.pdf": "2310.00604",
    "FusionAD Multi-modality Fusion Prediction Planning.pdf": "2308.01006",
    "GenAD Generative End-to-End Autonomous Driving.pdf": "2402.11502",
    "VAD Vectorized Scene Representation Efficient Autonomous Driving.pdf": "2303.12077",
    "AD-MLP Autonomous Driving with MLP.pdf": "2310.10984",
    "SparseDrivev2 Sparse Scene Modeling End-to-End AD.pdf": "2403.18994",
    "GameFormer Learning Interactive Driving Game-aware Transformers.pdf": "2312.14206",
    "DriveDreamer World Models for Autonomous Driving.pdf": "2310.12074",
    "MagicDrive Street View Generation Diverse 3D Geometry.pdf": "2305.11816",
    "HDMapNet Learning HD Map for Autonomous Driving.pdf": "2111.14813",
    "MapTR Structured Modeling Online Vectorized HD Map.pdf": "2208.14437",
    "VectorMapNet End-to-end Vectorized HD Map Learning.pdf": "2206.08920",
    "StreamMapNet Streaming Mapping Online HD Map.pdf": "2308.10116",
    "MapTracker Tracking Strided Memory Vector HD Mapping.pdf": "2309.06228",
    "NeuralMapPrior Online HD Map Reconstruction Neural Priors.pdf": "2312.08344",
    "Delving into Devils Bird-eye-view Perception Review.pdf": "2209.05324",
    "BEV-SAN Bird-eye-view Segmentation Attention Network.pdf": "2209.09959",
    "MUTR3D Multi-object Tracking with 3D Detection.pdf": "2210.05616",
    "M3D-RPN Monocular 3D Region Proposal Network.pdf": "2107.08000",
    "CRN Camera Radar Net 3D Object Detection.pdf": "2209.09826",
    "RCBEV Radar-Camera Fusion BEV 3D Object Detection.pdf": "2306.10155",
    "4D-Net Learning from 3D and LiDAR Data.pdf": "2212.11720",
    "RadarNet Exploiting Radar Robust 3D Object Detection.pdf": "2305.13112",
    "MonoDepth2 Monocular Self-Supervised Depth Estimation.pdf": "1812.03245",
    "DAD Depth-aware BEV Multi-view 3D Object Detection.pdf": "2303.17104",
    "AB3DMOT Real-time 3D Multi-Object Tracking.pdf": "2004.01289",
    "Changan 3D Multi-Object Tracking.pdf": "2105.10017",
    "MOTRv2 Bootstrapping End-to-End Multi-Object Tracking.pdf": "2305.13338",
    "LA-BEVv2 Adapting Multi-view BEV Lane Detection.pdf": "2309.17382",
    "CLRNet Cross Layer Refinement Network Lane Detection.pdf": "2206.04584",
    "PersFormer Geometry-aware Attention for 3D Lane Detection.pdf": "2111.05233",
    "3D-Aug Auto-Augmenting for 3D Object Detection.pdf": "2210.04166",
    "UniSim Unified Simulation for Autonomous Driving.pdf": "2305.04581",
}

# Build lookup: raw_path -> arxiv_id
raw_to_arxiv = {}
for filename, arxiv_id in ARXIV_MAP.items():
    raw_path = f"data/sources/raw/papers/{filename}"
    raw_to_arxiv[raw_path] = arxiv_id

with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
    registry = json.load(f)

fixed = 0
for entry in registry:
    if not entry.get('origin_url') and entry.get('raw_path') in raw_to_arxiv:
        arxiv_id = raw_to_arxiv[entry['raw_path']]
        entry['origin_url'] = f"https://arxiv.org/abs/{arxiv_id}"
        fixed += 1

with open(REGISTRY_PATH, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f"Fixed {fixed} entries with missing origin_url")
