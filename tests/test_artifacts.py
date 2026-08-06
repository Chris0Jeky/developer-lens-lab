from __future__ import annotations

from pathlib import Path

import pytest

from developer_lens_lab.artifacts import ArtifactError, ArtifactStore


def test_scope_store_roundtrip_deduplicates_and_invalidates(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    first = store.put_bytes("scope_demo", b"invented payload", "application/json")
    second = store.put_bytes("scope_demo", b"invented payload", "application/json")

    assert first == second
    assert store.get_bytes("scope_demo", first) == b"invented payload"
    manifest = store.write_scope_manifest("scope_demo", (first,))
    assert manifest.is_file()
    assert store.invalidate_scope("scope_demo")
    assert not manifest.parent.exists()
    assert not store.invalidate_scope("scope_demo")


def test_store_detects_tampering_and_rejects_unscoped_names(tmp_path: Path) -> None:
    root = tmp_path / ".dllab"
    store = ArtifactStore(root)
    reference = store.put_bytes("scope_demo", b"original", "application/json")
    hex_digest = reference.sha256.removeprefix("sha256:")
    object_path = root / "scopes" / "scope_demo" / "objects" / hex_digest[:2] / hex_digest
    object_path.write_bytes(b"tampered")

    with pytest.raises(ArtifactError, match="digest or size"):
        store.get_bytes("scope_demo", reference)
    with pytest.raises(ArtifactError, match="scope_id"):
        store.put_bytes("../escape", b"x", "application/json")
