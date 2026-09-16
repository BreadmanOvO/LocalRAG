import assert from "node:assert/strict";
import test from "node:test";
import { formatDateTime, parseTimestamp } from "../src/shared/time.ts";

test("converts explicit UTC offsets once when formatting in the target timezone", () => {
  assert.equal(formatDateTime("2026-09-14T15:32:45.852671+00:00", { timeZone: "Asia/Shanghai" }), "2026/09/14 23:32:45");
});
test("keeps timezone-less timestamps as local wall-clock values", () => {
  assert.equal(formatDateTime("2026-09-14T15:32:45", { timeZone: "Asia/Shanghai" }), "2026/09/14 15:32:45");
  assert.equal(formatDateTime("2026-09-14", { timeZone: "Asia/Shanghai" }), "2026/09/14 00:00:00");
});

test("returns null for malformed or impossible local timestamps", () => {
  assert.equal(parseTimestamp("2026-02-30T10:00:00"), null);
  assert.equal(parseTimestamp("not-a-timestamp"), null);
});
