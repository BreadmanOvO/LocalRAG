# Apollo 预测模块

## 概述

预测模块（Prediction Module）是Apollo自动驾驶平台中连接感知与规划的关键桥梁，负责基于感知模块提供的周围障碍物状态信息，预测这些障碍物在未来一段时间内的运动轨迹和行为意图。准确的预测对于自动驾驶车辆的安全规划至关重要——规划模块需要知道周围车辆是否会变道、行人是否会横穿马路、自行车是否会转弯，才能规划出安全、高效的行驶轨迹。

Apollo预测模块的核心任务包括轨迹预测（Trajectory Prediction）和行为预测（Behavior Prediction）。轨迹预测给出障碍物在未来预测时域（Prediction Horizon，通常为3-8秒）内的具体位置序列；行为预测判断障碍物的高层意图（如直行、左转、右转、停车等）。预测模块的输入来自感知模块的障碍物检测结果和定位模块的自车位姿信息，输出为包含多模态预测轨迹（Multi-modal Trajectory）及其概率分布的预测结果，通过`/apollo/prediction` Channel发送给规划模块。

## 架构设计

Apollo预测模块采用模块化架构，由四个核心子模块组成：信息容器（Container）、场景选择器（Scenario）、评估器（Evaluator）和预测器（Predictor）。

**信息容器（Container）**负责存储和管理上游输入信息，包括感知信息容器（Perception Container）、定位信息容器（Localization Container）和规划信息容器（Planning Container）。信息容器对原始数据进行预处理和特征提取，为后续预测提供结构化的输入特征。感知信息容器维护障碍物的历史轨迹序列（通常保留最近N帧），用于计算运动特征（如速度、加速度、曲率等）。

**场景选择器（Scenario）**根据当前驾驶场景（如巡航Cruising、路口Intersection、汇入Merging等）选择相应的预测策略。不同场景下障碍物的运动模式差异显著——路口场景中车辆的转向意图更为重要，而巡航场景中车辆的跟车行为和变道意图是预测重点。场景选择器通过有限状态机（Finite State Machine）管理场景切换。

**评估器（Evaluator）**基于障碍物的状态信息和预测模型，评估障碍物采取不同行为的可能性。评估器输出行为概率（如直行概率0.7、左转概率0.2、右转概率0.1）和短期轨迹预测（通常为1-2秒）。

**预测器（Predictor）**结合评估器的结果，生成障碍物在完整预测时域内的多模态预测轨迹。每条预测轨迹附带概率权重，表示该轨迹的置信度。

## 核心组件

### 轨迹生成器（Trajectory Generator）

轨迹生成器负责生成候选预测轨迹。Apollo支持多种轨迹生成方法：

**基于规则的轨迹生成（Rule-based Trajectory Generation）**：对于运动模式较为固定的场景（如跟车、停车），使用运动学模型（Kinematic Model）生成轨迹。常用的运动学模型包括：
- 恒速模型（Constant Velocity, CV）：假设目标保持当前速度直线运动
- 恒加速模型（Constant Acceleration, CA）：假设目标保持当前加速度运动
- 恒曲率模型（Constant Turn Rate, CTR）：假设目标以恒定转弯速率运动

**基于车道序列的轨迹生成（Lane Sequence-based Trajectory Generation）**：在结构化道路上，将目标的运动约束在车道序列（Lane Sequence）上。预测模块首先识别目标可能的车道序列（如当前车道直行、向左变道、向右变道），然后在每条车道序列上生成符合车道几何形状的轨迹。该方法的优势在于生成的轨迹自然符合道路结构，避免了不合理轨迹的产生。

**基于神经网络的轨迹生成（Neural Network-based Trajectory Generation）**：使用深度学习模型直接从输入特征生成预测轨迹。常用模型架构包括：
- 循环神经网络（RNN, Recurrent Neural Network）/ LSTM（Long Short-Term Memory）：处理时序输入，捕捉目标的历史运动模式
- 图神经网络（GNN, Graph Neural Network）：建模多个障碍物之间的交互关系
- 条件变分自编码器（CVAE, Conditional Variational Autoencoder）：生成多模态预测轨迹，捕捉运动的不确定性

### 行为预测器（Behavior Predictor）

行为预测器判断障碍物的高层运动意图。Apollo采用分层预测策略：

**意图分类（Intent Classification）**：使用分类模型（如MLP、LSTM或Transformer）将障碍物的行为意图分为有限类别：直行（Go Straight）、左转（Turn Left）、右转（Turn Right）、停车（Stop）、变道（Lane Change）等。分类模型输入包括障碍物的运动特征（速度、加速度、航向角变化率）、周围环境特征（车道线位置、交通信号灯状态）和交互特征（与自车的距离、相对速度）。

