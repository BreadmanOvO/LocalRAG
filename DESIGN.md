# Design

## Source of truth

- Status: Active
- Last refreshed: 2026-09-13
- Primary product surfaces: 新任务、任务房间、资料资产、公司设置
- Evidence reviewed: `frontend/src/app/App.tsx`、`frontend/src/app/theme.tsx`、`frontend/src/pages/WorkspacePage.tsx`、`frontend/src/pages/RoomPage.tsx`、`frontend/src/pages/CompanyPage.tsx`、`frontend/src/features/rooms/MessageThread.tsx`、`frontend/src/features/rooms/MultiAgentPanel.tsx`、`frontend/src/styles.css` 及 `frontend/src/shared/api/` 的 FastAPI OpenAPI 客户端。
- Scope: v1.8 的 React + TypeScript + Vite 前端。任务执行、持久状态、模型路由、工具调用和权限控制由 Python/FastAPI 负责。

## Brand

- Personality: BeTheBoss 是沉稳、可追溯的任务领导产品。它让负责人、进度、证据和问题可见，但不要求用户操作框架内部概念。
- Trust signals: 明确负责人、持久化房间历史、可读任务轨迹、完整或失败状态、可关联证据的产物，以及 Agent 发言实际使用的模型。
- Avoid: 深色单色仪表盘、纯装饰性角色头像、营销式大卡片、正常任务流程中的架构讲解、虚构协作和以原始 JSON 代替产品界面。

## Product goals

- Goals: 从一个入口下达任务、查看协作进度、继续追问，并回溯到负责 Agent 和实际模型。
- Goals: 将 RAG、分析、工具、模型路由和 Subagent 执行作为对话后的可插拔能力，而非多个分离的用户模式。
- Goals: 多 Agent 的价值来自真实组织、可观察、可保存和可复盘，而不是同时展示许多角色名称。
- Non-goals: 让普通用户选择执行拓扑；把 Runtime 标识当作主内容；让页面设置改写运行中或历史房间；根据模型正文推断执行真相。
- Success signals: 新用户无需填写空间标识即可下达任务；回到历史任务时能找到负责人、进度、模型选择、证据和问题步骤；刷新和后续追问后房间仍清晰可读。

## Personas and jobs

- Primary personas: 用户是任务发起人，负责给出目标、补充资料、检查进展并判断结果是否可接受。
- Core jobs: 下达目标、查看或补充资料、观察项目组、在执行中追加约束、定位停滞步骤、回到历史房间，以及配置可用模型。
- Theme presets: 公司主题使用董事长助理、战略负责人、技术负责人、项目经理、架构师、工程师、研究员、数据分析师、审查员和报告撰写员等正式治理角色；当皇上主题使用皇上、内阁大学士、司礼监、六部尚书、都察院和翰林院等古代称谓。两者共用同一套运行能力。
- Persona contract: 预设角色的身份和职责固定；自定义人设明确标为后续开发。已配置 Agent 仅可调整模型绑定和自动路由约束。

## Information architecture

| 路由 | 用途 |
|---|---|
| `/workspace` | 新任务：可选标题和一段任务说明创建房间，不展示内部空间标识。 |
| `/rooms/:roomId` | 可持续追问的任务房间，包含协作动态、成员、产物、轨迹和问题回溯。 |
| `/assets` | 与任务关联的资料资产库。 |
| `/company` | 人设设置、模型设置、页面设置三个一级 Tab。 |

- Desktop: 左侧导航，中间任务内容，右侧为房间进度与详细信息。
- Navigation: BeTheBoss 品牌、新任务、资料资产、最近房间；设置固定在侧栏底部。
- 普通对话和召集后的项目组协作写入同一房间历史，不形成两个割裂的产品。

## Design principles

- 一个任务，一个房间：第一条任务直接创建房间，后续协作一直在该历史中完成。
- 先显示人能用的信息：目标、进度、负责人、模型、结果和阻塞优先于内部事件标识。
- 设置只影响未来：主题、模型绑定和自动路由偏好不能修改运行中任务。
- 结构化数据是真相：消息卡通过关联 `step_completed` 事件的 `message_id` 获取模型信息，绝不解析回答正文。
- 自动路由必须有边界：页面展示约束，后端选择候选；没有匹配模型时明确失败，不能静默替换。
- 房间证据优先：一次执行开始时生成 Agent 到模型的快照；即使之后设置变化，该 Agent 在这次 run 中仍使用冻结模型。

## Visual language

