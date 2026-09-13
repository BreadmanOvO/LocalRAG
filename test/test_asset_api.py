from __future__ import annotations

import base64
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from agent_platform.api import create_app
from agent_platform.capability_packs import LocalObjectStore


class AssetApiTests(unittest.TestCase):
    def test_upload_is_content_addressed_and_evaluation_optional(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            client = TestClient(create_app(asset_store=LocalObjectStore(Path(directory))))
            encoded = base64.b64encode("alpha\nbeta\n".encode()).decode()
            response = client.post("/assets", json={"filename": "notes.txt", "content_base64": encoded})
            self.assertEqual(201, response.status_code, response.text)
            payload = response.json()
            self.assertEqual("not_requested", payload["evaluation_status"])
            self.assertEqual(["alpha\nbeta\n"], payload["chunks"])
            self.assertEqual(encoded, client.get(f"/assets/{payload['asset_id']}").json()["content_base64"])
            replay = client.post("/assets", json={"filename": "copy.txt", "content_base64": encoded, "evaluate": True})
            self.assertEqual(201, replay.status_code)
            self.assertEqual("requested", replay.json()["evaluation_status"])

    def test_invalid_base64_is_structured(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            client = TestClient(create_app(asset_store=LocalObjectStore(directory)))
            response = client.post("/assets", json={"filename": "x.txt", "content_base64": "%%%"})
            self.assertEqual(422, response.status_code)
            self.assertEqual("invalid_asset", response.json()["code"])


if __name__ == "__main__":
    unittest.main()
