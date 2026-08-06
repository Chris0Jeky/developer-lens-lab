from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Literal

from developer_lens_lab.contracts import ArtifactRef

_SCOPE_RE = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
_DIGEST_RE = re.compile(r"^sha256:([0-9a-f]{64})$")


class ArtifactError(RuntimeError):
    """Raised when an artifact is missing, invalid, or outside the store contract."""


def canonical_json_bytes(value: Any) -> bytes:
    try:
        rendered = json.dumps(
            value,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise ArtifactError("JSON artifact contains a non-finite or unsupported value") from exc
    return rendered.encode("utf-8")


class ArtifactStore:
    """Scope-confined content-addressed objects with atomic same-directory publication."""

    def __init__(self, root: Path) -> None:
        if root.exists() and root.is_symlink():
            raise ArtifactError("artifact root must not be a symlink")
        self.root = root.resolve()

    def _scope_root(self, scope_id: str) -> Path:
        if not _SCOPE_RE.fullmatch(scope_id):
            raise ArtifactError("scope_id must be an opaque lowercase identifier")
        return self.root / "scopes" / scope_id

    def scope_root(self, scope_id: str) -> Path:
        """Return the validated scope directory for runner metadata."""
        return self._scope_root(scope_id)

    def _object_path(self, scope_id: str, digest: str) -> Path:
        match = _DIGEST_RE.fullmatch(digest)
        if match is None:
            raise ArtifactError("artifact digest must be lowercase sha256:<hex>")
        hex_digest = match.group(1)
        return self._scope_root(scope_id) / "objects" / hex_digest[:2] / hex_digest

    @staticmethod
    def _ensure_no_symlink_parents(path: Path, stop: Path) -> None:
        current = path
        while current != stop:
            if current.exists() and current.is_symlink():
                raise ArtifactError("artifact path traverses a symlink")
            current = current.parent
        if stop.exists() and stop.is_symlink():
            raise ArtifactError("artifact root must not be a symlink")

    @staticmethod
    def _atomic_write(path: Path, payload: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        handle, temporary_name = tempfile.mkstemp(prefix=".dllab-tmp-", dir=path.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(handle, "wb") as stream:
                stream.write(payload)
                stream.flush()
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    def write_scope_file(self, scope_id: str, name: str, payload: bytes) -> Path:
        if Path(name).name != name or not name:
            raise ArtifactError("scope file name must be a simple file name")
        path = self._scope_root(scope_id) / name
        self._ensure_no_symlink_parents(path.parent, self.root)
        self._atomic_write(path, payload)
        return path

    def put_bytes(
        self,
        scope_id: str,
        payload: bytes,
        media_type: Literal[
            "application/json", "application/x-parquet", "text/markdown", "text/html"
        ],
    ) -> ArtifactRef:
        digest = "sha256:" + hashlib.sha256(payload).hexdigest()
        reference = ArtifactRef(sha256=digest, size_bytes=len(payload), media_type=media_type)
        path = self._object_path(scope_id, digest)
        self._ensure_no_symlink_parents(path.parent, self.root)
        if path.exists():
            existing = path.read_bytes()
            if existing != payload:
                raise ArtifactError(
                    "existing content-addressed object failed integrity verification"
                )
            return reference
        self._atomic_write(path, payload)
        return reference

    def put_json(self, scope_id: str, value: Any) -> ArtifactRef:
        return self.put_bytes(scope_id, canonical_json_bytes(value), "application/json")

    def put_text(
        self, scope_id: str, value: str, media_type: Literal["text/markdown", "text/html"]
    ) -> ArtifactRef:
        return self.put_bytes(scope_id, value.encode("utf-8"), media_type)

    def get_bytes(self, scope_id: str, reference: ArtifactRef) -> bytes:
        path = self._object_path(scope_id, reference.sha256)
        self._ensure_no_symlink_parents(path.parent, self.root)
        try:
            payload = path.read_bytes()
        except FileNotFoundError as exc:
            raise ArtifactError("artifact object is missing") from exc
        actual = "sha256:" + hashlib.sha256(payload).hexdigest()
        if actual != reference.sha256 or len(payload) != reference.size_bytes:
            raise ArtifactError("artifact object failed digest or size verification")
        return payload

    def write_scope_manifest(self, scope_id: str, references: tuple[ArtifactRef, ...]) -> Path:
        scope_root = self._scope_root(scope_id)
        manifest = scope_root / "manifest.json"
        self._ensure_no_symlink_parents(manifest.parent, self.root)
        payload = canonical_json_bytes(
            {
                "schema_version": "DeveloperLensArtifactScope.v1",
                "scope_id": scope_id,
                "artifacts": [reference.model_dump(mode="json") for reference in references],
            }
        )
        self._atomic_write(manifest, payload)
        return manifest

    def invalidate_scope(self, scope_id: str) -> bool:
        scope_root = self._scope_root(scope_id)
        self._ensure_no_symlink_parents(scope_root, self.root)
        if not scope_root.exists():
            return False
        quarantine = scope_root.with_name(f".deleting-{scope_id}")
        if quarantine.exists():
            raise ArtifactError("scope invalidation quarantine already exists")
        os.replace(scope_root, quarantine)
        shutil.rmtree(quarantine)
        return True
