"""Immutable local object-store adapter for the D38 asset intake path."""

from __future__ import annotations

import base64
import json
import os
import tempfile
from dataclasses import dataclass
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol

from .assets import AssetParser, AssetRecord


@dataclass(frozen=True)
class AssetIngestResult:
    record: AssetRecord
    object_path: str
    chunks: tuple[str, ...]
    published: bool = False
    evaluation_requested: bool = False


class ObjectStore(Protocol):
    def ingest(self, filename: str, content: bytes, *, evaluate: bool = False, space_id: str | None = None) -> AssetIngestResult: ...
    def read_asset(self, asset_id: str) -> bytes: ...
    def read_asset_space(self, asset_id: str) -> str | None: ...
    def delete_asset(self, asset_id: str) -> None: ...


def _scoped_record(record: AssetRecord, space_id: str | None) -> AssetRecord:
    if not space_id:
        return record
    scoped = sha256(f"{space_id}\0{record.content_hash}".encode("utf-8")).hexdigest()[:16]
    return replace(record, asset_id=f"asset-{scoped}")


class LocalObjectStore:
    """Content-addressed object store used until S3/MinIO is configured."""

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or os.environ.get("LOCALRAG_OBJECT_STORE", "results/object_store")).resolve()
        # Create the backing directory on first write; importing the API must
        # not create runtime artifacts in a source checkout.
        self.parser = AssetParser()

    def ingest(self, filename: str, content: bytes, *, evaluate: bool = False, space_id: str | None = None) -> AssetIngestResult:
        record = _scoped_record(self.parser.parse(filename, content), space_id)
        directory = self.root / "blobs" / record.content_hash
        self.root.mkdir(parents=True, exist_ok=True)
        directory.mkdir(parents=True, exist_ok=True)
        object_file = directory / "original.bin"
        if object_file.exists() and object_file.read_bytes() != content:
            raise ValueError("content hash collision")
        if not object_file.exists():
            fd, temporary = tempfile.mkstemp(prefix="asset-", dir=directory)
            try:
                with os.fdopen(fd, "wb") as handle:
                    handle.write(content)
                os.replace(temporary, object_file)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
        chunks = self._chunks(record, content)
        refs = self.root / "refs"
        refs.mkdir(parents=True, exist_ok=True)
        reference = refs / f"{record.asset_id}.json"
        reference.write_text(json.dumps({"record": record.__dict__, "chunks": chunks, "evaluation_requested": evaluate, "space_id": space_id}, ensure_ascii=False, indent=2), encoding="utf-8")
        return AssetIngestResult(record, str(object_file), chunks, False, evaluate)

    def read(self, content_hash: str) -> bytes:
        path = self.root / "blobs" / content_hash / "original.bin"
        if not path.exists():
            path = self.root / content_hash / "original.bin"
        if not path.exists():
            raise FileNotFoundError(content_hash)
        return path.read_bytes()

    def read_asset(self, asset_id: str) -> bytes:
        try:
            payload = json.loads((self.root / "refs" / f"{asset_id}.json").read_text(encoding="utf-8"))
            content_hash = str(payload["record"]["content_hash"])
            return self.read(content_hash)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            prefix = asset_id.removeprefix("asset-")
            matches = tuple(self.root.glob(f"{prefix}*/original.bin"))
        if len(matches) != 1:
            raise FileNotFoundError(asset_id)
        return matches[0].read_bytes()

    def read_asset_space(self, asset_id: str) -> str | None:
        """Read the persisted space owner without exposing manifest internals."""
        reference = self.root / "refs" / f"{asset_id}.json"
        if reference.exists():
            payload = json.loads(reference.read_text(encoding="utf-8"))
        else:
            prefix = asset_id.removeprefix("asset-")
            manifests = tuple(self.root.glob(f"{prefix}*/manifest.json"))
            if len(manifests) != 1:
                raise FileNotFoundError(asset_id)
            payload = json.loads(manifests[0].read_text(encoding="utf-8"))
        value = payload.get("space_id")
        return str(value) if value else None

    def delete_asset(self, asset_id: str) -> None:
        reference = self.root / "refs" / f"{asset_id}.json"
        if not reference.exists():
            return
        payload = json.loads(reference.read_text(encoding="utf-8"))
        content_hash = payload.get("record", {}).get("content_hash")
        reference.unlink(missing_ok=True)
        # Blobs are content-addressed and may be referenced by multiple
        # spaces (or multiple uploads).  Keep the shared original until the
        # last manifest disappears; deleting one asset must not invalidate the
        # other asset's read path.
        if content_hash and not self._has_blob_reference(str(content_hash)):
            import shutil
            shutil.rmtree(self.root / "blobs" / str(content_hash), ignore_errors=True)

    def _has_blob_reference(self, content_hash: str) -> bool:
        refs = self.root / "refs"
        if not refs.exists():
            return False
        for candidate in refs.glob("*.json"):
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
                if str(payload.get("record", {}).get("content_hash", "")) == content_hash:
                    return True
            except (OSError, json.JSONDecodeError, AttributeError):
                # A malformed manifest is not evidence that the blob is
                # unused; retain the blob so recovery can inspect it.
                return True
        return False

    @staticmethod
    def _chunks(record: AssetRecord, content: bytes) -> tuple[str, ...]:
        if record.media_type.startswith("text/") or record.media_type == "application/json":
            text = content.decode("utf-8", errors="replace")
            return tuple(text[index:index + 800] for index in range(0, len(text), 800)) or ("",)
        return (record.derived_preview or "binary asset pending modality parser",)


