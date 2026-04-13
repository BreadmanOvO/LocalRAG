# Apollo Open Platform Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/Apollo-Open-Platform-overview.pdf
- Original URL: https://developer.apollo.auto/developer.html
- Language: en
- Version: Apollo Open Platform
- Pages: 5
- Topic tags: [system_architecture, perception, planning_control]

## Summary
Official platform-overview material describing Apollo’s software stack, hardware stack, and module boundaries across perception, localization, planning, control, and simulation.

## Key points
- Apollo Open Platform This is an overview: 从最底层的硬件到顶层的云服务，具体可以拆解为以下几个部分： 1.
- • 基础运行环境：Apollo Cyber RT 是 Apollo 自研的高性能运行时框架，用于管 理模块间的通信和任务调度；RTOS（实时操作系统）则用于处理对时间要求极 高的底层控制任务。
- • 数据与安全：Fuel Data Service（数据服务）负责数据的采集、存储和分析； Security 保障系统和数据的安全。
- The large-scale deep-learning platform and GPU clusters drastically shorten the learning time for large quantities of data.

## Structured notes
### Pages 1-2
- [p.1] Apollo Open Platform This is an overview: 从最底层的硬件到顶层的云服务，具体可以拆解为以下几个部分： 1. 开放车辆认证平台 这是 Apollo 架构的最底层，旨在确保自动驾驶车辆的硬件兼容性和标准化。 • 认证 Apollo 兼容的线控车辆：这一层关注的是车辆本身的物理平台。Apollo 定 义了标准接口，使得经过认证的“线控车辆”（即可以通过电子信号控制转向、 加速和制动的车辆）能够接入…
- [p.1] • 人机交互设备：用于车内人员与自动驾驶系统进行交互的硬件。 • 其他关键组件：包括 Black Box（黑匣子，用于数据记录） 、ASU（可能是指天 线服务单元或特定传感器单元） 、AXU（可能是指加速扩展单元）以及 V2X OBU（车载单元，用于车路协同通信） 。 3. 开放软件平台 这是 Apollo 的核心，包含了自动驾驶所需的全套软件栈。
- [p.2] • 基础运行环境：Apollo Cyber RT 是 Apollo 自研的高性能运行时框架，用于管 理模块间的通信和任务调度；RTOS（实时操作系统）则用于处理对时间要求极 高的底层控制任务。 • 核心算法模块： o Map Engine（地图引擎） ：处理高精地图数据。 o Localization（定位） ：确定车辆在地图中的精确位置。 o Perception（感知） ：识别道路、障碍物、交通标志等。 o Prediction（…

### Pages 3-4
- [p.3] 1. Accurate Perception: Various sensors, such as LiDAR, cameras and radar collect environmental data surrounding the vehicle. Using sensor fusion technology perception algorithms can determine in real time the type, loc…
- [p.3] The large-scale deep-learning platform and GPU clusters drastically shorten the learning time for large quantities of data. Once trained, the new models are deployed onto the vehicle using over-the-air updates through t…
- [p.3] 2. Simulation Simulation provides the ability to virtually drive millions of kilometers daily using an array of real world traffic and autonomous driving data. Through the simulation service, partners gain access to a l…

### Pages 5-5
- [p.5] 5. Intelligent Control The Apollo intelligent vehicle control and canbus-proxy modules are precise, broadly applicable and adaptive to different environments. The modules handle different road conditions, speeds, vehicl…
- [p.5] Currently, there are two open datasets, Apollo-SouthBay and Apollo-DaoxiangLake. The data was collected in Silicon Valley, California, the United States, and Daoxiang Lake, Beijing, China. The datasets contain time-stam…

## Evidence-ready excerpts
- [p.1] Apollo Open Platform This is an overview: 从最底层的硬件到顶层的云服务，具体可以拆解为以下几个部分： 1. 开放车辆认证平台 这是 Apollo 架构的最底层，旨在确保自动驾驶车辆的硬件兼容性和标准化。 • 认证 Apollo 兼容的线控车辆：这一层关注的是车辆本身的物理平台。Apollo 定 义了标准接口，使得经过认证的“线控车辆”（即可以通过电子信号控制转向、 加速和制动的车辆）能够接入 Apollo 系统。 • 开放车辆接口标准：为了实现上述兼容性，Apollo 制定了一套开放的接口标 准，确保不同厂商的车辆都能与 Apollo 的软件和硬件平台无缝对接。 2. 硬件开发平台 这一层提供了自动驾驶系统所需的物理计算和感知硬件。 • 计算单元：负责处理海量数据的核心计算硬件。 • 传感器套件：包括 GPS/IMU（定位与惯性测量） 、Camera（摄像头） 、LIDAR （激光雷达） 、Radar（毫米波雷达）以及 Ultrasonic Radar（超声波雷达） ，用 于全方位感知周围环境。
- [p.3] The large-scale deep-learning platform and GPU clusters drastically shorten the learning time for large quantities of data. Once trained, the new models are deployed onto the vehicle using over-the-air updates through the cloud. Artificial intelligence and data-driven solutions combine to enable Apollo’s perception system to continuously improve its detection and recognition capabilities, which provide accurate, stable, and reliable input for other autonomous system modules.
- [p.5] Currently, there are two open datasets, Apollo-SouthBay and Apollo-DaoxiangLake. The data was collected in Silicon Valley, California, the United States, and Daoxiang Lake, Beijing, China. The datasets contain time-stamped LiDAR scans, camera images, and post-processed GPS trajectories.

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
