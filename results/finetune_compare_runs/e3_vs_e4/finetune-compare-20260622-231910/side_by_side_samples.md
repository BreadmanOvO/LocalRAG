# 微调前后对比报告：qwen3-4b-e3-webui-adapter-topk2 vs qwen3-4b-e4-webui-adapter-topk2

## 结论摘要

- 样本数：`10`
- 自动判定：`mixed_or_regressed`
- qwen3-4b-e3-webui-adapter-topk2 平均回答长度：`78.7`
- qwen3-4b-e4-webui-adapter-topk2 平均回答长度：`80.5`
- 平均回答长度变化：`1.8`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `0.1` |
| `answered_ratio_delta` | `0.0` |
| `citation_support_risk_ratio_delta` | `0.1` |
| `correct_refusal_ratio_delta` | `0.0` |
| `directional_contradiction_risk_ratio_delta` | `0.0` |
| `evidence_locator_hit_ratio_delta` | `0.0` |
| `evidence_source_hit_ratio_delta` | `0.0` |
| `over_refusal_risk_ratio_delta` | `0.0` |
| `reference_coverage_ratio_delta` | `0.0` |
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
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`apollo-doc-006, apollo-doc-006`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`apollo-doc-006, apollo-doc-006`
- 回答长度变化：`54 -> 54`，delta `0`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
红绿灯检测、车道线检测、基于摄像头的障碍物检测。

引用：
- apollo-doc-006 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
红绿灯检测、车道线检测、基于摄像头的障碍物检测。

引用：
- apollo-doc-006 unknown
```

### gen-eval-002：normal_answerable

- 预期行为：`answer`
- 问题：CRN 融合了哪两类传感器来构建 BEV 特征？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`paper-030, paper-030`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`paper-030, paper-030`
- 回答长度变化：`31 -> 31`，delta `0`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.0`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.0`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
相机和雷达。

引用：
- paper-030 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
相机和雷达。

引用：
- paper-030 unknown
```

### gen-eval-003：hallucination_prone

- 预期行为：`answer`
- 问题：Apollo 感知融合模块是否只依赖摄像头结果？请根据资料回答。
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`126 -> 99`，delta `-27`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
不，Apollo感知融合模块不只依赖摄像头结果，而是融合了摄像头、毫米波雷达和激光雷达三种传感器的感知结果，以实现更准确的目标检测和环境感知。

引用：
- apollo-doc-005 unknown
- apollo-doc-005 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
不，Apollo感知融合模块不只依赖摄像头结果，而是融合了摄像头、毫米波雷达和激光雷达三种传感器的感知结果，以达到更准确的目标检测和识别。

引用：
- apollo-doc-005 unknown
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`paper-030, paper-080`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`paper-030, paper-080`
- 回答长度变化：`47 -> 47`，delta `0`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.0`；无来源数字：`12.5`；引用支持风险：`是`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.0`；无来源数字：`12.5`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
延迟降低 76%，检测指标提升 12.5%。

引用：
- paper-030 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
延迟降低 76%，检测指标提升 12.5%。

引用：
- paper-030 unknown
```

### gen-eval-005：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否给出了 Apollo 视觉感知模块在雨夜施工区域的具体误检率？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`apollo-doc-006, apollo-doc-005`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`apollo-doc-006, apollo-doc-005`
- 回答长度变化：`41 -> 63`，delta `22`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`1.0`；无来源数字：`无`；引用支持风险：`否`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
资料未给出具体误检率。

引用：
- apollo-doc-006 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
资料未给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。

引用：
- apollo-doc-006 unknown
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`paper-069, paper-030`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`paper-069, paper-030`
- 回答长度变化：`56 -> 76`，delta `20`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`否`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.05`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
资料未说明 CRN 是否在某量产车型上部署，也未给出部署成本。

引用：
- paper-069 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
资料未说明 CRN 是否在某量产车型上部署，也未给出部署成本。

引用：
- paper-069 unknown
- paper-030 unknown
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`apollo-doc-008, apollo-doc-006`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`apollo-doc-008, apollo-doc-006`
- 回答长度变化：`48 -> 48`，delta `0`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.2`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.2`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
/apollo/prediction

引用：
- apollo-doc-008 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
/apollo/prediction

引用：
- apollo-doc-008 unknown
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`85 -> 85`，delta `0`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.571`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.571`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
Apollo感知融合模块最终输出到 /apollo/perception/obstacles channel。

引用：
- apollo-doc-005 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
Apollo感知融合模块最终输出到 /apollo/perception/obstacles channel。

引用：
- apollo-doc-005 unknown
```

### gen-eval-009：hard_case_pattern_d

- 预期行为：`answer`
- 问题：文档中提到的 parameter-free design 主要想解决 BEV 感知中的什么问题？它试图与哪些相机因素解耦？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`paper-038, paper-078`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`paper-038, paper-078`
- 回答长度变化：`122 -> 122`，delta `0`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.25`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.25`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的 domain adaptation 问题，它试图与相机的 intrinsic parameters 解耦。

引用：
- paper-038 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
文档中提到的 parameter-free design 主要想解决 BEV 感知中的 domain adaptation 问题，它试图与相机的 intrinsic parameters 解耦。

引用：
- paper-038 unknown
```

### gen-eval-010：hard_case_pattern_d

- 预期行为：`answer`
- 问题：Part-A2 Net 如何利用 3D 边界框标注中自动提供的免费监督信息？
- qwen3-4b-e3-webui-adapter-topk2 检索来源：`paper-066, paper-066`
- qwen3-4b-e4-webui-adapter-topk2 检索来源：`paper-066, paper-066`
- 回答长度变化：`177 -> 180`，delta `3`
- qwen3-4b-e3-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e4-webui-adapter-topk2 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-e3-webui-adapter-topk2 参考覆盖率：`0.111`；无来源数字：`无`；引用支持风险：`是`
- qwen3-4b-e4-webui-adapter-topk2 参考覆盖率：`0.111`；无来源数字：`无`；引用支持风险：`是`

**qwen3-4b-e3-webui-adapter-topk2 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，通过以下方式学习更好的 3D 特征：首先，使用这些标注的 3D 内部部分位置标签和分割标签作为额外监督，学习更有效的 3D 特征；然后，将预测的 3D 内部部分位置和每个 3D 候选框内的点云特征进行聚合，以评分候选框并优化其位置。

引用：
- paper-066 unknown
```

**qwen3-4b-e4-webui-adapter-topk2 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，即每个 3D 建议框内的点的相对位置，作为额外监督来学习更好的 3D 特征。这些信息在第一阶段用于学习更有效的 3D 特征，然后在第二阶段将预测的 3D 内部部分位置和每个 3D 建议框内的点的 3D 特征进行聚合，以评分框并优化其位置。

引用：
- paper-066 unknown
```
