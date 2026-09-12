import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "../shared/api/client";

export function RoomPage() {
  const { roomId = "" } = useParams();
  const room = useQuery({ queryKey: ["room", roomId], queryFn: () => api.room(roomId), enabled: Boolean(roomId) });
  const messages = useQuery({ queryKey: ["messages", roomId], queryFn: () => api.messages(roomId), enabled: Boolean(roomId) });
  const events = useQuery({ queryKey: ["events", roomId], queryFn: () => api.events(roomId), enabled: Boolean(roomId) });
  if (room.isLoading) return <section className="page state-page"><p>正在加载工作房间…</p></section>;
  if (room.isError || !room.data) return <section className="page state-page"><p className="error-text">无法加载工作房间：{room.error?.message}</p><Link to="/workspace" className="text-link">返回工作台</Link></section>;
  return (
    <section className="page room-page">
      <header className="page-header room-header"><div><p className="eyebrow">工作房间 · {room.data.space_id}</p><h1>{room.data.title || "未命名房间"}</h1><p className="subtitle"><span className="status-dot" /> {room.data.status} · 版本 {room.data.row_version}</p></div><Link to="/workspace" className="ghost-button">新建房间</Link></header>
      <div className="room-grid"><article className="panel thread-panel"><div className="panel-heading"><h2>消息线程</h2><span className="muted">{messages.data?.items.length ?? 0} 条</span></div>{messages.isLoading && <p className="muted">加载消息…</p>}{messages.isError && <p className="error-text">消息读取失败</p>}<div className="message-list">{messages.data?.items.map((message) => <div className={`message-card ${message.role}`} key={message.message_id}><span className="message-role">{message.role}</span><p>{message.content}</p><small>#{message.room_sequence} · {message.status}</small></div>)}</div>{messages.data?.items.length === 0 && <p className="empty-state">房间还没有消息，等待总助理接收任务。</p>}</article><article className="panel trace-panel"><div className="panel-heading"><h2>运行轨迹</h2><span className="muted">游标 {events.data?.next ?? 0}</span></div>{events.isLoading && <p className="muted">加载事件…</p>}{events.data?.items.map((event) => <div className="event-row" key={event.identity.event_id}><span className="event-index">{event.identity.room_sequence}</span><div><b>{event.event_type}</b><p>{event.timestamp}</p></div></div>)}{events.data?.items.length === 0 && <p className="empty-state">暂无运行事件。</p>}</article></div>
    </section>
  );
}
