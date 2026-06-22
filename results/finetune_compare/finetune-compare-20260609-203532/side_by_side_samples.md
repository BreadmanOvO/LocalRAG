# 微调前后对比报告：qwen3-4b-base vs qwen3-4b-webui-e1-adapter

## 结论摘要

- 样本数：`10`
- 自动判定：`no_clear_change`
- qwen3-4b-base 平均回答长度：`183.7`
- qwen3-4b-webui-e1-adapter 平均回答长度：`179.5`
- 平均回答长度变化：`-4.2`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `0.0` |
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
- qwen3-4b-base 检索来源：`apollo-doc-006, apollo-doc-006`
- qwen3-4b-webui-e1-adapter 检索来源：`apollo-doc-006, apollo-doc-006`
- 回答长度变化：`239 -> 205`，delta `-34`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
在 Apollo 平台中，自动驾驶视觉感知模块主要处理以下任务：

1. **红绿灯检测**：检测摄像头视野内的红绿灯状态，属于典型的目标检测任务，包含数据预处理、红绿灯位置检测、红绿灯识别和矫正等步骤。

2. **车道线检测**：识别道路中的车道线，帮助车辆保持在正确的车道内。

3. **基于摄像头的障碍物检测**：通过摄像头进行障碍物的检测，为自动驾驶系统提供周围环境中的障碍物信息。

这些任务共同构成了视觉感知模块的核心功能，为自动驾驶系统提供关键的环境感知数据。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
1. **红绿灯检测**：检测摄像头视野内的红绿灯状态，属于典型的目标检测任务，包含数据预处理、红绿灯位置检测、红绿灯识别和矫正等步骤。

2. **车道线检测**：识别道路中的车道线，帮助车辆保持在正确的车道内。

3. **基于摄像头的障碍物检测**：通过摄像头进行障碍物的检测，为自动驾驶系统提供周围环境中的障碍物信息。

这些任务共同构成了视觉感知模块的核心功能，为自动驾驶系统提供关键的环境感知数据。
```

### gen-eval-002：normal_answerable

- 预期行为：`answer`
- 问题：CRN 融合了哪两类传感器来构建 BEV 特征？
- qwen3-4b-base 检索来源：`paper-030, paper-030`
- qwen3-4b-webui-e1-adapter 检索来源：`paper-030, paper-030`
- 回答长度变化：`28 -> 28`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
CRN 融合了相机和雷达两类传感器来构建 BEV 特征。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
CRN 融合了相机和雷达两类传感器来构建 BEV 特征。
```

### gen-eval-003：hallucination_prone

- 预期行为：`answer`
- 问题：Apollo 感知融合模块是否只依赖摄像头结果？请根据资料回答。
- qwen3-4b-base 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-webui-e1-adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`142 -> 142`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
根据资料，Apollo 感知融合模块**不只依赖摄像头结果**。该模块支持对摄像头、毫米波雷达和激光雷达三种传感器的感知结果进行目标级融合，通过融合不同传感器的数据，结合各传感器的优势，提升整体感知的准确性和鲁棒性。因此，Apollo 感知融合模块是多传感器融合的，而非仅依赖摄像头。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
根据资料，Apollo 感知融合模块**不只依赖摄像头结果**。该模块支持对摄像头、毫米波雷达和激光雷达三种传感器的感知结果进行目标级融合，通过融合不同传感器的数据，结合各传感器的优势，提升整体感知的准确性和鲁棒性。因此，Apollo 感知融合模块是多传感器融合的，而非仅依赖摄像头。
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- qwen3-4b-base 检索来源：`paper-030, paper-080`
- qwen3-4b-webui-e1-adapter 检索来源：`paper-030, paper-080`
- 回答长度变化：`389 -> 389`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
根据提供的资料，当使用稀疏聚合将 Top-K 查询数从 All 减少到 4096 时，会对 MFA 的延迟和检测指标产生以下影响：

