# 微调前后对比报告：qwen3-4b-base-hardened-clean-v2-refusal-markers vs qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers

## 结论摘要

- 样本数：`10`
- 自动判定：`mixed_or_regressed`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 平均回答长度：`129.7`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 平均回答长度：`151.1`
- 平均回答长度变化：`21.4`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `-0.2` |
| `answered_ratio_delta` | `0.0` |
| `correct_refusal_ratio_delta` | `0.0` |
| `evidence_locator_hit_ratio_delta` | `0.0` |
| `evidence_source_hit_ratio_delta` | `0.0` |
| `over_refusal_risk_ratio_delta` | `0.0` |
| `refusal_ratio_delta` | `0.0` |
| `unsupported_claim_risk_ratio_delta` | `0.0` |

## 人工复核重点

- adapter 是否真的更会引用资料，而不是只改了措辞。
- adapter 是否只是回答变短，导致看起来更保守。
- adapter 是否对本来可回答的问题开始过度拒答。
- hard case 中是否减少无依据扩展。

## 逐样本并排对比

### gen-eval-001：normal_answerable

- 预期行为：`answer`
- 问题：自动驾驶视觉感知模块在 Apollo 中主要处理哪些任务？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-006, apollo-doc-006`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-006, apollo-doc-006`
- 回答长度变化：`139 -> 416`，delta `277`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
自动驾驶视觉感知模块在 Apollo 中主要处理红绿灯检测、车道线检测和基于摄像头的障碍物检测任务。引用：
- source_id=apollo-doc-006 locator=unknown
- source_id=apollo-doc-006 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
视觉感知模块在 Apollo 中主要处理红绿灯检测、车道线检测、基于摄像头的障碍物检测。

引用：
- [1] 1] 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。 因此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。 视觉感知算法在Apollo平台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。
- [2] 1] 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。 因此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。 视觉感知算法在Apollo平台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。 神经网络模型 红绿灯识别 红绿灯信息 多个目标投 红绿灯检测 提取检测ROI 票(voting) 车道线后处 车道线检测
```

### gen-eval-002：normal_answerable

- 预期行为：`answer`
- 问题：CRN 融合了哪两类传感器来构建 BEV 特征？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`paper-030, paper-030`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`paper-030, paper-030`
- 回答长度变化：`111 -> 51`，delta `-60`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
CRN 融合了相机和雷达两种传感器来构建 BEV 特征。引用：  
- source_id=paper-030 locator=unknown  
- source_id=paper-030 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
相机和雷达。

引用：
- paper-030 unknown
- paper-030 unknown
```

### gen-eval-003：hallucination_prone

- 预期行为：`answer`
- 问题：Apollo 感知融合模块是否只依赖摄像头结果？请根据资料回答。
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`137 -> 168`，delta `31`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
不，Apollo 感知融合模块不仅仅依赖摄像头结果，而是结合了摄像头、毫米波雷达和激光雷达三种传感器的数据进行目标级融合。通过融合不同传感器的优势，可以提高感知的准确性和可靠性。引用：  
- source_id=apollo-doc-005 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
不，Apollo感知融合模块不只依赖摄像头结果，而是融合了摄像头、毫米波雷达和激光雷达三种传感器的感知结果，通过目标级融合来提高感知性能。

引用：
- [1] source_id=apollo-doc-005 locator=unknown
- [2] source_id=apollo-doc-005 locator=unknown
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`paper-030, paper-080`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`paper-030, paper-080`
- 回答长度变化：`171 -> 156`，delta `-15`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
使用稀疏聚合时，将 Top-K 查询数从 All 减少到 4096，会显著降低 MFA 的延迟。根据资料，使用 4096 大小的查询可以将 MFA 的延迟减少 76%。然而，关于检测指标的变化，资料中没有提供具体信息。因此，无法确定检测指标会发生什么变化。

引用：
- paper-030: 使用 4096 大小的查询减少 MFA 的延迟。
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
延迟降低76%，检测指标提升1.3%。

