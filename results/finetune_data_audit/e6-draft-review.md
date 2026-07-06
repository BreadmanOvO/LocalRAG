# E6 表格 channel 精确抽取数据报告

E6 目标是修复 E5.1 剩余的 Apollo channel 相邻行干扰问题。
这些样本强调按问题中的说明字段定位同一行 channel，不能被邻近 channel 或其他模块输出带偏。

## 摘要

- 版本：`v1.3-e6`
- 训练样本数：`36`
- E5 保留样本数：`16`
- E6 hardcase 样本数：`20`
- 验证样本数：`20`
- 训练数据类型分布：`{'e6_key_value_field_alignment': 4, 'e6_table_channel_same_row': 16, 'pairwise_complete_context': 8, 'pairwise_partial_context_refusal': 8}`

## 设计原则

- 继续保留 E5 的 pairwise 数值/方向拒答样本，避免 E6 覆盖掉已修复能力。
- E6 hardcase 只训练表格、channel、key-value 的字段对齐行为。
- 每条 hardcase 都写入 `required_answer_terms` 和 `forbidden_answer_terms`，便于后续 gate 复核。

## E6 Hardcase 清单

### 1. e6-channel-001

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_planning_traffic_light`
- 目标 source_id：`apollo-doc-008`
- 必须包含：`['/apollo/perception/traffic_light']`
- 禁止包含：`['/apollo/prediction']`
- 来源文档：`data/sources/apollo/apollo-vision-plan-overview.md`

**输入**

```text
问题：在规划模块输入表中，标注为“感知红绿灯信息”的 channel 是哪一个？

参考资料：
[1] source_id=apollo-doc-008 locator=page=1
规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light 输入是感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning 输出自动驾驶车辆的轨迹信息
```

**期望输出**

```text
标注为“感知红绿灯信息”的规划输入 channel 是 /apollo/perception/traffic_light。

引用：
- apollo-doc-008 page=1
```

### 2. e6-channel-002

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_planning_prediction`
- 目标 source_id：`apollo-doc-008`
- 必须包含：`['/apollo/prediction']`
- 禁止包含：`['/apollo/perception/traffic_light']`
- 来源文档：`data/sources/apollo/apollo-vision-plan-overview.md`

**输入**

```text
问题：规划模块输入表里，预测障碍物信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-008 locator=page=1
规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light 输入是感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning 输出自动驾驶车辆的轨迹信息
```

**期望输出**

```text
预测障碍物信息对应的规划输入 channel 是 /apollo/prediction。

引用：
- apollo-doc-008 page=1
```

### 3. e6-channel-003

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_planning_localization`
- 目标 source_id：`apollo-doc-008`
- 必须包含：`['/apollo/localization/pose']`
- 禁止包含：`['/apollo/canbus/chassis', '/apollo/perception/traffic_light']`
- 来源文档：`data/sources/apollo/apollo-vision-plan-overview.md`

**输入**

```text
问题：规划模块输入表中，车辆定位信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-008 locator=page=1
规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light 输入是感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning 输出自动驾驶车辆的轨迹信息
```

**期望输出**

```text
车辆定位信息对应的规划输入 channel 是 /apollo/localization/pose。

引用：
- apollo-doc-008 page=1
```

### 4. e6-channel-004

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_planning_relative_map`
- 目标 source_id：`apollo-doc-008`
- 必须包含：`['/apollo/relative_map']`
- 禁止包含：`['/apollo/routing_response']`
- 来源文档：`data/sources/apollo/apollo-vision-plan-overview.md`

**输入**

```text
问题：规划模块输入表中，局部地图信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-008 locator=page=1
规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light 输入是感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning 输出自动驾驶车辆的轨迹信息
```

**期望输出**

```text
局部地图信息对应的规划输入 channel 是 /apollo/relative_map。

引用：
- apollo-doc-008 page=1
```

