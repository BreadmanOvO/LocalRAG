# 微调前后对比报告：base vs e5_adapter

## 结论摘要

- 样本数：`10`
- 自动判定：`mixed_or_regressed`
- base 平均回答长度：`117.3`
- e5_adapter 平均回答长度：`110.7`
- 平均回答长度变化：`-6.6`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `0.2` |
| `answer_contract_risk_ratio_delta` | `0.0` |
| `answered_ratio_delta` | `0.0` |
| `citation_support_risk_ratio_delta` | `0.1` |
| `correct_refusal_ratio_delta` | `0.0` |
| `directional_contradiction_risk_ratio_delta` | `0.0` |
| `evidence_locator_hit_ratio_delta` | `0.0` |
| `evidence_source_hit_ratio_delta` | `0.0` |
| `forbidden_term_risk_ratio_delta` | `0.0` |
| `over_refusal_risk_ratio_delta` | `0.0` |
| `reference_coverage_ratio_delta` | `0.01` |
| `reference_coverage_risk_ratio_delta` | `0.0` |
| `refusal_ratio_delta` | `0.0` |
| `required_term_risk_ratio_delta` | `0.0` |
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
- base 检索来源：`apollo-doc-006, apollo-doc-006`
- e5_adapter 检索来源：`apollo-doc-006, apollo-doc-006`
- 回答长度变化：`139 -> 103`，delta `-36`
- base 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`1.0`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`1.0`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
自动驾驶视觉感知模块在 Apollo 中主要处理红绿灯检测、车道线检测和基于摄像头的障碍物检测任务。引用：
- source_id apollo-doc-006 locator unknown
- source_id apollo-doc-006 locator unknown
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
- base 检索来源：`paper-030, paper-030`
- e5_adapter 检索来源：`paper-030, paper-030`
- 回答长度变化：`59 -> 71`，delta `12`
- base 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`0.087`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.087`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
CRN 融合了相机和雷达两种传感器来构建 BEV 特征。引用：
- paper-030 locator=unknown
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
- base 检索来源：`apollo-doc-005, apollo-doc-005`
- e5_adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`117 -> 137`，delta `20`
- base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`1.0`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`1.0`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
不，Apollo 感知融合模块不仅仅依赖摄像头结果，而是结合了摄像头、毫米波雷达和激光雷达三种传感器的数据进行目标级融合。感知融合模块通过融合不同传感器的优势，提高了感知的准确性和可靠性。引用：
- source_id locator
```

**e5_adapter 回答**

```text
不，Apollo 感知融合模块不仅仅依赖摄像头结果。根据资料，Apollo 感知融合模块能够支持对摄像头、毫米波雷达和激光雷达传感器感知的结果进行目标级融合。通过结合不同传感器的优点，模块能够更准确地识别和跟踪障碍物。引用：
- apollo-doc-005 unknown
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- base 检索来源：`paper-030, paper-080`
- e5_adapter 检索来源：`paper-030, paper-080`
- 回答长度变化：`154 -> 141`，delta `-13`
- base 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`0.059`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.059`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
根据提供的资料，使用 4096 大小的查询可以减少 MFA 的延迟，具体来说，将查询数量从 All 减少到 4096 可以使 MFA 的延迟降低 76%。然而，关于检测指标的变化，资料中没有提供具体信息。因此，无法确定检测指标会发生什么变化。

引用：
- paper-030 locator=unknown
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
- base 检索来源：`apollo-doc-006, apollo-doc-005`
- e5_adapter 检索来源：`apollo-doc-006, apollo-doc-005`
- 回答长度变化：`79 -> 63`，delta `-16`
- base 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- base 参考覆盖率：`1.0`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`1.0`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
资料中没有给出Apollo视觉感知模块在雨夜施工区域的具体误检率。引用：
- source_id apollo-doc-006 locator unknown
```

**e5_adapter 回答**

```text
资料中没有给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。引用：
- apollo-doc-006 unknown
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- base 检索来源：`paper-069, paper-030`
- e5_adapter 检索来源：`paper-069, paper-030`
- 回答长度变化：`76 -> 76`，delta `0`
- base 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- base 参考覆盖率：`0.05`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.05`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
资料中没有说明 CRN 已经在某量产车型上部署，也没有给出部署成本。引用：- paper-069 unknown - paper-030 unknown
```

**e5_adapter 回答**

```text
资料中没有说明 CRN 已经在某量产车型上部署，也没有给出部署成本。引用：- paper-069 unknown - paper-030 unknown
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- base 检索来源：`apollo-doc-008, apollo-doc-006`
- e5_adapter 检索来源：`apollo-doc-008, apollo-doc-006`
- 回答长度变化：`78 -> 91`，delta `13`
- base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`0.4`；无来源数字：`无`；答案合同风险：`是`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.4`；无来源数字：`无`；答案合同风险：`是`；引用支持风险：`是`

**base 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 /apollo/prediction。引用：
- source_id locator
```

**e5_adapter 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 /apollo/prediction。引用：
- apollo-doc-008 locator=unknown
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- base 检索来源：`apollo-doc-005, apollo-doc-005`
- e5_adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`108 -> 90`，delta `-18`
- base 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`0.571`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.571`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
Apollo 感知融合模块最终输出到 /apollo/perception/obstacles 障碍物 channel。

引用：
- source_id apollo-doc-005 locator unknown
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
- base 检索来源：`paper-038, paper-078`
- e5_adapter 检索来源：`paper-038, paper-078`
- 回答长度变化：`113 -> 122`，delta `9`
- base 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`0.15`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.25`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的 domain adaptation 问题。它试图与相机的内参和外参因素解耦。引用：
- paper-038 locator=unknown
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
- base 检索来源：`paper-066, paper-066`
- e5_adapter 检索来源：`paper-066, paper-066`
- 回答长度变化：`250 -> 213`，delta `-37`
- base 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- e5_adapter 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- base 参考覆盖率：`0.111`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`
- e5_adapter 参考覆盖率：`0.111`；无来源数字：`无`；答案合同风险：`否`；引用支持风险：`否`

**base 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过使用这些标注来学习更有效的 3D 特征。具体来说，Part-A2 Net 利用 3D 内部部分位置标签和分割标签作为额外的监督信息，在第一阶段学习更好的 3D 特征。然后，在第二阶段，将预测的 3D 内部部分位置和每个 3D 候选框内的点-wise 3D 特征进行聚合，以对框进行评分并细化其位置。引用：  
- paper-066 locator=unknown  
- paper-066 locator=unknown
```

**e5_adapter 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过使用这些标注来学习更有效的 3D 特征。具体来说，Part-A2 Net 在第一阶段使用免费的 3D 内部部分位置标签和分割标签作为额外的监督信息，以学习更好的 3D 特征。然后，在第二阶段，预测的 3D 内部部分位置和每个 3D 候选框内的点-wise 3D 特征被聚合起来，以对框进行评分并细化其位置。引用：- paper-066 unknown
```
