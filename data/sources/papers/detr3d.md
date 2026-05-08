# DETR3D: 3D Object Detection from Multi-view Images via 3D-to-2D Queries

## 概述

DETR3D 是由清华大学和麻省理工学院联合提出的基于纯视觉的3D目标检测方法，发表于CoRL 2021。该方法将DETR（Detection Transformer）的集合预测范式从2D检测扩展到3D空间，通过引入3D reference points实现从多视角图像中直接进行3D目标检测，无需依赖LiDAR点云数据。DETR3D是首个将Transformer架构成功应用于多相机3D目标检测的端到端框架，对后续BEV（Bird's Eye View）感知研究产生了深远影响。

## 核心贡献

1. **3D-to-2D Query机制**：提出了一种新颖的从3D空间到2D图像平面的投影采样机制。模型首先在3D空间中生成reference points，然后通过相机内外参数将这些3D点投影到各视角的2D图像上，从而采样对应的图像特征，实现了3D检测与多视角2D特征的高效融合。

2. **端到端集合预测**：借鉴DETR的设计，采用固定数量的object queries直接预测3D bounding boxes，消除了传统方法中anchor设计、NMS后处理等繁琐步骤，实现了真正的端到端3D检测。

3. **无需深度估计**：与许多依赖显式深度估计的纯视觉方法不同，DETR3D隐式地通过几何变换学习3D空间信息，避免了深度估计带来的误差累积问题。

4. **多尺度特征融合**：在Transformer decoder中引入多尺度特征交互，增强了模型对不同尺度目标的检测能力。

## 方法架构

### 整体流程

DETR3D的整体架构包含三个核心模块：**Backbone网络**、**Transformer检测头**和**集合预测损失**。

**Backbone网络**采用ResNet结合FPN（Feature Pyramid Network）作为图像特征提取器。输入为多视角（通常为6个相机）图像，经过Backbone后生成多尺度特征图。每个尺度的特征图保留了丰富的空间和语义信息，为后续的3D特征采样提供基础。

**3D Reference Points生成**是DETR3D的核心创新。对于每一个object query，模型通过一个小型MLP预测其对应的3D reference point坐标（x, y, z）。这些3D坐标随后通过已知的相机投影矩阵（包含内参和外参）投影到各个相机视角的2D图像平面上。

**特征采样与聚合**阶段，投影后的2D坐标用于在对应图像特征图上进行双线性插值采样。对于投影落在图像边界内的视角，采样其特征；落在边界外的视角则被mask掉。采样得到的多视角特征通过可学习的加权聚合机制融合为统一的特征表示。

**Transformer Decoder**包含多层deformable attention层。每一层中，object queries首先通过self-attention进行交互，然后通过cross-attention与采样得到的图像特征进行融合。解码器输出的特征经过FFN（Feed-Forward Network）预测最终的3D bounding box参数，包括中心坐标（x, y, z）、尺寸（l, w, h）、朝向角（heading angle）和类别置信度。

### 损失函数

DETR3D采用匈牙利匹配算法（Hungarian Matching）建立predicted boxes与ground truth之间的最优一对一匹配，然后基于匹配结果计算损失。损失函数包含三个部分：

- **分类损失**：使用Focal Loss处理前景/背景分类以及多类别分类问题。
- **3D IoU损失**：计算预测框与GT框之间的IoU loss，用于监督bounding box的回归质量。
- **L1回归损失**：对bounding box的中心坐标和尺寸参数施加L1损失，提供稳定的梯度信号。

总损失函数为三者的加权和：L = λ_cls * L_cls + λ_iou * L_iou + λ_L1 * L_L1。

## 实验结果

DETR3D在nuScenes数据集上进行了全面评估。在nuScenes val set上，DETR3D达到了30.3% NDS（nuScenes Detection Score）和34.9% mAP，显著超越了当时的纯视觉方法如FCOS3D（28.8% NDS）。在nuScenes test set的排行榜上，DETR3D提交时取得了43.4% NDS的成绩，展示了纯视觉方法在3D检测任务上的竞争力。

与基于LiDAR的方法相比，DETR3D虽然在绝对精度上仍有差距（如CenterPoint LiDAR版本达到67.3% NDS），但考虑到其仅使用相机输入且无需昂贵的LiDAR传感器，这一结果具有重要的实际意义。消融实验表明，3D-to-2D投影机制相比直接在BEV空间进行特征提取的方案，在精度和效率上均具有优势。

在推理速度方面，DETR3D在单张V100 GPU上达到了约6.1 FPS，虽然不及PointPillars等实时LiDAR方法，但在纯视觉方法中具有合理的计算开销。

## 局限性与讨论

DETR3D存在以下主要局限性：

1. **训练收敛慢**：受DETR本身特性影响，DETR3D需要较长的训练周期（通常需要24个epoch）才能收敛，远超传统检测器的训练时间。

2. **对相机参数的依赖**：模型需要精确的相机内外参数进行3D到2D的投影，在相机标定不准确的场景下性能可能下降。

3. **小目标检测能力有限**：由于采样点数量有限且采样策略相对粗糙，DETR3D对远距离小目标的检测能力受到一定制约。

4. **缺乏时序信息融合**：DETR3D仅利用单帧信息，未考虑多帧时序信息对3D检测的增益作用，后续工作如PETRv2和StreamPETR在此方向上进行了改进。

尽管存在上述局限，DETR3D作为开创性工作，为纯视觉3D感知开辟了新的研究方向，启发了大量后续BEV感知和Transformer-based 3D检测方法的发展。