**交互建模（Interaction Modeling）**：障碍物的行为受到周围其他交通参与者的影响。Apollo使用注意力机制（Attention Mechanism）或图注意力网络（GAT, Graph Attention Network）建模障碍物之间的交互关系。例如，一辆车可能因为旁边车辆的变道而减速，这种交互效应需要在预测中被捕捉。

### 场景识别器（Scenario Recognizer）

场景识别器负责识别当前驾驶场景并选择合适的预测策略：

- **巡航场景（Cruising Scenario）**：车辆在高速或城市快速路上行驶，主要关注跟车行为和变道意图
- **路口场景（Intersection Scenario）**：车辆接近或通过路口，主要关注转向意图和信号灯响应
- **汇入/汇出场景（Merging/Diverging Scenario）**：车辆在匝道汇入或汇出，主要关注合流行为
- **行人横穿场景（Pedestrian Crossing Scenario）**：行人可能横穿马路，主要关注行人意图和速度

场景识别基于高精地图信息（如是否在路口区域）、交通信号灯状态和障碍物位置等信息进行综合判断。

## 算法与实现

### 多模态轨迹预测

多模态轨迹预测是Apollo预测模块的核心算法，旨在生成多条可能的未来轨迹及其概率。实现方法包括：

**基于聚类的多模态预测**：对历史轨迹数据进行聚类，每个聚类中心代表一种典型的运动模式。预测时，将当前障碍物状态与各聚类中心匹配，生成对应模式的预测轨迹。该方法简单直观，但难以处理复杂的交互场景。

**基于CVAE的多模态预测**：使用条件变分自编码器生成多模态轨迹。CVAE的编码器（Encoder）将真实未来轨迹编码为隐变量（Latent Variable），解码器（Decoder）结合隐变量和输入条件生成预测轨迹。预测时，从先验分布中采样多个隐变量，生成多条候选轨迹。损失函数包括重构损失（Reconstruction Loss）和KL散度（KL Divergence）：L = E[||τ - τ̂||²] + β * KL(q(z|τ) || p(z))，其中β为平衡系数。

**基于Transformer的预测**：Apollo最新版本引入了基于Transformer的预测架构，利用自注意力机制（Self-attention）捕捉障碍物之间的长程依赖关系。输入特征通过位置编码（Positional Encoding）和多头注意力（Multi-Head Attention）进行处理，输出多模态轨迹和对应的概率分布。

### 预测评估指标

Apollo预测模块使用以下指标评估预测质量：

- **最小平均位移误差（minADE, Minimum Average Displacement Error）**：多条预测轨迹中与真实轨迹最接近的那条的平均位移误差
- **最小终点位移误差（minFDE, Minimum Final Displacement Error）**：预测轨迹终点与真实轨迹终点的最小距离
- **碰撞率（Collision Rate）**：预测轨迹与自车规划轨迹发生碰撞的比例
- **意图分类准确率（Intent Classification Accuracy）**：行为意图预测的准确率

## 与其他模块的交互

预测模块在Apollo系统中承上启下，与多个模块紧密交互：

**上游输入：**
- 感知模块：通过`/apollo/perception/obstacles` Channel接收障碍物的位置、速度、加速度、航向角和类别信息
- 定位模块：通过`/apollo/localization/pose` Channel接收自车的位置、速度和姿态信息
- 规划模块：通过`/apollo/planning` Channel接收自车规划轨迹，用于计算障碍物与自车的交互关系
- 高精地图：提供道路拓扑、车道线、交通规则等先验信息

**下游输出：**
- 预测轨迹：通过`/apollo/prediction` Channel输出障碍物的多模态预测轨迹及概率分布，供规划模块使用
- 预测轨迹格式：每个障碍物包含多条候选轨迹（通常3-5条），每条轨迹包含未来3-8秒的位置序列和对应概率

**与规划模块的协同：**
- 预测模块为规划模块提供障碍物的未来运动估计，规划模块据此评估候选轨迹的安全性
- 预测结果的不确定性通过概率分布传递给规划模块，规划模块可据此进行鲁棒规划（Robust Planning）
- 规划模块的自车轨迹信息反馈给预测模块，用于建模自车与周围障碍物的交互

预测模块的性能直接影响自动驾驶系统的安全性和舒适性。Apollo预测模块在nuScenes预测benchmark上的minADE指标达到1.2米以下（3秒预测时域），意图分类准确率达到90%以上。