class S3ObjectStore:
    """S3-compatible content-addressed storage for AWS S3 and MinIO."""

    def __init__(
        self,
        bucket: str,
        *,
        prefix: str = "localrag/assets",
        endpoint_url: str | None = None,
        region_name: str | None = None,
        client: Any | None = None,
        create_bucket: bool = False,
        addressing_style: str | None = None,
        connect_timeout: float = 10.0,
        read_timeout: float = 60.0,
        max_attempts: int = 3,
        server_side_encryption: str | None = None,
        kms_key_id: str | None = None,
    ) -> None:
        if not bucket.strip():
            raise ValueError("S3 bucket must not be empty")
        self.bucket = bucket.strip()
        self.prefix = prefix.strip("/")
        self.parser = AssetParser()
        if client is None:
            try:
                import boto3
            except ImportError as exc:
                raise RuntimeError("boto3 is required for S3 object storage") from exc
            from botocore.config import Config
            config = Config(s3={"addressing_style": addressing_style} if addressing_style else {}, connect_timeout=connect_timeout, read_timeout=read_timeout, retries={"max_attempts": max_attempts, "mode": "standard"})
            verify = os.environ.get("LOCALRAG_S3_TLS_VERIFY", "true").lower() not in {"0", "false", "no"}
            client = boto3.client("s3", endpoint_url=endpoint_url or None, region_name=region_name or None, config=config, verify=verify)
        self.client = client
        self.server_side_encryption = server_side_encryption
        self.kms_key_id = kms_key_id
        if create_bucket:
            self._ensure_bucket(region_name)

    @classmethod
    def from_env(cls) -> "S3ObjectStore":
        bucket = os.environ.get("LOCALRAG_S3_BUCKET", "").strip()
        if not bucket:
            raise RuntimeError("LOCALRAG_S3_BUCKET is required for S3 object storage")
        return cls(
            bucket,
            prefix=os.environ.get("LOCALRAG_S3_PREFIX", "localrag/assets"),
            endpoint_url=os.environ.get("LOCALRAG_S3_ENDPOINT"),
            region_name=os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION"),
            create_bucket=os.environ.get("LOCALRAG_S3_CREATE_BUCKET", "0").strip().lower() in {"1", "true", "yes", "on"},
            addressing_style=os.environ.get("LOCALRAG_S3_ADDRESSING_STYLE") or ("path" if os.environ.get("LOCALRAG_OBJECT_STORE_BACKEND", "").lower() == "minio" else None),
            connect_timeout=float(os.environ.get("LOCALRAG_S3_CONNECT_TIMEOUT", "10")),
            read_timeout=float(os.environ.get("LOCALRAG_S3_READ_TIMEOUT", "60")),
            max_attempts=int(os.environ.get("LOCALRAG_S3_MAX_ATTEMPTS", "3")),
            server_side_encryption=os.environ.get("LOCALRAG_S3_SERVER_SIDE_ENCRYPTION"),
            kms_key_id=os.environ.get("LOCALRAG_S3_KMS_KEY_ID"),
        )

    def _ensure_bucket(self, region_name: str | None) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket)
            return
        except Exception:
            params: dict[str, Any] = {"Bucket": self.bucket}
            if region_name and region_name != "us-east-1":
                params["CreateBucketConfiguration"] = {"LocationConstraint": region_name}
            self.client.create_bucket(**params)

    def _key(self, content_hash: str, name: str) -> str:
        return "/".join(part for part in (self.prefix, "blobs", content_hash, name) if part)

    def _reference_key(self, asset_id: str) -> str:
        return "/".join(part for part in (self.prefix, "refs", f"{asset_id}.json") if part)

    def ingest(self, filename: str, content: bytes, *, evaluate: bool = False, space_id: str | None = None) -> AssetIngestResult:
        record = _scoped_record(self.parser.parse(filename, content), space_id)
        chunks = LocalObjectStore._chunks(record, content)
        object_key = self._key(record.content_hash, "original.bin")
        manifest_key = self._reference_key(record.asset_id)
        manifest = json.dumps(
            {"record": record.__dict__, "chunks": chunks, "evaluation_requested": evaluate, "space_id": space_id},
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        args: dict[str, Any] = {"Bucket": self.bucket, "Key": object_key, "Body": content, "ContentType": record.media_type, "Metadata": {"sha256": record.content_hash, "asset-id": record.asset_id}, "ChecksumSHA256": base64.b64encode(bytes.fromhex(record.content_hash)).decode("ascii")}
        if self.server_side_encryption:
            args["ServerSideEncryption"] = self.server_side_encryption
        if self.kms_key_id:
            args["SSEKMSKeyId"] = self.kms_key_id
        self.client.put_object(**args)
        self.client.put_object(Bucket=self.bucket, Key=manifest_key, Body=manifest, ContentType="application/json")
        return AssetIngestResult(record, f"s3://{self.bucket}/{object_key}", chunks, False, evaluate)

    def _manifest(self, asset_id: str) -> dict[str, Any]:
        try:
            body = self.client.get_object(Bucket=self.bucket, Key=self._reference_key(asset_id))["Body"].read()
        except Exception as exc:
            raise FileNotFoundError(asset_id)
        return json.loads(body.decode("utf-8"))

    def read_asset(self, asset_id: str) -> bytes:
        manifest = self._manifest(asset_id)
        content_hash = str(manifest["record"]["content_hash"])
        return self.client.get_object(Bucket=self.bucket, Key=self._key(content_hash, "original.bin"))["Body"].read()

    def read_asset_space(self, asset_id: str) -> str | None:
        value = self._manifest(asset_id).get("space_id")
        return str(value) if value else None

    def delete_asset(self, asset_id: str) -> None:
        """Delete one manifest and garbage-collect an unreferenced blob."""
        manifest_key = self._reference_key(asset_id)
        manifest = self._manifest(asset_id)
        content_hash = str(manifest.get("record", {}).get("content_hash", ""))
        self.client.delete_object(Bucket=self.bucket, Key=manifest_key)
        if not content_hash or self._has_blob_reference(content_hash):
            return
        self.client.delete_object(Bucket=self.bucket, Key=self._key(content_hash, "original.bin"))

    def _has_blob_reference(self, content_hash: str) -> bool:
        prefix = "/".join(part for part in (self.prefix, "refs") if part) + "/"
        continuation = None
        while True:
            params: dict[str, Any] = {"Bucket": self.bucket, "Prefix": prefix}
            if continuation:
                params["ContinuationToken"] = continuation
            response = self.client.list_objects_v2(**params)
            for item in response.get("Contents", []):
                key = item.get("Key")
                if not key or not str(key).endswith(".json"):
                    continue
                try:
                    body = self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
                    payload = json.loads(body.decode("utf-8"))
                except (OSError, ValueError, KeyError, TypeError):
                    return True
                if str(payload.get("record", {}).get("content_hash", "")) == content_hash:
                    return True
            if not response.get("IsTruncated"):
                return False
            continuation = response.get("NextContinuationToken")
            if not continuation:
                return True


def object_store_from_env() -> ObjectStore:
    backend = os.environ.get("LOCALRAG_OBJECT_STORE_BACKEND", "local").strip().lower()
    if backend == "local":
        return LocalObjectStore()
    if backend in {"s3", "minio"}:
        return S3ObjectStore.from_env()
    raise RuntimeError(f"unsupported object storage backend: {backend}")
