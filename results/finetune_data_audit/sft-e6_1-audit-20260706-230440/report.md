# LocalRAG SFT Dataset Audit

- Created at: `2026-07-06T23:04:40`
- Train path: `finetune\datasets\localrag_sft_e6_1.jsonl`
- Validation path: `finetune\datasets\localrag_sft_e6_1_validation.jsonl`
- Train records: `48`
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

- Train input length: `{'min': 143, 'max': 466, 'mean': 293.1, 'median': 281.0}`
- Train output length: `{'min': 53, 'max': 112, 'mean': 77.5, 'median': 74.0}`
- Validation input length: `{'min': 163, 'max': 936, 'mean': 441.9, 'median': 408.0}`
- Validation output length: `{'min': 31, 'max': 239, 'mean': 139.9, 'median': 137.0}`

## Train Distributions

- doc_type: `{'official_doc': 32, 'paper': 14, 'standard': 2}`
- difficulty: `{'easy': 4, 'hard': 40, 'medium': 4}`
- topics: `{'3d_detection': 2, '3d_object_detection': 2, 'lidar': 2, 'map_construction': 2, 'perception': 1, 'planning_control': 23, 'safety': 2, 'self_supervised': 2, 'sensor_fusion': 6, 'system_architecture': 4, 'transformer': 2}`

## Validation Distributions

- doc_type: `{'official_doc': 8, 'paper': 10, 'report': 1, 'standard': 1}`
- difficulty: `{'easy': 6, 'medium': 14}`
- topics: `{'3d_detection': 2, 'lidar': 1, 'monocular_3d_detection': 1, 'online_mapping': 1, 'perception': 2, 'planning_control': 4, 'safety': 1, 'sensor_fusion': 1, 'sparse': 1, 'system_architecture': 4, 'tracking': 1, 'world_model': 1}`

## Issues

No structural issues found.
