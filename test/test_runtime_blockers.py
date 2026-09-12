from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
import subprocess
from fastapi.testclient import TestClient
from agent_platform.api import create_app
from agent_platform.runtime import RecoveryService, read_backup, write_backup

class RuntimeBlockerTests(unittest.TestCase):
    def test_api_health_is_runnable(self) -> None:
        response = TestClient(create_app()).get("/health")
        self.assertEqual(200, response.status_code); self.assertEqual("ok", response.json()["status"])

    def test_backup_round_trip_is_checksum_verified(self) -> None:
        service = RecoveryService(); service.save_persona_snapshot("space-demo", "assistant", "v1", {"tone": "brief"})
        bundle = service.create_backup()
        with tempfile.TemporaryDirectory() as directory:
            path = write_backup(bundle, Path(directory) / "backup.json")
            restored = read_backup(path)
            self.assertTrue(restored.verify())
            target = RecoveryService(); report = target.restore_backup(restored)
            self.assertEqual(1, report.restored_personas)

    def test_deployment_script_has_valid_powershell_syntax(self) -> None:
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_agent_platform.ps1"
        command = f"$errors=$null; [System.Management.Automation.Language.Parser]::ParseFile('{script}', [ref]$null, [ref]$errors) | Out-Null; if ($errors.Count) {{ exit 1 }}"
        result = subprocess.run(["powershell", "-NoProfile", "-Command", command], capture_output=True, text=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)

if __name__ == "__main__": unittest.main()
