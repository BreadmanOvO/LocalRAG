import type { Event } from "../../shared/api/client";

export type StepState =
  | "waiting"
  | "claimed"
  | "queued"
  | "running"
  | "retrying"
  | "completed"
  | "reused"
  | "blocked"
  | "failed"
  | "interrupted";

export type TaskStep = {
  id: string;
  sequence: number;
  agentId: string;
  agentName: string;
  title: string;
  dependencies: number[];
  state: StepState;
  input: string;
  output: string;
  error: string;
  model: string;
  modelProfile: string;
  responsibility: string;
  started?: string;
  ended?: string;
  durationMs?: number;
  attempt?: number;
  nextAttempt?: number;
  isFinal?: boolean;
};

export type TaskHandoff = {
  id: string;
  fromStepId: string;
  toStepId: string;
  sourceSequence?: number;
  targetSequence?: number;
  fromAgentId: string;
  toAgentId: string;
  summary: string;
  output: string;
  createdAt?: string;
  acceptedAt?: string;
  createdSequence: number;
  acceptedSequence?: number;
  packet?: Record<string, unknown>;
};

export type CollaborationProjection = {
  architecture: string;
  runState: string;
  resumeFrom: string;
  hasPlan: boolean;
  steps: TaskStep[];
  handoffs: TaskHandoff[];
};

type AgentInfo = {
  displayName: string;
  model: string;
  responsibility: string;
};

type MutableStep = Omit<TaskStep, "agentName">;

type EventLike = Event & {
  run_id?: unknown;
  step_id?: unknown;
  timestamp?: unknown;
  identity?: { event_id?: unknown; room_sequence?: unknown };
};

export const stateLabels: Record<StepState, string> = {
  waiting: "待开始",
  claimed: "已认领",
  queued: "等待模型",
  running: "执行中",
  retrying: "等待重试",
  completed: "已完成",
  reused: "已复用",
  blocked: "上游阻塞",
  failed: "失败",
  interrupted: "已中断",
};

export const architectureLabels: Record<string, string> = {
  direct: "直接处理",
  hierarchical: "分层协作",
  swarm: "蜂群协作",
  adversarial: "对抗协作",
  heterogeneous: "异构协作",
  graph: "图式协作",
};

export const architectureStages: Record<string, string> = {
  direct: "负责人直接完成并交付",
  hierarchical: "任务书 -> 拆解 -> 执行 -> 核对交付",
  swarm: "独立探索并行 -> 汇总核对",
  adversarial: "提出方案 -> 独立质疑 -> 综合裁量",
  heterogeneous: "明确任务 -> 按能力分工 -> 汇合交付",
  graph: "明确任务 -> 并行分支 -> 汇合交付",
};

const taskEvents = new Set([
  "step_claimed",
  "step_queued",
  "step_started",
  "step_retrying",
  "step_completed",
  "step_failed",
  "step_blocked",
  "step_reused",
]);

const unfinishedStates = new Set<StepState>(["waiting", "claimed", "queued", "running", "retrying"]);

function text(value: unknown): string {
  return typeof value === "string" ? value : "";
}
function integer(value: unknown): number | undefined {
  if (typeof value === "number" && Number.isInteger(value)) return value;
  if (typeof value === "string" && /^-?\d+$/.test(value)) return Number(value);
  return undefined;
}

function payloadOf(event: EventLike): Record<string, unknown> {
  const payload = event.payload;
  return payload && typeof payload === "object" && !Array.isArray(payload) ? payload as Record<string, unknown> : {};
}

function has(payload: Record<string, unknown>, key: string): boolean {
  return Object.prototype.hasOwnProperty.call(payload, key);
}

function sequenceOf(event: EventLike, fallback: number): number {
  return integer(event.identity?.room_sequence) ?? fallback;
}

function eventId(event: EventLike, fallback: number): string {
  return text(event.identity?.event_id) || `event-${sequenceOf(event, fallback)}-${fallback}`;
}

function timestampOf(event: EventLike): string | undefined {
  const timestamp = text(event.timestamp);
  return timestamp || undefined;
}