1. **延迟降低**：将 Top-K 查询数从 All 减少到 4096 可以显著减少 Multi-modal Deformable Cross Attention (MDCA) 的计算量，从而降低 MFA 的延迟。具体而言，使用 4096 大小的查询可将 MFA 的延迟降低 76%。

2. **检测指标变化**：减少查询数量（即从 All 减少到 4096）可以降低优化难度，有助于提升模型的检测性能。虽然资料中未明确提及具体的检测指标（如 mAP、FPS 等）变化，但可以推测，由于计算效率的提升和训练稳定性增强，检测指标可能会有所改善。

综上，减少 Top-K 查询数到 4096 会显著降低 MFA 的延迟，并可能提升检测性能。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
根据提供的资料，当使用稀疏聚合将 Top-K 查询数从 All 减少到 4096 时，会对 MFA 的延迟和检测指标产生以下影响：

1. **延迟降低**：将 Top-K 查询数从 All 减少到 4096 可以显著减少 Multi-modal Deformable Cross Attention (MDCA) 的计算量，从而降低 MFA 的延迟。具体而言，使用 4096 大小的查询可将 MFA 的延迟降低 76%。

2. **检测指标变化**：减少查询数量（即从 All 减少到 4096）可以降低优化难度，有助于提升模型的检测性能。虽然资料中未明确提及具体的检测指标（如 mAP、FPS 等）变化，但可以推测，由于计算效率的提升和训练稳定性增强，检测指标可能会有所改善。

综上，减少 Top-K 查询数到 4096 会显著降低 MFA 的延迟，并可能提升检测性能。
```

### gen-eval-005：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否给出了 Apollo 视觉感知模块在雨夜施工区域的具体误检率？
- qwen3-4b-base 检索来源：`apollo-doc-006, apollo-doc-005`
- qwen3-4b-webui-e1-adapter 检索来源：`apollo-doc-006, apollo-doc-005`
- 回答长度变化：`113 -> 113`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`是`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
根据提供的资料，未给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。资料主要介绍了 Apollo 视觉感知模块的应用场景、原理以及感知融合模块的功能，但未涉及具体环境下的误检率数据。因此，无法从现有资料中获取该信息。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
根据提供的资料，未给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。资料主要介绍了 Apollo 视觉感知模块的应用场景、原理以及感知融合模块的功能，但未涉及具体环境下的误检率数据。因此，无法从现有资料中获取该信息。
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- qwen3-4b-base 检索来源：`paper-069, paper-030`
- qwen3-4b-webui-e1-adapter 检索来源：`paper-069, paper-030`
- 回答长度变化：`158 -> 158`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`是`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
根据提供的资料内容，并未说明CRN已经在某量产车型上部署，也未给出相关的部署成本信息。资料中仅提到“Car class mAP in the same manner as CRN [13]”以及“0%) while CRN still”，但这些内容并未涉及CRN的部署情况或成本。因此，无法从现有资料中得出相关结论。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
根据提供的资料内容，并未说明CRN已经在某量产车型上部署，也未给出相关的部署成本信息。资料中仅提到“Car class mAP in the same manner as CRN [13]”以及“0%) while CRN still”，但这些内容并未涉及CRN的部署情况或成本。因此，无法从现有资料中得出相关结论。
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- qwen3-4b-base 检索来源：`apollo-doc-008, apollo-doc-006`
- qwen3-4b-webui-e1-adapter 检索来源：`apollo-doc-008, apollo-doc-006`
- 回答长度变化：`57 -> 57`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 `/apollo/prediction`。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 `/apollo/prediction`。
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- qwen3-4b-base 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-webui-e1-adapter 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`64 -> 64`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
Apollo 感知融合模块最终输出到的障碍物 channel 是 `/apollo/perception/obstacles`。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
Apollo 感知融合模块最终输出到的障碍物 channel 是 `/apollo/perception/obstacles`。
```

### gen-eval-009：hard_case_pattern_d

