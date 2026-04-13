# Apollo Vision Perception Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-vision-perception-overview.pdf
- Original URL: https://developer.apollo.auto/platform/perception_cn.html
- Language: zh
- Version: Apollo Perception CN
- Pages: 4
- Topic tags: [perception, sensor_fusion]

## Summary
Official Apollo perception material describing the perception module, its obstacle understanding responsibilities, and how visual perception supports autonomous driving.

## Key points
- 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。因 此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。视觉感知算法在Apollo平 台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。
- 视觉感知模块的原理 红绿灯检测模块原理 红绿灯检测模块的主要作用是检测当前路况下在摄像头的视觉范围内的红绿灯的状态，这是一个典型的目标检测任 务。如下图所示，红绿灯检测模块一共包含4个部分，分别是数据预处理、红绿灯位置检测、红绿灯识别和矫正。
- 4.最后，矫正器主要针对识别置信度不高的情况，通过查询前面几帧的检测状态对当前的红绿灯颜色进行矫正。
- 障碍物检测模块原理 障碍物检测部分采用的是基于单目视觉的障碍物检测算法，根据相机获取的图像得到障碍的类别和位置信息。

## Structured notes
### Pages 1-2
- [p.1] 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。因 此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。视觉感知算法在Apollo平 台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。 神经网络模型 红绿灯识别 红绿灯信息 多个目标投 红绿灯检测 提取检测ROI 票(voting) 车道线后处 车道线检测 图像预处理 camera 障…
- [p.1] 视觉感知模块的原理 红绿灯检测模块原理 红绿灯检测模块的主要作用是检测当前路况下在摄像头的视觉范围内的红绿灯的状态，这是一个典型的目标检测任 务。如下图所示，红绿灯检测模块一共包含4个部分，分别是数据预处理、红绿灯位置检测、红绿灯识别和矫正。 1.通常红绿灯在图像中所占比例比较低，为了能够有效的检测出红绿灯，我们会借助高精地图给出的的信息预先从 相机图像中将包含红绿灯区域的大致位置取出来。 2.红绿灯位置检测部分采用了一种常规的基于C…
- [p.2] 4.最后，矫正器主要针对识别置信度不高的情况，通过查询前面几帧的检测状态对当前的红绿灯颜色进行矫正。 交通灯投影，相机选择输入：不同摄像头，定位信息，高精地图，标是结架 图像缓存和信号灯同步输出：选择摄像头的图像，交通灯图像坐耘筹的原理 红绿灯检测模块原理 车道线检测模块原理 输入：摄像机图像伟导精紧息 ·提供交通灯准确的位置信息 输出：交通灯位置边框和类别（形状属性） 红绿灯检测模块 输实碍通效的图像和形状属性 ·识别检测到的交通等…

### Pages 3-4
- [p.3] 红绿灯检测模块 红绿灯检测模块输入输入如下表所示： channel名称 /apollo/sensor/camera/front_6mm /apollo/sensor/camera/front_12mm /apollo/perception/traffic_light 障碍物检测模块 障碍物检测模块输入输入如下表所示： channel名称 /apollo/sensor/camera/front_6mm /apollo/sensor/ca…
- [p.4] /apollo/localization/pose 王车速度和用速度 /perception/obstacles 具有航向、速度和分类信息的三维障碍物轨迹 视觉感知模块简介 输出给融合模块的障碍物偏感知模块的原理 /perception/inner/Prefusedobjects 红绿灯检测模块原理 车道线检测模块原理 [±h/2] ±w/2 ±l/2] 输入：RGB图像IERWXHx3 输出：物体类别C和3D边框 （h,w,l)：物…

## Evidence-ready excerpts
- [p.1] 但摄像头有着容易受环境影响、缺乏深度信息等缺点，给无人驾驶系统中的视觉感知算法带来了巨大的挑战。因 此，如何建立一套高精确率和高稳定性的视觉感知算法，是无人车感知模块的核心问题。视觉感知算法在Apollo平 台上主要有3个应用场景，分别是红绿灯检测、车道线检测、基于摄像头的障碍物检测。 神经网络模型 红绿灯识别 红绿灯信息 多个目标投 红绿灯检测 提取检测ROI 票(voting) 车道线后处 车道线检测 图像预处理 camera 障碍物信息 摄像头障碍物 摄像头障碍 2D到3D转换 多传感器 其他传感器 障碍物信息 每个模块又可以分为3部分，分别是图像的预处理、神经网络模型以及后处理。 ·预处理：对上游信息做一些处理和整合，以方便把信息直接输入到模型中做预测。 ·神经网络模型：主要涉及一些深度学习算法，包括目标检测、语义分割、图像分类等。 ·后处理：为了优化模型效果，我们会利用一些传统的算法进一步优化网络模型的预测，让我们的算法可以在实车 上跑得更加流畅。
- [p.2] 障碍物检测模块原理 障碍物检测部分采用的是基于单目视觉的障碍物检测算法，根据相机获取的图像得到障碍的类别和位置信息。 这里使用7个变量来表示3D边框，分别是物体的长宽高，物体的位置x，y，z以及物体的旋转角度日。 检测模块 分类结果（x1,x2…xc) 2D 边框[x,y,w,h ]2D 3D形状[w",h',l']3D 3D 中心[xy]p,z3D 3D角度3D 3D角点x（m），y"（m），z（m） 上图是3D障碍物检测模块的模型结构图，输入的是单张的图像信息，经过神经网络提取特征，最后接上检测模块 (Apollo有两个检测模型，分别是基于YOLO的one-stage检测方法和基于中心点检测的检测方法)。
- [p.4] /apollo/localization/pose 王车速度和用速度 /perception/obstacles 具有航向、速度和分类信息的三维障碍物轨迹 视觉感知模块简介 输出给融合模块的障碍物偏感知模块的原理 /perception/inner/Prefusedobjects 红绿灯检测模块原理 车道线检测模块原理 [±h/2] ±w/2 ±l/2] 输入：RGB图像IERWXHx3 输出：物体类别C和3D边框 （h,w,l)：物体长宽高（米） （x,y，z）：中心点坐标（米） 设定K= 物体的偏航角 如果您在使用文档的过程中，遇到任何问题，请到我们在【开发者社区】建立的反馈意见收集问答页面，反馈相关 的问题。我们会根据反馈意见对文档进行选代优化。 实时通信框架CyberRT Apollo视觉感知模块

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
