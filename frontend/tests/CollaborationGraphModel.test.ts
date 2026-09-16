import assert from "node:assert/strict";
import test from "node:test";
import { architectureStages, projectCollaboration } from "../src/features/rooms/collaborationGraphModel.ts";

type EventInput = {
  event_type: string;
  sequence: number;
  payload?: Record<string, unknown>;
  stepSequence?: number;
  runId?: string;
  eventId?: string;
};

function event({ event_type, sequence, payload = {}, stepSequence, runId = "run-alpha", eventId }: EventInput) {
  return {
    event_type,
    room_id: "room-alpha",
    task_id: "task-alpha",
    run_id: runId,
    step_id: stepSequence === undefined ? undefined : `step-${runId}-${stepSequence}`,
    timestamp: `2026-09-14T00:00:${String(sequence).padStart(2, "0")}Z`,
    payload,
    identity: { event_id: eventId ?? `event-${sequence}`, room_sequence: sequence },
  } as never;
}

function plan(sequence: number, steps: Array<Record<string, unknown>>, runId = "run-alpha") {
  return event({ event_type: "team_plan_created", sequence, runId, payload: { architecture: "hierarchical", steps } });
}

test("provides distinct short stages for all supported collaboration modes", () => {
  const modes = ["direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"];
  assert.deepEqual(Object.keys(architectureStages).sort(), [...modes].sort());
  assert.equal(new Set(modes.map((mode) => architectureStages[mode])).size, modes.length);
});

test("keeps a retrying step out of the final failure state", () => {
  const projection = projectCollaboration([
    event({ event_type: "run_started", sequence: 1, payload: { architecture: "hierarchical" } }),
    plan(2, [{ sequence: 1, agent_id: "engineer", title: "实现接口", dependencies: [] }]),
    event({ event_type: "step_started", sequence: 3, stepSequence: 1, payload: { agent_id: "engineer", model: "model-a" } }),
    event({ event_type: "step_failed", sequence: 4, stepSequence: 1, payload: { agent_id: "engineer", error: "TimeoutError" } }),
    event({ event_type: "step_retrying", sequence: 5, stepSequence: 1, payload: { agent_id: "engineer", error: "TimeoutError", attempt: 1, next_attempt: 2 } }),
  ]);

  const step = projection.steps[0];
  assert.equal(step.state, "retrying");
  assert.equal(step.attempt, 1);
  assert.equal(step.nextAttempt, 2);
  assert.equal(step.error, "TimeoutError");
});

test("keeps multiple planned steps for one Agent as separate cards", () => {
  const projection = projectCollaboration([
    plan(1, [
      { sequence: 1, agent_id: "engineer", title: "实现接口", dependencies: [] },
      { sequence: 2, agent_id: "engineer", title: "补充验证", dependencies: [1] },
    ], "run-many"),
  ]);

  assert.deepEqual(projection.steps.map((step) => step.id), ["step-run-many-1", "step-run-many-2"]);
  assert.deepEqual(projection.steps.map((step) => step.title), ["实现接口", "补充验证"]);
  assert.ok(projection.steps.every((step) => step.agentId === "engineer"));
});

test("projects a historical event prefix independently from the latest state", () => {
  const events = [
    event({ event_type: "run_started", sequence: 1, payload: { architecture: "direct" } }),
    plan(2, [{ sequence: 1, agent_id: "chairperson", title: "直接处理", dependencies: [] }]),
    event({ event_type: "step_claimed", sequence: 3, stepSequence: 1, payload: { agent_id: "chairperson" } }),
    event({ event_type: "step_queued", sequence: 4, stepSequence: 1, payload: { agent_id: "chairperson", input: "目标" } }),
    event({ event_type: "step_started", sequence: 5, stepSequence: 1, payload: { agent_id: "chairperson" } }),
    event({ event_type: "step_completed", sequence: 6, stepSequence: 1, payload: { agent_id: "chairperson", output: "完成", model: "model-a", duration_ms: 820 } }),
  ];

  assert.equal(projectCollaboration(events.slice(0, 3)).steps[0].state, "claimed");
  const latest = projectCollaboration(events);
  assert.equal(latest.steps[0].state, "completed");
  assert.equal(latest.steps[0].output, "完成");
  assert.equal(latest.steps[0].durationMs, 820);
});

test("retains dependency information when an upstream failure blocks a task", () => {
  const projection = projectCollaboration([
    plan(1, [
      { sequence: 1, agent_id: "researcher", title: "收集证据", dependencies: [] },
      { sequence: 2, agent_id: "writer", title: "整合报告", dependencies: [1] },
    ]),
    event({ event_type: "step_failed", sequence: 2, stepSequence: 1, payload: { agent_id: "researcher", error: "ModelError" } }),
    event({ event_type: "step_blocked", sequence: 3, stepSequence: 2, payload: { agent_id: "writer", dependencies: [1], error: "上游步骤未完成" } }),
  ]);

  const blocked = projection.steps.find((step) => step.sequence === 2);
  assert.equal(blocked?.state, "blocked");
  assert.deepEqual(blocked?.dependencies, [1]);
  assert.equal(blocked?.error, "上游步骤未完成");
});

test("records restored steps and accepted handoffs without requiring both endpoints", () => {
  const priorEvents = [
    event({ event_type: "step_completed", sequence: 1, stepSequence: 1, runId: "run-prior", payload: { agent_id: "researcher", output: "此前证据", model: "model-a", duration_ms: 120 } }),
  ];
  const projection = projectCollaboration([
    event({ event_type: "run_started", sequence: 1, payload: { architecture: "graph", resume_from: "run-prior" }, runId: "run-restored" }),
    plan(2, [
      { sequence: 1, agent_id: "researcher", title: "分析资料", dependencies: [] },
      { sequence: 2, agent_id: "writer", title: "汇总结果", dependencies: [1] },
    ], "run-restored"),
    event({ event_type: "step_reused", sequence: 3, stepSequence: 1, runId: "run-restored", payload: { agent_id: "researcher" } }),
    event({ event_type: "handoff_created", sequence: 4, stepSequence: 2, runId: "run-restored", payload: { agent_id: "writer", from_agent_id: "researcher", to_agent_id: "writer", source_sequence: 1, sequence: 2, summary: "汇总结果", shared_output: "此前证据" } }),
    event({ event_type: "handoff_accepted", sequence: 5, stepSequence: 2, runId: "run-restored", payload: { agent_id: "writer", sequence: 2, source_sequences: [1] } }),
  ], priorEvents);

  assert.equal(projection.resumeFrom, "run-prior");
  assert.equal(projection.steps.find((step) => step.sequence === 1)?.state, "reused");
  assert.equal(projection.steps.find((step) => step.sequence === 1)?.output, "此前证据");
  assert.equal(projection.handoffs.length, 1);
  assert.equal(projection.handoffs[0].output, "此前证据");
  assert.ok(projection.handoffs[0].acceptedAt);
});

test("tolerates a recorded handoff when either task endpoint is absent", () => {
  const projection = projectCollaboration([
    event({ event_type: "handoff_created", sequence: 1, runId: "run-incomplete", payload: { from_agent_id: "researcher", to_agent_id: "writer", summary: "遗留共享内容", shared_output: "可用结果" } }),
  ]);

  assert.equal(projection.handoffs.length, 1);
  assert.equal(projection.handoffs[0].summary, "遗留共享内容");
  assert.equal(projection.steps.length, 0);
});
