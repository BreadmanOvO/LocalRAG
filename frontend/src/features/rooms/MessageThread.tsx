import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Bot, ChevronDown, ChevronUp, Clock3, Cpu, LoaderCircle, RefreshCw, SendHorizontal, UserRound } from "lucide-react";
import { api, type Event, type Message } from "../../shared/api/client";
import { enqueueMessage, readOutbox, removeFromOutbox, type PendingMessage } from "../../shared/realtime/outbox";
import { modelSelectionLabel, modelResolutionFromEvent, resolutionByMessageId } from "./modelResolution";
import { formatDateTime } from "../../shared/time";

function payload(event: Event): Record<string, unknown> { return event.payload as Record<string, unknown>; }
function text(value: unknown): string { return typeof value === "string" ? value : ""; }

function duration(value: unknown): string {
  if (typeof value !== "number") return "";
  const seconds = Math.max(0, Math.round(value / 1000));
  return seconds < 60 ? `${seconds} 秒` : `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`;
}

function CollapsibleText({ children }: { children: string }) {
  const [expanded, setExpanded] = useState(false);
  const lines = children.split("\n");
  const shouldFold = children.length > 800 || lines.length > 12;
  const visible = shouldFold && !expanded ? `${children.slice(0, 800).split("\n").slice(0, 12).join("\n").trimEnd()}…` : children;
  return <div className="collapsible-message"><p>{visible}</p>{shouldFold && <button type="button" className="message-expand" onClick={() => setExpanded((value) => !value)}>{expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}{expanded ? "收起" : "显示全部"}</button>}</div>;
}

type ProcessRun = { runId: string; events: Event[]; architecture: string; terminal: boolean };

function processRuns(events: Event[]): ProcessRun[] {
  const groups = new Map<string, Event[]>();
  for (const event of events) {
    if (!event.run_id) continue;
    groups.set(event.run_id, [...(groups.get(event.run_id) ?? []), event]);
  }
  return [...groups].map(([runId, items]) => {
    const start = items.find((item) => item.event_type === "run_started");
    return { runId, events: items, architecture: text(start?.payload.architecture), terminal: items.some((item) => ["run_completed", "run_failed", "run_cancelled"].includes(item.event_type)) };
  });
}

function ProcessingRecord({ run, onFocusStep }: { run: ProcessRun; onFocusStep?: (sequence: number) => void }) {
  const participants = new Map<string, string>();
  const plan = run.events.find((event) => event.event_type === "team_plan_created");
  const steps = Array.isArray(plan?.payload.steps) ? plan.payload.steps as Array<Record<string, unknown>> : [];
  for (const event of run.events.filter((item) => item.event_type === "team_planned")) {
    const rows = Array.isArray(event.payload.participants) ? event.payload.participants : [];
    for (const row of rows) if (row && typeof row === "object") participants.set(text((row as Record<string, unknown>).agent_id), text((row as Record<string, unknown>).display_name));
  }
  const completions = run.events.filter((event) => event.event_type === "step_completed");
  const handoffs = run.events.filter((event) => event.event_type === "handoff_created");
  const started = run.events.find((event) => event.event_type === "run_started")?.timestamp;
  const ended = [...run.events].reverse().find((event) => ["run_completed", "run_failed", "run_cancelled"].includes(event.event_type))?.timestamp;
  const elapsed = started && ended ? duration(new Date(ended).getTime() - new Date(started).getTime()) : "进行中";
  return <details className="processing-record" open={!run.terminal}>
    <summary><span className={run.terminal ? "process-dot done" : "process-dot active"} /><span>处理过程</span><small>{elapsed}</small><ChevronDown size={15} /></summary>
    <div className="processing-body">
      <div className="process-meta"><span>{run.architecture || "路由中"}</span><span>{steps.length} 个步骤</span><span>{run.runId.slice(-8)}</span></div>
      {steps.map((step) => {
        const sequence = Number(step.sequence);
        const complete = completions.find((event) => Number(event.payload.sequence) === sequence);
        const queued = run.events.find((event) => event.event_type === "step_queued" && Number(event.payload.sequence) === sequence);
        const agentId = text(step.agent_id);
        return <details className="process-step" key={sequence}><summary><span>#{sequence}</span><b>{participants.get(agentId) || agentId}</b><span>{text(step.title)}</span><small>{duration(complete?.payload.duration_ms) || (complete ? "已完成" : "处理中")}</small></summary><div className="process-step-detail"><p><b>模型</b>{text(complete?.payload.model) || text(queued?.payload.model) || "等待调用"}</p><details><summary>查看实际输入上下文</summary><pre>{text(queued?.payload.input) || "尚未生成输入"}</pre></details><details><summary>查看阶段产出</summary><pre>{text(complete?.payload.output) || "正在生成"}</pre></details></div></details>;
      })}
      {handoffs.map((handoff) => {
        const sequence = Number(handoff.payload.sequence);
        const target = text(handoff.payload.to_agent_id);
        return <button type="button" className="handoff-chat-line" key={handoff.identity.event_id} onClick={() => onFocusStep?.(sequence)}><span>@{participants.get(target) || target}</span><p>{text(handoff.payload.summary) || "已接收上游整理的信息"}</p><small>查看交接</small></button>;
      })}
      {run.events.filter((event) => event.event_type === "memory_read").map((event) => <details className="memory-read-record" key={event.identity.event_id}><summary>读取记忆 · {Array.isArray(event.payload.message_refs) ? event.payload.message_refs.length : 0} 条引用</summary><pre>{text(event.payload.summary) || "本轮没有可用历史记忆"}</pre></details>)}
    </div>
  </details>;
}

