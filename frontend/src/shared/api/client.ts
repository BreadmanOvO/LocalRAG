import createClient from "openapi-fetch";
import type { paths } from "./schema";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";
const client = createClient<paths>({ baseUrl: API_BASE });

function unwrap<T>(data: T | undefined, error: unknown): T {
  if (error) {
    const payload = error as { message?: string };
    throw new Error(payload.message ?? "API 请求失败");
  }
  if (data === undefined) throw new Error("API 未返回数据");
  return data;
}

export const api = {
  health: async () => {
    const { data, error } = await client.GET("/health");
    return unwrap(data, error);
  },
  room: async (roomId: string) => {
    const { data, error } = await client.GET("/rooms/{room_id}", { params: { path: { room_id: roomId } } });
    return unwrap(data, error);
  },
  messages: async (roomId: string) => {
    const { data, error } = await client.GET("/rooms/{room_id}/messages", { params: { path: { room_id: roomId } } });
    return unwrap(data, error);
  },
  events: async (roomId: string, after = 0) => {
    const { data, error } = await client.GET("/rooms/{room_id}/events", { params: { path: { room_id: roomId }, query: { after, limit: 100 } } });
    return unwrap(data, error);
  },
  createRoom: async (spaceId: string, title: string) => {
    const { data, error } = await client.POST("/rooms", {
      params: { header: { "Idempotency-Key": `workspace-${crypto.randomUUID()}` } },
      body: { space_id: spaceId, title },
    });
    return unwrap(data, error);
  },
};
