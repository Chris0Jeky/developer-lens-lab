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


@pytest.mark.parametrize(
    ("relation", "columns"),
    [
        ("coverage", _valid_coverage_columns()),
        (
            "repository_week",
            {
                "repository_alias": ["system_a"],
                "week_start": ["2025-01-06T00:00:00Z"],
                "metric_code": ["DL.WEEK.CHANGE_COUNT.v1"],
                "value": [3.0],
                "coverage_id": ["coverage_a"],
            },
        ),
        (
            "pr_episode",
            {
                "episode_id": ["episode_a"],
                "repository_alias": ["system_a"],
                "opened_at": ["2025-01-06T00:00:00Z"],
                "ready_at": ["2025-01-06T01:00:00Z"],
                "merged_at": ["2025-01-06T02:00:00Z"],
                "status": ["merged"],
                "coverage_id": ["coverage_a"],
            },
        ),
        (
            "ci_attempt",
            {
                "attempt_id": ["attempt_a"],
                "repository_alias": ["system_a"],
                "started_at": ["2025-01-06T00:00:00Z"],
                "completed_at": ["2025-01-06T01:00:00Z"],
                "outcome_code": ["success"],
                "coverage_id": ["coverage_a"],
            },
        ),
        (
            "release_episode",
            {
                "release_id": ["release_a"],
                "repository_alias": ["system_a"],
                "week_start": ["2025-01-06T00:00:00Z"],
                "change_count": [3],
                "coverage_id": ["coverage_a"],
            },
        ),
        (
            "collection_probe",
            {
                "probe_id": ["probe_a"],
                "repository_alias": ["system_a"],
                "observed_at": ["2025-01-06T00:00:00Z"],
                "status": ["present"],
                "coverage_id": ["coverage_a"],
            },
        ),
        (
            "system_event",
            {
                "event_id": ["event_a"],
                "repository_alias": ["system_a"],
                "occurred_at": ["2025-01-06T00:00:00Z"],
                "event_code": ["invented.event"],
                "coverage_id": ["coverage_a"],
            },
        ),
    ],
)
def test_relation_arrow_schema(
    tmp_path: Path, relation: str, columns: dict[str, list[object]]
) -> None:
    from developer_lens_lab.contracts.research_pack import RELATION_SCHEMA_IDS

    store = ArtifactStore(tmp_path / ".dllab")

    def validate(table: pa.Table) -> None:
        sink = pa.BufferOutputStream()
        pq.write_table(table, sink)
        reference = store.put_bytes(SCOPE, sink.getvalue().to_pybytes(), "application/x-parquet")
        raw = research_pack()
        raw["relations"][relation] = {
            "state": "present",
            "schema_id": RELATION_SCHEMA_IDS[relation],
            "row_count": 1,
            "artifact": reference.model_dump(mode="json"),
            "reason_code": None,
        }
        pack = ResearchPack.model_validate_json(json.dumps(raw))
        validate_pack_artifacts(pack, store, SCOPE)

    table = pa.table(columns)
    validate(table)
    for index, field in enumerate(table.schema):
        wrong = pa.array([{"invented": "not-a-scalar"}])
        with pytest.raises(ManifestError, match=f"relation {relation}.*type") as error:
            validate(table.set_column(index, field.name, wrong))
        assert str(tmp_path) not in str(error.value)
        assert "not-a-scalar" not in str(error.value)

        nullable = field.name in {"ready_at", "merged_at", "completed_at", "expected_units"}
        with_null = table.set_column(index, field.name, pa.array([None], type=field.type))
        if nullable:
            validate(with_null)
        else:
            with pytest.raises(ManifestError, match="null"):
                validate(with_null)

        if field.name == "value":
            with pytest.raises(ManifestError, match=r"value.*type"):
                validate(table.set_column(index, field.name, pa.array(["not-a-number"])))
            for value in (float("nan"), float("inf"), float("-inf")):
                with pytest.raises(ManifestError, match="finite"):
                    validate(table.set_column(index, field.name, pa.array([value])))
        elif pa.types.is_integer(field.type):
            with pytest.raises(ManifestError, match="non-negative"):
                validate(table.set_column(index, field.name, pa.array([-1])))
        elif field.name.endswith(("_at", "_start", "_end")):
            for value in ("not-a-timestamp", "2025-02-30T00:00:00Z", "2025-01-06T00:00:00+00:00"):
                with pytest.raises(ManifestError, match="UTC"):
                    validate(table.set_column(index, field.name, pa.array([value])))
