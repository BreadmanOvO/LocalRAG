import createClient from "openapi-fetch";
import type { components, paths } from "./schema";

export type Room = components["schemas"]["RoomResponse"];
export type Message = components["schemas"]["MessageResponse"];
export type Event = components["schemas"]["EventResponse"];
export type Member = components["schemas"]["MemberResponse"];
export type Role = components["schemas"]["RoleResponse"];
export type Persona = components["schemas"]["PersonaResponse"];
export type MultiAgentTurn = components["schemas"]["MultiAgentTurnResponse"] & {
  model?: string;
  model_profile?: string;
  selection_mode?: AgentBindingMode;
  selection_reason?: string;
};
export type MultiAgentExecution = Omit<components["schemas"]["MultiAgentExecuteResponse"], "turns"> & { turns: MultiAgentTurn[] };
export type ModelSettings = components["schemas"]["ModelSettingsResponse"];
export type AgentBindingMode = "fixed" | "auto";
export type CompatibleAgentConfig = components["schemas"]["AgentConfigRequest"] & {
  model_binding_mode?: AgentBindingMode;
  auto_tier?: string;
  auto_modalities?: string[];
  auto_scenarios?: string[];
  auto_capabilities?: string[];
};

export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";
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
  roles: async () => {
    const { data, error } = await client.GET("/roles");
    return unwrap(data, error);
  },
  persona: async (personaId: string) => {
    const { data, error } = await client.GET("/persona-profiles/{persona_id}", { params: { path: { persona_id: personaId } } });
    return unwrap(data, error);
  },
  room: async (roomId: string) => {
    const { data, error } = await client.GET("/rooms/{room_id}", { params: { path: { room_id: roomId } } });
    return unwrap(data, error);
  },
  rooms: async (spaceId?: string) => {
    const { data, error } = await client.GET("/rooms", { params: { query: spaceId ? { space_id: spaceId } : {} } });
    return unwrap(data, error);
  },
  messages: async (roomId: string, after = 0, limit = 100) => {
    const { data, error } = await client.GET("/rooms/{room_id}/messages", { params: { path: { room_id: roomId }, query: { after, limit } } });
    return unwrap(data, error);
  },
  members: async (roomId: string) => {
    const { data, error } = await client.GET("/rooms/{room_id}/members", { params: { path: { room_id: roomId } } });
    return unwrap(data, error);
  },
  createMessage: async (roomId: string, content: string) => {
    const { data, error } = await client.POST("/rooms/{room_id}/messages", {
      params: { path: { room_id: roomId }, header: { "Idempotency-Key": `message-${crypto.randomUUID()}` } },
      body: { content, role: "user" },
    });
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
  assistantMessage: async (spaceId: string, content: string, title?: string) => {
    const { data, error } = await client.POST("/assistant/messages", {
      params: { header: { "Idempotency-Key": `assistant-${crypto.randomUUID()}` } },
      body: { space_id: spaceId, content, title: title ?? "" },
    });
    return unwrap(data, error);
  },
  modelSettings: async () => {
    const { data, error } = await client.GET("/settings/models");
    return unwrap(data, error);
  },
  modelCatalog: async () => {
    const { data, error } = await client.GET("/settings/model-catalog");
    return unwrap(data, error);
  },
  discoverModels: async (baseUrl: string, apiKey: string, profileId = "") => {
    const { data, error } = await client.POST("/settings/model-discovery", { body: { base_url: baseUrl, api_key: apiKey, profile_id: profileId } });
    return unwrap(data, error);
  },
  saveModelProfile: async (profileId: string, body: components["schemas"]["ModelProfileRequest"]) => {
    const { data, error } = await client.PUT("/settings/model-profiles/{profile_id}", { params: { path: { profile_id: profileId } }, body });
    return unwrap(data, error);
  },
  saveAgentConfig: async (agentId: string, body: CompatibleAgentConfig) => {
    const { data, error } = await client.PUT("/settings/agents/{agent_id}", { params: { path: { agent_id: agentId } }, body });
    return unwrap(data, error);
  },
  deleteModelProfile: async (profileId: string) => {
    const { data, error } = await client.DELETE("/settings/model-profiles/{profile_id}", { params: { path: { profile_id: profileId } } });
    return unwrap(data, error);
  },
  deleteAgentConfig: async (agentId: string) => {
    const { data, error } = await client.DELETE("/settings/agents/{agent_id}", { params: { path: { agent_id: agentId } } });
    return unwrap(data, error);
  },
  updateModelBinding: async (agentId: string, sourceAgentId: string, tier?: string) => {
    const { data, error } = await client.PUT("/settings/models/{agent_id}", {
      params: { path: { agent_id: agentId } },
      body: { source_agent_id: sourceAgentId, tier: tier ?? null },
    });
    return unwrap(data, error);
  },
  executeMultiAgent: async (roomId: string, goal: string, architecture: components["schemas"]["MultiAgentExecuteRequest"]["architecture"] = "hierarchical", maxAgents = 3) => {
    const { data, error } = await client.POST("/rooms/{room_id}/multi-agent/execute", {
      params: { path: { room_id: roomId } },
      body: { goal, architecture, max_agents: maxAgents, background: false },
    });
    return unwrap(data, error);
  },
};