- 公司主题: 专业、明亮、安静的中性表面，以克制青绿色作为主操作色、砖红作为辅助色；绿色表示完成、琥珀表示待验证、红色表示问题。
- 当皇上主题: 克制的朱红、墨色和金色搭配浅中性背景；只改变称谓和氛围，不改变信息层级与交互行为。
- Typography: 中文优先的系统无衬线字；正文 14-16px；仅在诊断中用等宽字体显示代码和不透明 ID。
- Spacing/layout rhythm: 4px 间距基准、紧凑的工作布局和稳定栅格，不使用随视口缩放的字体。
- Shape/radius/elevation: 圆角不超过 8px，轻边框，几乎不使用阴影；仅重复条目和实际工具使用卡片，页面分区不悬浮成卡。
- Iconography: 使用 Lucide 的熟悉图标搭配清晰命令文本；纯图标控件必须有可访问名称和 tooltip。
- Avoid: 渐变、装饰圆球、作为命令的圆角文字胶囊、超大 Hero 卡、只靠颜色表达状态以及装饰性卡片嵌套。

## Components

| 组件 | 合同 |
|---|---|
| `ThemeProvider` | 首次本机访问必须选择公司或当皇上主题，只保存浏览器偏好；本机创建的房间保留创建时主题语义。 |
| `NewTaskComposer` | 隐藏稳定生成的空间标识，创建房间后直接进入。 |
| `SettingsTabs` | 拆分人设、模型、页面配置，避免无边界的长表单。 |
| `PresetRoleGrid` | 展示固定主题角色目录，不提供编辑或删除。 |
| `AgentBindingCard` | 支持固定模型和自动路由，展示等级、模态、场景和能力约束，并支持批量修改。 |
| `ModelEditor` | 支持 Provider、OpenAI-compatible URL、本机 Key、模型发现、手动模型名兜底、单选等级、多选能力/模态/场景和并发。发现失败不阻止保存手填模型，界面明确显示待验证。 |
| `TaskRoom` | 在同一房间展示对话、协作、成员、产物、失败和结构化任务轨迹。 |
| `ModelResolution` | 读取持久化 `step_completed.payload` 中的实际模型、profile、选择方式和理由，不根据消息正文猜测。 |

## Accessibility

- Target standard: WCAG 2.1 AA 的正文对比度和核心操作可用性。
- Keyboard/focus: Tab、模型控件、主题选择、消息输入、批量选择和重试均可键盘访问并有可见焦点。
- Semantics: 设置页使用 `role=tab`；状态同时包含文字与颜色；模型和错误信息在 DOM 中可被读屏读取。
- Responsive behavior: 低于 820px 时导航变为紧凑顶部布局，任务与房间变为单列，设置仍可访问；低于 600px 时表单操作为全宽。
- Content safety: 不执行 Markdown 或原始 HTML。API Key 使用密码字段，绝不能写入房间事件、日志、文档或 Git。

## Interaction states

- Loading: 说明正在加载的对象，避免通用空白 spinner。
- Empty: 展示直接下一步，例如下达任务或添加模型，不出现技术路线图措辞。
- Error: 保留已完成的房间内容，说明失败操作，并将用户留在相关步骤。
- Discovery failure: 手填模型名仍可保存，并明确说明配置处于待验证状态。
- Fixed binding: 未选择 profile 时不能保存固定绑定。
- Automatic routing: 展示所选约束；选择理由与无候选失败由后端返回。
- Running room: run 内模型绑定冻结，后续页面修改只影响新任务。
- Historical room: 历史消息和创建时主题语义在手动删除前保持稳定；切换浏览器主题不会改写房间记录。

## Content voice

- Tone: 直接、沉稳、可追责。
- Use: 新任务、任务房间、项目组、负责人、任务动态、进度与追溯、待验证、下达任务。
- Avoid in ordinary UI: Runtime、contract version、内部空间标识、worker、attempt、topology 和原始 API 术语。
- 当皇上主题可使用旨意、御前议事、内阁大学士等称谓，但仍保持清晰的任务语言。

## Implementation constraints

- Framework/styling: React 18、TypeScript、Vite、React Router、TanStack Query、CSS custom properties 与 Lucide 图标。
- API source: 现有字段以生成的 OpenAPI 类型为准；在后端 schema 重新生成前，前端以窄范围兼容扩展承接新增模型路由字段。
- State: 服务端数据存于 TanStack Query；本地状态仅用于草稿、侧栏/主题偏好、表单和未发送消息 outbox。
- Security: API Key 只能发送给本机模型配置接口并写入被 Git 忽略的本地配置，不得进入前端存储、事件、错误文本或示例配置。
- Validation: `npm run build` 会重新生成 OpenAPI 类型、运行 TypeScript 并打包 Vite。浏览器验收覆盖首次主题选择、页面主题切换、响应式 Tab、新任务创建、模型绑定、模型发现失败后的手填兜底和房间结构化模型展示。

## Open questions

- [ ] 将 `room_theme` 服务端持久化，使房间跨浏览器和设备仍保留语义；当前前端为它创建的房间在本机保存关联。
- [ ] 为手填模型名增加后端持久化的验证状态，使“待验证”不再依赖 readiness 推断。
- [ ] 在角色所有权、版本与删除语义明确后开放自定义人设。
