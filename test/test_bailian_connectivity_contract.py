import importlib
import unittest
from pathlib import Path


class BailianConnectivityContractTests(unittest.TestCase):
    def test_connectivity_script_exists_and_exposes_main(self):
        project_root = Path(__file__).resolve().parents[1]
        script_path = project_root / "test_bailian_connectivity.py"
        self.assertTrue(script_path.exists(), "test_bailian_connectivity.py should exist")

        module = importlib.import_module("test_bailian_connectivity")
        self.assertTrue(hasattr(module, "main"), "test_bailian_connectivity must define main")


if __name__ == "__main__":
    unittest.main()