function sequenceFromStepId(stepId: string): number | undefined {
  const match = stepId.match(/-(\d+)$/);
  return match ? Number(match[1]) : undefined;
}

function numberList(value: unknown): number[] {
  if (!Array.isArray(value)) return [];
  const values = value.map(integer).filter((item): item is number => item !== undefined);
  return [...new Set(values)];
}

function runIdOf(event: EventLike): string {
  return text(event.run_id);
}

function stepIdFor(runId: string, sequence: number | undefined, explicitId = "", fallback = 0): string {
  if (explicitId) return explicitId;
  if (runId && sequence !== undefined) return `step-${runId}-${sequence}`;
  return `step-${runId || "unknown"}-${sequence ?? fallback}`;
}

function defaultTitle(sequence: number): string {
  return `步骤 ${sequence}`;
}

function isTerminalRunEvent(eventType: string): boolean {
  return eventType === "run_completed" || eventType === "run_failed" || eventType === "run_cancelled" || eventType === "run_paused";
}

export function projectCollaboration(events: Event[], priorEvents: Event[] = []): CollaborationProjection {
  const ordered = events
    .map((event, index) => ({ event: event as EventLike, index }))
    .sort((first, second) => sequenceOf(first.event, first.index) - sequenceOf(second.event, second.index) || first.index - second.index);
  const steps = new Map<string, MutableStep>();
  const stepsBySequence = new Map<number, string>();
  const agents = new Map<string, AgentInfo>();
  const handoffs: TaskHandoff[] = [];
  const seenEvents = new Set<string>();
  let architecture = "";
  let runState = "running";
  let resumeFrom = "";
  let hasPlan = false;
  const projectionRunId = ordered.map(({ event }) => runIdOf(event)).find(Boolean) ?? "";
  const reusableResults = new Map<number, Pick<TaskStep, "input" | "output" | "error" | "model" | "modelProfile" | "responsibility" | "ended" | "durationMs">>();

  for (const item of priorEvents) {
    const event = item as EventLike;
    if (event.event_type !== "step_completed") continue;
    const payload = payloadOf(event);
    const sequence = integer(payload.sequence) ?? sequenceFromStepId(text(event.step_id));
    if (sequence === undefined) continue;
    reusableResults.set(sequence, {
      input: text(payload.input),
      output: text(payload.output),
      error: text(payload.error),
      model: text(payload.model),
      modelProfile: text(payload.model_profile),
      responsibility: text(payload.responsibility),
      ended: timestampOf(event),
      durationMs: integer(payload.duration_ms),
    });
  }

  const updateAgent = (agentId: string, payload: Record<string, unknown>) => {
    if (!agentId) return;
    const current = agents.get(agentId) ?? { displayName: "", model: "", responsibility: "" };
    const displayName = text(payload.display_name);
    const model = text(payload.model);
    const responsibility = text(payload.responsibility);
    agents.set(agentId, {
      displayName: displayName || current.displayName,
      model: model || current.model,
      responsibility: responsibility || current.responsibility,
    });
  };

  const ensureStep = (event: EventLike, payload: Record<string, unknown>, fallback: number, overrides: Partial<Pick<MutableStep, "sequence" | "agentId" | "title" | "dependencies">> = {}) => {
    const explicitId = text(event.step_id);
    const sequence = overrides.sequence ?? integer(payload.sequence) ?? sequenceFromStepId(explicitId) ?? sequenceOf(event, fallback);
    const runId = runIdOf(event) || projectionRunId;
    const existingId = stepsBySequence.get(sequence);
    const id = existingId ?? stepIdFor(runId, sequence, explicitId, fallback);
    const agentId = overrides.agentId ?? text(payload.agent_id);
    let step = steps.get(id);
    if (!step) {
      step = {
        id,
        sequence,
        agentId: agentId || "unassigned",
        title: overrides.title || text(payload.title) || defaultTitle(sequence),
        dependencies: overrides.dependencies ?? (has(payload, "dependencies") ? numberList(payload.dependencies) : []),
        state: "waiting",
        input: "",
        output: "",
        error: "",
        model: "",
        modelProfile: "",
        responsibility: "",
      };
      steps.set(id, step);
    }
    stepsBySequence.set(sequence, id);
    if (agentId) step.agentId = agentId;
    if (overrides.title || text(payload.title)) step.title = overrides.title || text(payload.title);
    if (overrides.dependencies || has(payload, "dependencies")) step.dependencies = overrides.dependencies ?? numberList(payload.dependencies);
    return step;
  };

  const updateTaskMetadata = (step: MutableStep, payload: Record<string, unknown>) => {
    const agentId = text(payload.agent_id);
    if (agentId) step.agentId = agentId;
    updateAgent(step.agentId, payload);
    const model = text(payload.model);
    const modelProfile = text(payload.model_profile);
    const responsibility = text(payload.responsibility);
    if (model) step.model = model;
    if (modelProfile) step.modelProfile = modelProfile;
    if (responsibility) step.responsibility = responsibility;
    if (has(payload, "input")) step.input = text(payload.input);
    if (has(payload, "output")) step.output = text(payload.output);
    if (has(payload, "error")) step.error = text(payload.error);
    const duration = integer(payload.duration_ms);
    if (duration !== undefined) step.durationMs = duration;
  };

  const handoffStepId = (event: EventLike, sequence: number | undefined, fallback: number) => {
    if (sequence !== undefined) {
      const plannedId = stepsBySequence.get(sequence);
      if (plannedId) return plannedId;
    }
    return stepIdFor(runIdOf(event) || projectionRunId, sequence, "", fallback);
  };

  for (const { event, index } of ordered) {
    const id = eventId(event, index);
    if (seenEvents.has(id)) continue;
    seenEvents.add(id);
    const payload = payloadOf(event);
    const eventSequence = sequenceOf(event, index);

    if (event.event_type === "run_started") {
      architecture = text(payload.architecture) || architecture;
      resumeFrom = text(payload.resumed_from) || text(payload.resume_from) || resumeFrom;
      runState = "running";
    }
    if (event.event_type === "run_queued") runState = "queued";

    if (event.event_type === "team_planned") {
      architecture = text(payload.architecture) || architecture;
      if (Array.isArray(payload.participants)) {
        for (const participant of payload.participants) {
          if (!participant || typeof participant !== "object" || Array.isArray(participant)) continue;
          const details = participant as Record<string, unknown>;
          const agentId = text(details.agent_id);
          updateAgent(agentId, details);
        }
      }
    }

    if (event.event_type === "team_plan_created") {
      architecture = text(payload.architecture) || architecture;
      hasPlan = true;
      if (Array.isArray(payload.steps)) {
        for (const item of payload.steps) {
          if (!item || typeof item !== "object" || Array.isArray(item)) continue;
          const plan = item as Record<string, unknown>;
          const sequence = integer(plan.sequence);
          if (sequence === undefined) continue;
          const step = ensureStep(event, plan, index, {
            sequence,
            agentId: text(plan.agent_id),
            title: text(plan.title) || defaultTitle(sequence),
            dependencies: numberList(plan.dependencies),
          });
          step.isFinal = plan.is_final === true;
          updateAgent(step.agentId, plan);
        }
      }
    }

    if (taskEvents.has(event.event_type)) {
      const step = ensureStep(event, payload, index);
      updateTaskMetadata(step, payload);
      switch (event.event_type) {
        case "step_claimed":
          step.state = "claimed";
          break;
        case "step_queued":
          step.state = "queued";
          break;
        case "step_started":
          runState = "running";
          step.attempt = step.nextAttempt ?? step.attempt ?? 1;
          step.state = "running";
          step.started = timestampOf(event) ?? step.started;
          break;
        case "step_retrying":
          step.state = "retrying";
          step.attempt = integer(payload.attempt) ?? step.attempt;
          step.nextAttempt = integer(payload.next_attempt) ?? step.nextAttempt;
          break;
        case "step_completed":
          step.error = "";
          step.state = "completed";
          step.ended = timestampOf(event) ?? step.ended;
          break;
        case "step_reused":
          step.state = "reused";
          step.ended = timestampOf(event) ?? step.ended;
          {
            const prior = reusableResults.get(step.sequence);
            if (prior) {
              step.input ||= prior.input;
              step.output ||= prior.output;
              step.error ||= prior.error;
              step.model ||= prior.model;
              step.modelProfile ||= prior.modelProfile;
              step.responsibility ||= prior.responsibility;
              step.durationMs ??= prior.durationMs;
            }
          }
          break;
        case "step_blocked":
          step.state = "blocked";
          break;
        case "step_failed":
          step.state = "failed";
          step.ended = timestampOf(event) ?? step.ended;
          break;
      }
    }

    if (event.event_type === "step_output_delta") {
      const step = ensureStep(event, payload, index);
      const delta = text(payload.delta);
      if (delta) step.output += delta;
      step.state = "running";
      updateTaskMetadata(step, payload);
    }

    if (event.event_type === "handoff_created") {
      const targetSequence = integer(payload.sequence) ?? sequenceFromStepId(text(event.step_id));
      const sourceSequence = integer(payload.source_sequence);
      const target = targetSequence === undefined ? undefined : ensureStep(event, payload, index, { sequence: targetSequence });
      handoffs.push({
        id,
        fromStepId: handoffStepId(event, sourceSequence, index),
        toStepId: target?.id ?? handoffStepId(event, targetSequence, index),
        sourceSequence,
        targetSequence,
        fromAgentId: text(payload.from_agent_id),
        toAgentId: text(payload.to_agent_id) || target?.agentId || "",
        summary: text(payload.summary),
        output: text(payload.shared_output),
        packet: payload.handoff_packet && typeof payload.handoff_packet === "object" && !Array.isArray(payload.handoff_packet) ? payload.handoff_packet as Record<string, unknown> : undefined,
        createdAt: timestampOf(event),
        createdSequence: eventSequence,
      });
    }

    if (event.event_type === "handoff_accepted") {
      const targetSequence = integer(payload.sequence) ?? sequenceFromStepId(text(event.step_id));
      const target = targetSequence === undefined ? undefined : ensureStep(event, payload, index, { sequence: targetSequence });
      const sources = numberList(payload.source_sequences);
      const acceptedAt = timestampOf(event);
      const markAccepted = (sourceSequence: number | undefined, suffix: string) => {
        const existing = [...handoffs].reverse().find((handoff) => handoff.targetSequence === targetSequence && handoff.sourceSequence === sourceSequence && handoff.acceptedAt === undefined);
        if (existing) {
          existing.acceptedAt = acceptedAt;
          existing.acceptedSequence = eventSequence;
          return;
        }
        handoffs.push({
          id: `${id}-${suffix}`,
          fromStepId: handoffStepId(event, sourceSequence, index),
          toStepId: target?.id ?? handoffStepId(event, targetSequence, index),
          sourceSequence,
          targetSequence,
          fromAgentId: "",
          toAgentId: text(payload.agent_id) || target?.agentId || "",
          summary: "已接收上游结果",
          output: "",
          acceptedAt,
          createdSequence: eventSequence,
          acceptedSequence: eventSequence,
        });
      };
      if (sources.length) sources.forEach((sourceSequence, sourceIndex) => markAccepted(sourceSequence, String(sourceIndex)));
      else markAccepted(undefined, "unknown");
    }

    if (isTerminalRunEvent(event.event_type)) {
      runState = event.event_type;
      for (const step of steps.values()) {
        if (unfinishedStates.has(step.state)) {
          step.state = "interrupted";
          step.ended = timestampOf(event) ?? step.ended;
        }
      }
    }
  }

  const projectedSteps = [...steps.values()]
    .sort((first, second) => first.sequence - second.sequence || first.id.localeCompare(second.id))
    .map((step): TaskStep => {
      const agent = agents.get(step.agentId);
      return {
        ...step,
        agentName: agent?.displayName || step.agentId || "未分配",
        model: step.model || agent?.model || "",
        responsibility: step.responsibility || agent?.responsibility || "",
      };
    });

  return { architecture, runState, resumeFrom, hasPlan, steps: projectedSteps, handoffs };
}

