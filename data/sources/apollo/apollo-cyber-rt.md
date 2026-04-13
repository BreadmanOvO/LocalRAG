# Apollo Cyber RT Framework

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/Apollo-Cyber-RT-framework.pdf
- Original URL: https://developer.apollo.auto/cyber.html
- Language: en
- Version: Apollo Cyber RT
- Pages: 3
- Topic tags: [system_architecture, planning_control]

## Summary
Official Apollo runtime-framework material describing Cyber RT, its component model, scheduling model, and how it supports low-latency autonomous-driving workloads.

## Key points
- Apollo Cyber RT framework 全球首个开源高性能自动驾驶计算框架 自动驾驶的顶端技术 Apollo Cyber RT 是世界上第一个专为自动驾驶定制的高性能开源框架。它与 Apollo 3.5 开放平台同期发布 。
- 系统的架构是由一系列具有特定输入和输出的组件构成，每一个组件包含一个特定的 算法模块来处理一组数据的输入并生成一组输出。Apollo Cyber RT 框架建立在这些组 件之上，从组件中提取依赖项并通过 DAG 依赖关系图将它们连接在一起。
- Apollo 项目于 2017 年 7 月首次推出，标志着汽车行业演进的一个巨大飞跃，开发者可 以以 Apollo 技术平台为基础，使用一系列广泛的工具和软件模块来创新和构建自己的 自动驾驶解决方案。
- 研发效率的显著提升 Apollo Cyber RT 框架背后的革命性技术提供了高效的数据处理和抽象的通信接口。框 架中提供了简单易用的任务接口和高效的数据融合机制，使开发者能够直接在其上构 建解决方案。

## Structured notes
### Pages 1-1
- [p.1] Apollo Cyber RT framework 全球首个开源高性能自动驾驶计算框架 自动驾驶的顶端技术 Apollo Cyber RT 是世界上第一个专为自动驾驶定制的高性能开源框架。它与 Apollo 3.5 开放平台同期发布 。 Apollo 项目于 2017 年 7 月首次推出，标志着汽车行业演进的一个巨大飞跃，开发者可 以以 Apollo 技术平台为基础，使用一系列广泛的工具和软件模块来创新和构建自己的 自动驾驶解决方案。…
- [p.1] 系统的架构是由一系列具有特定输入和输出的组件构成，每一个组件包含一个特定的 算法模块来处理一组数据的输入并生成一组输出。Apollo Cyber RT 框架建立在这些组 件之上，从组件中提取依赖项并通过 DAG 依赖关系图将它们连接在一起。 在运行时，Apollo Cyber RT 框架加载上面提到的预定义组件，建立轻量级的用户任务 并与传感器输入数据结合，然后根据资源的可利用性以及任务的优先级对每一个任务 进行调度和执行。 Apol…
- [p.1] Apollo 项目于 2017 年 7 月首次推出，标志着汽车行业演进的一个巨大飞跃，开发者可 以以 Apollo 技术平台为基础，使用一系列广泛的工具和软件模块来创新和构建自己的 自动驾驶解决方案。 在过去的两年里，Apollo 平台发展迅速，实现了从封闭场所的自动驾驶，到简单城市 道路和高速公路的自动驾驶的突破发展。作为 Apollo3.5 发布的一部分，Apollo Cyber

### Pages 2-2
- [p.2] RT 框架将 Apollo 平台推向了一个新的高度。 专为自动驾驶打造的最先进开源运行框架 由于自动驾驶技术本身会遇到意想不到的情况和极具挑战的场景，开发者需要一个有 着高计算性能的可靠框架来支持和处理复杂的城市道路自动驾驶。而 Apollo Cyber RT 正为此提供了解决方案。 系统的架构是由一系列具有特定输入和输出的组件构成，每一个组件包含一个特定的 算法模块来处理一组数据的输入并生成一组输出。Apollo Cyber RT…
- [p.2] 研发效率的显著提升 Apollo Cyber RT 框架背后的革命性技术提供了高效的数据处理和抽象的通信接口。框 架中提供了简单易用的任务接口和高效的数据融合机制，使开发者能够直接在其上构 建解决方案。 框架中集成了丰富的研发工具和传感器驱动程序，使开发者能够在不牺牲性能或者品 牌形象的同时，更快地构建自动驾驶系统。 易于部署的自适应设计 Apollo Cyber RT 框架的灵活的集成方案以及最小的环境依赖使得应用程序的部署更加 简…

