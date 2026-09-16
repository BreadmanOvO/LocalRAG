import type { Event } from "../../shared/api/client";

export function FailureCard({ event }: { event: Event }) {
  const payload = event.payload ?? {};
  const errorType = typeof payload.error_type === "string" ? payload.error_type : typeof payload.error === "string" ? payload.error : event.event_type;
  const errorCode = typeof payload.error_code === "string" ? payload.error_code : "";
  const legacyMessages: Record<string, string> = {
    APIError: "模型服务请求失败，供应商没有返回可直接展示的具体原因。",
    RuntimeError: "执行器返回了运行时错误，已保留失败步骤和运行记录。",
    worker_unavailable: "后台执行器不可用，任务没有真正开始执行。",
  };
  const message = typeof payload.error_message === "string" ? payload.error_message : legacyMessages[errorType] ?? errorType;
  const suggestion = typeof payload.suggestion === "string" ? payload.suggestion : errorType === "APIError" ? "展开右侧任务轨迹查看失败步骤；检查模型 URL、模型名称、API Key、额度和供应商状态后重试。" : "请查看运行轨迹并检查模型设置后重试。";
  const phase = typeof payload.phase === "string" ? payload.phase : "runtime";
  const agent = typeof payload.agent_name === "string" ? payload.agent_name : typeof payload.agent_id === "string" ? payload.agent_id : "未标记 Agent";
  const model = typeof payload.model === "string" ? payload.model : "未记录模型";
  const status = typeof payload.status_code === "number" ? `HTTP ${payload.status_code}` : "";
  const retryable = payload.retryable === true;
  return <div className="failure-card">
    <span className="message-role">任务出现问题</span>
    <p>{message}</p>
    <p className="muted">{suggestion}</p>
    <div className="failure-meta"><span>阶段：{phase}</span><span>Agent：{agent}</span><span>模型：{model}</span>{status && <span>{status}</span>}<span>{retryable ? "可重试" : "需检查配置"}</span></div>
    <details><summary>展开技术详情</summary><small>错误码：{errorCode || "未分类"} · 类型：{errorType}</small></details>
    <small>问题步骤：{event.step_id ?? "查看右侧任务卡"} · 记录号：{event.identity.event_id}</small>
  </div>;
}
