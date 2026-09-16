import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { PlusSquare, Trash2 } from "lucide-react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../shared/api/client";
import { ArtifactCard } from "../features/artifacts/ArtifactCard";
import { MemberCard } from "../features/rooms/MemberCard";
import { MessageThread } from "../features/rooms/MessageThread";
import { RoomHeader } from "../features/rooms/RoomHeader";
import { FailureCard } from "../features/rooms/FailureCard";
import { useRoomEvents } from "../shared/realtime/useRoomEvents";
import { CollaborationGraph } from "../features/rooms/CollaborationGraph";
import { TaskTrace } from "../features/rooms/TaskTrace";
import { mergeRoomEvents } from "../features/rooms/taskTraceModel";
import { forgetRoomTheme } from "../app/theme";
import { clearRoomOutbox } from "../shared/realtime/outbox";

export function RoomPage() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { roomId = "" } = useParams();
  const [focusedSequence, setFocusedSequence] = useState<number | null>(null);
  const execution = useQuery({ queryKey: ["execution", roomId], queryFn: () => api.roomExecution(roomId), enabled: Boolean(roomId), refetchInterval: 3000 });
  const restart = useMutation({ mutationFn: () => api.startRoom(roomId), onSuccess: () => { void queryClient.invalidateQueries({ queryKey: ["execution", roomId] }); void queryClient.invalidateQueries({ queryKey: ["events", roomId] }); } });
  const room = useQuery({ queryKey: ["room", roomId], queryFn: () => api.room(roomId), enabled: Boolean(roomId) });
  const messages = useQuery({ queryKey: ["messages", roomId], queryFn: () => api.messages(roomId), enabled: Boolean(roomId) });
  const events = useQuery({ queryKey: ["events", roomId], queryFn: () => api.events(roomId), enabled: Boolean(roomId) });
  const artifacts = useQuery({ queryKey: ["artifacts", roomId], queryFn: () => api.artifacts(roomId), enabled: Boolean(roomId) });
  const liveEvents = useRoomEvents(roomId, events.data?.next ?? 0);
  useEffect(() => {
    if (liveEvents.cursor > 0) {
      void queryClient.invalidateQueries({ queryKey: ["messages", roomId] });
      void queryClient.invalidateQueries({ queryKey: ["members", roomId] });
    }
  }, [liveEvents.cursor, roomId, queryClient]);
  const displayedEvents = mergeRoomEvents(roomId, events.data?.items ?? [], liveEvents.events);
  const legacyAgentMessageCount = displayedEvents.filter((event) => event.event_type === "step_completed" && !event.payload.message_id && typeof event.payload.output === "string" && event.payload.output.trim()).length;
  const latestFailure = [...displayedEvents].reverse().find((event) => ["run_failed", "task_start_failed"].includes(event.event_type));
  const latestRecovery = [...displayedEvents].reverse().find((event) => ["run_started", "run_completed"].includes(event.event_type));
  const activeFailure = latestFailure && (!latestRecovery || latestRecovery.identity.room_sequence <= latestFailure.identity.room_sequence)
    ? latestFailure
    : null;
  const members = useQuery({ queryKey: ["members", roomId], queryFn: () => api.members(roomId), enabled: Boolean(roomId) });
  if (room.isLoading) return <section className="page state-page"><p>正在打开任务房间…</p></section>;
  if (room.isError || !room.data) {
    const missing = room.error?.message.includes("not_found") ?? false;
    const clearMissingRoom = () => {
      forgetRoomTheme(roomId);
      clearRoomOutbox(roomId);
      queryClient.removeQueries({ queryKey: ["room", roomId] });
      queryClient.removeQueries({ queryKey: ["messages", roomId] });
      queryClient.removeQueries({ queryKey: ["events", roomId] });
      void navigate("/workspace", { replace: true });
    };
    return <section className="page state-page"><p className="error-text">无法打开任务房间：{room.error?.message}</p>{missing ? <><p className="muted">该房间来自旧的临时数据，服务端记录已不存在。可以清理本机残留后返回新任务。</p><button type="button" className="ghost-button danger-button" onClick={clearMissingRoom}><Trash2 size={15} />清理旧房间记录</button></> : <Link to="/workspace" className="text-link">返回新任务</Link>}</section>;
  }

  return <section className="page room-page">
    <header className="page-header room-header"><RoomHeader room={room.data} /><Link to="/workspace" className="ghost-button"><PlusSquare aria-hidden="true" size={16} />新任务</Link></header>
    {execution.data?.can_resume && <div className="panel"><p>任务尚未完成，可从已保存的进度继续。</p><button className="primary-button" onClick={() => restart.mutate()} disabled={restart.isPending}>{restart.isPending ? "正在恢复" : "恢复任务"}</button> <Link to="/company" className="text-link">检查模型设置</Link>{restart.isError && <p className="error-text">{restart.error.message}</p>}</div>}
    <div className="room-grid">
      <article className="panel thread-panel">
        <div className="panel-heading"><div><p className="eyebrow">协作记录</p><h2>任务动态</h2></div><span className="muted">{(messages.data?.items.length ?? 0) + legacyAgentMessageCount} 条</span></div>
        {messages.isLoading && <p className="muted">加载消息…</p>}
        {messages.isError && <p className="error-text">消息读取失败</p>}
        <MessageThread roomId={roomId} spaceId={room.data.space_id} disabled={room.data.status !== "active" || execution.data?.status === "running"} messages={messages.data?.items ?? []} events={displayedEvents} onFocusStep={setFocusedSequence} />
        {activeFailure && <FailureCard event={activeFailure} key={`failure-${activeFailure.identity.event_id}`} />}
      </article>
      <aside className="side-stack">
        <CollaborationGraph key={roomId} roomId={roomId} events={displayedEvents} connected={liveEvents.connected} focusSequence={focusedSequence} />
        <TaskTrace key={roomId} events={displayedEvents} connected={liveEvents.connected} loading={events.isLoading} />
        <article className="panel"><MemberCard roomId={roomId} members={members.data?.items ?? []} /></article>
        <article className="panel"><ArtifactCard artifacts={artifacts.data?.items ?? []} loading={artifacts.isLoading} /></article>
      </aside>
    </div>
  </section>;
}
