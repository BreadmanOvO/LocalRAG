# 微调前后对比报告：e4_adapter vs e5_adapter

## 结论摘要

- 样本数：`10`
- 自动判定：`mixed`
- e4_adapter 平均回答长度：`80.5`
- e5_adapter 平均回答长度：`110.7`
- 平均回答长度变化：`30.2`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `0.0` |
| `answered_ratio_delta` | `0.0` |
| `citation_support_risk_ratio_delta` | `0.0` |
| `correct_refusal_ratio_delta` | `0.0` |
| `directional_contradiction_risk_ratio_delta` | `-0.1` |
| `evidence_locator_hit_ratio_delta` | `0.0` |
| `evidence_source_hit_ratio_delta` | `0.0` |
| `over_refusal_risk_ratio_delta` | `0.0` |
| `reference_coverage_ratio_delta` | `0.035` |
| `reference_coverage_risk_ratio_delta` | `0.0` |
| `refusal_ratio_delta` | `0.0` |
| `unsupported_claim_risk_ratio_delta` | `0.0` |
| `unsupported_numeric_claim_risk_ratio_delta` | `-0.1` |

## 人工复核重点

- adapter 是否真的更会引用资料，而不是只改了措辞。
- adapter 是否只是回答变短，导致看起来更保守。
- adapter 是否对本来可回答的问题开始过度拒答。
- hard case 中是否减少无依据扩展。

## 逐样本并排对比

### gen-eval-001：normal_answerable

- 预期行为：`answer`
- 问题：自动驾驶视觉感知模块在 Apollo 中主要处理哪些任务？
- e4_adapter 检索来源：`apollo-doc-006, apollo-doc-006`
- e5_adapter 检索来源：`apollo-doc-006, apollo-doc-006`
- 回答长度变化：`54 -> 103`，delta `49`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**e4_adapter 回答**

```text
红绿灯检测、车道线检测、基于摄像头的障碍物检测。

引用：
- apollo-doc-006 unknown
```

**e5_adapter 回答**

```text
自动驾驶视觉感知模块在 Apollo 中主要处理红绿灯检测、车道线检测和基于摄像头的障碍物检测任务。引用：
- apollo-doc-006 unknown
- apollo-doc-006 unknown
```

### gen-eval-002：normal_answerable

- 预期行为：`answer`
- 问题：CRN 融合了哪两类传感器来构建 BEV 特征？
- e4_adapter 检索来源：`paper-030, paper-030`
- e5_adapter 检索来源：`paper-030, paper-030`
- 回答长度变化：`31 -> 71`，delta `40`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.0`；无来源数字：`无`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.087`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
相机和雷达。

引用：
- paper-030 unknown
```

**e5_adapter 回答**

```text
CRN 融合了相机和雷达两种传感器来构建 BEV 特征。引用：
- paper-030 unknown
- paper-030 unknown
```

### gen-eval-003：hallucination_prone

- 预期行为：`answer`
- 问题：Apollo 感知融合模块是否只依赖摄像头结果？请根据资料回答。
- e4_adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- e5_adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`99 -> 137`，delta `38`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**e4_adapter 回答**

```text
不，Apollo感知融合模块不只依赖摄像头结果，而是融合了摄像头、毫米波雷达和激光雷达三种传感器的感知结果，以达到更准确的目标检测和识别。

引用：
- apollo-doc-005 unknown
```

**e5_adapter 回答**

```text
不，Apollo 感知融合模块不仅仅依赖摄像头结果。根据资料，Apollo 感知融合模块能够支持对摄像头、毫米波雷达和激光雷达传感器感知的结果进行目标级融合。通过结合不同传感器的优点，模块能够更准确地识别和跟踪障碍物。引用：
- apollo-doc-005 unknown
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- e4_adapter 检索来源：`paper-030, paper-080`
- e5_adapter 检索来源：`paper-030, paper-080`
- 回答长度变化：`47 -> 141`，delta `94`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.0`；无来源数字：`12.5`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.059`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
延迟降低 76%，检测指标提升 12.5%。

引用：
- paper-030 unknown
```

**e5_adapter 回答**

```text
根据提供的资料，使用 4096 大小的查询可以减少 MFA 的延迟，具体来说，将查询数量从全部减少到 4096 会降低 MFA 的延迟 76%。然而，关于检测指标的变化，资料中没有提供具体信息。因此，无法确定检测指标会发生什么变化。

