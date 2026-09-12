# LocalRAG 工作台

这是 v1.8 的 React + TypeScript + Vite 前端壳。页面只负责路由、展示和服务器状态缓存；任务拆分、命令 CAS、事件写入和工具执行由 FastAPI/Python Runtime 负责。

```bash
npm install
npm run dev
```

开发服务器默认在 `5173`，`/api` 请求代理到 `http://127.0.0.1:8000`。构建前会从 `agent_platform.api.create_app()` 导出 `openapi.json`，再生成 `src/shared/api/schema.d.ts`，确保前后端字段由同一份合同产生。

当前页面：

- `/workspace`：统一入口和新建房间
- `/rooms/:roomId`：消息线程与事件轨迹
- `/assets`：资产中心占位页，等待 D23–D24
