import type { Event } from "../../shared/api/client";

export function FailureCard({ event }: { event: Event }) {
  const error = typeof event.payload?.error === "string" ? event.payload.error : event.event_type;
  return <div className="failure-card"><span className="message-role">执行失败</span><p>{error}</p><small>事件 {event.identity.event_id} · 节点 {event.step_id ?? "未绑定"} · attempt {event.attempt_id ?? "未绑定"}</small></div>;
}
