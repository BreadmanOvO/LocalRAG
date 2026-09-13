from __future__ import annotations

import unittest
from threading import Lock

from agent_platform.runtime.reliability import run_concurrency_probe, run_long_session_probe


class ReliabilityProbeTests(unittest.TestCase):
    def test_concurrency_probe_covers_one_two_four_workers(self) -> None:
        lock = Lock()
        counter = {"value": 0}

        def operation() -> None:
            with lock:
                counter["value"] += 1

        levels = run_concurrency_probe(operation)
        self.assertEqual([1, 2, 4], [level.workers for level in levels])
        self.assertTrue(all(level.failures == 0 and level.completed == level.calls for level in levels))

    def test_long_session_continues_after_context_compression(self) -> None:
        seen: list[str] = []

        def turn(prompt: str, context: str) -> str:
            seen.append(context)
            return f"answer-{len(seen)}"

        count, compressed = run_long_session_probe(turn, turns=5, compression_after=3)
        self.assertEqual(3, count)
        self.assertTrue(compressed)
        self.assertTrue(any("summary:" in item for item in seen))


if __name__ == "__main__":
    unittest.main()

