import createClient from "openapi-fetch";
import type { components, paths } from "./schema";
import { roomTheme, type ThemeId } from "../../app/theme";

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
export type AssetIngestion = components["schemas"]["AssetIngestionResponse"];
export type Artifact = components["schemas"]["ArtifactResponse"];
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

function unwrap<T>(data: T | undefined, error: unknown, response?: Response): T {
  if (error) {
    const payload = error as { message?: string; detail?: unknown; code?: string };
    const fallback = response?.status === 404 ? "保存接口未找到，请检查配置标识后重试" : "API 请求失败";
    const message = typeof payload.message === "string" && payload.message.trim() ? payload.message : fallback;
    const code = typeof payload.code === "string" && payload.code.trim() ? `（${payload.code}）` : "";
    const status = response ? ` [HTTP ${response.status}]` : "";
    throw new Error(`${message}${code}${status}`);
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
    const items: Message[] = [];
    while (true) {
      const { data, error } = await client.GET("/rooms/{room_id}/messages", { params: { path: { room_id: roomId }, query: { after, limit } } });
      const page = unwrap(data, error); items.push(...page.items);
      if (page.items.length < limit || page.next <= after) return { items, next: page.next };
      after = page.next;
    }
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
    const items: Event[] = [];
    while (true) {
      const { data, error } = await client.GET("/rooms/{room_id}/events", { params: { path: { room_id: roomId }, query: { after, limit: 1000 } } });
      const page = unwrap(data, error); items.push(...page.items);
      if (page.items.length < 1000 || page.next <= after) return { items, next: page.next };
      after = page.next;
    }
  },
  createRoom: async (spaceId: string, title: string) => {
    const { data, error } = await client.POST("/rooms", {
      params: { header: { "Idempotency-Key": `workspace-${crypto.randomUUID()}` } },
      body: { space_id: spaceId, title },
    });
    return unwrap(data, error);
  },
  assistantMessage: async (spaceId: string, content: string, title?: string, personaTheme?: ThemeId, architecture: components["schemas"]["AssistantMessageRequest"]["architecture"] = "auto") => {
    const { data, error } = await client.POST("/assistant/messages", {
      params: { header: { "Idempotency-Key": `assistant-${crypto.randomUUID()}` } },
      body: { space_id: spaceId, content, title: title ?? "", persona_theme: personaTheme, architecture },
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
  artifacts: async (roomId: string) => {
    const { data, error, response } = await client.GET("/rooms/{room_id}/artifacts", { params: { path: { room_id: roomId } } });
    return unwrap(data, error, response);
  },
  archiveRoom: async (roomId: string) => { const { data, error } = await client.POST("/rooms/{room_id}/archive", { params: { path: { room_id: roomId } } }); return unwrap(data, error); },
  reopenRoom: async (roomId: string) => { const { data, error } = await client.POST("/rooms/{room_id}/reopen", { params: { path: { room_id: roomId } } }); return unwrap(data, error); },
  startRoom: async (roomId: string) => { const { data, error } = await client.POST("/rooms/{room_id}/start", { params: { path: { room_id: roomId } } }); return unwrap(data, error); },
  roomExecution: async (roomId: string): Promise<{ status: string; can_resume: boolean }> => { const { data, error } = await client.GET("/rooms/{room_id}/execution", { params: { path: { room_id: roomId } } }); return unwrap(data, error) as { status: string; can_resume: boolean }; },
  deleteRoom: async (roomId: string) => { const { data, error } = await client.DELETE("/rooms/{room_id}", { params: { path: { room_id: roomId } } }); return unwrap(data, error); },
  assistantRoomMessage: async (roomId: string, spaceId: string, content: string, personaTheme?: ThemeId, architecture: components["schemas"]["AssistantMessageRequest"]["architecture"] = "auto") => {
    const { data, error } = await client.POST("/assistant/messages", {
      params: { header: { "Idempotency-Key": `assistant-${crypto.randomUUID()}` } },
      body: { room_id: roomId, space_id: spaceId, content, title: "", persona_theme: personaTheme, architecture },
    });
    return unwrap(data, error);
  },
  savePersona: async (body: components["schemas"]["PersonaCreateRequest"]) => {
    const { data, error } = await client.POST("/persona-profiles", { body });
    return unwrap(data, error);
  },
  uploadAsset: async (spaceId: string, file: File, evaluate = false) => {
    if (file.size > 30 * 1024 * 1024) throw new Error("单个文件不能超过 30 MB");
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = "";
    for (let offset = 0; offset < bytes.length; offset += 8192) {
      binary += String.fromCharCode(...bytes.subarray(offset, offset + 8192));
    }
    const content_base64 = btoa(binary);
    const { data, error, response } = await client.POST("/asset-ingestions", { body: { space_id: spaceId, filename: file.name, content_base64, evaluate } });
    return unwrap(data, error, response);
  },
  assetIngestions: async (spaceId: string) => {
    const { data, error, response } = await client.GET("/asset-ingestions", { params: { query: { space_id: spaceId } } });
    return unwrap(data, error, response);
  },
  retryIngestion: async (jobId: string) => {
    const { data, error, response } = await client.POST("/asset-ingestions/{job_id}/retry", { params: { path: { job_id: jobId } } });
    return unwrap(data, error, response);
  },
  deleteIngestion: async (jobId: string) => {
    const { data, error, response } = await client.DELETE("/asset-ingestions/{job_id}", { params: { path: { job_id: jobId } } });
    return unwrap(data, error, response);
  },
  searchAssets: async (spaceId: string, query: string) => {
    const { data, error, response } = await client.GET("/assets/search", { params: { query: { space_id: spaceId, q: query } } });
    return unwrap(data, error, response);
  },
  saveModelProfile: async (profileId: string, body: components["schemas"]["ModelProfileRequest"]) => {
    const normalizedId = profileId.trim();
    if (!/^[A-Za-z0-9_-]{1,100}$/.test(normalizedId)) {
      throw new Error("Profile ID 只能使用英文、数字、短横线或下划线；模型名称（例如 ZhipuAI/GLM-5.2）请填写在“模型名称”字段");
    }
    const { data, error, response } = await client.PUT("/settings/model-profiles/{profile_id}", { params: { path: { profile_id: normalizedId } }, body: { ...body, profile_id: normalizedId } });
    return unwrap(data, error, response);
  },
  saveAgentConfig: async (agentId: string, body: CompatibleAgentConfig) => {
    const { data, error } = await client.PUT("/settings/agents/{agent_id}", { params: { path: { agent_id: agentId } }, body });
    return unwrap(data, error);
  },
  deleteModelProfile: async (profileId: string) => {
    const { data, error } = await client.DELETE("/settings/model-profiles/{profile_id}", { params: { path: { profile_id: profileId } } });
    return unwrap(data, error);
  },
  cloneModelProfile: async (profileId: string) => {
    const { data, error, response } = await client.POST("/settings/model-profiles/{profile_id}/clone", { params: { path: { profile_id: profileId } } });
    return unwrap(data, error, response);
  },
  verifyModelProfile: async (profileId: string) => {
    const { data, error, response } = await client.POST("/settings/model-profiles/{profile_id}/verify", { params: { path: { profile_id: profileId } } });
    return unwrap(data, error, response);
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
      body: { goal, architecture, max_agents: maxAgents, background: false, persona_theme: roomTheme(roomId) ?? undefined },
    });
    return unwrap(data, error);
  },
};
