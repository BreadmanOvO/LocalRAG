# E4 数据草案人工复核表

这不是正式训练记录，而是 E4 multi-metric partial-context hard-case slice 的可复核草案。

## 摘要

- 版本：`v1.3-e4-draft`
- 样本数：`8`
- 数据类型分布：`{'multi_metric_partial_context_refusal': 8}`
- 缺失指标分布：`{'AP': 2, 'ATE': 1, 'mAP': 1, 'mATE': 1, 'mIoU': 1, '内存占用': 1, '推理 FPS': 1, '显存占用': 1, '测试里程': 1}`
- generation_eval_set 源样本重叠：`[]`

## 复核标准

- multi-metric partial-context 样本：问题同时询问多个指标，但资料只支持其中一部分。
- 期望输出必须回答已支持指标，并明确说明缺失指标无法根据资料确定。
- 期望输出不能猜测缺失指标的数值、提升/下降方向或结论。

## 样本清单

### 1. e4-draft-multi-metric-001

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_direction_guess`
- 缺失指标：`['AP', 'ATE']`
- 来源训练样本：`['train-001']`
- 目标 source_id：`paper-030`

**输入**

```text
问题：使用 4096 个 Top-K 查询时，MFA 延迟、AP 和 ATE 分别发生什么变化？

参考资料：
[1] source_id=paper-030 locator=page=2
using 4096 size queries reduce the latency of MFA by 76.4%.
```

**期望输出**

```text
资料只说明 4096 个查询会让 MFA 延迟降低 76.4%。不能根据资料确定 AP 或 ATE 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-030 page=2
```

### 2. e4-draft-multi-metric-002

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_missing_value_guess`
- 缺失指标：`['mATE']`
- 来源训练样本：`['train-004']`
- 目标 source_id：`paper-037`

**输入**

```text
问题：CSDP 的 mask ratio=0.2 时，NDS、mAP 和 mATE 分别是多少？

参考资料：
[1] source_id=paper-037 locator=page=2
mask ratio 0.2 achieves the best result with NDS 58.5 and mAP 50.5.
```

**期望输出**

```text
资料只说明 mask ratio 为 0.2 时 NDS 为 58.5、mAP 为 50.5。不能根据资料确定 mATE 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-037 page=2
```

### 3. e4-draft-multi-metric-003

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_missing_value_guess`
- 缺失指标：`['显存占用']`
- 来源训练样本：`['train-047']`
- 目标 source_id：`paper-033`

**输入**

```text
问题：Cross-view Transformer 的推理速度、训练 GPU 小时和显存占用分别是多少？

参考资料：
[1] source_id=paper-033 locator=page=1
The model comfortably runs in real-time (35 FPS) on a single RTX 2080 Ti GPU and trains within 32 GPU hours.
```

**期望输出**

```text
资料说明推理速度为 35 FPS，训练需要 32 GPU 小时。不能根据资料确定 显存占用 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-033 page=1
```

### 4. e4-draft-multi-metric-004

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_metric_improvement_guess`
- 缺失指标：`['mIoU']`
- 来源训练样本：`['train-052']`
- 目标 source_id：`paper-045`

**输入**

```text
问题：GaussianOcc 的训练速度、渲染速度和 mIoU 分别提升了多少？

参考资料：
[1] source_id=paper-045 locator=page=1
GaussianOcc has low computational cost with 2.7 times faster training and 5 times faster rendering.
```

**期望输出**

```text
资料说明 GaussianOcc 训练快 2.7 倍、渲染快 5 倍。不能根据资料确定 mIoU 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-045 page=1
```

### 5. e4-draft-multi-metric-005

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_missing_speed_guess`
- 缺失指标：`['推理 FPS']`
- 来源训练样本：`['train-170']`
- 目标 source_id：`paper-025`

**输入**

```text
问题：BEVDet4D-Base 的 NDS、mAP 和推理 FPS 分别是多少？

参考资料：
[1] source_id=paper-025 locator=page=1-2
BEVDet4D-Base scores high as 42.1% mAP and 54.5% NDS.
```

**期望输出**

```text
资料说明 BEVDet4D-Base 的 NDS 为 54.5%，mAP 为 42.1%。不能根据资料确定 推理 FPS 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-025 page=1-2
```

### 6. e4-draft-multi-metric-006

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_direction_guess`
- 缺失指标：`['AP']`
- 来源训练样本：`['train-177']`
- 目标 source_id：`paper-001`

**输入**

```text
问题：相机外参噪声等级为 4 时，BEVFormer 的 NDS 和 AP 分别下降多少？

参考资料：
[1] source_id=paper-001 locator=page=17 (Section B, Robustness on Camera Extrinsics)
with the noise level being 4, BEVFormer only drops 14.3% NDS.
```

**期望输出**

```text
资料说明噪声等级为 4 时 BEVFormer 的 NDS 下降 14.3%。不能根据资料确定 AP 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-001 page=17 (Section B, Robustness on Camera Extrinsics)
```

### 7. e4-draft-multi-metric-007

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_missing_value_guess`
- 缺失指标：`['mAP', '内存占用']`
- 来源训练样本：`['train-186']`
- 目标 source_id：`paper-068`

**输入**

```text
问题：PointPillars 的运行速度、mAP 和内存占用分别是多少？

参考资料：
[1] source_id=paper-068 locator=page=1 (Abstract and Figure 1 description)
This detection performance is achieved while running at 62 Hz: a 2-4 fold runtime improvement.
```

**期望输出**

```text
资料说明 PointPillars 运行速度为 62 Hz，并带来 2-4 倍运行速度提升。不能根据资料确定 mAP 或 内存占用 是提升还是下降，也不能补充未给出的数值。

引用：
- paper-068 page=1 (Abstract and Figure 1 description)
```

### 8. e4-draft-multi-metric-008

- 类型：`multi_metric_partial_context_refusal`
- 复核重点：`multi_metric_partial_context_no_missing_value_guess`
- 缺失指标：`['测试里程']`
- 来源训练样本：`['train-192']`
- 目标 source_id：`standard-005`

**输入**

```text
问题：NHTSA 进口豁免计划自 2016 年 10 月以来批准了多少辆 ADS 车辆？这些车辆的测试里程是多少？

参考资料：
[1] source_id=standard-005 locator=page=4
Since October 2016, 264 ADS-equipped vehicles have received temporary import permission.
```

**期望输出**

```text
资料说明自 2016 年 10 月以来有 264 辆 ADS 车辆获得临时进口许可。不能根据资料确定 测试里程 是提升还是下降，也不能补充未给出的数值。

引用：
- standard-005 page=4
```
