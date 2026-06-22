# 微调前后对比报告：qwen3-4b-base-citation vs qwen3-4b-webui-e1-adapter-citation

## 结论摘要

- 样本数：`10`
- 自动判定：`mixed_or_regressed`
- qwen3-4b-base-citation 平均回答长度：`240.0`
- qwen3-4b-webui-e1-adapter-citation 平均回答长度：`258.1`
- 平均回答长度变化：`18.1`

## 行为指标变化

| 指标 delta | 数值 |
| --- | ---: |
| `answer_cites_evidence_ratio_delta` | `-0.1` |
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
- qwen3-4b-base-citation 检索来源：`apollo-doc-006, apollo-doc-006`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`apollo-doc-006, apollo-doc-006`
- 回答长度变化：`266 -> 402`，delta `136`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
自动驾驶视觉感知模块在 Apollo 中主要处理以下任务：

1. 红绿灯检测  
2. 车道线检测  
3. 基于摄像头的障碍物检测  

引用：  
- source_id=apollo-doc-006, locator=资料内容：1] 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。 因 此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。 视觉感知算法在Apollo平 台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
1. **红绿灯检测**：检测摄像头视野内的红绿灯状态，属于典型的目标检测任务，包含数据预处理、红绿灯位置检测、红绿灯识别和矫正等步骤。

2. **车道线检测**：识别道路中的车道线，帮助车辆保持在正确的车道内。

3. **基于摄像头的障碍物检测**：通过摄像头进行障碍物的检测，为自动驾驶系统提供周围环境中的障碍物信息。

这些任务共同构成了视觉感知模块的核心功能，为自动驾驶系统提供关键的环境感知数据。

引用：  
- source_id=apollo-doc-006, locator=资料内容：1] 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。 因 此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。 视觉感知算法在Apollo平 台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。
```

### gen-eval-002：normal_answerable

- 预期行为：`answer`
- 问题：CRN 融合了哪两类传感器来构建 BEV 特征？
- qwen3-4b-base-citation 检索来源：`paper-030, paper-030`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`paper-030, paper-030`
- 回答长度变化：`287 -> 287`，delta `0`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
CRN 融合了相机和雷达两类传感器来构建 BEV 特征。  
引用：  
- source_id paper-030 locator=资料内容：kr  
- source_id paper-030 locator=资料内容：be adaptive in order to tackle noisy and ambiguous radar measurements. To this end, we design a novel two-stage fusion method for BEV feature encoding, Camera Radar Net (CRN).
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
CRN 融合了相机和雷达两类传感器来构建 BEV 特征。  
引用：  
- source_id paper-030 locator=资料内容：kr  
- source_id paper-030 locator=资料内容：be adaptive in order to tackle noisy and ambiguous radar measurements. To this end, we design a novel two-stage fusion method for BEV feature encoding, Camera Radar Net (CRN).
```

### gen-eval-003：hallucination_prone

- 预期行为：`answer`
- 问题：Apollo 感知融合模块是否只依赖摄像头结果？请根据资料回答。
- qwen3-4b-base-citation 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`407 -> 407`，delta `0`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
Apollo 感知融合模块**不只依赖摄像头结果**。该模块支持对摄像头、毫米波雷达和激光雷达三种传感器的感知结果进行目标级融合，通过融合不同传感器的数据，结合各传感器的优势，提升整体感知的准确性和鲁棒性。因此，Apollo 感知融合模块是多传感器融合的，而非仅依赖摄像头。

引用：
- source_id=apollo-doc-005 locator=资料内容：1] Apollo感知融合能力介绍 传感群性能比较 感知融合模块的原理 感知融合模块的相关参数 文栏意见反馈 本文档旨在简要介绍Apollo感知融合模块的原理和过程，并且说明运行Apollo感知融合模块的步骤。 通过本文 档，您可以了解到以下内容： ·Apollo的感知融合原理 Apollo感知融合模块的输入与输出channel信息 传感器性能比较 在Apollo感知模块里，多传感器融合是一个重要的环节，并且也是感知的最后环节。 在感知模块里…
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
Apollo 感知融合模块**不只依赖摄像头结果**。该模块支持对摄像头、毫米波雷达和激光雷达三种传感器的感知结果进行目标级融合，通过融合不同传感器的数据，结合各传感器的优势，提升整体感知的准确性和鲁棒性。因此，Apollo 感知融合模块是多传感器融合的，而非仅依赖摄像头。

