# v1.8 Agent Platform 包边界

这里是 BeTheBoss 工作台的 Python 后端：提供 FastAPI、任务调度、云模型执行、房间持久化、事件流与资产接口。v1.7 的 `agent/`、`core/`、`model_gateway/`、`model_serving/` 和 Streamlit 入口继续运行，通过适配器复用。

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

D01 建立目录与依赖边界，后续功能按 Day 节点加入。目录存在不表示功能已验收，状态见下文。

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

截至 2026-09-15，直办、分层、蜂群、对抗、图式、异构六种执行模式已接入 `TeamStepScheduler`，支持依赖等待、并行分支、有限重试、熔断、摘要交接和完成步骤恢复。用户提交任务后自动执行，Agent 实际模型固定到房间绑定，模型选择及处理进度写入房间事件。

一键启动默认使用 SQLite；SQLAlchemy 同时提供 PostgreSQL 适配，迁移包含 `0001`–`0006`。房间、消息、事件、task/run、命令与房间租约可持久保存。取消命令事务化提交，checkpoint 校验计划指纹，SSE 按原始游标补读，前端轨迹按当前任务合并并使用连续展示编号。

资产解析/入库、OCR/VLM 接口、MCP stdio、S3/MinIO 适配和 Bearer/space 鉴权均有代码与定向测试。工作台当前在 API 进程内使用有界后台线程；独立 SQL worker 提供领取与 fencing 合同，但其命令行默认 handler 仍为空确认，不能作为真实任务执行部署。生产 PostgreSQL 故障接管、真实对象存储恢复及云模型长期稳定性需分别验收。测试结果与限制统一见 [当前验收记录](../RAG_md/docs/v1.8/evidence/2026-09-15-runtime-closure.md)，历史 Day 文档记录当时范围。
