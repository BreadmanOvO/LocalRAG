# Apollo Planning Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-vision-plan-overview.pdf
- Original URL: https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E8%A7%84%E5%88%92%E8%83%BD%E5%8A%9B/apollo%E8%A7%84%E5%88%92%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D
- Language: zh
- Version: Apollo Doc CN 6.0
- Pages: 1
- Topic tags: [planning_control, system_architecture]

## Summary
Official Apollo planning material describing scenario-based planning, planner responsibilities, and the inputs and outputs of the planning module.

## Key points
- apollo规划能力介绍 规划是自动驾驶中重要的模块。规划模块基于预测模块输入的障碍物信息、地图定位信息、路径导航信息对车辆的未来的运动 轨迹进行规划，保证自动驾驶车辆高效、安全、舒适的行至目标位置。
- Apollo规划模块原理 Apolo规划模块功能的实现是基于场景（scenario-based）实现的，针对不同的场景，规划模块通过一系列独立的任务 (task）组合来完成轨迹的规划。开发者可以根据自己的使用需求，调整apollo/modules/planning/conf/scenario/下 的配置文件，调配任务组合实现自己的规划要求。
- handler handler handler handler handler handler handler Apollo规划架构示意图如上，其中部分重要模块如下： ·状态机（ApolloFSM（FiniteStateMachine)）：一个有限状态机，结合导航、环境等信息确定自动驾驶车辆的驾驶场景 ·规划分发器（PlanningDispatcher)：…
- 规划模块的输入输出 规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light输入是 感知红绿灯信息 输入预测障碍物信息 /apollo/predicti…

## Structured notes
### Pages 1-1
- [p.1] apollo规划能力介绍 规划是自动驾驶中重要的模块。规划模块基于预测模块输入的障碍物信息、地图定位信息、路径导航信息对车辆的未来的运动 轨迹进行规划，保证自动驾驶车辆高效、安全、舒适的行至目标位置。 本文档主要介绍规划模块的基本原理以及输入输出，帮助开发者快速了解规划模块的运作机制，方便开发者开展后续的模块开 Apollo规划能力介绍 Apolo规划模块的主要作用是结合障碍物、地图定位以及导航信息为自动驾驶车辆规划一条运动轨迹，这条…
- [p.1] Apollo规划模块原理 Apolo规划模块功能的实现是基于场景（scenario-based）实现的，针对不同的场景，规划模块通过一系列独立的任务 (task）组合来完成轨迹的规划。开发者可以根据自己的使用需求，调整apollo/modules/planning/conf/scenario/下 的配置文件，调配任务组合实现自己的规划要求。
- [p.1] handler handler handler handler handler handler handler Apollo规划架构示意图如上，其中部分重要模块如下： ·状态机（ApolloFSM（FiniteStateMachine)）：一个有限状态机，结合导航、环境等信息确定自动驾驶车辆的驾驶场景 ·规划分发器（PlanningDispatcher)：根据状态机与车辆相关信息，调用合适当前场景的规划器 ·规划器（Planner)：…

## Evidence-ready excerpts
- [p.1] apollo规划能力介绍 规划是自动驾驶中重要的模块。规划模块基于预测模块输入的障碍物信息、地图定位信息、路径导航信息对车辆的未来的运动 轨迹进行规划，保证自动驾驶车辆高效、安全、舒适的行至目标位置。 本文档主要介绍规划模块的基本原理以及输入输出，帮助开发者快速了解规划模块的运作机制，方便开发者开展后续的模块开 Apollo规划能力介绍 Apolo规划模块的主要作用是结合障碍物、地图定位以及导航信息为自动驾驶车辆规划一条运动轨迹，这条轨迹由若干轨迹点 组成，每个轨迹点均包含了位置坐标、速度、加速度、加加速度、相对时间等信息，这些信息为自动驾驶车辆的运动提供依 据，参照规划的轨迹，自动驾驶车辆可以高效、安全、舒适的驶向目的地。
- [p.1] handler handler handler handler handler handler handler Apollo规划架构示意图如上，其中部分重要模块如下： ·状态机（ApolloFSM（FiniteStateMachine)）：一个有限状态机，结合导航、环境等信息确定自动驾驶车辆的驾驶场景 ·规划分发器（PlanningDispatcher)：根据状态机与车辆相关信息，调用合适当前场景的规划器 ·规划器（Planner)：结合上游模块信息，通过一系列的任务组合，完成自动驾驶车辆的轨迹规划 ·决策器&优化器（Deciders&Optimizers）：一组实现决策和优化任务的task集合。优化器用于优化车辆的轨迹和速度。决 策器则基于规则，确定自动驾驶车辆何时换车道、何时停车、何时蠕行（慢速行进）或螺行何时完成等驾驶行为。
- [p.1] 规划模块的输入输出 规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light输入是 感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning输出自动驾驶车辆的轨迹信息 如果您在使用文档的过程中，遇到任何问题，请到我们在【开发者社区】建立的反馈意见收集问答页面，反馈相关的问题。我 们会根据反馈意见对文档进行迭代优化。 < apollo规划模块实践

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