### 5. e6-channel-005

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_planning_routing`
- 目标 source_id：`apollo-doc-008`
- 必须包含：`['/apollo/routing_response']`
- 禁止包含：`['/apollo/relative_map']`
- 来源文档：`data/sources/apollo/apollo-vision-plan-overview.md`

**输入**

```text
问题：规划模块输入表中，导航 routing 信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-008 locator=page=1
规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light 输入是感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning 输出自动驾驶车辆的轨迹信息
```

**期望输出**

```text
导航 routing 信息对应的规划输入 channel 是 /apollo/routing_response。

引用：
- apollo-doc-008 page=1
```

### 6. e6-channel-006

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_planning_output`
- 目标 source_id：`apollo-doc-008`
- 必须包含：`['/apollo/planning']`
- 禁止包含：`['/apollo/prediction', '/apollo/routing_response']`
- 来源文档：`data/sources/apollo/apollo-vision-plan-overview.md`

**输入**

```text
问题：规划模块输出自动驾驶车辆轨迹信息时使用哪个 channel？

参考资料：
[1] source_id=apollo-doc-008 locator=page=1
规划模块的输入 channel名称 输入channel说明 输入车身底盘反馈信息 /apollo/canbus/chassis 输入车辆定位信息 /apollo/localization/pose /apollo/perception/traffic_light 输入是感知红绿灯信息 输入预测障碍物信息 /apollo/prediction 局部地图信息 /apollo/relative_map /apollo/routing_response 输入导航routing信息 规划模块的输出 输出channel说明 channel名称 /apollo/planning 输出自动驾驶车辆的轨迹信息
```

**期望输出**

```text
规划模块输出自动驾驶车辆轨迹信息时使用 /apollo/planning。

引用：
- apollo-doc-008 page=1
```

### 7. e6-channel-007

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_prediction_obstacles`
- 目标 source_id：`apollo-doc-007`
- 必须包含：`['/apollo/perception/obstacles']`
- 禁止包含：`['/apollo/prediction']`
- 来源文档：`data/sources/apollo/apollo-vision-prediction-overview.md`

**输入**

```text
问题：预测模块输入表中，感知信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-007 locator=page=1
预测模块的输入输出 channel名称 输入输出channel说明 /apollo/perception/obstacles 输入感知信息，包含障碍物的位置、朝向、速度、加速度 /apollo/localization/pose 定位信息，自车的位置、速度信息 /apollo/planning 规划信息，自车规划的轨迹信息 /apollo/prediction 预测轨迹，包含障碍物在预测时域内的未来轨迹信息
```

**期望输出**

```text
预测模块输入表中，感知信息对应 /apollo/perception/obstacles。

引用：
- apollo-doc-007 page=1
```

### 8. e6-channel-008

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_prediction_localization`
- 目标 source_id：`apollo-doc-007`
- 必须包含：`['/apollo/localization/pose']`
- 禁止包含：`['/apollo/perception/obstacles', '/apollo/planning']`
- 来源文档：`data/sources/apollo/apollo-vision-prediction-overview.md`

**输入**

```text
问题：预测模块输入表中，自车的位置和速度信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-007 locator=page=1
预测模块的输入输出 channel名称 输入输出channel说明 /apollo/perception/obstacles 输入感知信息，包含障碍物的位置、朝向、速度、加速度 /apollo/localization/pose 定位信息，自车的位置、速度信息 /apollo/planning 规划信息，自车规划的轨迹信息 /apollo/prediction 预测轨迹，包含障碍物在预测时域内的未来轨迹信息
```

**期望输出**

```text
自车的位置和速度信息对应 /apollo/localization/pose。

引用：
- apollo-doc-007 page=1
```

