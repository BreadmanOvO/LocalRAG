# Apollo Localization Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-vision-location-overview.pdf
- Original URL: https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E5%AE%9A%E4%BD%8D%E8%83%BD%E5%8A%9B/Apollo%E5%AE%9A%E4%BD%8D%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D/
- Language: zh
- Version: Apollo Doc CN 6.0
- Pages: 1
- Topic tags: [system_architecture, planning_control]

## Summary
Official Apollo localization material describing the localization stack, map alignment, and the role of high-precision position estimation in autonomous driving.

## Key points
- 本文档介绍Apollo定位模块以及ApolloMSF（Multi-SensorFusion）的原理。
- MSF定位模块原理 这里重点介绍（Multi-SensorFusion）定位模块实现原理，系统框图如下图所示： MSF定位系统以多种传感器数据和离线制作的高精度Lidar定位地图为输入，其中GNSSLocalization模块以车端 GPS信号和基站数据为输入，输出高精度RTK定位结果。LiDARLocalization模块以在线lidar扫描数据和高精度…

## Structured notes
### Pages 1-1
- [p.1] 本文档介绍Apollo定位模块以及ApolloMSF（Multi-SensorFusion）的原理。 Apollo定位模块 高精度、高鲁棒性的定位系统是自动驾驶系统不可或缺的基础模块。Apollo定位模块针对不同的应用需求提供了三 种不同实现方式的定位模块。 RTK（RealTimeKinematic）定位模块 利用GPS+IMU实现的全局定位导航系统，在GPS信号良好的情况下可以实现厘米级定位精度。 MSF（Multi-Sensor…
- [p.1] MSF定位模块原理 这里重点介绍（Multi-SensorFusion）定位模块实现原理，系统框图如下图所示： MSF定位系统以多种传感器数据和离线制作的高精度Lidar定位地图为输入，其中GNSSLocalization模块以车端 GPS信号和基站数据为输入，输出高精度RTK定位结果。LiDARLocalization模块以在线lidar扫描数据和高精度 Lidar定位地图为输入，提供高精度lidar定位结果。SINS模块利用IMU…

## Evidence-ready excerpts
- [p.1] 本文档介绍Apollo定位模块以及ApolloMSF（Multi-SensorFusion）的原理。 Apollo定位模块 高精度、高鲁棒性的定位系统是自动驾驶系统不可或缺的基础模块。Apollo定位模块针对不同的应用需求提供了三 种不同实现方式的定位模块。 RTK（RealTimeKinematic）定位模块 利用GPS+IMU实现的全局定位导航系统，在GPS信号良好的情况下可以实现厘米级定位精度。 MSF（Multi-SensorFusion）定位模块 结合GPS+IMU+Lidar实现的多传感器融合全局定位导航系统，利用多传感器优缺点的互补，实现高精度、高鲁棒 性的定位能力。对于GPS失效或者Lidar地图环境变更场景具备一定的冗余处理能力。本模块可提供城市道路、高 速、部分隧道等场景下的定位能力。 NDT（NormalDistributionTransform）定位模块 结合GPS+IMU+Lidar实现的简单融合定位系统，其中lidar定位采用开源NDT算法实现。本系统依赖GPS信号 质量，具备简单城市场景下的高精度，鲁棒的定位能力。
- [p.1] MSF定位模块原理 这里重点介绍（Multi-SensorFusion）定位模块实现原理，系统框图如下图所示： MSF定位系统以多种传感器数据和离线制作的高精度Lidar定位地图为输入，其中GNSSLocalization模块以车端 GPS信号和基站数据为输入，输出高精度RTK定位结果。LiDARLocalization模块以在线lidar扫描数据和高精度 Lidar定位地图为输入，提供高精度lidar定位结果。SINS模块利用IMU数据进行惯性导航。后端采用error-state Kalmanfilter融合多种传感器量测信息。输出高精度的车辆位置和姿态。

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
