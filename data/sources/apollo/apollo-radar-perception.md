# Apollo 雷达感知模块

## 概述

雷达感知（Radar Perception）是Apollo自动驾驶平台中负责毫米波雷达（Millimeter Wave Radar）数据处理的模块，主要承担目标检测、测速和跟踪任务。毫米波雷达通过发射和接收毫米波段（通常为77GHz）的电磁波，能够直接测量目标的距离、方位角和径向速度（Radial Velocity），具有全天候工作能力（不受雨雪雾等恶劣天气影响）、可直接测速、成本较低等优势。

在Apollo的多传感器融合架构中，雷达感知模块扮演着独特而重要的角色。与激光雷达和摄像头不同，雷达能够直接测量目标的多普勒速度（Doppler Velocity），这对于运动目标的状态估计和轨迹预测具有重要价值。同时，雷达的探测距离通常可达200米以上，远超激光雷达的有效探测范围（约100-150米），是实现远距离感知的关键传感器。Apollo平台支持多种商用毫米波雷达，包括Continental ARS408、Delphi ESR等前向雷达，以及角雷达（Corner Radar）用于侧向感知。

## 架构设计

雷达感知模块采用轻量级处理架构，整体分为数据解析、目标处理和输出三个阶段。

**数据解析阶段（Data Parsing Stage）**接收来自雷达传感器的原始数据报文，按照雷达通信协议进行解析，提取目标列表（Target List）和检测点（Detection Points）信息。不同厂商的雷达数据格式存在差异，Apollo通过统一的雷达适配层（Radar Adapter Layer）屏蔽底层差异，为上层提供标准化的目标数据接口。

**目标处理阶段（Target Processing Stage）**是模块的核心，包括目标过滤（Target Filtering）、目标聚类（Target Clustering）、目标跟踪（Target Tracking）和目标分类（Target Classification）。处理流程将原始雷达检测点转化为具有稳定身份标识和运动状态估计的目标列表。

**输出阶段（Output Stage）**将处理后的目标信息打包为Apollo标准的障碍物格式（Obstacle），通过Cyber RT的Channel发送给下游的传感器融合模块。输出的目标信息包括位置、速度、加速度、类别和置信度等属性。

## 核心组件

### 雷达数据适配器（Radar Adapter）

雷达数据适配器负责将不同厂商的雷达原始数据转换为Apollo内部统一的表示格式。主要功能包括：

- **协议解析（Protocol Parsing）**：解析雷达CAN总线或以太网数据报文，提取目标ID、距离（Range）、方位角（Azimuth）、径向速度（Radial Velocity）、雷达散射截面积（RCS, Radar Cross Section）等原始测量值。
- **坐标变换（Coordinate Transformation）**：将雷达测量值从极坐标系（Polar Coordinate）转换到车辆直角坐标系（Cartesian Coordinate）。变换公式为：x = R * cos(θ), y = R * sin(θ)，其中R为距离，θ为方位角。
- **数据校验（Data Validation）**：检查数据完整性和合理性，过滤无效测量值（如距离为零、速度超出物理范围的异常值）。

### 目标过滤器（Target Filter）

原始雷达数据包含大量噪声和杂波（Clutter），需要通过过滤器进行净化：

- **静态目标过滤（Static Target Filtering）**：雷达对静态目标的检测存在较多虚警（False Alarm），特别是路侧护栏、标志牌等物体产生的强反射。Apollo使用速度阈值法和多帧一致性检查来过滤静态杂波。对于自车运动补偿（Ego-motion Compensation），需要将目标速度与自车速度进行合成，计算目标在世界坐标系下的绝对速度。
- **多径效应过滤（Multipath Filtering）**：毫米波雷达存在多径传播（Multipath Propagation）问题，即电磁波经地面或建筑物反射后到达目标，导致虚假目标。Apollo通过空间聚类和时间一致性分析来识别和过滤多径产生的幽灵目标（Ghost Target）。
- **信噪比过滤（SNR Filtering）**：基于信噪比（Signal-to-Noise Ratio, SNR）阈值过滤低质量检测点，保留高置信度的目标。

### 目标聚类器（Target Clustering）

雷达目标聚类将空间上邻近的检测点聚合为单个目标。Apollo采用的聚类方法包括：

