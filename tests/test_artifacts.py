from __future__ import annotations

import os
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


def test_write_scope_file_once_cleans_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    store.reserve_scope("scope_demo")
    target = store.scope_root("scope_demo") / "custody.json"

    def _failing_fsync(fd: int) -> None:
        raise OSError("injected fsync failure")

    monkeypatch.setattr(os, "fsync", _failing_fsync)
    with pytest.raises(OSError, match="injected fsync failure"):
        store.write_scope_file_once("scope_demo", "custody.json", b"{}\n")
    assert not target.exists()
    with pytest.raises(OSError, match="injected fsync failure"):
        store.write_scope_file_once("scope_demo", "custody.json", b"{}\n")
    assert not target.exists()
    monkeypatch.undo()
    assert store.write_scope_file_once("scope_demo", "custody.json", b"complete\n") == target
    assert target.read_bytes() == b"complete\n"


def test_invalidate_scope_removes_only_target(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    target_root = store.reserve_scope("scope_target")
    sibling_root = store.reserve_scope("scope_sibling")
    target_ref = store.put_bytes("scope_target", b"target payload", "application/json")
    sibling_ref = store.put_bytes("scope_sibling", b"sibling payload", "application/json")
    store.write_scope_file("scope_target", "target.txt", b"target file")
    store.write_scope_file("scope_sibling", "sibling.txt", b"sibling file")
    assert store.get_bytes("scope_target", target_ref) == b"target payload"
    assert store.get_bytes("scope_sibling", sibling_ref) == b"sibling payload"

    assert store.invalidate_scope("scope_target") is True
    assert not target_root.exists()
    assert sibling_root.is_dir()
    assert store.get_bytes("scope_sibling", sibling_ref) == b"sibling payload"
    assert (sibling_root / "sibling.txt").read_bytes() == b"sibling file"
    assert store.invalidate_scope("scope_target") is False

    target_root = store.reserve_scope("scope_target")
    recreated_ref = store.put_bytes("scope_target", b"target payload v2", "application/json")
    store.write_scope_file("scope_target", "target.txt", b"target file v2")
    quarantine = target_root.with_name(".deleting-scope_target")
    quarantine.mkdir()
    with pytest.raises(ArtifactError, match="quarantine"):
        store.invalidate_scope("scope_target")
    assert target_root.is_dir()
    assert store.get_bytes("scope_target", recreated_ref) == b"target payload v2"
    assert (target_root / "target.txt").read_bytes() == b"target file v2"
    assert store.get_bytes("scope_sibling", sibling_ref) == b"sibling payload"
    assert (sibling_root / "sibling.txt").read_bytes() == b"sibling file"
