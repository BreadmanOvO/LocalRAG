# v1.8 Agent Platform 包边界

这里是 v1.8 新增 Python Runtime 的唯一顶层包。当前只建立边界和依赖方向；v1.7 的 `agent/`、`core/`、`model_gateway/`、`model_serving/` 和 Streamlit 入口继续按现状运行，迁移通过适配器完成，不在 D01 直接改写。

## 仓库中的位置

```text
LocalRAG/
├── agent/                 # v1.7 Agent 与研究流程（保留）
├── core/                  # v1.7 检索、记忆和数据逻辑（保留）
├── model_gateway/         # v1.7 模型访问适配（保留）
├── model_serving/         # v1.7 本地模型服务（保留）
├── app_*.py               # v1.7 Streamlit 入口（迁移期保留）
└── agent_platform/        # v1.8 Runtime 的唯一新顶层包
    ├── contracts/         # 稳定的数据与事件合同
    ├── runtime/           # 状态、租约、预算、恢复
    ├── routing/           # 任务画像与路由
    ├── architectures/     # 五类协作架构的计划策略
    ├── collaboration/     # 成员协作与共享知识
    ├── conversations/     # 持久房间、消息与追溯投影
    ├── personas/          # 公司角色与人设快照
    ├── capability_packs/  # RAG、解析、计算、多模态工具
    ├── integrations/      # 模型、MCP、旧系统适配
    ├── sandbox/           # 执行隔离与资源策略
    ├── api/               # FastAPI 组合层
    └── worker/            # 后台领取与提交入口
```

D01 只提交目录和依赖边界。目录下的 `__init__.py` 是可导入的空壳，不表示对应功能已经可用；功能代码按开发计划中对应 Day 节点逐步加入。

## 目录职责

| 子包 | 负责什么 | 不负责什么 |
|---|---|---|
| `contracts` | 任务、计划、角色、事件、结果、预算和沙箱 schema | 不调用模型、工具或数据库 |
| `runtime` | 状态机、租约、预算、checkpoint、提交与恢复 | 不写业务拆分 Prompt |
| `routing` | TaskProfile、架构候选和能力绑定 | 不直接执行步骤 |
| `architectures` | 分层、蜂群、对抗、异构和图的计划策略 | 不维护第二套状态机 |
| `collaboration` | Blackboard、Inbox、Handoff、共享知识和成员通信 | 不绕过 Runtime 写状态 |
| `conversations` | Room、消息、事件投影、保留、归档和删除 | 不触发模型执行 |
| `personas` | 公司预设、角色、人设版本和运行快照 | 不授予额外权限 |
| `capability_packs` | RAG、文件解析、计算和多模态能力适配 | 不决定任务拓扑 |
| `integrations` | 模型、MCP、外部工具和旧系统适配 | 不定义核心状态 |
| `sandbox` | 文件、网络、CPU、内存和输出边界 | 不把 Prompt 当权限控制 |
| `api` | FastAPI 命令、查询和 SSE 组合层 | 不复制 Runtime 逻辑 |
| `worker` | 后台领取、执行和提交入口 | 不持有独立业务真相 |

依赖方向固定为：`api/worker → runtime → contracts`；`runtime` 通过接口调用 `routing`、`architectures`、`collaboration`、`capability_packs`、`integrations` 和 `sandbox`。这些子包不能自行创建模型循环或另建持久化状态。详细字段合同见 [Runtime 协议草案](../RAG_md/docs/v1.8/runtime-contracts.md)，Day 排程见 [完整开发计划](../RAG_md/docs/v1.8/development-plan.md)，D01 验收记录见 [D01 acceptance](../RAG_md/docs/v1.8/evidence/d01-acceptance.md)。

## 当前状态

所有子包目前都是边界占位，状态为 `planned`。D01 只验收目录、依赖方向和基线记录；直到对应 Day 节点通过，不应从旧入口导入这些占位包，也不应把目录存在描述为 v1.8 功能已实现。