### 9. e6-channel-009

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_prediction_planning_input`
- 目标 source_id：`apollo-doc-007`
- 必须包含：`['/apollo/planning']`
- 禁止包含：`['/apollo/prediction']`
- 来源文档：`data/sources/apollo/apollo-vision-prediction-overview.md`

**输入**

```text
问题：预测模块输入表中，自车规划的轨迹信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-007 locator=page=1
预测模块的输入输出 channel名称 输入输出channel说明 /apollo/perception/obstacles 输入感知信息，包含障碍物的位置、朝向、速度、加速度 /apollo/localization/pose 定位信息，自车的位置、速度信息 /apollo/planning 规划信息，自车规划的轨迹信息 /apollo/prediction 预测轨迹，包含障碍物在预测时域内的未来轨迹信息
```

**期望输出**

```text
自车规划的轨迹信息对应 /apollo/planning。

引用：
- apollo-doc-007 page=1
```

### 10. e6-channel-010

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_prediction_output`
- 目标 source_id：`apollo-doc-007`
- 必须包含：`['/apollo/prediction']`
- 禁止包含：`['/apollo/planning', '/apollo/perception/obstacles']`
- 来源文档：`data/sources/apollo/apollo-vision-prediction-overview.md`

**输入**

```text
问题：预测模块输出障碍物未来预测轨迹时对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-007 locator=page=1
预测模块的输入输出 channel名称 输入输出channel说明 /apollo/perception/obstacles 输入感知信息，包含障碍物的位置、朝向、速度、加速度 /apollo/localization/pose 定位信息，自车的位置、速度信息 /apollo/planning 规划信息，自车规划的轨迹信息 /apollo/prediction 预测轨迹，包含障碍物在预测时域内的未来轨迹信息
```

**期望输出**

```text
预测模块输出障碍物未来预测轨迹时对应 /apollo/prediction。

引用：
- apollo-doc-007 page=1
```

### 11. e6-channel-011

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_fusion_input`
- 目标 source_id：`apollo-doc-005`
- 必须包含：`['/perception/inner/PrefusedObjects']`
- 禁止包含：`['/apollo/perception/obstacles']`
- 来源文档：`data/sources/apollo/apollo-perception-fusion-overview.md`

**输入**

```text
问题：感知融合模块的统一输入 channel 是哪一个？

参考资料：
[1] source_id=apollo-doc-005 locator=page=1
感知融合模块的相关参数 channel名称 channel说明 统一输入channel：各传感器感知的结果都会输出到 /perception/inner/PrefusedObjects，作为感知融合模块的源数据。感知融合模块的主要输出channel 是 /apollo/perception/obstacles，该 channel 输出的是多传感器融合之后的障碍物信息。
```

**期望输出**

```text
感知融合模块的统一输入 channel 是 /perception/inner/PrefusedObjects。

引用：
- apollo-doc-005 page=1
```

### 12. e6-channel-012

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_fusion_output`
- 目标 source_id：`apollo-doc-005`
- 必须包含：`['/apollo/perception/obstacles']`
- 禁止包含：`['/perception/inner/PrefusedObjects']`
- 来源文档：`data/sources/apollo/apollo-perception-fusion-overview.md`

**输入**

```text
问题：感知融合模块的主要输出 channel 是哪一个？

参考资料：
[1] source_id=apollo-doc-005 locator=page=1
感知融合模块的相关参数 channel名称 channel说明 统一输入channel：各传感器感知的结果都会输出到 /perception/inner/PrefusedObjects，作为感知融合模块的源数据。感知融合模块的主要输出channel 是 /apollo/perception/obstacles，该 channel 输出的是多传感器融合之后的障碍物信息。
```

**期望输出**

```text
感知融合模块的主要输出 channel 是 /apollo/perception/obstacles。

引用：
- apollo-doc-005 page=1
```

### 13. e6-channel-013

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_fusion_source_data`
- 目标 source_id：`apollo-doc-005`
- 必须包含：`['/perception/inner/PrefusedObjects']`
- 禁止包含：`['/apollo/perception/obstacles']`
- 来源文档：`data/sources/apollo/apollo-perception-fusion-overview.md`

**输入**

```text
问题：各传感器感知结果会输出到哪个 channel 作为感知融合模块的源数据？

