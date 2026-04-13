# Apollo Prediction Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-vision-prediction-overview.pdf
- Original URL: https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E9%A2%84%E6%B5%8B%E8%83%BD%E5%8A%9B/Apollo%E9%A2%84%E6%B5%8B%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D
- Language: zh
- Version: Apollo Doc CN 6.0
- Pages: 1
- Topic tags: [planning_control, perception]

## Summary
Official Apollo prediction material describing how the system predicts surrounding-agent behavior and feeds that forecast into planning.

## Key points
- Apollo预测能力介绍 本文为开发者介绍Apollo预测模块的基本知识，包括预测模块在自动驾驶系统中的主要作用，预测模块的基本组成以及预测模 块的输入输出。

## Structured notes
### Pages 1-1
- [p.1] Apollo预测能力介绍 本文为开发者介绍Apollo预测模块的基本知识，包括预测模块在自动驾驶系统中的主要作用，预测模块的基本组成以及预测模 块的输入输出。 Apollo预测能力介绍 预测模块通过障碍物的历史状态信息，来预测障碍物的未来轨迹。感知模块作为预测模块的上游，提供障碍物的位置、朝向、 速度、加速度等信息，预测模块根据这些信息，给出障碍物未来的预测轨迹，供下游规戏模块进行自车轨迹的规划。 预测模块的原理 预测模块主要有四个子…
- [p.1] ·预测器：预测器直接或结合评估器的结果给出障碍物的完整预测时域的预测轨迹。 预测模块的输入输出 channel名称 输入输出channel说明 /apollo/perception/obstacles输入 感知信息，包含障碍物的位置、朝向、速度、加速度 /apollo/localization/pose 定位信息，自车的位置、速度信息 /apollo/planning 规划信息，自车规划的轨迹信息 /apollo/prediction…

## Evidence-ready excerpts
- [p.1] Apollo预测能力介绍 本文为开发者介绍Apollo预测模块的基本知识，包括预测模块在自动驾驶系统中的主要作用，预测模块的基本组成以及预测模 块的输入输出。 Apollo预测能力介绍 预测模块通过障碍物的历史状态信息，来预测障碍物的未来轨迹。感知模块作为预测模块的上游，提供障碍物的位置、朝向、 速度、加速度等信息，预测模块根据这些信息，给出障碍物未来的预测轨迹，供下游规戏模块进行自车轨迹的规划。 预测模块的原理 预测模块主要有四个子模块组成，分别是：信息容器（container）、场景选择（scenario)、评估器（evaluator）和预测器 (predictor)。 ·信息容器：储存上游信息，为之后的轨迹预测提供输入，当期储存的主要有：感知信息、定位信息以及自车轨迹规划信息。 Apollo预测模块实践 ·场景选择：预测模块针对不同的场景采用不同的预测方法（如巡航、路口等场景），便于后续扩展，提高算法的泛化能力。 ·评估器：评估器基于障碍物的状态信息，结合预测模型，给出障碍物预测轨迹的概率或短预测时域的轨迹信息。
- [p.1] ·预测器：预测器直接或结合评估器的结果给出障碍物的完整预测时域的预测轨迹。 预测模块的输入输出 channel名称 输入输出channel说明 /apollo/perception/obstacles输入 感知信息，包含障碍物的位置、朝向、速度、加速度 /apollo/localization/pose 定位信息，自车的位置、速度信息 /apollo/planning 规划信息，自车规划的轨迹信息 /apollo/prediction 预测轨迹，包含障碍物在预测时域内的未来轨迹信息 感知模块 /apollo/perception/obstacles /apollo/localization/pose 定位模块 /apollo/prediction 预测模块 规划模块 /apollo/planning 规划模块 如果您在使用文档的过程中，遇到任何问题，请麻烦到我们在【开发者社区】建立的反馈意见收集问答页面，反馈相关的问 题。我们会根据反馈意见对文档进行选代优化。 Apollo预测模块实践

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
