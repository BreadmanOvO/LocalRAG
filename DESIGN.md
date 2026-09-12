# Design

## Source of truth

- Status: Draft — v1.8 目标设计，尚未实现
- Last refreshed: 2026-09-12
- Primary product surfaces: 公司式助理工作台、项目群聊、任务追溯、资产库与公司设置
- Scope: 主仓 v1.8，与 main 按验收批次同步；小仓文档使用 main。总体方案及角色目录见 [v1.8 升级方案](RAG_md/docs/v1.8/agent-platform-upgrade-plan.md)，执行排程见 [完整开发计划](RAG_md/docs/v1.8/development-plan.md)。
- Protocol: 身份、执行中追问、交接与恢复以 [Runtime 协议草案](RAG_md/docs/v1.8/runtime-contracts.md) 为准；本文件定义这些状态如何呈现。
- Evidence reviewed: 当前页面为 Streamlit；`app_qa.py:76` 初始化、`:288` 工具轨迹、`:306` 答复详情、`:367` 研究计划、`:444` 上下文状态、`:658` 事件消费；`app_file_uploader.py:16` 上传／预览／发布入口。历史 UI 截图保存在 `RAG_md/docs/assets/ui/`，不作为新界面视觉基准。当前没有 React 前端；以下布局和技术栈是 v1.8 新决策。

## Brand

- Personality: 一个做事认真、成员风格鲜明的项目团队；总助理持续对接用户，部门帮助分工。
- Trust signals: 谁负责、正在做什么、依据是什么、什么失败了、哪些结论还需确认；状态能从持久记录核验。
- Avoid: 只堆角色头像的装饰性群聊、虚构讨论、用模型赞同数证明事实、把日志堆给用户当答案。
- 人设表达允许差异：研究员善于追问、工程师重验证、编辑重清晰、风险审查员偏审慎；表达差异不改变权限和结果合同。

## Product goals

- Goals: 用户像董事长一样交代目标，总助理独办或组织项目组；成员在群内交接、共享证据并回报，最终由总助理汇总。
- Goals: 群聊同时承担持续沟通、任务进度和故障追溯；未手动删除的聊天室可保存、重开和继续追问。
- Goals: 前端独立重做为 React + TypeScript，Python 保留 Agent 框架、算法、调度、记忆、检索和计算逻辑。
- Non-goals: 让用户每次选择五种架构；角色全部常驻；前端复制执行器；通过聊天文本自动判断任务完成。
- Success signals: 无需理解架构即可下达任务；能找到负责人、交付物和问题节点；刷新或重启恢复已确认消息，打开历史不触发执行。具体质量和性能门槛以升级计划第 9 节为准。

## Personas and jobs

- Primary personas: 用户是董事长／任务发起人，总助理是唯一常驻对接角色。平台开发者可展开执行详情，但不是默认界面的唯一受众。
- User jobs: 下达目标；补充资料；查看成员与进展；质疑结论；定位失败；暂停／继续；取回产物；重开历史项目。
- 公司预设：董事长办公室、战略研究、产品、研发架构、数据知识、设计体验、质量风险、市场内容、财务运营、法务合规。具体角色、风格和交付边界以升级计划第 0.5 节为唯一目录。
- 初始化：公司名、总助理名字与风格、启用部门、工具接入。支持修改预设并另存，允许跳过非必填项。
- 角色配置：界面区分“人设风格”“工作职责”“本次模型与权限”；能力未配置时解释缺口。预设属于角色库，不增加独立业务模式。
- Key contexts: 桌面长任务、跨部门协作、图文资料分析、网络断连、多标签页、历史故障复盘；窄屏支持完整核心操作。

## Information architecture

主导航只保留工作台、资产库、公司设置；聊天室历史放在工作台左侧，可搜索、归档和重开。诊断作为房间内部的追溯视图，不增加一个与任务脱节的主页面。

| 路由 | 内容与身份 |
|---|---|
| `/workspace` | 总助理入口与最近项目；第一条消息原子创建 Room 和消息后进入房间 |
| `/rooms/:roomId` | 总助理直办与项目群聊共用；组群只添加成员，地址和消息 ID 不变 |
| `/rooms/:roomId?step=:stepId&event=:eventId` | 在同一房间定位问题节点与对应消息，可复制链接复盘 |
| `/assets` | 原件、解析预览、纠错、版本和显式发布；发布后评测仍由用户选择 |
| `/company` | 公司、部门、角色预设、自定义人设、模型能力与工具权限配置 |

布局：桌面左侧导航，中间消息与产物，右侧任务／证据／追溯抽屉。任务图与群聊是同一房间的两个视图，点击节点定位消息，点击消息定位步骤。单助理会话复用消息组件和持久化协议，不强制展示成员面板。

## Design principles