- 预期行为：`answer`
- 问题：文档中提到的 parameter-free design 主要想解决 BEV 感知中的什么问题？它试图与哪些相机因素解耦？
- qwen3-4b-base 检索来源：`paper-038, paper-078`
- qwen3-4b-webui-e1-adapter 检索来源：`paper-038, paper-078`
- 回答长度变化：`225 -> 225`，delta `0`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
文档中提到的 **parameter-free design** 主要想解决 **BEV 感知中的领域适应（domain adaptation）** 问题。由于不同传感器（如激光雷达和相机）获取的数据在分布上可能存在差异，导致模型在不同场景下的泛化能力不足，因此需要一种不依赖特定传感器参数的通用设计。

该设计试图与 **相机的内在参数** 解耦，例如相机的焦距、畸变参数等，以提高模型对不同相机配置的适应能力，从而增强模型在不同场景下的泛化性能。
```

**qwen3-4b-webui-e1-adapter 回答**

```text
文档中提到的 **parameter-free design** 主要想解决 **BEV 感知中的领域适应（domain adaptation）** 问题。由于不同传感器（如激光雷达和相机）获取的数据在分布上可能存在差异，导致模型在不同场景下的泛化能力不足，因此需要一种不依赖特定传感器参数的通用设计。

该设计试图与 **相机的内在参数** 解耦，例如相机的焦距、畸变参数等，以提高模型对不同相机配置的适应能力，从而增强模型在不同场景下的泛化性能。
```

### gen-eval-010：hard_case_pattern_d

- 预期行为：`answer`
- 问题：Part-A2 Net 如何利用 3D 边界框标注中自动提供的免费监督信息？
- qwen3-4b-base 检索来源：`paper-066, paper-066`
- qwen3-4b-webui-e1-adapter 检索来源：`paper-066, paper-066`
- 回答长度变化：`422 -> 414`，delta `-8`
- qwen3-4b-base 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base 回答**

```text
Part-A2 Net 通过利用 3D 边界框标注中自动提供的免费监督信息，增强了对点云中 3D 物体的检测能力。具体来说，它利用了以下两种关键类型的监督信息：

1. **3D 内部部分位置标签**：  
   3D 边界框标注中包含了每个点在该边界框内的相对位置信息（即“intra-object part locations”）。这些信息为模型提供了丰富的结构信息，帮助模型学习更具判别性的 3D 特征，而传统方法通常未充分利用此类信息。

2. **语义分割标签**：  
   3D 边界框标注还隐含了语义分割信息，即每个点在 3D 真实边界框内的位置，这可以视为一种“免费的语义掩码”。这些信息进一步增强了模型对物体内部结构的理解。

**实现方式**：  
在第一阶段，Part-A2 Net 利用上述两种监督信息（内部部分位置标签和语义分割标签）作为额外的监督信号，学习更丰富的 3D 特征。在第二阶段，模型将预测的 3D 内部
```

**qwen3-4b-webui-e1-adapter 回答**

```text
Part-A2 Net 通过以下方式利用 3D 边界框标注中自动提供的免费监督信息：

1. **3D 内部部分位置标签**：  
   3D 边界框标注中包含了每个点在该边界框内的相对位置信息（即“intra-object part locations”）。这些信息为模型提供了丰富的结构信息，帮助模型学习更具判别性的 3D 特征，而传统方法通常未充分利用此类信息。

2. **语义分割标签**：  
   3D 边界框标注还隐含了语义分割信息，即每个点在 3D 真实边界框内的位置，这可以视为一种“免费的语义掩码”。这些信息进一步增强了模型对物体内部结构的理解。

**实现方式**：  
在第一阶段，Part-A2 Net 利用上述两种监督信息（内部部分位置标签和语义分割标签）作为额外的监督信号，学习更丰富的 3D 特征。在第二阶段，模型将预测的 3D 内部部分位置和点云特征进行聚合，以对边界框进行评分并优化其位置。
```