引用：
- source_id=apollo-doc-005 locator=资料内容：1] Apollo感知融合能力介绍 传感群性能比较 感知融合模块的原理 感知融合模块的相关参数 文栏意见反馈 本文档旨在简要介绍Apollo感知融合模块的原理和过程，并且说明运行Apollo感知融合模块的步骤。 通过本文 档，您可以了解到以下内容： ·Apollo的感知融合原理 Apollo感知融合模块的输入与输出channel信息 传感器性能比较 在Apollo感知模块里，多传感器融合是一个重要的环节，并且也是感知的最后环节。 在感知模块里…
```

### gen-eval-004：hallucination_prone

- 预期行为：`answer`
- 问题：使用稀疏聚合时，把 Top-K 查询数从 All 减少到 4096，会让 MFA 延迟和检测指标发生什么变化？
- qwen3-4b-base-citation 检索来源：`paper-030, paper-080`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`paper-030, paper-080`
- 回答长度变化：`184 -> 184`，delta `0`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
使用稀疏聚合时，将 Top-K 查询数从 All 减少到 4096，会显著降低 MFA 的延迟，具体表现为 MFA 的延迟降低 76%。关于检测指标，资料中未明确说明具体变化，但减少查询数量可以降低优化难度，可能有助于提升检测性能。

引用：
- source_id paper-030 locator= 
- source_id paper-080 locator=
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
使用稀疏聚合时，将 Top-K 查询数从 All 减少到 4096，会显著降低 MFA 的延迟，具体表现为 MFA 的延迟降低 76%。关于检测指标，资料中未明确说明具体变化，但减少查询数量可以降低优化难度，可能有助于提升检测性能。

引用：
- source_id paper-030 locator= 
- source_id paper-080 locator=
```

### gen-eval-005：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否给出了 Apollo 视觉感知模块在雨夜施工区域的具体误检率？
- qwen3-4b-base-citation 检索来源：`apollo-doc-006, apollo-doc-005`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`apollo-doc-006, apollo-doc-005`
- 回答长度变化：`75 -> 75`，delta `0`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
资料未给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。引用：  
- source_id=apollo-doc-006, locator=
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
资料未给出 Apollo 视觉感知模块在雨夜施工区域的具体误检率。引用：  
- source_id=apollo-doc-006, locator=
```

### gen-eval-006：insufficient_context

- 预期行为：`refuse`
- 问题：资料是否说明 CRN 已经在某量产车型上部署，并给出了部署成本？
- qwen3-4b-base-citation 检索来源：`paper-069, paper-030`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`paper-069, paper-030`
- 回答长度变化：`195 -> 195`，delta `0`
- qwen3-4b-base-citation 引用证据：`否`；拒答：`是`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`否`；拒答：`是`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
根据提供的资料内容，并未说明CRN已经在某量产车型上部署，也未给出相关的部署成本信息。资料中仅提到“Car class mAP in the same manner as CRN [13]”以及“0%) while CRN still”，但这些内容并未涉及CRN的部署情况或成本。因此，无法从现有资料中得出相关结论。

引用：
- source_id=paper-069, locator=
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
根据提供的资料内容，并未说明CRN已经在某量产车型上部署，也未给出相关的部署成本信息。资料中仅提到“Car class mAP in the same manner as CRN [13]”以及“0%) while CRN still”，但这些内容并未涉及CRN的部署情况或成本。因此，无法从现有资料中得出相关结论。

引用：
- source_id=paper-069, locator=
```

### gen-eval-007：distractor_context

