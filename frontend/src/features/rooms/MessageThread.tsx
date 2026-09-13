import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Cpu, LoaderCircle, RefreshCw, SendHorizontal } from "lucide-react";
import { api, type Event, type Message } from "../../shared/api/client";
import { enqueueMessage, readOutbox, removeFromOutbox, type PendingMessage } from "../../shared/realtime/outbox";
import { modelSelectionLabel, resolutionByMessageId } from "./modelResolution";

export function MessageThread({ roomId, messages, events }: { roomId: string; messages: Message[]; events: Event[] }) {
  const [content, setContent] = useState("");
  const [pending, setPending] = useState<PendingMessage[]>(() => readOutbox(roomId));
  const queryClient = useQueryClient();
  const resolutions = useMemo(() => resolutionByMessageId(events), [events]);
  const send = useMutation({ mutationFn: (value: string) => api.createMessage(roomId, value), onSuccess: () => { setContent(""); void queryClient.invalidateQueries({ queryKey: ["messages", roomId] }); } });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    const value = content.trim();
    if (!value) return;
    if (!navigator.onLine) {
      setPending((items) => [...items, enqueueMessage(roomId, value)]);
      setContent("");
      return;
    }
    send.mutate(value);
  };
  const retry = (item: PendingMessage) => send.mutate(item.content, { onSuccess: () => { removeFromOutbox(roomId, item.clientId); setPending(readOutbox(roomId)); void queryClient.invalidateQueries({ queryKey: ["messages", roomId] }); } });

  return <>
    <div className="message-list">
      {messages.map((message) => {
        const resolution = resolutions.get(message.message_id);
        return <article className={`message-card ${message.role}`} key={message.message_id}>
          <div className="message-card-heading"><span className="message-role">{message.role === "assistant" ? "项目组" : message.role}</span><small>#{message.room_sequence} · {message.status}</small></div>
          <p>{message.content}</p>
          {resolution && <div className="message-model" title={resolution.selectionReason ?? undefined}>
            <Cpu aria-hidden="true" size={14} />
            <span>{resolution.agentId ?? "Agent"}</span>
            <b>{resolution.model}</b>
            {resolution.modelProfile && <span>{resolution.modelProfile}</span>}
            <span>{modelSelectionLabel(resolution.selectionMode)}</span>
            {resolution.selectionReason && <small>{resolution.selectionReason}</small>}
          </div>}
        </article>;
      })}
      {pending.map((item) => <article className="message-card pending" key={item.clientId}><div className="message-card-heading"><span className="message-role">待发送</span><small>{item.createdAt} · 尚未保存</small></div><p>{item.content}</p><button type="button" className="ghost-button" onClick={() => retry(item)} disabled={send.isPending}><RefreshCw aria-hidden="true" size={15} />重试</button></article>)}
      {messages.length === 0 && pending.length === 0 && <p className="empty-state">任务已创建，等待成员开始处理。</p>}
    </div>
    <form className="message-composer" onSubmit={submit}>
      <textarea className="composer-textarea" value={content} onChange={(event) => setContent(event.target.value)} placeholder="补充信息或继续追问" rows={3} aria-label="消息输入框" />
      <button className="primary-button" disabled={send.isPending || !content.trim()}>{send.isPending ? <LoaderCircle aria-hidden="true" size={16} className="spin" /> : <SendHorizontal aria-hidden="true" size={16} />}{send.isPending ? "发送中" : "发送"}</button>
      {send.isError && <p className="error-text" role="alert">发送失败：{send.error.message}</p>}
    </form>
  </>;
}
