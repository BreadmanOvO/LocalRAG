import { useQuery } from "@tanstack/react-query";
import { NavLink } from "react-router-dom";
import { api } from "../../shared/api/client";

export function RoomList() {
  const rooms = useQuery({ queryKey: ["rooms"], queryFn: () => api.rooms() });
  return <div className="room-list" aria-label="最近房间"><div className="list-heading"><span>最近房间</span><span className="muted">{rooms.data?.items.length ?? 0}</span></div>{rooms.isLoading && <p className="muted">加载中…</p>}{rooms.data?.items.map((room) => <NavLink className={({ isActive }) => isActive ? "room-list-item active" : "room-list-item"} to={`/rooms/${room.room_id}`} key={room.room_id}><span className="room-avatar">{(room.title || "R").slice(0, 1)}</span><span><b>{room.title || "未命名房间"}</b><small>{room.status}</small></span></NavLink>)}{rooms.data?.items.length === 0 && <p className="muted">还没有房间</p>}</div>;
}
