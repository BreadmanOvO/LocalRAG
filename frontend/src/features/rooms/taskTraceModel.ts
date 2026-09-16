import type { Event } from "../../shared/api/client";

export function mergeRoomEvents(roomId: string, ...batches: Event[][]): Event[] {
  const byId = new Map<string, Event>();
  for (const batch of batches) for (const event of batch) {
    if (event.identity.room_id === roomId && event.room_id === roomId) byId.set(event.identity.event_id, event);
  }
  return [...byId.values()].sort((a, b) => a.identity.room_sequence - b.identity.room_sequence);
}

export const traceLabels: Record<string, string> = {
  run_started: "开始执行", run_queued: "等待执行", team_plan_created: "已生成任务分工",
  step_queued: "成员已排队", step_claimed: "成员已领取任务", step_started: "成员正在处理",
  step_completed: "成员完成步骤", step_failed: "成员步骤失败", step_retrying: "正在重试",
  step_reused: "复用已完成步骤", step_blocked: "前置任务未完成",
  handoff_created: "传递任务结果", handoff_accepted: "已接收任务交接",
  memory_read: "已读取房间记忆", task_start_failed: "任务暂未启动",
  run_completed: "任务已完成", run_failed: "任务出现问题", run_cancelled: "任务已停止", run_paused: "任务已暂停",
  tool_started: "正在调用工具", tool_completed: "工具调用完成",
};

export type TraceItem = { key: string; event: Event; records: Event[]; ordinal: number };

export function projectTaskTrace(events: Event[], runId: string | null): TraceItem[] {
  const rows = new Map<string, Omit<TraceItem, "ordinal">>();
  for (const event of events) {
    if (event.run_id !== runId || !traceLabels[event.event_type]) continue;
    const isStep = event.event_type.startsWith("step_") && (event.step_id || event.payload.sequence != null);
    const key = isStep ? `step:${event.step_id || event.payload.sequence}` : event.event_type === "run_queued" || event.event_type === "run_started" ? "run-start" : event.identity.event_id;
    const row = rows.get(key);
    if (row) {
      row.records.push(event);
      // A restored step emits step_completed then step_reused: keep its model metadata.
      if (!(event.event_type === "step_reused" && row.event.event_type === "step_completed")
        && !(event.event_type === "run_queued" && row.event.event_type === "run_started")) row.event = event;
    } else rows.set(key, { key, event, records: [event] });
  }
  return [...rows.values()].map((row, index) => ({ ...row, ordinal: index + 1 }));
}
