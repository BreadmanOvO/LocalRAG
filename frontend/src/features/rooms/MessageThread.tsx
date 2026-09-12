import { FormEvent, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type Message } from "../../shared/api/client";
import { enqueueMessage, readOutbox, removeFromOutbox, type PendingMessage } from "../../shared/realtime/outbox";

export function MessageThread({ roomId, messages }: { roomId: string; messages: Message[] }) {
  const [content, setContent] = useState("");
  const [pending, setPending] = useState<PendingMessage[]>(() => readOutbox(roomId));
  const queryClient = useQueryClient();
  const send = useMutation({ mutationFn: (value: string) => api.createMessage(roomId, value), onSuccess: () => { setContent(""); void queryClient.invalidateQueries({ queryKey: ["messages", roomId] }); } });
  const submit = (event: FormEvent) => { event.preventDefault(); const value = content.trim(); if (!value) return; if (!navigator.onLine) { setPending((items) => [...items, enqueueMessage(roomId, value)]); setContent(""); return; } send.mutate(value); };
  const retry = (item: PendingMessage) => send.mutate(item.content, { onSuccess: () => { removeFromOutbox(roomId, item.clientId); setPending(readOutbox(roomId)); void queryClient.invalidateQueries({ queryKey: ["messages", roomId] }); } });
  return <><div className="message-list">{messages.map((message) => <div className={`message-card ${message.role}`} key={message.message_id}><span className="message-role">{message.role}</span><p>{message.content}</p><small>#{message.room_sequence} · {message.status}</small></div>)}{pending.map((item) => <div className="message-card pending" key={item.clientId}><span className="message-role">待发送</span><p>{item.content}</p><small>{item.createdAt} · 尚未保存</small><button type="button" className="ghost-button" onClick={() => retry(item)} disabled={send.isPending}>重试</button></div>)}{messages.length === 0 && pending.length === 0 && <p className="empty-state">房间还没有消息，等待总助理接收任务。</p>}</div><form className="message-composer" onSubmit={submit}><textarea className="composer-textarea" value={content} onChange={(event) => setContent(event.target.value)} placeholder="继续告诉总助理你的目标…" rows={3} aria-label="消息输入框" /><button className="primary-button" disabled={send.isPending || !content.trim()}>{send.isPending ? "发送中…" : "发送"}</button>{send.isError && <p className="error-text">{send.error.message}</p>}</form></>;
}
