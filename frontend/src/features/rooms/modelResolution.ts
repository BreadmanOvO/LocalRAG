import type { Event } from "../../shared/api/client";

export type ModelResolution = {
  agentId: string | null;
  model: string;
  modelProfile: string | null;
  selectionMode: "fixed" | "auto" | null;
  selectionReason: string | null;
  messageId: string | null;
};

function text(payload: Record<string, unknown>, key: string) {
  const value = payload[key];
  return typeof value === "string" && value.trim() ? value : null;
}

export function modelResolutionFromEvent(event: Event): ModelResolution | null {
  if (event.event_type !== "step_completed") return null;
  const model = text(event.payload, "model");
  if (!model) return null;
  const selectionMode = text(event.payload, "selection_mode");
  return {
    agentId: text(event.payload, "agent_id"),
    model,
    modelProfile: text(event.payload, "model_profile"),
    selectionMode: selectionMode === "fixed" || selectionMode === "auto" ? selectionMode : null,
    selectionReason: text(event.payload, "selection_reason"),
    messageId: text(event.payload, "message_id"),
  };
}

export function resolutionByMessageId(events: Event[]) {
  const resolutions = new Map<string, ModelResolution>();
  events.forEach((event) => {
    const resolution = modelResolutionFromEvent(event);
    if (resolution?.messageId) resolutions.set(resolution.messageId, resolution);
  });
  return resolutions;
}

export function modelSelectionLabel(selectionMode: ModelResolution["selectionMode"]) {
  if (selectionMode === "auto") return "自动路由";
  if (selectionMode === "fixed") return "固定模型";
  return "模型已选定";
}
