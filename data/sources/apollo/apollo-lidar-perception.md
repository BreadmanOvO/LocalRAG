# Apollo 激光雷达感知模块

## 概述

激光雷达感知（LiDAR Perception）是Apollo自动驾驶平台中最为关键的感知模块之一，负责基于激光雷达点云数据进行三维目标检测与识别。激光雷达传感器通过发射激光脉冲并接收反射信号，能够获取高精度的三维空间信息，具有测量精度高、不受光照条件影响等优势，是实现L4级自动驾驶的核心传感器。

Apollo平台的激光雷达感知模块经历了从Apollo 3.0到Apollo 8.0的持续演进，从早期依赖传统点云处理方法逐步过渡到以深度学习为核心的端到端检测框架。该模块的主要任务包括：三维障碍物检测（3D Object Detection）、点云分割（Point Cloud Segmentation）、目标跟踪（Object Tracking）以及点云配准（Point Cloud Registration）。在实际部署中，激光雷达感知模块需要在保证高召回率（Recall）的同时，将误检率（False Positive Rate）控制在可接受范围内，并满足实时性要求（通常在100ms以内完成一帧处理）。

## 架构设计

Apollo激光雷达感知模块采用流水线（Pipeline）架构，整体分为数据预处理、特征提取与检测、后处理三个主要阶段。

**数据预处理阶段**接收来自激光雷达传感器的原始点云数据（通常为Velodyne VLP-16、HDL-64E或自研激光雷达），进行去噪（Noise Filtering）、地面点去除（Ground Removal）和感兴趣区域裁剪（ROI Cropping）。预处理后的点云被组织为体素化（Voxelization）格式，以便后续神经网络高效处理。

**特征提取与检测阶段**是模块的核心，采用基于体素的三维卷积神经网络（Voxel-based 3D CNN）或基于点的直接处理网络（Point-based Network）对点云进行特征编码，然后通过检测头（Detection Head）输出候选目标的三维边界框（3D Bounding Box）、类别标签和置信度分数。

**后处理阶段**包括非极大值抑制（NMS, Non-Maximum Suppression）、时序融合（Temporal Fusion）和轨迹关联（Trajectory Association），将检测结果与历史帧进行关联，输出稳定的目标轨迹。

模块内部各组件通过Cyber RT框架的Channel进行通信，主要数据流为：原始点云 -> 预处理 -> 检测网络 -> NMS -> 融合输出。

## 核心组件

### 点云预处理器（Point Cloud Preprocessor）

点云预处理器负责将原始点云数据转换为适合神经网络处理的格式。主要操作包括：

- **坐标变换（Coordinate Transform）**：将点云从传感器坐标系转换到车辆坐标系（Vehicle Frame）和世界坐标系（World Frame），需要依赖高精度定位模块提供的位姿信息。
- **地面分割（Ground Segmentation）**：采用RANSAC（Random Sample Consensus）算法或基于高度图（Height Map）的方法拟合地面平面，将地面点与非地面点分离，减少后续检测的计算量。
- **体素化（Voxelization）**：将三维空间划分为均匀的小立方体（Voxel），每个体素内保留若干个点云特征。体素大小通常设置为0.1m x 0.1m x 0.15m，在精度和计算效率之间取得平衡。

### 三维检测网络（3D Detection Network）

Apollo支持多种三维检测网络架构，主要包括：

- **PointPillars**：将点云组织为柱状体（Pillar），通过PointNet提取特征后生成伪图像（Pseudo Image），再使用2D卷积网络进行检测。该方法推理速度快，适合实时部署。
- **CenterPoint**：基于中心点检测的无锚框（Anchor-Free）方法，通过预测目标中心点的热力图（Heatmap）和回归偏移量来定位目标，避免了锚框设计的先验假设。
- **VoxelNet / SECOND**：基于体素的三维卷积网络，使用稀疏卷积（Sparse Convolution）高效处理稀疏点云数据，在检测精度和速度之间取得良好平衡。

检测网络输出每个候选目标的七自由度（7-DoF）三维边界框，包括中心坐标（x, y, z）、尺寸（长、宽、高）和偏航角（Yaw Angle）。

### 目标跟踪器（Object Tracker）

目标跟踪器基于卡尔曼滤波（Kalman Filter）或扩展卡尔曼滤波（Extended Kalman Filter, EKF）对检测到的目标进行帧间关联和轨迹管理。跟踪过程包括：

- **数据关联（Data Association）**：采用匈牙利算法（Hungarian Algorithm）或GNN（Global Nearest Neighbor）方法，将当前帧检测结果与已有轨迹进行匹配。
- **状态更新（State Update）**：对匹配成功的轨迹，使用滤波器更新目标的位置、速度和加速度估计。
- **轨迹管理（Track Management）**：维护轨迹的生命周期状态，包括初始化（Tentative）、确认（Confirmed）和丢失（Lost）状态。

## 算法与实现

### 体素特征编码

体素特征编码是将离散点云转换为规则表示的关键步骤。Apollo采用的体素特征编码器（Voxel Feature Encoder, VFE）对每个体素内的点云进行特征聚合：

1. 计算体素内所有点的均值作为体素中心
2. 将每个点与体素中心的偏移量拼接到原始特征（x, y, z, intensity, elongation）
3. 通过全连接层（Fully Connected Layer）和最大池化（Max Pooling）聚合体素特征

对于稀疏体素，Apollo使用子流形稀疏卷积（Submanifold Sparse Convolution）避免在空白区域进行无效计算，显著提升推理效率。

### 后处理与优化

检测网络输出的原始结果需要经过多个后处理步骤：

- **NMS（非极大值抑制）**：使用旋转IoU（Intersection over Union）计算三维边界框的重叠度，去除冗余检测。Apollo实现了GPU加速的旋转NMS，支持BEV（Bird's Eye View）视角下的快速抑制。
- **多帧融合（Multi-frame Fusion）**：将当前帧检测结果与历史N帧（通常3-5帧）的结果进行融合，利用时序信息提高检测稳定性。融合方法包括简单拼接（Concatenation）和基于注意力的时序聚合（Attention-based Temporal Aggregation）。

## 与其他模块的交互

激光雷达感知模块在Apollo系统中与多个上下游模块紧密协作：

**上游模块：**
- 传感器驱动模块（Sensor Driver）：提供原始点云数据，通过`/apollo/sensor/lidar/point_cloud` Channel传输
- 定位模块（Localization）：提供车辆位姿信息，用于点云坐标变换，通过`/apollo/localization/pose` Channel传输
- 高精地图模块（HD Map）：提供道路结构信息，用于ROI裁剪和语义增强

**下游模块：**
- 传感器融合模块（Sensor Fusion）：接收激光雷达检测结果，与摄像头、雷达检测结果进行多传感器融合
- 预测模块（Prediction）：接收融合后的目标信息，进行行为预测
- 规划模块（Planning）：基于预测结果进行路径规划

**关键数据通道（Channel）：**
- 输入：`/apollo/sensor/lidar/point_cloud`（原始点云）、`/apollo/localization/pose`（定位信息）
- 输出：`/apollo/perception/obstacles`（检测到的障碍物列表）、`/apollo/perception/point_cloud/segmented`（分割后的点云）

在实际系统中，激光雷达感知模块的输出延迟通常在50-80ms之间，检测精度（AP@0.7 IoU）在标准benchmark上达到80%以上，是Apollo自动驾驶系统中最可靠的感知源之一。