- 一个连续入口：总助理从接收目标到最终交付持续在场；原房间邀请成员，收尾后仍可直办，无需复制会话或切换模式页。
- 群聊展示真实交流：分工、证据请求、进展、交接、反例、裁决均有事件依据；可见沟通与隐藏模型推理区分。
- 先显示用户能用的信息：目标、负责人、阻塞与产物优先；架构 ID、原始 JSON、fencing token 只在诊断中展示。
- 可追溯的失败：错误卡标出失败节点、输入来源、受影响步骤和下一步；“已观察故障”与“推测原因”分开。
- 保存是服务端合同：本地缓存只改善体验；聊天是否已保存由后端确认，关闭页面不发取消命令。
- 人工操作有可见后果：暂停、继续、调整目标、重新分派和删除分别定义，不用一个“重试”重开全部任务。
- Tradeoffs: 采用独立 React 前端以支持长消息列表和图联动。复用现有状态、引用和错误语义，Streamlit 控件不直接迁移。

## Visual language

- Color: 浅色中性背景，蓝色用于操作和选中；绿色表示完成，琥珀表示待确认／部分结果，红色表示失败。角色头像颜色不代替运行状态。
- Typography: 中文正文采用系统无衬线字体，14–16px；等宽字体只用于代码、标识符和诊断值。
- Spacing/layout rhythm: 以 4px 为间距单位；桌面侧栏约 240px，右侧检查器约 360px，消息区占剩余空间，面板可收起。
- Shape/radius/elevation: 轻边框和 8px 圆角，减少阴影；任务卡、消息和证据卡有明确层级。
- Motion: 用户查看旧消息时不强行滚到底部，显示新消息计数；动态状态不抢键盘焦点。
- Imagery/iconography: 角色头像＋部门＋职责文字；图表和文件显示真实区域预览，缺失资源显式标记。
- 完成态先显示交付摘要；执行态先显示当前工作和阻塞，避免空等最终结果。

## Components

| 组件 | 行为与数据依据 |
|---|---|
| `CompanySetup / RoleLibrary` | 初始化公司与总助理，启用部门，编辑人设和能力；旧运行使用固定角色快照 |
| `AssistantComposer` | 单一输入框、附件、暂停；活动任务中仍可保存追问，并显示关联任务及处理状态；auto/direct/delegate 语义以协议为准 |
| `RoomList / RoomHeader` | 搜索历史、未读、归档与重开；顶部显示目标、成员和状态 |
| `MemberCard` | 部门、职责、当前工作、模型能力与参与历史；空闲不伪装成执行中 |
| `TaskRoom / MessageThread` | 真实协作消息、回复、交接、证据和历史修订，虚拟列表＋游标分页 |
| `PlanSummary` | 简短说明为何委派及当前分工；诊断中显示分层、蜂群、对抗、异构、图的组合 |
| `TaskGraph` | React Flow 展示后端计划节点和边；责任关系与数据依赖用不同标记，默认只读 |
| `SwarmBoard` | 认领、进行中、待协助、待复核、完成；租约时钟只在详情中，不混作记录保留期 |
| `ReviewThread` | 提案、反例、修改、裁决和未解决争议，各自指向对应论断版本 |
| `TracePanel / FailureCard` | 从消息跳节点、attempt、调用及输入输出；展示受影响后继、重试条件和操作是否已生效，未知时先核对 |
| `EvidenceCard / ArtifactCard` | 来源区域、输入版本、核验状态、产物依赖和下载；stale 显示为需更新 |
| `ToolPanel / ApprovalCard` | 已登记工具与数据范围；需要新增授权时列具体目标、影响及资源上限 |
| `RetentionNotice / DeleteRoomDialog` | 默认持续保留；删除明确影响、活动工作处理和备份清除规则 |

- Variants and states: 房间 `active/archived/deleted`；run `queued/running/paused/needs_input/completed/failed/cancelled`；结果完整性 `complete/partial`，不把 partial 混成运行状态。
- Message states: `sending/persisted/failed`；流式消息另带 `streaming/interrupted/complete`。服务端确认前可重送，不能提前显示保存成功。
- Processing states: 消息“已保存”和请求“待处理／已应用／已拒绝”分开展示；生效记录关联命令、输入版本及计划版本。任务进行中不禁用输入框，不用研究任务冲突提示代替收件。
- Command states: `accepted/applied/rejected` 由服务端确认；取消、继续发生跨标签页版本冲突时刷新当前状态，不能乐观显示控制已生效。
- Evidence states: `unreviewed/supported/contradicted/insufficient`，stale 是独立版本失效标记。人工确认与模型复核分开。
- Token/component ownership: 后端 schema 为状态定义来源；前端仅渲染和发命令，不靠正文、颜色或流结束推断成功。

## Accessibility

- Target standard: WCAG 2.1 AA 基本可用性；中文优先，技术标识保留原文。
- Keyboard/focus: 输入、引用、暂停、成员筛选、追溯和删除均可键盘操作；弹窗关闭后焦点返回触发处。
- Contrast/readability: 状态用文字＋图标，表格和代码可横向滚动。
- Screen-reader semantics: 消息作者、部门、时间、状态可读；图提供等价步骤列表，非视觉用户能定位失败。
- Reduced motion: 关闭动画，不强制跟随流式内容；新消息提示采用低干扰播报。

