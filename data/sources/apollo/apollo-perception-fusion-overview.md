# Apollo Perception Fusion Overview

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-perception-fusion-overview.pdf
- Original URL: https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E4%B8%8A%E6%9C%BA%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B/%E4%B8%8A%E6%9C%BA%E5%AE%9E%E8%B7%B5Apollo%E6%84%9F%E7%9F%A5%E8%9E%8D%E5%90%88%E8%83%BD%E5%8A%9B/Apollo%E6%84%9F%E7%9F%A5%E8%9E%8D%E5%90%88%E8%83%BD%E5%8A%9B%E4%BB%8B%E7%BB%8D
- Language: zh
- Version: Apollo Doc CN 6.0
- Pages: 1
- Topic tags: [perception, sensor_fusion]

## Summary
Official Apollo perception-fusion material describing the multi-sensor fusion workflow and the role of fused perception in downstream driving tasks.

## Key points
- Apollo感知融合能力介绍 传感群性能比较 感知融合模块的原理 感知融合模块的相关参数 文栏意见反馈 本文档旨在简要介绍Apollo感知融合模块的原理和过程，并且说明运行Apollo感知融合模块的步骤。通过本文 档，您可以了解到以下内容： ·Apollo的感知融合原理 Apollo感知融合模块的输入与输出channel信息 传感器性能比较 在Apollo…
- +Radar+Lidar 目标检测 目标分类 距离估计 速度估计 可见范围 车道跟踪 极端天气下的性能 不良光照下的性能 感知融合模块的原理 Apollo感知融合模块能支持对摄像头、毫米波雷达和激光雷达传感器感知的结果进行目标级融合。
- channel名称 channel说明 统一输入channel。各传感器感知的结果都会输出到该 /perception/inner/Prefusedlobjects chamnel里作为感知融合模块的源数据。

## Structured notes
### Pages 1-1
- [p.1] Apollo感知融合能力介绍 传感群性能比较 感知融合模块的原理 感知融合模块的相关参数 文栏意见反馈 本文档旨在简要介绍Apollo感知融合模块的原理和过程，并且说明运行Apollo感知融合模块的步骤。通过本文 档，您可以了解到以下内容： ·Apollo的感知融合原理 Apollo感知融合模块的输入与输出channel信息 传感器性能比较 在Apollo感知模块里，多传感器融合是一个重要的环节，并且也是感知的最后环节。 在感知模块里…
- [p.1] +Radar+Lidar 目标检测 目标分类 距离估计 速度估计 可见范围 车道跟踪 极端天气下的性能 不良光照下的性能 感知融合模块的原理 Apollo感知融合模块能支持对摄像头、毫米波雷达和激光雷达传感器感知的结果进行目标级融合。 通过对各传感器检测算法输出的障碍物分析，结合每个障碍物的传感器来源、位置、形状、速度、类别等信息，以 及历史目标跟踪的信息，过滤掉一些检测不准确的障碍物。 并且感知融合模块根据各个传感器的优缺点，调整障…
- [p.1] channel名称 channel说明 统一输入channel。各传感器感知的结果都会输出到该 /perception/inner/Prefusedlobjects chamnel里作为感知融合模块的源数据。 感知融合模块的主要输出channel。该channel 输出的是多传 /apollo /perception/obstacles 感器融合之后的障碍物信息。 如果您在使用文档的过程中，遇到任何问题，请到我们在【开发者社区】建立的…

## Evidence-ready excerpts
- [p.1] Apollo感知融合能力介绍 传感群性能比较 感知融合模块的原理 感知融合模块的相关参数 文栏意见反馈 本文档旨在简要介绍Apollo感知融合模块的原理和过程，并且说明运行Apollo感知融合模块的步骤。通过本文 档，您可以了解到以下内容： ·Apollo的感知融合原理 Apollo感知融合模块的输入与输出channel信息 传感器性能比较 在Apollo感知模块里，多传感器融合是一个重要的环节，并且也是感知的最后环节。 在感知模块里，不同的传感器各有各的优缺点，而Apollo感知模块则是把各个传感器的优点结合起来，在目标级别 上进行融合。 下图表示了摄像头（Camera）、毫米波雷达（Radar）和激光雷达（Lidar）传感器在不同任务和不同条件下的性 能。其中， ·摄像头：对于分类任务尤其准确， ·毫米波雷达：在穿透性、距离估计和极端天气抗干扰性具有卓越的性能， 数据格式 ·激光雷达：擅长目标检测任务。 如果能有效将三种传感器进行融合感知，就能在各种情况下都能达到优良的性能。
- [p.1] +Radar+Lidar 目标检测 目标分类 距离估计 速度估计 可见范围 车道跟踪 极端天气下的性能 不良光照下的性能 感知融合模块的原理 Apollo感知融合模块能支持对摄像头、毫米波雷达和激光雷达传感器感知的结果进行目标级融合。 通过对各传感器检测算法输出的障碍物分析，结合每个障碍物的传感器来源、位置、形状、速度、类别等信息，以 及历史目标跟踪的信息，过滤掉一些检测不准确的障碍物。 并且感知融合模块根据各个传感器的优缺点，调整障碍物的类别、位置、形状、速度等属性，最络融合输出，得到 当前的经果。 /perception/inner/PrefusedObjects 激光雷达感知 /perception/inner/PrefusedObjects /apollo/perception/obstacles 视觉感知 融合感知 /perception/inner/PrefusedObjects 毫米波雷达感知 感知融合模块的相关参数 以下是感知融合模块的输入和输出的channel说明。
- [p.1] channel名称 channel说明 统一输入channel。各传感器感知的结果都会输出到该 /perception/inner/Prefusedlobjects chamnel里作为感知融合模块的源数据。 感知融合模块的主要输出channel。该channel 输出的是多传 /apollo /perception/obstacles 感器融合之后的障碍物信息。 如果您在使用文档的过程中，遇到任何问题，请到我们在【开发者社区】建立的反馈意见收集问答页面，反馈相关 的问题。我们会根据反馈意见对文栏进行选代优化。 雷达感知能力 Apollo感知融合模块

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
