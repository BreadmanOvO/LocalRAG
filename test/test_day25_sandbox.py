from __future__ import annotations
import unittest
from agent_platform.sandbox import SandboxPolicy

class Day25SandboxTests(unittest.TestCase):
    def test_path_network_and_credentials_are_denied_by_default(self) -> None:
        policy = SandboxPolicy(("/workspace/",))
        policy.validate("/workspace/input.csv")
        with self.assertRaises(PermissionError): policy.validate("/etc/passwd")
        with self.assertRaises(PermissionError): policy.validate("/workspace/x", network=True)
        with self.assertRaises(PermissionError): policy.validate("/workspace/x", credentials=True)

if __name__ == "__main__": unittest.main()