## Responsive behavior

- Desktop: 1280px 以上三栏；1024–1279px 右侧面板改为抽屉；更窄时左侧导航折叠。
- Mobile: 单栏群聊，成员和任务图独立抽屉，保留提交、审批、暂停、恢复和查历史；复杂图可切列表。
- Touch/hover: 所有核心操作可点击，不依赖 hover；删除入口位于房间菜单，与归档分开。

## Interaction states

- Loading: 显示具体工作、已收到事件和取消／暂停入口；分页历史单独加载。
- Empty: 总助理欢迎信息符合人设；给一个真实任务示例，能力未配置时提供设置入口。
- Error: 保留失败消息及已完成结果，显示影响、可恢复性和问题节点；原始错误码放详情。
- Success: 总助理交付产物并附证据、参与者、未解决项；仍可继续追问，不清空房间。
- Disabled: 数据／权限不足、删除中或不可恢复时解释原因。禁用模型切换不阻止查看历史。
- Offline: 显示最后保存状态，断网期间新发送内容保持待发送；恢复后按 room_sequence 补读并去重。存储不可用时不显示已保存。
- Resume: 重开聊天室只读历史；继续执行校验 checkpoint／版本／权限。终态追问创建关联新 run。
- Steering: 执行中补充约束先保存为待处理，在安全边界生效；暂停期间发消息不默认恢复。含义不明时在原房间澄清，不丢消息或静默改任务。
- Archive: 归档只整理列表，活动任务继续运行；菜单说明这一点，并提供独立暂停操作。取消归档只恢复可见性。
- Uncertain effect: 工具请求已发出但结果未知时显示“正在核对操作结果”；有待核对副作用时禁用自动重发，保留状态查询或人工核对入口。
- Delete: 显示受影响房间和产物，确认后后端停止新派发并删除／标记记录；共享知识库不被级联删除。未手动删除的历史不因空闲或任务完成自动清理。

## Content voice

- Tone: 默认总助理沉稳直接；成员可以保留研究、工程、编辑或审查风格，不能虚构身份资质。
- Terminology: 面向用户说“项目组、负责人、交接、证据、待复核、问题步骤”；拓扑、attempt、lease、plan revision 放诊断。
- Microcopy: “表格解析失败，计算步骤尚未开始”“补充内容已保存，等待应用到当前任务”“暂停已生效，仍有一个调用在途”“操作结果尚未确认，先核对再重试”。
- 共享进展只描述已完成或正在执行的工作；估计、推断、审核意见均与事实区分。

## Implementation constraints

- Framework: React + TypeScript + Vite、React Router、TanStack Query、Tailwind CSS + shadcn/ui；React Flow 展示依赖。v1.8 不再以 Streamlit 为新前端基础。
- Frontend organization: `src/app` 负责路由和 Provider，`pages` 装配页面，`features` 实现发送／重试等用户动作，`entities` 展示房间／消息／任务，`shared` 放 UI、主题和生成客户端。先按实际功能建目录，不空建全部抽象。
- Backend: FastAPI + Python Runtime／worker，PostgreSQL 持久状态，现有索引与资产存储；LLM 调用、路由、图调度、知识权限和沙箱算法都在 Python。
- Transport: HTTP 命令查询＋SSE 已提交事件；OpenAPI 生成 TypeScript 客户端，事件有独立版本化 schema。SSE room_sequence 断点重连、event_id 去重，流式增量先持久化后推送；快照和游标具有一致性边界，前端不猜缺失的事件。
- State: TanStack Query 缓存服务器快照；本地状态只管面板、草稿与滚动位置，不承担任务状态真相。密钥不入前端，本地草稿不等于聊天室备份。
- Security/rendering: 同源 API 与受保护会话；Markdown 不执行原始 HTML，引用 URL 检查协议；附件下载校验授权；不把聊天文本当代码运行。
- Performance: 消息虚拟列表、历史游标分页、证据和大图按需加载；目标读写量在 P1 测量后冻结，避免无限返回全房间。
- Compatibility: 导入旧持久会话／任务时保留原 ID 映射，缺失原文显式标明；旧 task 参数可跳转到对应房间。新 UI 通过验收前保留 Streamlit 回归入口。
- Validation: 组件测试覆盖状态与操作；Playwright 覆盖真实 API 提交、直办转组群、执行中追问、跨标签页控制冲突、断网恢复、刷新、群聊回复、失败追溯、归档、删除、角色快照和窄屏。模拟数据只用于布局开发。

## Open questions

- 公司名称和默认头像尚未定稿，首版使用可编辑名称和字母／文字头像，不阻塞协议与布局。
- 实际大房间消息量和附件容量在 P1 基线记录后确定，用于设定分页与冷存储预算；不得以容量阈值自动删除未手动删除的聊天。
