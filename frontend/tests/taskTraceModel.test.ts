import assert from "node:assert/strict";
import test from "node:test";
import { mergeRoomEvents, projectTaskTrace } from "../src/features/rooms/taskTraceModel.ts";

function event(seq: number, type: string, room = "room-a", run: string | null = "run-a", step?: number) {
  return { room_id: room, run_id: run, event_type: type,
    step_id: step == null ? null : `step-${step}`, payload: { sequence: step },
    identity: { event_id: `event-${room}-${seq}`, room_id: room, room_sequence: seq } } as never;
}

test("room merge filters other rooms and deduplicates snapshot/SSE overlap", () => {
  const result = mergeRoomEvents("room-a", [event(9, "step_claimed"), event(1, "run_started", "room-b")], [event(9, "step_claimed"), event(10, "step_queued")]);
  assert.deepEqual(result.map(e => e.identity.room_sequence), [9, 10]);
});

test("hundreds of deltas produce one step row with continuous display numbers", () => {
  const input = [event(1, "run_started"), event(9, "step_claimed", "room-a", "run-a", 1), event(10, "step_queued", "room-a", "run-a", 1), event(11, "step_started", "room-a", "run-a", 1),
    ...Array.from({ length: 258 }, (_, i) => event(i + 12, "step_output_delta", "room-a", "run-a", 1)), event(270, "message_saved"), event(271, "step_completed", "room-a", "run-a", 1), event(272, "run_completed")];
  const rows = projectTaskTrace(input, "run-a");
  assert.deepEqual(rows.map(row => row.ordinal), [1, 2, 3]);
  assert.equal(rows[1].event.event_type, "step_completed");
  assert.deepEqual(rows[1].records.map(e => e.identity.room_sequence), [9, 10, 11, 271]);
});

test("task selection isolates runs and retains retries in step details", () => {
  const input = [event(1, "run_started"), event(2, "run_started", "room-a", "run-b"), event(3, "step_started", "room-a", "run-b", 1), event(4, "step_retrying", "room-a", "run-b", 1), event(5, "step_failed", "room-a", "run-b", 1)];
  const rows = projectTaskTrace(input, "run-b");
  assert.equal(rows.length, 2);
  assert.equal(rows[1].event.event_type, "step_failed");
  assert.equal(rows[1].records.length, 3);
  assert.equal(projectTaskTrace(input, "run-a").length, 1);
});