参考资料：
[1] source_id=apollo-doc-005 locator=page=1
感知融合模块的相关参数 channel名称 channel说明 统一输入channel：各传感器感知的结果都会输出到 /perception/inner/PrefusedObjects，作为感知融合模块的源数据。感知融合模块的主要输出channel 是 /apollo/perception/obstacles，该 channel 输出的是多传感器融合之后的障碍物信息。
```

**期望输出**

```text
各传感器感知结果会输出到 /perception/inner/PrefusedObjects，作为感知融合模块的源数据。

引用：
- apollo-doc-005 page=1
```

### 14. e6-channel-014

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_fusion_obstacle_output`
- 目标 source_id：`apollo-doc-005`
- 必须包含：`['/apollo/perception/obstacles']`
- 禁止包含：`['/perception/inner/PrefusedObjects']`
- 来源文档：`data/sources/apollo/apollo-perception-fusion-overview.md`

**输入**

```text
问题：多传感器融合后的障碍物信息由哪个 channel 输出？

参考资料：
[1] source_id=apollo-doc-005 locator=page=1
感知融合模块的相关参数 channel名称 channel说明 统一输入channel：各传感器感知的结果都会输出到 /perception/inner/PrefusedObjects，作为感知融合模块的源数据。感知融合模块的主要输出channel 是 /apollo/perception/obstacles，该 channel 输出的是多传感器融合之后的障碍物信息。
```

**期望输出**

```text
多传感器融合后的障碍物信息由 /apollo/perception/obstacles 输出。

引用：
- apollo-doc-005 page=1
```

### 15. e6-channel-015

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_control_chassis`
- 目标 source_id：`apollo-doc-009`
- 必须包含：`['/Apollo/canbus/chassis']`
- 禁止包含：`['/Apollo/control', '/Apollo/planning']`
- 来源文档：`data/sources/apollo/apollo-vision-control-overview.md`

**输入**

```text
问题：控制模块输入表中，底盘信息对应哪个 channel？

参考资料：
[1] source_id=apollo-doc-009 locator=page=1
控制模块输入channel 控制模块有三个输入channel：/Apollo/planning 规划信息，自车规划的轨迹信息 /Apollo/localization/pose 定位信息，自车的位置 /Apollo/canbus/chassis 底盘信息，自车的方向盘、速度信息 控制模块输出channel 控制模块有一个输出channel：/Apollo/control 输出控制信息，方向盘角度、油门刹车
```

**期望输出**

```text
控制模块输入表中，底盘信息对应 /Apollo/canbus/chassis。

引用：
- apollo-doc-009 page=1
```

### 16. e6-channel-016

- 类型：`e6_table_channel_same_row`
- 复核重点：`same_row_channel_alignment_control_output`
- 目标 source_id：`apollo-doc-009`
- 必须包含：`['/Apollo/control']`
- 禁止包含：`['/Apollo/canbus/chassis', '/Apollo/planning']`
- 来源文档：`data/sources/apollo/apollo-vision-control-overview.md`

**输入**

```text
问题：控制模块输出方向盘角度、油门刹车控制信息时使用哪个 channel？

参考资料：
[1] source_id=apollo-doc-009 locator=page=1
控制模块输入channel 控制模块有三个输入channel：/Apollo/planning 规划信息，自车规划的轨迹信息 /Apollo/localization/pose 定位信息，自车的位置 /Apollo/canbus/chassis 底盘信息，自车的方向盘、速度信息 控制模块输出channel 控制模块有一个输出channel：/Apollo/control 输出控制信息，方向盘角度、油门刹车
```

**期望输出**

```text
控制模块输出方向盘角度、油门刹车控制信息时使用 /Apollo/control。

引用：
- apollo-doc-009 page=1
```

### 17. e6-channel-017

- 类型：`e6_key_value_field_alignment`
- 复核重点：`key_value_field_alignment_cyberrt_channel_name`
- 目标 source_id：`apollo-doc-003`
- 必须包含：`['ChannelName']`
- 禁止包含：`['MessageType', 'FrameRatio', 'MessageSize']`
- 来源文档：`data/sources/apollo/apollo-channel-data-format.md`

**输入**

```text
问题：CyberRT Channel 数据字段里，表示数据通道名字的是哪个字段？

