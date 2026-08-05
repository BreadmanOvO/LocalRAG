"""Download autonomous driving papers from arxiv to fill source library to 100."""
import urllib.request
import os
import time

DEST = "data/sources/raw/papers"

# (arxiv_id, filename)
PAPERS = [
    # === BEV Perception ===
    ("2112.11790", "BEVDet High-performance Multi-camera 3D Object Detection.pdf"),
    ("2211.10439", "BEVFormer v2 Adapting Modern Image Backbones.pdf"),
    ("2203.17054", "BEVDet4D Exploit Temporal Cues in Multi-camera 3D Detection.pdf"),
    ("2212.03027", "BEVStereo Enhancing Depth Estimation in Multi-view 3D Detection.pdf"),
    ("2205.02833", "Cross-view Transformers for Real-time Map-view Segmentation.pdf"),
    ("2008.05711", "Lift Splat Shoot Encoding Images from Arbitrary Camera Rigs.pdf"),
    ("2205.13542", "BEVFusion Multi-Task Multi-Sensor Fusion Unified BEV.pdf"),
    ("2203.05625", "PETR Position Embedding Transformation Multi-view 3D Detection.pdf"),
    ("2304.10592", "Far3D Expanding Horizon Surround-view 3D Object Detection.pdf"),
    ("2306.12965", "SparseDrive End-to-End Autonomous Driving Sparse Scene.pdf"),
    ("2304.02643", "ViP3D End-to-end Visual Trajectory Prediction via 3D Agent Queries.pdf"),
    ("2109.01604", "SE-SSD Self-Ensembling Single-Stage Object Detector Point Cloud.pdf"),
    # === Monocular 3D Detection ===
    ("2211.10641", "MonoDLE Delving into Localization Errors Monocular 3D Detection.pdf"),
    ("2103.04630", "MonoFlex Monocular 3D Object Detection Flexible Reconstruction.pdf"),
    ("2104.13137", "DD3D Depth-aware 3D Object Detection Fully Convolutional.pdf"),
    ("2212.05998", "DETRs3D Monocular 3D Object Detection with DETR.pdf"),
    ("2108.06417", "SMOKE Single-Stage Monocular 3D Object Detection Keypoint.pdf"),
    ("2211.14682", "MonoGround Monocular 3D Object Detection Ground-truth.pdf"),
    ("2311.08108", "SparseFusion Fusing Multi-modal Sparse Representations 3D Detection.pdf"),
    ("2110.06922", "DETR3D 3D Object Detection from Multi-view Images.pdf"),
    ("2206.01256", "PETRv2 A Unified Framework for 3D Perception.pdf"),
    # === LiDAR Detection ===
    ("1711.06396", "VoxelNet End-to-End Learning Point Cloud 3D Object Detection.pdf"),
    ("1803.05958", "SECOND Sparsely Embedded Convolutional Detection.pdf"),
    ("1907.12736", "Part-A2 3D Object Detection Point Cloud Part-aware Aggregation.pdf"),
    ("1912.13192", "PV-RCNN Point-Voxel Feature Set Abstraction 3D Detection.pdf"),
    ("2108.13203", "PV-RCNN++ Point-Voxel Feature Set Abstraction Local Vector.pdf"),
    ("1812.05784", "PointPillars Fast Encoders Object Detection Point Clouds.pdf"),
    ("2006.11275", "CenterPoint Center-based 3D Object Detection and Tracking.pdf"),
    ("2203.11496", "TransFusion Robust LiDAR-Camera Fusion 3D Object Detection.pdf"),
    # === Occupancy Prediction ===
    ("2305.18323", "Occ3D A Large-Scale 3D Occupancy Prediction Benchmark.pdf"),
    ("2304.02650", "TPVFormer Tri-perspective View 3D Semantic Occupancy.pdf"),
    ("2306.09317", "RenderOcc Vision-centric 3D Occupancy Prediction 2D Rendering.pdf"),
    ("2312.09243", "FB-OCC Flow-based 3D Occupancy Prediction.pdf"),
    ("2403.12556", "GaussianOcc 3D Gaussian Splatting Occupancy Prediction.pdf"),
    ("2312.17118", "FlashOcc Fast Camera-Only 3D Occupancy Prediction.pdf"),
    ("2308.16245", "OccWorld 3D Occupancy World Model.pdf"),
    ("2310.00604", "UniDepth Unified Depth Estimation.pdf"),
    # === End-to-End AD ===
    ("2308.01006", "FusionAD Multi-modality Fusion Prediction Planning.pdf"),
    ("2402.11502", "GenAD Generative End-to-End Autonomous Driving.pdf"),
    ("2303.12077", "VAD Vectorized Scene Representation Efficient Autonomous Driving.pdf"),
    ("2310.10984", "AD-MLP Autonomous Driving with MLP.pdf"),
    ("2403.18994", "SparseDrivev2 Sparse Scene Modeling End-to-End AD.pdf"),
    ("2312.14206", "GameFormer Learning Interactive Driving Game-aware Transformers.pdf"),
    ("2310.12074", "DriveDreamer World Models for Autonomous Driving.pdf"),
    ("2305.11816", "MagicDrive Street View Generation Diverse 3D Geometry.pdf"),
    # === HD Map Construction ===
    ("2111.14813", "HDMapNet Learning HD Map for Autonomous Driving.pdf"),
    ("2208.14437", "MapTR Structured Modeling Online Vectorized HD Map.pdf"),
    ("2206.08920", "VectorMapNet End-to-end Vectorized HD Map Learning.pdf"),
    ("2308.10116", "StreamMapNet Streaming Mapping Online HD Map.pdf"),
    ("2309.06228", "MapTracker Tracking Strided Memory Vector HD Mapping.pdf"),
    ("2312.08344", "NeuralMapPrior Online HD Map Reconstruction Neural Priors.pdf"),
    # === Multi-task / Survey ===
    ("2209.05324", "Delving into Devils Bird-eye-view Perception Review.pdf"),
    ("2209.09959", "BEV-SAN Bird-eye-view Segmentation Attention Network.pdf"),
    ("2210.05616", "MUTR3D Multi-object Tracking with 3D Detection.pdf"),
    ("2107.08000", "M3D-RPN Monocular 3D Region Proposal Network.pdf"),
    # === Radar / 4D ===
    ("2209.09826", "CRN Camera Radar Net 3D Object Detection.pdf"),
    ("2306.10155", "RCBEV Radar-Camera Fusion BEV 3D Object Detection.pdf"),
    ("2212.11720", "4D-Net Learning from 3D and LiDAR Data.pdf"),
    ("2305.13112", "RadarNet Exploiting Radar Robust 3D Object Detection.pdf"),
    # === Depth Estimation ===
    ("1812.03245", "MonoDepth2 Monocular Self-Supervised Depth Estimation.pdf"),
    ("2303.17104", "DAD Depth-aware BEV Multi-view 3D Object Detection.pdf"),
    # === Tracking ===
    ("2004.01289", "AB3DMOT Real-time 3D Multi-Object Tracking.pdf"),
    ("2105.10017", "Changan 3D Multi-Object Tracking.pdf"),
    ("2305.13338", "MOTRv2 Bootstrapping End-to-End Multi-Object Tracking.pdf"),
    # === Lane Detection ===
    ("2309.17382", "LA-BEVv2 Adapting Multi-view BEV Lane Detection.pdf"),
    ("2206.04584", "CLRNet Cross Layer Refinement Network Lane Detection.pdf"),
    ("2111.05233", "PersFormer Geometry-aware Attention for 3D Lane Detection.pdf"),
    # === Data Augmentation / Generation ===
    ("2210.04166", "3D-Aug Auto-Augmenting for 3D Object Detection.pdf"),
    ("2305.04581", "UniSim Unified Simulation for Autonomous Driving.pdf"),
]

os.makedirs(DEST, exist_ok=True)

success = 0
failed = []
for arxiv_id, filename in PAPERS:
    filepath = os.path.join(DEST, filename)
    if os.path.exists(filepath):
        print(f"SKIP (exists): {filename}")
        success += 1
        continue
    url = f"https://arxiv.org/pdf/{arxiv_id}"
    print(f"Downloading: {filename} ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        with open(filepath, "wb") as f:
            f.write(data)
        size_mb = len(data) / 1024 / 1024
        if len(data) > 10000:
            print(f"  OK ({size_mb:.1f} MB)")
            success += 1
        else:
            print(f"  FAILED (too small: {len(data)} bytes)")
            failed.append((arxiv_id, filename))
            os.remove(filepath)
    except Exception as e:
        print(f"  ERROR: {e}")
        failed.append((arxiv_id, filename))
        if os.path.exists(filepath):
            os.remove(filepath)
    time.sleep(1)  # rate limit

print("\n=== Results ===")
print(f"Downloaded: {success}/{len(PAPERS)}")
if failed:
    print(f"Failed ({len(failed)}):")
    for aid, fn in failed:
        print(f"  {aid}: {fn}")