### Pages 3-3
- [p.3] 同类型的自动驾驶应用程序，以给开发者提供高度的灵活性。 以 Apollo Cyber RT 为基础构建的自动驾驶解决方案不需要任何繁琐的配置和复杂的部 署环境，便可获得很好的性能表现。 高可靠的框架赋能您独特的自动驾驶解决方案 Apollo Cyber RT 是一个独立的开源框架，它包含专为构建自动驾驶模块和应用的组 件。路径规划、控制、感知、定位和 HMI 在 Apollo Cyber RT 框架中无缝集成。它们 给开发者提供了标准…
- [p.3] 一起创造未来全球化的自动驾驶平台 Apollo Cyber RT 框架考虑到了高度集成，多个子系统协同工作来优化自动驾驶的发 展。它利用 Apollo 团队的专业知识、结合开源的技术力量，为您提供当前最先进的自 动驾驶开放平台。因此，我们将会继续开创先例，攻克自动驾驶技术中最复杂、最困 难的挑战。

## Evidence-ready excerpts
- [p.1] Apollo Cyber RT framework 全球首个开源高性能自动驾驶计算框架 自动驾驶的顶端技术 Apollo Cyber RT 是世界上第一个专为自动驾驶定制的高性能开源框架。它与 Apollo 3.5 开放平台同期发布 。 Apollo 项目于 2017 年 7 月首次推出，标志着汽车行业演进的一个巨大飞跃，开发者可 以以 Apollo 技术平台为基础，使用一系列广泛的工具和软件模块来创新和构建自己的 自动驾驶解决方案。 在过去的两年里，Apollo 平台发展迅速，实现了从封闭场所的自动驾驶，到简单城市 道路和高速公路的自动驾驶的突破发展。作为 Apollo3.5 发布的一部分，Apollo Cyber RT 框架将 Apollo 平台推向了一个新的高度。 专为自动驾驶打造的最先进开源运行框架 由于自动驾驶技术本身会遇到意想不到的情况和极具挑战的场景，开发者需要一个有 着高计算性能的可靠框架来支持和处理复杂的城市道路自动驾驶。而 Apollo Cyber RT 正为此提供了解决方案。
- [p.2] RT 框架将 Apollo 平台推向了一个新的高度。 专为自动驾驶打造的最先进开源运行框架 由于自动驾驶技术本身会遇到意想不到的情况和极具挑战的场景，开发者需要一个有 着高计算性能的可靠框架来支持和处理复杂的城市道路自动驾驶。而 Apollo Cyber RT 正为此提供了解决方案。 系统的架构是由一系列具有特定输入和输出的组件构成，每一个组件包含一个特定的 算法模块来处理一组数据的输入并生成一组输出。Apollo Cyber RT 框架建立在这些组 件之上，从组件中提取依赖项并通过 DAG 依赖关系图将它们连接在一起。 在运行时，Apollo Cyber RT 框架加载上面提到的预定义组件，建立轻量级的用户任务 并与传感器输入数据结合，然后根据资源的可利用性以及任务的优先级对每一个任务 进行调度和执行。 Apollo Cyber RT 的高度集成的并行计算模型，能够实现任务执行的高并发、低延迟以 及高吞吐量。针对自动驾驶业务场景的定制开发，使其能够满足自动驾驶解决方案的 高性能要求。
- [p.3] 一起创造未来全球化的自动驾驶平台 Apollo Cyber RT 框架考虑到了高度集成，多个子系统协同工作来优化自动驾驶的发 展。它利用 Apollo 团队的专业知识、结合开源的技术力量，为您提供当前最先进的自 动驾驶开放平台。因此，我们将会继续开创先例，攻克自动驾驶技术中最复杂、最困 难的挑战。

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