- 预期行为：`answer`
- 问题：Apollo 规划模块输入中的感知红绿灯信息对应哪个 channel？
- qwen3-4b-base-citation 检索来源：`apollo-doc-008, apollo-doc-006`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`apollo-doc-008, apollo-doc-006`
- 回答长度变化：`328 -> 328`，delta `0`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 `/apollo/prediction`。  
引用：  
- source_id=apollo-doc-008, locator=规划模块的输入 channel名称 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light输入是 感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
Apollo 规划模块输入中的感知红绿灯信息对应的 channel 是 `/apollo/prediction`。  
引用：  
- source_id=apollo-doc-008, locator=规划模块的输入 channel名称 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light输入是 感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息
```

### gen-eval-008：distractor_context

- 预期行为：`answer`
- 问题：Apollo 感知融合模块最终输出到哪个障碍物 channel？
- qwen3-4b-base-citation 检索来源：`apollo-doc-005, apollo-doc-005`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`apollo-doc-005, apollo-doc-005`
- 回答长度变化：`92 -> 92`，delta `0`
- qwen3-4b-base-citation 引用证据：`否`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
Apollo 感知融合模块最终输出到的障碍物 channel 是 `/apollo/perception/obstacles`。  
引用：  
- source_id locator
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
Apollo 感知融合模块最终输出到的障碍物 channel 是 `/apollo/perception/obstacles`。  
引用：  
- source_id locator
```

### gen-eval-009：hard_case_pattern_d

- 预期行为：`answer`
- 问题：文档中提到的 parameter-free design 主要想解决 BEV 感知中的什么问题？它试图与哪些相机因素解耦？
- qwen3-4b-base-citation 检索来源：`paper-038, paper-078`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`paper-038, paper-078`
- 回答长度变化：`183 -> 181`，delta `-2`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
文档中提到的 **parameter-free design** 主要想解决 **BEV 感知中的领域适应（domain adaptation）** 问题。它试图与 **相机的内在参数**（如焦距、畸变参数等）解耦。  

引用：  
- source_id=paper-038, locator=  
- source_id=paper-078, locator=
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
文档中提到的 **parameter-free design** 主要想解决 **BEV 感知中的领域适应（domain adaptation）** 问题。它试图与 **相机的内在参数**（如焦距、畸变参数等）解耦。

引用：  
- source_id=paper-038, locator=  
- source_id=paper-078, locator=
```

### gen-eval-010：hard_case_pattern_d

- 预期行为：`answer`
- 问题：Part-A2 Net 如何利用 3D 边界框标注中自动提供的免费监督信息？
- qwen3-4b-base-citation 检索来源：`paper-066, paper-066`
- qwen3-4b-webui-e1-adapter-citation 检索来源：`paper-066, paper-066`
- 回答长度变化：`383 -> 430`，delta `47`
- qwen3-4b-base-citation 引用证据：`是`；拒答：`否`；过度拒答风险：`否`
- qwen3-4b-webui-e1-adapter-citation 引用证据：`否`；拒答：`否`；过度拒答风险：`否`

**qwen3-4b-base-citation 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，主要通过以下方式实现：

- 利用 3D 边界框内的点的“内部部分位置标签”（intra-object part locations），这些标签提供了丰富的结构信息，帮助模型学习更具判别性的 3D 特征。
- 利用 3D 边界框标注隐含的语义分割信息，即每个点在 3D 真实边界框内的位置，作为“免费的语义掩码”，进一步增强模型对物体内部结构的理解。

在第一阶段，Part-A2 Net 使用这些监督信息作为额外的训练信号，学习更丰富的 3D 特征；在第二阶段，模型将预测的 3D 内部部分位置和点云特征进行聚合，以对边界框进行评分并优化其位置。

引用：  
- source_id=paper-066, locator=  
- source_id=paper-066, locator=
```

**qwen3-4b-webui-e1-adapter-citation 回答**

```text
Part-A2 Net 利用 3D 边界框标注中自动提供的免费监督信息，主要通过以下方式实现：

- **利用 3D 内部部分位置标签**：3D 边界框标注中包含了每个点在该边界框内的相对位置信息（即“intra-object part locations”）。这些信息为模型提供了丰富的结构信息，帮助模型学习更具判别性的 3D 特征，而传统方法通常未充分利用此类信息。
- **利用语义分割标签**：3D 边界框标注还隐含了语义分割信息，即每个点在 3D 真实边界框内的位置，这可以视为一种“免费的语义掩码”。这些信息进一步增强了模型对物体内部结构的理解。

**实现方式**：  
在第一阶段，Part-A2 Net 利用上述两种监督信息（内部部分位置标签和语义分割标签）作为额外的监督信号，学习更丰富的 3D 特征。在第二阶段，模型将预测的 3D 内部部分位置和点云特征进行聚合，以对边界框进行评分并优化其位置。

引用：  
- source_id=p
```
