# Apollo Control Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-vision-control-overview.pdf
- Original URL: https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E6%8E%A7%E5%88%B6%E8%83%BD%E5%8A%9B/Apollo%20%E6%8E%A7%E5%88%B6%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D
- Language: zh
- Version: Apollo Doc CN 6.0
- Pages: 1
- Topic tags: [planning_control, system_architecture]

## Summary
Official Apollo control material describing how planned trajectories are converted into steering, throttle, and brake commands.

## Key points
- Apollo控制能力介绍 本文档为开发者介绍Apollo控制模块的基本知识、Apollo控制能力、控制模块的组成及其输入输出。
- /Apollo/planning 规划模块 /Apollo/control /Apollo/localization/pose 定位模块 控制模块 canbus模块 /Apollo/canbus/chassis chassis模块 控制模块输入channel 控制模块有三个输入channel： channel名称 输入输出channel说明 /Apollo…

## Structured notes
### Pages 1-1
- [p.1] Apollo控制能力介绍 本文档为开发者介绍Apollo控制模块的基本知识、Apollo控制能力、控制模块的组成及其输入输出。 Apollo控制能力介绍 控制模块是整个自动驾驶软件系统中的执行环节，控制模块的目标是基于规划模块输出的目标轨迹和定位模块输出的车辆状态 生成方向盘、油门、刹车控制命令，并通过canbus模块给车辆底层执行器。简单而言，就是告诉车辆该打多大方向盘、多大 的油门开度、多大的刹车制动力。 Apollo控制模块原理…
- [p.1] 纵向控制模块 纵向模块根据规划模块的轨迹生成油门、刹车指令。 细向控制模块如下图所示： 纵向控制 位置闭环 速度闭环 ·位置闭环：通过规划模块的目标车辆位置和定位模块给出的实际车辆位置做差，经过纵向位置控制器生成对应的速度偏差。 ·速度闭环：结合位置闭环的结果，规划模块的目标速度以及canbus模块返回的实际车速，通过纵向速度控制器生成对应的 加速度偏差。 ·表定表：速度，加速度和油门、刹车对应关系表，通过输入速度、加速度可以查出对应…
- [p.1] /Apollo/planning 规划模块 /Apollo/control /Apollo/localization/pose 定位模块 控制模块 canbus模块 /Apollo/canbus/chassis chassis模块 控制模块输入channel 控制模块有三个输入channel： channel名称 输入输出channel说明 /Apollo/planing 规划信息，自车规划的轨迹信息 定位信息，自车的位置 /Apol…

## Evidence-ready excerpts
- [p.1] Apollo控制能力介绍 本文档为开发者介绍Apollo控制模块的基本知识、Apollo控制能力、控制模块的组成及其输入输出。 Apollo控制能力介绍 控制模块是整个自动驾驶软件系统中的执行环节，控制模块的目标是基于规划模块输出的目标轨迹和定位模块输出的车辆状态 生成方向盘、油门、刹车控制命令，并通过canbus模块给车辆底层执行器。简单而言，就是告诉车辆该打多大方向盘、多大 的油门开度、多大的刹车制动力。 Apollo控制模块原理 控制模块由两个子模块组成：横向控制模块和组向控制模块。 横向控制模块 向控制根据规划模块的轨迹生成方向盘指令。 横向控制模块如下图所示： 横向控制 方向盘闭环 方向盘开环 ·方向盘闭环：通过上游规划模块输出的目标方向盘角度和下游canbus模块返回的实际方向盘角度做差，作为控制器的方向 盘闭环输出。 ·方向盘开环：通过上游规划模块输出的目标道路曲率经过转换，输出控制器方向盘开环输出。 ·车辆：是控制器的控制对象，通过方向盘开环、方向盘闭不生成的方向盘角度打方向盘。
- [p.1] 纵向控制模块 纵向模块根据规划模块的轨迹生成油门、刹车指令。 细向控制模块如下图所示： 纵向控制 位置闭环 速度闭环 ·位置闭环：通过规划模块的目标车辆位置和定位模块给出的实际车辆位置做差，经过纵向位置控制器生成对应的速度偏差。 ·速度闭环：结合位置闭环的结果，规划模块的目标速度以及canbus模块返回的实际车速，通过纵向速度控制器生成对应的 加速度偏差。 ·表定表：速度，加速度和油门、刹车对应关系表，通过输入速度、加速度可以查出对应的油门、刹车。 Apollo控制模块输入输出 控制模块的输入输出的dhannel 如下图所示。
- [p.1] /Apollo/planning 规划模块 /Apollo/control /Apollo/localization/pose 定位模块 控制模块 canbus模块 /Apollo/canbus/chassis chassis模块 控制模块输入channel 控制模块有三个输入channel： channel名称 输入输出channel说明 /Apollo/planing 规划信息，自车规划的轨迹信息 定位信息，自车的位置 /Apollo/localizatio/pose /Apollo/canbus/chassis 底盘信息，自车的方向盘、速度信息 控制模块输出channel 控制模块有一个输出channel： 输入输出channel说明 channel名称 控制信息，方向盘角度、油门刹车 /Apollo/control 输出

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
