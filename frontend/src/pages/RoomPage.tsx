import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api } from "../shared/api/client";
import { ArtifactCard } from "../features/artifacts/ArtifactCard";
import { MemberCard } from "../features/rooms/MemberCard";
import { MessageThread } from "../features/rooms/MessageThread";
import { RoomHeader } from "../features/rooms/RoomHeader";
import { FailureCard } from "../features/rooms/FailureCard";
import { useRoomEvents } from "../shared/realtime/useRoomEvents";
import { MultiAgentPanel } from "../features/rooms/MultiAgentPanel";

export function RoomPage() {
  const queryClient = useQueryClient();
  const { roomId = "" } = useParams();
  const room = useQuery({ queryKey: ["room", roomId], queryFn: () => api.room(roomId), enabled: Boolean(roomId) });
  const messages = useQuery({ queryKey: ["messages", roomId], queryFn: () => api.messages(roomId), enabled: Boolean(roomId) });
  const events = useQuery({ queryKey: ["events", roomId], queryFn: () => api.events(roomId), enabled: Boolean(roomId) });
  const liveEvents = useRoomEvents(roomId, events.data?.next ?? 0);
  useEffect(() => {
    if (liveEvents.cursor > 0) {
      void queryClient.invalidateQueries({ queryKey: ["messages", roomId] });
      void queryClient.invalidateQueries({ queryKey: ["members", roomId] });
    }
  }, [liveEvents.cursor, roomId, queryClient]);
  const displayedEvents = [...(events.data?.items ?? []), ...liveEvents.events].filter((event, index, all) => all.findIndex((item) => item.identity.event_id === event.identity.event_id) === index);
  const members = useQuery({ queryKey: ["members", roomId], queryFn: () => api.members(roomId), enabled: Boolean(roomId) });
  if (room.isLoading) return <section className="page state-page"><p>正在加载工作房间…</p></section>;
  if (room.isError || !room.data) return <section className="page state-page"><p className="error-text">无法加载工作房间：{room.error?.message}</p><Link to="/workspace" className="text-link">返回工作台</Link></section>;
  return (
    <section className="page room-page">
      <header className="page-header room-header"><RoomHeader room={room.data} /><Link to="/workspace" className="ghost-button">新建房间</Link></header>
      <MultiAgentPanel key={roomId} roomId={roomId} /><div className="room-grid"><article className="panel thread-panel"><div className="panel-heading"><h2>消息线程</h2><span className="muted">{messages.data?.items.length ?? 0} 条</span></div>{messages.isLoading && <p className="muted">加载消息…</p>}{messages.isError && <p className="error-text">消息读取失败</p>}<MessageThread roomId={roomId} messages={messages.data?.items ?? []} />{displayedEvents.filter((event) => event.event_type === "run_failed").map((event) => <FailureCard event={event} key={`failure-${event.identity.event_id}`} />)}</article><aside className="side-stack"><article className="panel trace-panel"><div className="panel-heading"><h2>运行轨迹</h2><span className={liveEvents.connected ? "muted live-status" : "muted"}>{liveEvents.connected ? "实时连接" : "断线，自动恢复"} · 游标 {Math.max(events.data?.next ?? 0, liveEvents.cursor)}</span></div>{events.isLoading && <p className="muted">加载事件…</p>}{displayedEvents.map((event) => <div className="event-row" key={event.identity.event_id}><span className="event-index">{event.identity.room_sequence}</span><div><b>{event.event_type}</b><p>{event.timestamp}</p></div></div>)}{displayedEvents.length === 0 && <p className="empty-state">暂无运行事件。</p>}</article><article className="panel"><MemberCard members={members.data?.items ?? []} /></article><article className="panel"><ArtifactCard /></article></aside></div>
    </section>
  );
}
