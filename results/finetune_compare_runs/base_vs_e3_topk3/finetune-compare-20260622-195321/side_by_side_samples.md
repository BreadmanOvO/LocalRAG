# 微调前后对比报告：qwen3-4b-base-topk3 vs qwen3-4b-e3-webui-adapter-topk3

## 结论摘要

- 样本数：`10`
- 自动判定：`adapter_improved`
- qwen3-4b-base-topk3 平均回答长度：`153.9`
- qwen3-4b-e3-webui-adapter-topk3 平均回答长度：`85.4`
- 平均回答长度变化：`-68.5`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `0.3` |
| `answered_ratio_delta` | `0.0` |
| `citation_support_risk_ratio_delta` | `0.0` |
| `correct_refusal_ratio_delta` | `0.0` |
| `directional_contradiction_risk_ratio_delta` | `0.0` |
| `evidence_locator_hit_ratio_delta` | `0.0` |
| `evidence_source_hit_ratio_delta` | `0.0` |
| `over_refusal_risk_ratio_delta` | `0.0` |
| `reference_coverage_ratio_delta` | `-0.039` |
| `reference_coverage_risk_ratio_delta` | `0.0` |
| `refusal_ratio_delta` | `0.0` |
| `unsupported_claim_risk_ratio_delta` | `0.0` |
| `unsupported_numeric_claim_risk_ratio_delta` | `0.0` |

## 人工复核重点

- adapter 是否真的更会引用资料，而不是只改了措辞。
- adapter 是否只是回答变短，导致看起来更保守。
- adapter 是否对本来可回答的问题开始过度拒答。
- hard case 中是否减少无依据扩展。

## 逐样本并排对比

### gen-eval-001：normal_answerable

- 预期行为：`answer`
- 问题：自动驾驶视觉感知模块在 Apollo 中主要处理哪些任务？
- qwen3-4b-base-topk3 检索来源：`apollo-doc-006, apollo-doc-006, apollo-doc-006`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`apollo-doc-006, apollo-doc-006, apollo-doc-006`
- 回答长度变化：`161 -> 51`，delta `-110`
- qwen3-4b-base-topk3 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-base-topk3 回答**

```text
自动驾驶视觉感知模块在 Apollo 中主要处理红绿灯检测、车道线检测和基于摄像头的障碍物检测任务。引用：
- source_id unknown locator unknown
- source_id unknown locator unknown
- source_id unknown locator unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
红绿灯检测、车道线检测、基于摄像头的障碍物检测。

引用：
- apollo-doc-006 p. 1
```

### gen-eval-002：normal_answerable

- 预期行为：`answer`
- 问题：CRN 融合了哪两类传感器来构建 BEV 特征？
- qwen3-4b-base-topk3 检索来源：`paper-030, paper-030, paper-038`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`paper-030, paper-030, paper-038`
- 回答长度变化：`145 -> 51`，delta `-94`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`0.087`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.0`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-base-topk3 回答**

```text
CRN 融合了相机和雷达两种传感器来构建 BEV 特征。引用：
- source_id paper-030 locator unknown
- source_id paper-030 locator unknown
- source_id paper-038 locator unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
相机和雷达。

引用：
- paper-030 unknown
- paper-038 unknown
```

### gen-eval-003：hallucination_prone

- 预期行为：`answer`
- 问题：Apollo 感知融合模块是否只依赖摄像头结果？请根据资料回答。
- qwen3-4b-base-topk3 检索来源：`apollo-doc-005, apollo-doc-005, apollo-doc-005`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`apollo-doc-005, apollo-doc-005, apollo-doc-005`
- 回答长度变化：`141 -> 99`，delta `-42`
- qwen3-4b-base-topk3 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-base-topk3 回答**

```text
不，Apollo 感知融合模块不仅仅依赖摄像头结果。根据资料，Apollo 感知融合模块支持对摄像头、毫米波雷达和激光雷达传感器感知的结果进行目标级融合。通过融合这三种传感器的数据，模块能够结合各传感器的优点，提高感知的准确性和可靠性。引用：
- source_id locator
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
不，Apollo感知融合模块不只依赖摄像头结果，而是融合了摄像头、毫米波雷达和激光雷达三种传感器的感知结果，通过目标级融合来提高感知性能。

引用：
- apollo-doc-005 unknown
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- qwen3-4b-base-topk3 检索来源：`paper-030, paper-080, paper-030`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`paper-030, paper-080, paper-030`
- 回答长度变化：`230 -> 93`，delta `-137`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`0.176`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.118`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-base-topk3 回答**

```text
使用稀疏聚合时，将 Top-K 查询数从 All 减少到 4096，会显著降低 MFA 的延迟。具体来说，使用 4096 大小的查询可以将 MFA 的延迟减少 76%。此外，由于 BEV 特征图在 top-k 抽样后变得稀疏和离散化，检测指标（如 True Positive 指标）会有所下降。引用：  
- source_id paper-030 locator unknown  
- source_id paper-080 locator unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
延迟从 21.01ms 降低到 4.96ms，但检测指标（True Positive）性能下降。

