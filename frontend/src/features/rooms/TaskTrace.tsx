import { useState } from "react";
import type { Event } from "../../shared/api/client";
import { formatDateTime } from "../../shared/time";
import { modelResolutionFromEvent, modelSelectionLabel } from "./modelResolution";
import { projectTaskTrace, traceLabels } from "./taskTraceModel";

export function TaskTrace({ events, connected, loading }: { events: Event[]; connected: boolean; loading: boolean }) {
  const [selection, setSelection] = useState("latest");
  const [expanded, setExpanded] = useState(false);
  const starts = events.filter((e) => e.event_type === "run_started");
  const runId = selection === "latest" ? starts[starts.length - 1]?.run_id ?? null : selection;
  const rows = projectTaskTrace(events, runId);
  const names = new Map<string, string>();
  for (const event of events) {
    if (event.run_id !== runId) continue;
    const participants = event.payload.participants;
    if (Array.isArray(participants)) for (const member of participants) {
      if (member && typeof member === "object" && "agent_id" in member && "display_name" in member)
        names.set(String(member.agent_id), String(member.display_name));
    }
  }
  const visible = expanded ? rows : rows.slice(-12);
  return <article className="panel trace-panel">
    <div className="panel-heading"><div><p className="eyebrow">进度与追溯</p><h2>任务轨迹</h2></div><span className={connected ? "live-indicator" : "muted"}>{connected ? "实时更新" : "等待重连"}</span></div>
    {starts.length > 1 && <label>查看任务<select aria-label="查看任务轨迹" value={selection} onChange={(e) => { setSelection(e.target.value); setExpanded(false); }}>
      <option value="latest">当前任务</option>
      {starts.map((start, index) => <option key={start.run_id} value={start.run_id ?? ""}>任务 {index + 1} · {formatDateTime(start.timestamp)}</option>)}
    </select></label>}
    {loading && <p className="muted">加载进度…</p>}
    {rows.length > 12 && <button className="text-link" onClick={() => setExpanded(!expanded)}>{expanded ? "收起较早步骤" : `查看较早 ${rows.length - 12} 条进度`}</button>}
    {visible.map(({ key, event, records, ordinal }) => {
      const resolution = modelResolutionFromEvent(event);
      const name = event.payload.display_name || names.get(String(event.payload.agent_id)) || event.payload.agent_id;
      return <div className="event-row" key={key}>
        <span className="event-index">{ordinal}</span>
        <div className="event-copy"><b>{traceLabels[event.event_type]}</b>
          {typeof name === "string" && <p>{name}{typeof event.payload.title === "string" ? ` · ${event.payload.title}` : ""}</p>}
          <p><time dateTime={event.timestamp}>{formatDateTime(event.timestamp)}</time></p>
          {resolution && <p className="trace-model-name">{resolution.model} · {modelSelectionLabel(resolution.selectionMode)}</p>}
          <details><summary>查看记录{records.length > 1 ? `（${records.length} 条）` : ""}</summary>
            {records.map((record) => <p key={record.identity.event_id}>{traceLabels[record.event_type]} · {formatDateTime(record.timestamp)}<br/><small>事件游标 #{record.identity.room_sequence}</small></p>)}
            {resolution?.modelProfile && <p>模型配置：{resolution.modelProfile}</p>}
            {resolution?.selectionReason && <p className="trace-model-reason">{resolution.selectionReason}</p>}
            <small>记录号：{event.identity.event_id}</small>
          </details>
        </div>
      </div>;
    })}
    {!loading && rows.length === 0 && <p className="empty-state">暂无进度记录。</p>}
  </article>;
}
