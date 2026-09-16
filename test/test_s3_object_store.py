from __future__ import annotations

from io import BytesIO
import json
import unittest

from agent_platform.capability_packs import S3ObjectStore


class _FakeS3:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], bytes] = {}

    def put_object(self, *, Bucket, Key, Body, **kwargs):
        self.objects[(Bucket, Key)] = Body if isinstance(Body, bytes) else Body.read()

    def list_objects_v2(self, *, Bucket, Prefix):
        return {"Contents": [{"Key": key} for bucket, key in self.objects if bucket == Bucket and key.startswith(Prefix)]}

    def get_object(self, *, Bucket, Key):
        try:
            return {"Body": BytesIO(self.objects[(Bucket, Key)])}
        except KeyError as exc:
            raise FileNotFoundError(Key) from exc


class S3ObjectStoreTests(unittest.TestCase):
    def test_round_trip_keeps_content_address_and_space_owner(self) -> None:
        client = _FakeS3()
        store = S3ObjectStore("assets", prefix="tenant/assets", client=client)
        result = store.ingest("notes.txt", b"alpha\nbeta\n", space_id="space-a")

        self.assertTrue(result.record.asset_id.startswith("asset-"))
        self.assertEqual(f"s3://assets/tenant/assets/blobs/{result.record.content_hash}/original.bin", result.object_path)
        self.assertEqual(b"alpha\nbeta\n", store.read_asset(result.record.asset_id))
        self.assertEqual("space-a", store.read_asset_space(result.record.asset_id))
        manifest = next(value for (_, key), value in client.objects.items() if "/refs/" in key)
        self.assertNotIn("credential", json.loads(manifest))

    def test_same_blob_has_separate_space_references(self) -> None:
        client = _FakeS3()
        store = S3ObjectStore("assets", client=client)
        first = store.ingest("same.txt", b"same", space_id="space-a")
        second = store.ingest("same.txt", b"same", space_id="space-b")
        self.assertNotEqual(first.record.asset_id, second.record.asset_id)
        self.assertEqual("space-a", store.read_asset_space(first.record.asset_id))
        self.assertEqual("space-b", store.read_asset_space(second.record.asset_id))
        blob_keys = [key for _, key in client.objects if "/blobs/" in key]
        self.assertEqual(1, len(blob_keys))

    def test_unknown_asset_is_not_found(self) -> None:
        store = S3ObjectStore("assets", client=_FakeS3())
        with self.assertRaises(FileNotFoundError):
            store.read_asset("asset-deadbeefdeadbeef")


if __name__ == "__main__":
    unittest.main()
