from __future__ import annotations

import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError
from scripts.smoke_agent_platform import _wait_ready
from pathlib import Path


class DemoSmokeScriptTests(unittest.TestCase):
    def test_demo_smoke_script_runs_api_flow(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "scripts/smoke_agent_platform.py"], cwd=root, capture_output=True, text=True, check=False, timeout=150)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("smoke pass:", result.stdout)
        self.assertIn("message_saved=1", result.stdout)

    def test_probe_allows_cold_start_beyond_thirty_seconds(self):
        process = Mock()
        process.poll.return_value = None
        with patch("scripts.smoke_agent_platform.time.monotonic", side_effect=[0, 0, 0, 40, 40, 40]), patch("scripts.smoke_agent_platform.time.sleep"), patch("scripts.smoke_agent_platform._request", side_effect=[URLError("starting"), {"status": "ok"}]):
            _wait_ready(process, "http://127.0.0.1:1")

    def test_probe_fails_immediately_when_process_exits(self):
        process = Mock(returncode=3)
        process.poll.return_value = 3
        with patch("scripts.smoke_agent_platform._request") as request:
            with self.assertRaisesRegex(RuntimeError, "exit=3"):
                _wait_ready(process, "http://127.0.0.1:1")
            request.assert_not_called()

    def test_probe_has_bounded_timeout(self):
        process = Mock()
        process.poll.return_value = None
        with patch("scripts.smoke_agent_platform.time.monotonic", side_effect=[0, 2]):
            with self.assertRaisesRegex(RuntimeError, "within 1s"):
                _wait_ready(process, "http://127.0.0.1:1", timeout=1)


if __name__ == "__main__":
    unittest.main()
