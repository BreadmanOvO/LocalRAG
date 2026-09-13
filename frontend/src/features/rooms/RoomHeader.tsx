import type { Room } from "../../shared/api/client";
import { roomTheme, themes } from "../../app/theme";

export function RoomHeader({ room }: { room: Room }) {
  const createdTheme = roomTheme(room.room_id) ?? "company";
  const roomLabel = createdTheme === "emperor" ? "御前议事" : "任务房间";
  return <div><p className="eyebrow">{roomLabel} · {themes[createdTheme].leadLabel}</p><h1>{room.title || "未命名任务"}</h1><p className="subtitle"><span className="status-dot" /> {room.status}</p></div>;
}
