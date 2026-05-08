# TransFusion: Robust LiDAR-Camera Fusion for 3D Object Detection with Transformers

## 概述

TransFusion是由香港大学和华中科技大学联合提出的LiDAR-Camera多模态融合3D目标检测方法，发表于CVPR 2022。该方法利用Transformer的cross-attention机制实现了LiDAR点云特征与相机图像特征的深度融合，解决了传统融合方法中模态对齐困难和融合策略粗糙的问题。TransFusion在nuScenes数据集上取得了当时最优的3D检测性能，展示了Transformer在多模态3D感知中的强大能力，为后续的多模态融合研究奠定了重要基础。

## 核心贡献

1. **基于查询的软关联融合机制**：提出使用LiDAR特征生成的查询（queries）通过Transformer cross-attention机制与相机特征进行软关联，避免了传统方法中基于硬投影（projection）的模态对齐方式，有效缓解了传感器标定误差和时间同步问题的影响。

2. **热力图初始化查询策略**：创新性地使用LiDAR BEV热力图的峰值位置来初始化Transformer的object queries，使得查询能够自适应地关注3D空间中的有效位置，显著提升了融合效率和检测精度。

3. **渐进式两阶段融合**：第一阶段仅使用LiDAR数据进行粗检测，生成高质量的候选查询；第二阶段将这些查询与相机特征通过cross-attention融合进行精炼。这种渐进式设计使模型能够充分利用LiDAR的空间精度和相机的语义丰富性。

4. **强大的鲁棒性**：由于采用了软关联机制，TransFusion在传感器缺失或退化场景下（如相机被遮挡或LiDAR点云稀疏）仍能保持相对稳定的性能，具有重要的实际部署价值。

## 方法架构

### 整体流程

TransFusion包含两个主要阶段：**LiDAR分支**（第一阶段）和**Fusion分支**（第二阶段），两个阶段通过Transformer查询机制连接。

### LiDAR分支：BEV特征提取与初始检测

**点云编码**：输入LiDAR点云首先通过体素化（Voxelization）和3D稀疏卷积网络进行特征提取。TransFusion支持多种点云编码器，包括VoxelNet和CenterPoint-style的稀疏卷积编码器。编码后的3D特征在Z轴上进行压缩，生成BEV特征图F_lidar。

**BEV热力图预测**：BEV特征图通过一个简单的卷积网络预测类别热力图H。热力图中每个类别的峰值位置对应潜在的目标中心点。热力图通过Focal Loss监督，与CenterPoint的热力图预测方式类似。

**查询初始化**：从热力图H中提取top-K个峰值位置（通常K=200-500），对每个峰值位置提取对应BEV特征图上的特征向量作为初始object query。这一步是TransFusion的关键创新：通过热力图指导查询初始化，使得模型只在有意义的位置投入计算资源，大幅提升了效率。

**初始框回归**：每个初始query通过一个小型FFN预测粗糙的3D bounding box参数，包括中心坐标、尺寸和朝向角。这些粗糙预测为后续的融合精炼提供了几何先验。

### Fusion分支：Transformer跨模态融合

**图像特征提取**：多视角相机图像通过标准的图像Backbone（如ResNet-50/101）和FPN进行特征提取，生成多尺度图像特征图。

**3D位置编码生成**：对于每个object query，将其对应的3D参考点（由热力图峰值位置和预测高度确定）通过相机内外参数投影到各视角的2D图像平面上，生成3D感知的位置编码。这一步确保了cross-attention在几何上是有意义的。

**Cross-Attention融合**：TransFusion的核心融合模块采用deformable cross-attention机制：

- **Query**：来自LiDAR分支的object queries（包含BEV特征和位置编码）。
- **Key和Value**：来自图像分支的特征图，结合3D位置编码。

对于每个query，其对应的3D参考点投影到各相机视角后，在投影位置周围采样多个图像特征点（deformable sampling），通过注意力权重加权聚合这些特征。注意力权重的计算考虑了query特征与key特征的相似度以及空间位置的几何关系。

**FFN精炼**：融合了图像特征的queries通过Transformer FFN层进行特征变换，随后通过回归头精炼3D框参数，输出最终的检测结果。

### 查询去噪与冗余处理

TransFusion中可能存在多个query预测同一个目标的情况。为此，模型采用了soft-NMS或center-based suppression策略对冗余预测进行抑制。与传统硬NMS不同，TransFusion使用基于中心距离的软抑制机制，根据预测中心点的距离对置信度进行衰减，保留最优的预测结果。

### 损失函数

总损失函数包含以下部分：

L = L_heatmap + L_init + L_fusion

- L_heatmap：LiDAR热力图的Focal Loss。
- L_init：第一阶段初始框回归的L1 Loss和IoU Loss。
- L_fusion：第二阶段融合精炼后的框回归L1 Loss和IoU Loss，以及分类Focal Loss。

两个阶段的损失共同优化，确保端到端的训练收敛。

## 实验结果

在**nuScenes**数据集上，TransFusion取得了当时最优的性能。具体而言：

- **纯LiDAR版本**（TransFusion-L）：68.9% NDS，61.3% mAP，与CenterPoint性能相当。
- **LiDAR-Camera融合版本**（TransFusion）：71.3% NDS，67.5% mAP，相比纯LiDAR版本提升了2.4% NDS和6.2% mAP，展示了相机融合带来的显著增益。

与同期的融合方法相比，TransFusion超越了PointPainting（64.6% NDS）、PointFusion（65.3% NDS）和MVP（66.4% NDS）等方法，在融合策略的有效性上建立了新的标杆。

**鲁棒性实验**是TransFusion的重要评估维度。在模拟相机输入缺失的场景下（随机丢弃部分相机视角），TransFusion的性能下降幅度远小于基于硬投影的融合方法，验证了软关联机制的鲁棒性。在极端情况下（仅保留2个相机视角），TransFusion仍能保持约69% NDS的性能。

**消融实验**表明：热力图初始化查询相比随机初始化提升了约1.5% NDS；cross-attention融合相比简单的特征拼接提升了约2% NDS；使用deformable attention相比标准attention在精度和效率上均有提升。

## 局限性与讨论

1. **计算开销较大**：Transformer cross-attention模块和多模态特征提取增加了计算量，推理速度约为10-15 FPS，难以满足某些实时性要求严格的场景。

2. **对图像分辨率敏感**：相机特征的质量对融合效果有重要影响。在低分辨率图像或图像质量退化的场景下，融合增益可能减小。

3. **融合深度有限**：当前的融合仅在第二阶段的查询层面进行，未在更早的特征提取阶段进行多模态交互，可能限制了融合的充分性。

4. **依赖LiDAR初始化**：TransFusion的查询由LiDAR热力图初始化，在纯视觉输入场景下无法直接使用。对于仅配备相机的低成本平台，需要额外的初始化方案。

5. **时序信息利用不足**：TransFusion主要在单帧层面进行融合，未充分利用多帧时序信息。后续工作如BEVFusion和UniAD在此方向上进行了扩展。

TransFusion通过Transformer的注意力机制优雅地解决了多模态融合中的对齐难题，为LiDAR-Camera融合3D检测建立了强有力的技术范式，对后续的多模态感知研究产生了广泛影响。
