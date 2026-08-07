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


def test_json_store_rejects_non_finite_values_before_writing(tmp_path: Path) -> None:
    root = tmp_path / ".dllab"
    store = ArtifactStore(root)

    with pytest.raises(ArtifactError, match="non-finite"):
        store.put_json("scope_demo", {"metric": float("nan")})
    assert not root.exists()


def test_scope_reservation_and_append_only_records_refuse_reuse(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    scope = store.reserve_scope("scope_demo")
    custody = store.write_scope_file_once("scope_demo", "custody.json", b"{}\n")

    assert scope.is_dir()
    assert custody.read_bytes() == b"{}\n"
    with pytest.raises(ArtifactError, match="scope already exists"):
        store.reserve_scope("scope_demo")
    with pytest.raises(ArtifactError, match="scope file already exists"):
        store.write_scope_file_once("scope_demo", "custody.json", b"changed\n")
    assert custody.read_bytes() == b"{}\n"
