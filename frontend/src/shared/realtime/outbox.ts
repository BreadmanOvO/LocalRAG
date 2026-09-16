const key = (roomId: string) => `localrag:outbox:${roomId}`;

export type PendingMessage = { clientId: string; content: string; createdAt: string };

export function readOutbox(roomId: string): PendingMessage[] {
  try { return JSON.parse(localStorage.getItem(key(roomId)) ?? "[]") as PendingMessage[]; } catch { return []; }
}

export function enqueueMessage(roomId: string, content: string): PendingMessage {
  const item = { clientId: crypto.randomUUID(), content, createdAt: new Date().toISOString() };
  localStorage.setItem(key(roomId), JSON.stringify([...readOutbox(roomId), item]));
  return item;
}

export function removeFromOutbox(roomId: string, clientId: string): void {
  localStorage.setItem(key(roomId), JSON.stringify(readOutbox(roomId).filter((item) => item.clientId !== clientId)));
}

export function clearRoomOutbox(roomId: string): void {
  try { localStorage.removeItem(key(roomId)); } catch { /* The stale room can still be left. */ }
}
