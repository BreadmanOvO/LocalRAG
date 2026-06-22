# LocalRAG SFT Dataset Audit

- Created at: `2026-06-22T19:12:05`
- Train path: `finetune\datasets\localrag_sft_e3.jsonl`
- Validation path: `finetune\datasets\localrag_sft_e3_validation.jsonl`
- Train records: `211`
- Validation records: `20`
- Train issue rows: `0`
- Validation issue rows: `0`
- Train/validation ID overlap: `0`
- Eval set ID overlap: `0`
- Generation eval set ID overlap: `0`

## Citation Checks

- Train output citation ratio: `1.0`
- Validation output citation ratio: `1.0`
- Train input source marker ratio: `1.0`
- Validation input source marker ratio: `1.0`
- Train input locator marker ratio: `1.0`
- Validation input locator marker ratio: `1.0`

## Length Stats

- Train input length: `{'min': 127, 'max': 1368, 'mean': 466.2, 'median': 444}`
- Train output length: `{'min': 28, 'max': 285, 'mean': 116.4, 'median': 110}`
- Validation input length: `{'min': 163, 'max': 936, 'mean': 441.9, 'median': 408.0}`
- Validation output length: `{'min': 31, 'max': 239, 'mean': 139.9, 'median': 137.0}`

## Train Distributions

- doc_type: `{'official_doc': 19, 'paper': 171, 'report': 1, 'standard': 20}`
- difficulty: `{'easy': 66, 'hard': 74, 'medium': 71}`
- topics: `{'3d_detection': 17, '3d_geometry': 1, '3d_lane': 1, '3d_object_detection': 12, '3d_perception': 1, '3d_queries': 1, 'autonomous_driving': 7, 'benchmark': 1, 'bev_perception': 10, 'camera_fusion': 1, 'camera_radar_fusion': 1, 'dataset': 2, 'depth_estimation': 3, 'distillation': 1, 'domain_adaptation': 1, 'end_to_end': 4, 'end_to_end_driving': 3, 'gaussian_splatting': 1, 'generation': 1, 'hd_map': 5, 'lane_detection': 1, 'lidar': 3, 'lidar_perception': 1, 'localization': 2, 'map_construction': 4, 'mapping': 1, 'monocular_3d': 5, 'monocular_3d_detection': 2, 'monocular_perception': 1, 'motion': 1, 'multi_modal': 1, 'multi_object_tracking': 5, 'multi_view': 4, 'neural_prior': 1, 'occupancy_prediction': 7, 'online_mapping': 1, 'perception': 16, 'planning': 1, 'planning_control': 14, 'point_cloud': 2, 'prediction': 1, 'radar_perception': 2, 'rendering': 1, 'review': 1, 'safety': 14, 'segmentation': 2, 'self_supervised': 2, 'sensor_fusion': 14, 'sensor_simulation': 1, 'simulation': 1, 'sparse_representation': 1, 'surround_view': 1, 'survey': 1, 'system_architecture': 10, 'transformer': 5, 'vector_map': 2, 'vectorized': 1, 'vision_perception': 1, 'world_model': 3}`

## Validation Distributions

- doc_type: `{'official_doc': 8, 'paper': 10, 'report': 1, 'standard': 1}`
- difficulty: `{'easy': 6, 'medium': 14}`
- topics: `{'3d_detection': 2, 'lidar': 1, 'monocular_3d_detection': 1, 'online_mapping': 1, 'perception': 2, 'planning_control': 4, 'safety': 1, 'sensor_fusion': 1, 'sparse': 1, 'system_architecture': 4, 'tracking': 1, 'world_model': 1}`

## Issues

No structural issues found.
