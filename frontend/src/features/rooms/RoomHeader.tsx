import type { Room } from "../../shared/api/client";
import { roomTheme, themes } from "../../app/theme";
import { Archive, Trash2 } from "lucide-react";
import { api } from "../../shared/api/client";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

export function RoomHeader({ room }: { room: Room }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const createdTheme = roomTheme(room.room_id) ?? "company";
  const roomLabel = createdTheme === "emperor" ? "御前议事" : "任务房间";
  const action = async (kind: "close" | "reopen" | "delete") => {
    if (kind === "delete" && !window.confirm("删除此房间？聊天记录和任务将从页面移除，无法重新打开。")) return;
    setBusy(true); setError("");
    try {
      if (kind === "close") await api.archiveRoom(room.room_id);
      if (kind === "reopen") await api.reopenRoom(room.room_id);
      if (kind === "delete") await api.deleteRoom(room.room_id);
      await queryClient.invalidateQueries({ queryKey: ["rooms"] });
      await queryClient.invalidateQueries({ queryKey: ["room", room.room_id] });
      if (kind === "delete") navigate("/workspace");
    } catch (err) { setError(err instanceof Error ? err.message : "操作失败"); }
    finally { setBusy(false); }
  };
  return <div className="room-header-content"><div><p className="eyebrow">{roomLabel} · {themes[createdTheme].leadLabel}</p><h1>{room.title || "未命名任务"}</h1><p className="subtitle"><span className="status-dot" /> {room.status === "archived" ? "已关闭 · 历史记录保留" : "开放中"}</p></div><div className="room-actions"><button className="ghost-button" type="button" onClick={() => void action(room.status === "archived" ? "reopen" : "close")} disabled={busy}><Archive size={15} />{room.status === "archived" ? "重新打开" : "关闭"}</button><button className="ghost-button" type="button" onClick={() => void action("delete")} disabled={busy}><Trash2 size={15} />删除</button></div>{error && <p className="error-text" role="alert">{error}</p>}</div>;
}
