# Apollo Channel Data Format

- Source type: official_doc
- Category: apollo
- Original file: data/sources/raw/apollo/apollo-channel-data-format.pdf
- Original URL: https://developer.apollo.auto/Apollo-Homepage-Document/Apollo_Doc_CN_6_0/%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F/Channel%E6%95%B0%E6%8D%AE%E6%A0%BC%E5%BC%8F%E6%96%87%E6%A1%A3%E4%BB%8B%E7%BB%8D
- Language: zh
- Version: Apollo Doc CN 6.0
- Pages: 2
- Topic tags: [system_architecture, sensor_fusion, planning_control]

## Summary
Official Apollo channel-format material describing how modules communicate through Cyber RT channels and which message types are used for perception, prediction, planning, and control.

## Key points
- 安装逆明 数据格式 Channel数据格式文档介招 感知模块 CANBUS模块 控制模扶 定位模块 预测模扶 规划模块 监控模块 Guardian模块 人机交互模块 坐标变换模块 Channel数据格式文档介绍 【数据格式】文档，以【 】中介绍的 demo_35urecord数据包为对像，介绍各个Channel 和对应的内部消息格式 (slessan) 前…
- Apollo通信系统 Apollo的各个模块是以组件的形式存在的。细件之间利用数据通道进行通信。其中，最小的数据单元是消息格式采定义的。也 有其他Node、witereader等，为了避免混淆，这里只关注细件、数据通道和消息格式。
- 数据通道 Channel是传转辅输数据的通道，管理CybarRT 中的数据通信。用户可以发布/订阅同一个Charel建立通信，实现点对点（P2F) 招放数据包之后，打开CyherMonitor工具井进入特定数据通道，可以看到海个Channel中都有ChannelINae、 HessageType、FraeRatio、Rahessage Size数据字段。关…
- 例如：16863 字节 其中，MessageType字段展现的数据格式是本Chzame通道里使用的最小数据单元，由消息格式(Message）定义。示例中 apo1lo,perception,Perceptionobstacles 是数据通道/apollo/perception/obstacles 的核心消息格式。

## Structured notes
### Pages 1-1
- [p.1] 安装逆明 数据格式 Channel数据格式文档介招 感知模块 CANBUS模块 控制模扶 定位模块 预测模扶 规划模块 监控模块 Guardian模块 人机交互模块 坐标变换模块 Channel数据格式文档介绍 【数据格式】文档，以【 】中介绍的 demo_35urecord数据包为对像，介绍各个Channel 和对应的内部消息格式 (slessan) 前提条件 您需要提前了解 · CyberRT 工县 如包查看Apclo数据通道 ·…
- [p.1] 根据规划线目标，生成控制车辆指令(转角、速度、加速度）)。 控制 (Contrdl) 该模块类似于库。它不是发布和订说消息。而是经常用作查询引掌支持， 高精地图(HDMap) 以提供关于道路的特定结构化信息。高精地图还可以提仰环境静态感知能力。 定位模块利用GPS、LiDAR和IMU的各种信息源来定位自式驾驶车辆的位置。 定位(Localiation) CANBLS是格控制命令传递给车辆硬件的接口。将控制车辆指令发送至底盘， 底盘通信…
- [p.1] Apollo通信系统 Apollo的各个模块是以组件的形式存在的。细件之间利用数据通道进行通信。其中，最小的数据单元是消息格式采定义的。也 有其他Node、witereader等，为了避免混淆，这里只关注细件、数据通道和消息格式。 通信单元 在自动驾驶系统中，模块（如感知、定位、控制系统等）在CyberRT下以 组件 (Componen) Component 的形式存在。 不同 Component:之间通过 Chznnel进行通信 C…

### Pages 2-2
- [p.2] 安装逆明 数据格式 Channel数据格式文档介招 感知模块 CANBUS模块 控制模块 定位模块 预测模扶 规划模块 监控模块 Guardian模块 人机交互模块 坐标变换模块 消息格式主要分为两大类，即： ●通用（Common）消息格式 各模块通用的消息格式，如定义时间的时间戳消息格式、错误代码消息格式。 ·特定模块消息格式 各模块独有的消息格式。 下文将介绍demc_35uecord相关的通用消息格式和特定模块的消息格式。 通用…

## Evidence-ready excerpts
- [p.1] 安装逆明 数据格式 Channel数据格式文档介招 感知模块 CANBUS模块 控制模扶 定位模块 预测模扶 规划模块 监控模块 Guardian模块 人机交互模块 坐标变换模块 Channel数据格式文档介绍 【数据格式】文档，以【 】中介绍的 demo_35urecord数据包为对像，介绍各个Channel 和对应的内部消息格式 (slessan) 前提条件 您需要提前了解 · CyberRT 工县 如包查看Apclo数据通道 ·如何摄放数据包 Apollo各模块通信框架 Apollo系统各个模块之间的通信框策如下图所示： 前显条件 Apoli各模块通信框架 Apolo通售系统 数担通道 消息格式 通用沸息格式 特定模块的消息格式 橘色的实线为数据消动线，黑色实线为控制逻辑线。各个模块的功能如下： 识别交通参与者（汽车、自行车、行人等），识别交通信号灯等。 感知(Perception) 聚测 (Prediction) 对交通参与都的行为讲行测。 规划(Plamring) 对主车行为进行决策，实时生成车辆规划线。
- [p.1] 数据通道 Channel是传转辅输数据的通道，管理CybarRT 中的数据通信。用户可以发布/订阅同一个Charel建立通信，实现点对点（P2F) 招放数据包之后，打开CyherMonitor工具井进入特定数据通道，可以看到海个Channel中都有ChannelINae、 HessageType、FraeRatio、Rahessage Size数据字段。关于播放数据包，参见使用Dreamiew查看效据包。 各个数据字段的名称和描述如下所示： 数据通道的名字。 aenaep 例0： /apollc/perceptior/obstacles 例0: apollo.perceptionPerceptionObstades 通道内的数据的数据类型。 数据更新频率。 例如: 10 HZ 原始数据的数据大小。
- [p.2] 安装逆明 数据格式 Channel数据格式文档介招 感知模块 CANBUS模块 控制模块 定位模块 预测模扶 规划模块 监控模块 Guardian模块 人机交互模块 坐标变换模块 消息格式主要分为两大类，即： ●通用（Common）消息格式 各模块通用的消息格式，如定义时间的时间戳消息格式、错误代码消息格式。 ·特定模块消息格式 各模块独有的消息格式。 下文将介绍demc_35uecord相关的通用消息格式和特定模块的消息格式。 通用消息格式 常用的通用的消息格式如下所示 定义的数据内容 Message定义 h6ader 由apoll. error_code 关于获取更多通用消息格式的信息，参见Cm 特定模块的消息格式 播放数据包井打开CyberMonitor后，可以看到以下数据通道和对应的主消息格式。关于主消息格式的更多内容，参见对应的 文档深入了解。

## Cleaning notes
- Extracted from the raw PDF text layer using pypdf.
- OCR fallback is used when the PDF has no extractable text layer.
- Repeated header/footer lines were removed when they appeared on most pages.
- Figures, tables, and formulas may need manual follow-up if the PDF text layer is incomplete.
- Review this file before using it for Gold Set evidence extraction.