引用：
- paper-030 unknown
```

### gen-eval-005：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否给出了 Apollo 视觉感知模块在雨夜施工区域的具体误检率？
- e4_adapter 检索来源：`apollo-doc-006, apollo-doc-005`
- e5_adapter 检索来源：`apollo-doc-006, apollo-doc-005`
- 回答长度变化：`63 -> 63`，delta `0`
- e4_adapter 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**e4_adapter 回答**

```text
资料未给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。

引用：
- apollo-doc-006 unknown
```

**e5_adapter 回答**

```text
资料中没有给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。引用：
- apollo-doc-006 unknown
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- e4_adapter 检索来源：`paper-069, paper-030`
- e5_adapter 检索来源：`paper-069, paper-030`
- 回答长度变化：`76 -> 76`，delta `0`
- e4_adapter 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
资料未说明 CRN 是否在某量产车型上部署，也未给出部署成本。

引用：
- paper-069 unknown
- paper-030 unknown
```

**e5_adapter 回答**

```text
资料中没有说明 CRN 已经在某量产车型上部署，也没有给出部署成本。引用：- paper-069 unknown - paper-030 unknown
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- e4_adapter 检索来源：`apollo-doc-008, apollo-doc-006`
- e5_adapter 检索来源：`apollo-doc-008, apollo-doc-006`
- 回答长度变化：`48 -> 91`，delta `43`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.2`；无来源数字：`无`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.4`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
/apollo/prediction

引用：
- apollo-doc-008 unknown
```

**e5_adapter 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 /apollo/prediction。引用：
- apollo-doc-008 locator=unknown
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- e4_adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- e5_adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`85 -> 90`，delta `5`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.571`；无来源数字：`无`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.571`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
Apollo感知融合模块最终输出到 /apollo/perception/obstacles channel。

引用：
- apollo-doc-005 unknown
```

**e5_adapter 回答**

```text
Apollo 感知融合模块最终输出到 /apollo/perception/obstacles 障碍物 channel。

引用：
- apollo-doc-005 unknown
```

### gen-eval-009：hard_case_pattern_d

- 预期行为：`answer`
- 问题：文档中提到的 parameter-free design 主要想解决 BEV 感知中的什么问题？它试图与哪些相机因素解耦？
- e4_adapter 检索来源：`paper-038, paper-078`
- e5_adapter 检索来源：`paper-038, paper-078`
- 回答长度变化：`122 -> 122`，delta `0`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.25`；无来源数字：`无`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.25`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的 domain adaptation 问题，它试图与相机的 intrinsic parameters 解耦。

引用：
- paper-038 unknown
```

**e5_adapter 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的 domain adaptation 问题。它试图与相机的 intrinsic parameters 解耦。

引用：
- paper-038 unknown
```

### gen-eval-010：hard_case_pattern_d

- 预期行为：`answer`
- 问题：Part-A2 Net 如何利用 3D 边界框标注中自动提供的免费监督信息？
- e4_adapter 检索来源：`paper-066, paper-066`
- e5_adapter 检索来源：`paper-066, paper-066`
- 回答长度变化：`180 -> 213`，delta `33`
- e4_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e4_adapter 参考覆盖率：`0.111`；无来源数字：`无`；引用支持风险：`是`
- e5_adapter 参考覆盖率：`0.111`；无来源数字：`无`；引用支持风险：`是`

**e4_adapter 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，即每个 3D 建议框内的点的相对位置，作为额外监督来学习更好的 3D 特征。这些信息在第一阶段用于学习更有效的 3D 特征，然后在第二阶段将预测的 3D 内部部分位置和每个 3D 建议框内的点的 3D 特征进行聚合，以评分框并优化其位置。

引用：
- paper-066 unknown
```

**e5_adapter 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过使用这些标注来学习更有效的 3D 特征。具体来说，Part-A2 Net 在第一阶段使用免费的 3D 内部部分位置标签和分割标签作为额外的监督信息，以学习更好的 3D 特征。然后，在第二阶段，预测的 3D 内部部分位置和每个 3D 候选框内的点-wise 3D 特征被聚合起来，以对框进行评分并细化其位置。引用：- paper-066 unknown
```
