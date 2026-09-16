from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CloudSmokeScriptTests(unittest.TestCase):
    def test_missing_key_is_reported_without_live_request_or_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "models.json"
            path.write_text(json.dumps({
                "contract_version": "agent-platform-cloud-v1",
                "model_profiles": {"cloud": {"provider": "mock", "base_url": "https://example.com/v1", "model": "m", "api_key_env": "UNSET_TEST_KEY", "enabled": True}},
                "agents": {"chairperson": {"display_name": "助理", "responsibility": "完成", "model_profile": "cloud", "enabled": True}},
            }), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/smoke_cloud_multi_agent.py", "--config", str(path)], cwd=Path(__file__).parents[1], capture_output=True, text=True, check=False)
        self.assertEqual(2, completed.returncode)
        self.assertIn("not_configured", completed.stdout)
        self.assertNotIn("Authorization", completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
