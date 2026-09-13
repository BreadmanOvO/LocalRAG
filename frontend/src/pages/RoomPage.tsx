import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Activity, Cpu, PlusSquare } from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { api } from "../shared/api/client";
import { ArtifactCard } from "../features/artifacts/ArtifactCard";
import { MemberCard } from "../features/rooms/MemberCard";
import { MessageThread } from "../features/rooms/MessageThread";
import { RoomHeader } from "../features/rooms/RoomHeader";
import { FailureCard } from "../features/rooms/FailureCard";
import { useRoomEvents } from "../shared/realtime/useRoomEvents";
import { MultiAgentPanel } from "../features/rooms/MultiAgentPanel";
import { modelResolutionFromEvent, modelSelectionLabel } from "../features/rooms/modelResolution";

const eventLabels: Record<string, string> = {
  room_created: "任务房间已创建",
  message_created: "收到新消息",
  run_created: "已安排处理",
  step_started: "成员开始处理",
  step_completed: "成员完成步骤",
  run_completed: "任务已完成",
  run_failed: "任务出现问题",
};

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
  const displayedEvents = [...(events.data?.items ?? []), ...liveEvents.events]
    .filter((event, index, all) => all.findIndex((item) => item.identity.event_id === event.identity.event_id) === index)
    .sort((first, second) => first.identity.room_sequence - second.identity.room_sequence);
  const members = useQuery({ queryKey: ["members", roomId], queryFn: () => api.members(roomId), enabled: Boolean(roomId) });
  if (room.isLoading) return <section className="page state-page"><p>正在打开任务房间…</p></section>;
  if (room.isError || !room.data) return <section className="page state-page"><p className="error-text">无法打开任务房间：{room.error?.message}</p><Link to="/workspace" className="text-link">返回新任务</Link></section>;

  return <section className="page room-page">
    <header className="page-header room-header"><RoomHeader room={room.data} /><Link to="/workspace" className="ghost-button"><PlusSquare aria-hidden="true" size={16} />新任务</Link></header>
    <MultiAgentPanel key={roomId} roomId={roomId} />
    <div className="room-grid">
      <article className="panel thread-panel">
        <div className="panel-heading"><div><p className="eyebrow">协作记录</p><h2>任务动态</h2></div><span className="muted">{messages.data?.items.length ?? 0} 条</span></div>
        {messages.isLoading && <p className="muted">加载消息…</p>}
        {messages.isError && <p className="error-text">消息读取失败</p>}
        <MessageThread roomId={roomId} messages={messages.data?.items ?? []} events={displayedEvents} />
        {displayedEvents.filter((event) => event.event_type === "run_failed").map((event) => <FailureCard event={event} key={`failure-${event.identity.event_id}`} />)}
      </article>
      <aside className="side-stack">
        <article className="panel trace-panel">
          <div className="panel-heading"><div><p className="eyebrow">进度与追溯</p><h2>任务轨迹</h2></div><span className={liveEvents.connected ? "live-indicator" : "muted"}>{liveEvents.connected ? "实时更新" : "等待重连"}</span></div>
          {events.isLoading && <p className="muted">加载进度…</p>}
          {displayedEvents.map((event) => {
            const resolution = modelResolutionFromEvent(event);
            return <div className="event-row" key={event.identity.event_id}>
              <span className="event-index">{event.identity.room_sequence}</span>
              <div className="event-copy"><b>{eventLabels[event.event_type] ?? "任务状态已更新"}</b><p>{event.timestamp}</p>
                {resolution && <div className="event-model"><Cpu aria-hidden="true" size={13} /><span>{resolution.model}</span>{resolution.modelProfile && <span>{resolution.modelProfile}</span>}<span>{modelSelectionLabel(resolution.selectionMode)}</span>{resolution.selectionReason && <small>{resolution.selectionReason}</small>}</div>}
              </div>
            </div>;
          })}
          {displayedEvents.length === 0 && <p className="empty-state"><Activity aria-hidden="true" size={16} />暂无进度记录。</p>}
        </article>
        <article className="panel"><MemberCard members={members.data?.items ?? []} /></article>
        <article className="panel"><ArtifactCard /></article>
      </aside>
    </div>
  </section>;
}
