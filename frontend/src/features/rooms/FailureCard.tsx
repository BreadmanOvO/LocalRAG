import type { Event } from "../../shared/api/client";

export function FailureCard({ event }: { event: Event }) {
  const error = typeof event.payload?.error === "string" ? event.payload.error : event.event_type;
  return <div className="failure-card"><span className="message-role">任务出现问题</span><p>{error}</p><small>问题步骤：{event.step_id ?? "正在确认"} · 记录号：{event.identity.event_id}</small></div>;
}
