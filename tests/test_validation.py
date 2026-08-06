# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.cli import app
from developer_lens_lab.contracts import ResearchPack
from developer_lens_lab.validation import (
    ManifestError,
    assert_path_free_manifest,
    profile_research_pack,
    validate_pack_artifacts,
)

from .factories import evaluation_bundle, research_pack


def _repository_week_parquet() -> bytes:
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
    return sink.getvalue().to_pybytes()


def test_pack_artifact_validation_and_profile_preserve_states(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _repository_week_parquet()
    reference = store.put_bytes("pack_demo", payload, "application/x-parquet")
    descriptor = {
        "state": "present",
        "schema_id": "developer-lens.repository-week.v1",
        "row_count": 1,
        "artifact": reference.model_dump(mode="json"),
        "reason_code": None,
    }
    pack = ResearchPack.model_validate_json(json.dumps(research_pack(descriptor)))

    validate_pack_artifacts(pack, store)
    profile = profile_research_pack(pack)
    assert profile["relations"] == {"intentionally_omitted": 6, "present": 1}
    assert profile["present_rows"] == 1


def test_manifest_path_filter_and_read_only_cli(tmp_path: Path) -> None:
    with pytest.raises(ManifestError, match="local path"):
        assert_path_free_manifest({"note": "C:\\Users\\someone\\private"})

    manifest = tmp_path / "pack.json"
    manifest.write_text(json.dumps(research_pack()), encoding="utf-8")
    result = CliRunner().invoke(app, ["pack", "validate", str(manifest)])
    profile = CliRunner().invoke(app, ["pack", "profile", str(manifest)])

    assert result.exit_code == 0, result.output
    assert profile.exit_code == 0, profile.output
    assert '"intentionally_omitted": 7' in profile.output
    assert not (tmp_path / ".dllab").exists()

    bundle_manifest = tmp_path / "bundle.json"
    bundle_manifest.write_text(json.dumps(evaluation_bundle()), encoding="utf-8")
    bundle = CliRunner().invoke(app, ["bundle", "validate", str(bundle_manifest)])
    assert bundle.exit_code == 0, bundle.output
