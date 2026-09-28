# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.contracts import ResearchPack
from developer_lens_lab.validation import ManifestError, validate_pack_artifacts

from .factories import research_pack

SCOPE = "pack_demo"


def _coverage_parquet_bytes(columns: dict[str, list[object]]) -> bytes:
    sink = pa.BufferOutputStream()
    pq.write_table(pa.table(columns), sink)
    return sink.getvalue().to_pybytes()


def _valid_coverage_columns() -> dict[str, list[object]]:
    return {
        "coverage_id": ["coverage_a"],
        "capability_code": ["invented.wbc1"],
        "status": ["present"],
        "observed_units": [1],
        "expected_units": [1],
        "window_start": ["2025-01-06T00:00:00Z"],
        "window_end": ["2025-01-13T00:00:00Z"],
    }


def _pack_with_coverage(reference: dict[str, object], row_count: int) -> ResearchPack:
    raw = research_pack()
    raw["pack_id"] = SCOPE
    raw["relations"]["coverage"] = {
        "state": "present",
        "schema_id": "developer-lens.coverage.v1",
        "row_count": row_count,
        "artifact": reference,
        "reason_code": None,
    }
    return ResearchPack.model_validate_json(json.dumps(raw))


def test_coverage_row_count_mismatch_raises(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _coverage_parquet_bytes(_valid_coverage_columns())
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 2)

    with pytest.raises(ManifestError, match="row_count does not match"):
        validate_pack_artifacts(pack, store, SCOPE)


def test_coverage_column_mismatch_raises(tmp_path: Path) -> None:
    store = ArtifactStore(tmp_path / ".dllab")
    columns = _valid_coverage_columns()
    status = columns.pop("status")
    columns = {
        "coverage_id": columns["coverage_id"],
        "capability_code": columns["capability_code"],
        "state": status,
        "observed_units": columns["observed_units"],
        "expected_units": columns["expected_units"],
        "window_start": columns["window_start"],
        "window_end": columns["window_end"],
    }
    payload = _coverage_parquet_bytes(columns)
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 1)

    with pytest.raises(ManifestError, match="columns differ"):
        validate_pack_artifacts(pack, store, SCOPE)