参考资料：
[1] source_id=apollo-doc-003 locator=page=1
打开 CyberMonitor 并进入特定数据通道，可以看到每个 Channel 中都有 ChannelName、MessageType、FrameRatio、MessageSize 数据字段。ChannelName 是数据通道的名字；MessageType 是通道内数据的消息类型；FrameRatio 是数据更新频率；MessageSize 是原始数据的大小。
```

**期望输出**

```text
表示数据通道名字的字段是 ChannelName。

引用：
- apollo-doc-003 page=1
```

### 18. e6-channel-018

- 类型：`e6_key_value_field_alignment`
- 复核重点：`key_value_field_alignment_cyberrt_message_type`
- 目标 source_id：`apollo-doc-003`
- 必须包含：`['MessageType']`
- 禁止包含：`['ChannelName', 'FrameRatio', 'MessageSize']`
- 来源文档：`data/sources/apollo/apollo-channel-data-format.md`

**输入**

```text
问题：CyberRT Channel 数据字段里，表示通道内数据消息类型的是哪个字段？

参考资料：
[1] source_id=apollo-doc-003 locator=page=1
打开 CyberMonitor 并进入特定数据通道，可以看到每个 Channel 中都有 ChannelName、MessageType、FrameRatio、MessageSize 数据字段。ChannelName 是数据通道的名字；MessageType 是通道内数据的消息类型；FrameRatio 是数据更新频率；MessageSize 是原始数据的大小。
```

**期望输出**

```text
表示通道内数据消息类型的字段是 MessageType。

引用：
- apollo-doc-003 page=1
```

### 19. e6-channel-019

- 类型：`e6_key_value_field_alignment`
- 复核重点：`key_value_field_alignment_cyberrt_frame_ratio`
- 目标 source_id：`apollo-doc-003`
- 必须包含：`['FrameRatio']`
- 禁止包含：`['ChannelName', 'MessageType', 'MessageSize']`
- 来源文档：`data/sources/apollo/apollo-channel-data-format.md`

**输入**

```text
问题：CyberRT Channel 数据字段里，表示数据更新频率的是哪个字段？

参考资料：
[1] source_id=apollo-doc-003 locator=page=1
打开 CyberMonitor 并进入特定数据通道，可以看到每个 Channel 中都有 ChannelName、MessageType、FrameRatio、MessageSize 数据字段。ChannelName 是数据通道的名字；MessageType 是通道内数据的消息类型；FrameRatio 是数据更新频率；MessageSize 是原始数据的大小。
```

**期望输出**

```text
表示数据更新频率的字段是 FrameRatio。

引用：
- apollo-doc-003 page=1
```

### 20. e6-channel-020

- 类型：`e6_key_value_field_alignment`
- 复核重点：`key_value_field_alignment_cyberrt_message_size`
- 目标 source_id：`apollo-doc-003`
- 必须包含：`['MessageSize']`
- 禁止包含：`['ChannelName', 'MessageType', 'FrameRatio']`
- 来源文档：`data/sources/apollo/apollo-channel-data-format.md`

**输入**

```text
问题：CyberRT Channel 数据字段里，表示原始数据大小的是哪个字段？

参考资料：
[1] source_id=apollo-doc-003 locator=page=1
打开 CyberMonitor 并进入特定数据通道，可以看到每个 Channel 中都有 ChannelName、MessageType、FrameRatio、MessageSize 数据字段。ChannelName 是数据通道的名字；MessageType 是通道内数据的消息类型；FrameRatio 是数据更新频率；MessageSize 是原始数据的大小。
```

**期望输出**

```text
表示原始数据大小的字段是 MessageSize。

引用：
- apollo-doc-003 page=1
```