- **DBSCAN聚类（Density-Based Spatial Clustering）**：基于密度的聚类算法，能够自动发现任意形状的聚类，对噪声具有鲁棒性。算法参数包括邻域半径（Eps）和最小点数（MinPts），需要根据雷达特性和应用场景进行调优。
- **欧几里得聚类（Euclidean Clustering）**：基于欧几里得距离的简单聚类方法，计算效率高，适合实时应用。聚类结果通过计算簇内点的质心（Centroid）和边界框（Bounding Box）来表示目标位置和尺寸。

### 目标跟踪器（Radar Target Tracker）

雷达目标跟踪器基于贝叶斯滤波（Bayesian Filtering）框架，对聚类后的目标进行帧间关联和状态估计：

- **状态模型（State Model）**：使用匀速运动模型（Constant Velocity, CV）或匀加速运动模型（Constant Acceleration, CA）描述目标运动。状态向量通常包括位置（x, y）、速度（vx, vy）和加速度（ax, ay）。
- **观测模型（Measurement Model）**：将目标状态映射到雷达观测空间，考虑雷达的测量噪声特性。
- **滤波算法（Filtering Algorithm）**：采用扩展卡尔曼滤波（EKF）或无迹卡尔曼滤波（UKF, Unscented Kalman Filter）进行状态更新。UKF通过sigma点采样避免了EKF中的雅可比矩阵（Jacobian Matrix）计算，在非线性系统中具有更好的估计精度。
- **数据关联（Data Association）**：使用全局最近邻（GNN）或联合概率数据关联（JPDA, Joint Probabilistic Data Association）算法将当前帧观测与已有轨迹进行匹配。

## 算法与实现

### 雷达目标分类

雷达目标分类是根据雷达回波特征判断目标类型（车辆、行人、自行车等）的任务。由于雷达数据的稀疏性，传统基于规则的方法（如基于RCS和尺寸的分类）精度有限。Apollo采用的改进方法包括：

**基于特征工程的分类**：提取雷达目标的多维特征，包括RCS值、径向速度分布、尺寸估计、散射特性等，使用随机森林（Random Forest）或梯度提升树（Gradient Boosting Tree）进行分类。该方法在数据量有限的情况下表现良好。

**基于深度学习的分类**：随着雷达点云质量的提升，Apollo开始探索基于深度学习的雷达目标分类方法。将雷达检测点组织为伪图像或点云格式，使用轻量级CNN或PointNet进行特征提取和分类。

### 运动补偿与多帧融合

雷达运动补偿是处理自车运动对目标测量影响的关键步骤：

1. **自车运动估计（Ego-motion Estimation）**：利用IMU和轮速计数据估计自车在相邻帧间的位移和旋转
2. **坐标变换（Coordinate Transformation）**：将上一帧的目标位置变换到当前帧坐标系下
3. **位置预测（Position Prediction）**：基于目标运动模型预测目标在当前帧的位置
4. **残差计算（Residual Calculation）**：计算实际测量与预测位置的残差，用于滤波器更新

多帧融合通过维护目标的历史轨迹信息，利用时序信息提高检测稳定性和分类准确性。Apollo采用滑动窗口（Sliding Window）方法，保留最近N帧（通常5-10帧）的目标信息进行融合。

## 与其他模块的交互

雷达感知模块在Apollo系统中的交互关系：

**上游输入：**
- 雷达原始数据：来自前向雷达（Forward Radar）和角雷达（Corner Radar），通过`/apollo/sensor/radar/front`、`/apollo/sensor/radar/left`、`/apollo/sensor/radar/right`等Channel传输
- 定位数据：自车位姿信息，用于运动补偿和坐标变换
- 底盘数据：车速、转向角等信息，辅助运动补偿计算

**下游输出：**
- 雷达目标列表：通过`/apollo/sensor/radar/obstacles` Channel输出，包含目标的位置、速度、加速度、类别和置信度
- 原始检测点（可选）：为融合模块提供未处理的原始检测信息

**与融合模块的协同：**
- 雷达感知结果与激光雷达、摄像头感知结果在传感器融合模块中进行多传感器融合
- 雷达提供的径向速度信息可显著提升融合后目标速度估计的精度
- 雷达的远距离探测能力弥补了激光雷达和摄像头在远距离感知的不足

**与预测模块的协同：**
- 雷达直接测量的目标速度信息可辅助预测模块进行更准确的行为预测
- 雷达对目标加速度的估计有助于预测模块判断目标的运动意图

雷达感知模块虽然在空间分辨率和目标分类精度上不如激光雷达和摄像头，但其全天候工作能力和直接测速特性使其成为Apollo多传感器融合系统中不可或缺的组成部分，特别是在高速公路场景和恶劣天气条件下发挥关键作用。
