# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Standalone pack validation can read artifacts owned by an explicit run scope."""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from developer_lens_lab.artifacts import ArtifactStore, canonical_json_bytes
from developer_lens_lab.cli import app

from .factories import research_pack

PACK_ID = "pack_demo"
RUN_SCOPE = "run_owned_scope"


def _stored_pack(tmp_path: Path, scope: str = RUN_SCOPE) -> tuple[Path, Path, Path]:
    table = pa.table(
        {
            "repository_alias": ["system_a"],
            "week_start": ["2025-01-06T00:00:00Z"],
            "metric_code": ["DL.WEEK.CHANGE_COUNT.v1"],
            "value": [3.0],
            "coverage_id": ["coverage_a"],
        }
    )
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    artifact_root = tmp_path / "artifacts"
    store = ArtifactStore(artifact_root)
    reference = store.put_bytes(scope, sink.getvalue().to_pybytes(), "application/x-parquet")
    descriptor = {
        "state": "present",
        "schema_id": "developer-lens.repository-week.v1",
        "row_count": 1,
        "artifact": reference.model_dump(mode="json"),
        "reason_code": None,
    }
    manifest = tmp_path / "pack.json"
    manifest.write_bytes(canonical_json_bytes(research_pack(descriptor)))
    digest = reference.sha256.removeprefix("sha256:")
    object_path = store.scope_root(scope) / "objects" / digest[:2] / digest
    return manifest, artifact_root, object_path


def _snapshot(root: Path) -> dict[Path, bytes | None]:
    return {
        path.relative_to(root): path.read_bytes() if path.is_file() else None
        for path in root.rglob("*")
    }


@pytest.mark.parametrize("scope", [None, RUN_SCOPE, "other_run"])
def test_pack_validate_uses_only_the_selected_artifact_scope(
    tmp_path: Path, scope: str | None
) -> None:
    manifest, artifact_root, _ = _stored_pack(tmp_path)
    before = _snapshot(tmp_path)
    args = ["pack", "validate", str(manifest), "--artifact-root", str(artifact_root)]
    if scope is not None:
        args.extend(["--scope", scope])

    result = CliRunner().invoke(app, args)

    if scope == RUN_SCOPE:
        assert result.exit_code == 0, result.output
        assert "valid DeveloperLensResearchPack.v1 pack_demo" in result.output
    else:
        assert result.exit_code == 1
        assert "artifact object is missing" in result.output
    assert _snapshot(tmp_path) == before


def test_pack_validate_preserves_default_pack_id_scope(tmp_path: Path) -> None:
    manifest, artifact_root, _ = _stored_pack(tmp_path, scope=PACK_ID)
    before = _snapshot(tmp_path)

    result = CliRunner().invoke(
        app, ["pack", "validate", str(manifest), "--artifact-root", str(artifact_root)]
    )

    assert result.exit_code == 0, result.output
    assert "valid DeveloperLensResearchPack.v1 pack_demo" in result.output
    assert _snapshot(tmp_path) == before


def test_pack_validate_manifest_only_does_not_require_artifacts(tmp_path: Path) -> None:
    manifest, _, object_path = _stored_pack(tmp_path)
    object_path.unlink()
    before = _snapshot(tmp_path)

    result = CliRunner().invoke(app, ["pack", "validate", str(manifest)])

    assert result.exit_code == 0, result.output
    assert "valid DeveloperLensResearchPack.v1 pack_demo" in result.output
    assert _snapshot(tmp_path) == before


def test_pack_validate_scope_requires_an_explicit_artifact_root(tmp_path: Path) -> None:
    manifest = tmp_path / "pack.json"
    manifest.write_bytes(canonical_json_bytes(research_pack()))
    before = _snapshot(tmp_path)

    result = CliRunner().invoke(app, ["pack", "validate", str(manifest), "--scope", RUN_SCOPE])

    assert result.exit_code == 1
    assert "ERROR: --scope requires --artifact-root" in result.output
    assert str(tmp_path) not in result.output
    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("present", [False, True], ids=["omitted_relations", "present_relation"])
@pytest.mark.parametrize(
    "scope", ["", "../outside", "nested/scope", "bad\\scope", "UPPER", "ab", "a" * 65]
)
def test_pack_validate_rejects_invalid_scope_even_without_present_relations(
    tmp_path: Path, scope: str, present: bool
) -> None:
    if present:
        manifest, artifact_root, _ = _stored_pack(tmp_path)
    else:
        manifest = tmp_path / "pack.json"
        manifest.write_bytes(canonical_json_bytes(research_pack()))
        artifact_root = tmp_path / "artifacts"
    before = _snapshot(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "pack",
            "validate",
            str(manifest),
            "--artifact-root",
            str(artifact_root),
            "--scope",
            scope,
        ],
    )

    assert result.exit_code == 1
    assert "opaque lowercase identifier" in result.output
    assert str(tmp_path) not in result.output
    assert _snapshot(tmp_path) == before


@pytest.mark.parametrize("damage", ["missing", "tampered"])
def test_pack_validate_explicit_scope_still_verifies_object_integrity(
    tmp_path: Path, damage: str
) -> None:
    manifest, artifact_root, object_path = _stored_pack(tmp_path)
    if damage == "missing":
        object_path.unlink()
    else:
        object_path.write_bytes(b"invented tampered object")
    before = _snapshot(tmp_path)

    result = CliRunner().invoke(
        app,
        [
            "pack",
            "validate",
            str(manifest),
            "--artifact-root",
            str(artifact_root),
            "--scope",
            RUN_SCOPE,
        ],
    )

    assert result.exit_code == 1
    expected = (
        "artifact object is missing" if damage == "missing" else "digest or size verification"
    )
    assert expected in result.output
    assert str(tmp_path) not in result.output
    assert _snapshot(tmp_path) == before
