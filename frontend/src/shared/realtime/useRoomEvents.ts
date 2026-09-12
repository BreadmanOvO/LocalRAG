import { useEffect, useRef, useState } from "react";
import type { Event } from "../api/client";

type RoomEventState = { events: Event[]; cursor: number; connected: boolean };

/** SSE subscription with cursor-based reconnect. The server remains the source of truth. */
export function useRoomEvents(roomId: string, initialCursor = 0): RoomEventState {
  const [state, setState] = useState<RoomEventState>({ events: [], cursor: initialCursor, connected: false });
  const cursor = useRef(initialCursor);
  useEffect(() => {
    if (!roomId || typeof EventSource === "undefined") return;
    let source: EventSource | undefined;
    let stopped = false;
    const connect = () => {
      if (stopped) return;
      source = new EventSource(`/api/rooms/${encodeURIComponent(roomId)}/events/stream?after=${cursor.current}`);
      source.onopen = () => setState((current) => ({ ...current, connected: true }));
      source.onmessage = (message) => {
        try {
          const event = JSON.parse(message.data) as Event;
          cursor.current = Math.max(cursor.current, event.identity.room_sequence);
          setState((current) => ({ ...current, connected: true, cursor: cursor.current, events: [...current.events, event] }));
        } catch {
          // Ignore malformed frames; the next reconnect starts from the last valid cursor.
        }
      };
      source.onerror = () => {
        source?.close();
        setState((current) => ({ ...current, connected: false }));
        window.setTimeout(connect, 1000);
      };
    };
    connect();
    return () => { stopped = true; source?.close(); };
  }, [roomId]);
  return state;
}
