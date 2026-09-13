from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class DemoSmokeScriptTests(unittest.TestCase):
    def test_demo_smoke_script_runs_api_flow(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable, "scripts/smoke_agent_platform.py"], cwd=root, capture_output=True, text=True, check=False, timeout=30)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("smoke pass:", result.stdout)
        self.assertIn("events=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
