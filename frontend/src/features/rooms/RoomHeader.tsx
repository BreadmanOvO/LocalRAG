import type { Room } from "../../shared/api/client";

export function RoomHeader({ room }: { room: Room }) {
  return <div><p className="eyebrow">工作房间 · {room.space_id}</p><h1>{room.title || "未命名房间"}</h1><p className="subtitle"><span className="status-dot" /> {room.status} · 版本 {room.row_version}</p></div>;
}