引用：
- paper-030: 4096 size queries reduce the latency of MFA by 76.
- paper-080: the query positions to reduce optimization difficulty.
```

### gen-eval-005：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否给出了 Apollo 视觉感知模块在雨夜施工区域的具体误检率？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-006, apollo-doc-005`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-006, apollo-doc-005`
- 回答长度变化：`44 -> 56`，delta `12`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`否`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`否`；拒答：`是`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
资料中没有给出Apollo视觉感知模块在雨夜施工区域的具体误检率。引用：  
- [1]
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
没有给出具体数值。

引用：
- [1] 未提及雨夜施工区域的误检率。
- [2] 未提及雨夜施工区域的误检率。
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`paper-069, paper-030`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`paper-069, paper-030`
- 回答长度变化：`117 -> 67`，delta `-50`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`是`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
资料中没有说明 CRN 已经在某量产车型上部署，也没有给出部署成本。引用：  
- source_id=paper-069 locator=unknown  
- source_id=paper-030 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
没有提到 CRN 在量产车型上的部署或成本。

引用：
- paper-030 unknown
- paper-069 unknown
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-008, apollo-doc-006`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-008, apollo-doc-006`
- 回答长度变化：`86 -> 103`，delta `17`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
感知红绿灯信息对应的 channel 是 /apollo/prediction。引用：
- source_id=apollo-doc-008 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
/apollo/prediction

引用：
- [1] source_id=apollo-doc-008 locator=unknown
  - /apollo/prediction 输入预测障碍物信息
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`108 -> 123`，delta `15`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
Apollo 感知融合模块最终输出到 /apollo/perception/obstacles 障碍物 channel。

引用：
- source_id=apollo-doc-005 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
Apollo感知融合模块最终输出到 /apollo/perception/obstacles channel。

引用：
- [1] /perception/obstacles
- [2] /apollo/perception/obstacles
```

### gen-eval-009：hard_case_pattern_d

- 预期行为：`answer`
- 问题：文档中提到的 parameter-free design 主要想解决 BEV 感知中的什么问题？它试图与哪些相机因素解耦？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`paper-038, paper-078`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`paper-038, paper-078`
- 回答长度变化：`110 -> 175`，delta `65`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的领域适应问题。它试图与相机的内参和外参因素解耦。引用：  
- source_id=paper-038 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的 domain adaptation 问题，它试图与相机的 intrinsic parameters（相机内参）和 extrinsic parameters（相机外参）解耦。

引用：
- paper-038 unknown
- paper-078 unknown
```

### gen-eval-010：hard_case_pattern_d

- 预期行为：`answer`
- 问题：Part-A2 Net 如何利用 3D 边界框标注中自动提供的免费监督信息？
- qwen3-4b-base-hardened-clean-v2-refusal-markers 检索来源：`paper-066, paper-066`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 检索来源：`paper-066, paper-066`
- 回答长度变化：`274 -> 196`，delta `-78`
- qwen3-4b-base-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-hardened-clean-v2-refusal-markers 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过使用这些标注来学习更有效的 3D 特征。具体来说，Part-A2 Net 利用 3D 内部物体部分位置标签和分割标签作为额外的监督信息，在第一阶段学习更好的 3D 特征。然后，在第二阶段，将预测的 3D 内部物体部分位置和每个 3D 候选框内的点-wise 3D 特征进行聚合，以对框进行评分并细化其位置。引用：  
- source_id=paper-066 locator=unknown  
- source_id=paper-066 locator=unknown
```

**qwen3-4b-e1-webui-adapter-hardened-clean-v2-refusal-markers 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过以下方式学习更有效的 3D 特征：首先，使用 3D 内部物体部分位置标签和分割标签作为额外监督，学习更好的 3D 特征；然后，将预测的 3D 内部物体部分位置和每个 3D 候选框内的点云特征进行聚合，以评分候选框并优化其位置。

引用：
- paper-066 unknown
- paper-066 unknown
```