function streamingFinal(events: Event[]): { content: string; agent: string; model: string } | null {
  const runs = processRuns(events);
  const latest = runs[runs.length - 1];
  if (!latest || latest.terminal) return null;
  const plan = latest.events.find((event) => event.event_type === "team_plan_created");
  const steps = Array.isArray(plan?.payload.steps) ? plan.payload.steps as Array<Record<string, unknown>> : [];
  const final = steps.find((step) => step.is_final === true) ?? steps[steps.length - 1];
  if (!final) return null;
  const sequence = Number(final.sequence);
  const deltas = latest.events.filter((event) => event.event_type === "step_output_delta" && Number(event.payload.sequence) === sequence);
  if (!deltas.length) return null;
  const lastStream = text(deltas[deltas.length - 1].payload.stream_id);
  const unique = new Map<number, string>();
  for (const event of deltas) if (text(event.payload.stream_id) === lastStream) unique.set(Number(event.payload.token_index), text(event.payload.delta));
  const latestDelta = deltas[deltas.length - 1];
  return { content: [...unique].sort((a, b) => a[0] - b[0]).map((item) => item[1]).join(""), agent: text(latestDelta.payload.display_name) || text(latestDelta.payload.agent_id), model: text(latestDelta.payload.model) };
}

export function MessageThread({ roomId, spaceId, messages, events, disabled = false, onFocusStep }: { roomId: string; spaceId: string; messages: Message[]; events: Event[]; disabled?: boolean; onFocusStep?: (sequence: number) => void }) {
  const [content, setContent] = useState("");
  const [pending, setPending] = useState<PendingMessage[]>(() => readOutbox(roomId));
  const queryClient = useQueryClient();
  const { chatMessages, resolutions } = useMemo(() => {
    const mapped = resolutionByMessageId(events);
    const synthetic: Message[] = [];
    for (const event of events) {
      if (event.event_type !== "step_completed" || typeof event.payload.message_id === "string" && event.payload.message_id) continue;
      const content = text(event.payload.output);
      if (!content) continue;
      const messageId = `event-message-${event.identity.event_id}`;
      const resolution = modelResolutionFromEvent(event);
      if (resolution) mapped.set(messageId, { ...resolution, messageId });
      synthetic.push({ message_id: messageId, room_id: event.room_id, content, role: "assistant", status: "saved", room_sequence: event.identity.room_sequence, idempotency_key: null, content_sha256: "", created_at: event.timestamp } as Message);
    }
    const existing = new Set(messages.map((message) => message.message_id));
    return { chatMessages: [...messages, ...synthetic.filter((message) => !existing.has(message.message_id))].sort((a, b) => a.room_sequence - b.room_sequence), resolutions: mapped };
  }, [events, messages]);
  const runs = useMemo(() => processRuns(events), [events]);
  const draft = useMemo(() => streamingFinal(events), [events]);
  const send = useMutation({ mutationFn: (value: string) => api.assistantRoomMessage(roomId, spaceId, value), onSuccess: () => { setContent(""); void queryClient.invalidateQueries({ queryKey: ["messages", roomId] }); void queryClient.invalidateQueries({ queryKey: ["events", roomId] }); } });
  const submit = (event: FormEvent) => { event.preventDefault(); const value = content.trim(); if (!value || disabled) return; if (!navigator.onLine) { setPending((items) => [...items, enqueueMessage(roomId, value)]); setContent(""); return; } send.mutate(value); };
  const retry = (item: PendingMessage) => send.mutate(item.content, { onSuccess: () => { removeFromOutbox(roomId, item.clientId); setPending(readOutbox(roomId)); void queryClient.invalidateQueries({ queryKey: ["messages", roomId] }); } });

  return <>
    <div className="message-list chat-timeline">
      {chatMessages.map((message) => { const resolution = resolutions.get(message.message_id); const assistant = message.role === "assistant"; return <article className={`chat-row ${assistant ? "assistant" : "user"}`} key={message.message_id}><div className="chat-avatar">{assistant ? <Bot size={18} /> : <UserRound size={18} />}</div><div className="chat-message"><div className="chat-author"><b>{assistant ? resolution?.displayName || resolution?.agentId || "任务成员" : "你"}</b>{assistant && resolution?.model && <span><Cpu size={12} />{resolution.model}</span>}<small>#{message.room_sequence}</small></div><div className="chat-bubble"><CollapsibleText>{message.content}</CollapsibleText></div>{resolution && <div className="message-model"><span>{modelSelectionLabel(resolution.selectionMode)}</span>{resolution.modelProfile && <span>{resolution.modelProfile}</span>}</div>}</div></article>; })}
      {runs.map((run) => <ProcessingRecord run={run} onFocusStep={onFocusStep} key={run.runId} />)}
      {draft && <article className="chat-row assistant streaming"><div className="chat-avatar"><Bot size={18} /></div><div className="chat-message"><div className="chat-author"><b>{draft.agent || "任务助理"}</b><span><Cpu size={12} />{draft.model}</span><small>正在输出</small></div><div className="chat-bubble"><p>{draft.content}<span className="typing-caret" /></p></div></div></article>}
      {pending.map((item) => <article className="message-card pending" key={item.clientId}><div className="message-card-heading"><span className="message-role">待发送</span><small><time dateTime={item.createdAt}>{formatDateTime(item.createdAt)}</time> · 尚未保存</small></div><p>{item.content}</p><button type="button" className="ghost-button" onClick={() => retry(item)} disabled={send.isPending}><RefreshCw size={15} />重试</button></article>)}
      {chatMessages.length === 0 && pending.length === 0 && <p className="empty-state">任务已创建，等待成员开始处理。</p>}
    </div>
    <form className="message-composer" onSubmit={submit}><textarea className="composer-textarea" value={content} onChange={(event) => setContent(event.target.value)} placeholder="补充信息或继续追问" rows={3} aria-label="消息输入框" /><button className="primary-button" disabled={disabled || send.isPending || !content.trim()}>{send.isPending ? <LoaderCircle size={16} className="spin" /> : <SendHorizontal size={16} />}{send.isPending ? "发送中" : "发送"}</button>{send.isError && <p className="error-text" role="alert">发送失败：{send.error.message}</p>}</form>
  </>;
}