引用：
- paper-030 unknown
- paper-080 unknown
```

### gen-eval-005：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否给出了 Apollo 视觉感知模块在雨夜施工区域的具体误检率？
- qwen3-4b-base-topk3 检索来源：`apollo-doc-006, apollo-doc-005, apollo-doc-005`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`apollo-doc-006, apollo-doc-005, apollo-doc-005`
- 回答长度变化：`126 -> 80`，delta `-46`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-base-topk3 回答**

```text
资料中没有给出Apollo视觉感知模块在雨夜施工区域的具体误检率。引用：  
- source_id=apollo-doc-006 locator=unknown  
- source_id=apollo-doc-005 locator=unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
资料未给出具体误检率，但提到视觉感知模块在雨夜施工区域的性能可能受影响，需要结合其他传感器进行融合。

引用：
- apollo-doc-006 unknown
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- qwen3-4b-base-topk3 检索来源：`paper-069, paper-030, paper-073`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`paper-069, paper-030, paper-073`
- 回答长度变化：`96 -> 76`，delta `-20`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-base-topk3 回答**

```text
资料中没有说明 CRN 已经在某量产车型上部署，也没有给出部署成本。引用：- paper-069 unknown - paper-030 unknown - paper-073 unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
资料未说明 CRN 是否在某量产车型上部署，也未给出部署成本。

引用：
- paper-069 unknown
- paper-030 unknown
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- qwen3-4b-base-topk3 检索来源：`apollo-doc-008, apollo-doc-006, apollo-doc-008`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`apollo-doc-008, apollo-doc-006, apollo-doc-008`
- 回答长度变化：`77 -> 70`，delta `-7`
- qwen3-4b-base-topk3 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.8`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-base-topk3 回答**

```text
感知红绿灯信息对应的 channel 是 /apollo/perception/traffic_light。引用：
- source_id locator
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
/apollo/perception/traffic_light

引用：
- apollo-doc-008 locator=unknown
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- qwen3-4b-base-topk3 检索来源：`apollo-doc-005, apollo-doc-005, apollo-doc-005`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`apollo-doc-005, apollo-doc-005, apollo-doc-005`
- 回答长度变化：`151 -> 105`，delta `-46`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`0.571`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.571`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-base-topk3 回答**

```text
Apollo 感知融合模块最终输出到 /apollo/perception/obstacles 障碍物 channel。

引用：
- source_id apollo-doc-005 locator unknown
- source_id apollo-doc-005 locator unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
Apollo感知融合模块的输出是多传感器融合之后的障碍物信息，输出到 /apollo/perception/obstacles channel。

引用：
- apollo-doc-005 unknown 1]
```

### gen-eval-009：hard_case_pattern_d

- 预期行为：`answer`
- 问题：文档中提到的 parameter-free design 主要想解决 BEV 感知中的什么问题？它试图与哪些相机因素解耦？
- qwen3-4b-base-topk3 检索来源：`paper-038, paper-078, paper-038`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`paper-038, paper-078, paper-038`
- 回答长度变化：`110 -> 53`，delta `-57`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.0`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-base-topk3 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的领域适应问题。它试图与相机的位置和姿态变化解耦。引用：  
- source_id paper-038 locator unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
它试图与相机位置和传感器位置解耦，以实现更好的泛化能力。

引用：
- paper-038 unknown
```

### gen-eval-010：hard_case_pattern_d

- 预期行为：`answer`
- 问题：Part-A2 Net 如何利用 3D 边界框标注中自动提供的免费监督信息？
- qwen3-4b-base-topk3 检索来源：`paper-066, paper-066, paper-066`
- qwen3-4b-e3-webui-adapter-topk3 检索来源：`paper-066, paper-066, paper-066`
- 回答长度变化：`302 -> 176`，delta `-126`
- qwen3-4b-base-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk3 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-base-topk3 参考覆盖率：`0.111`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e3-webui-adapter-topk3 参考覆盖率：`0.111`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-base-topk3 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过使用这些标注来学习更具判别性的 3D 特征。具体来说，Part-A2 Net 将 3D 边界框内的部分位置作为额外的监督信息，在第一阶段学习更好的 3D 特征。然后，在第二阶段，通过聚合每个 3D 候选框内的预测 3D 部分位置和点-wise 3D 特征，对框进行评分并细化其位置。引用：  
- source_id paper-066 locator unknown  
- source_id paper-066 locator unknown  
- source_id paper-066 locator unknown
```

**qwen3-4b-e3-webui-adapter-topk3 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过以下方式学习更有效的 3D 特征：首先，使用 3D 内部物体部分位置标签和分割标签作为额外监督，学习更好的 3D 特征；然后，将预测的 3D 内部物体部分位置和每个 3D 候选框内的点云特征进行聚合，以评分候选框并优化其位置。

引用：
- paper-066 unknown
```
