# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Accept equivalent producer Arrow encodings without relaxing relation values."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.contracts import ResearchPack
from developer_lens_lab.contracts.research_pack import RELATION_SCHEMA_IDS
from developer_lens_lab.validation import ManifestError, validate_pack_artifacts

from .factories import research_pack

RELATION_COLUMNS: dict[str, dict[str, list[object]]] = {
    "coverage": {
        "coverage_id": ["coverage_a"],
        "capability_code": ["invented.wbc1"],
        "status": ["present"],
        "observed_units": [1],
        "expected_units": [1],
        "window_start": ["2025-01-06T00:00:00Z"],
        "window_end": ["2025-01-13T00:00:00Z"],
    },
    "repository_week": {
        "repository_alias": ["system_a"],
        "week_start": ["2025-01-06T00:00:00Z"],
        "metric_code": ["DL.WEEK.CHANGE_COUNT.v1"],
        "value": [3.0],
        "coverage_id": ["coverage_a"],
    },
    "pr_episode": {
        "episode_id": ["episode_a"],
        "repository_alias": ["system_a"],
        "opened_at": ["2025-01-06T00:00:00Z"],
        "ready_at": ["2025-01-06T01:00:00Z"],
        "merged_at": ["2025-01-06T02:00:00Z"],
        "status": ["merged"],
        "coverage_id": ["coverage_a"],
    },
    "ci_attempt": {
        "attempt_id": ["attempt_a"],
        "repository_alias": ["system_a"],
        "started_at": ["2025-01-06T00:00:00Z"],
        "completed_at": ["2025-01-06T01:00:00Z"],
        "outcome_code": ["success"],
        "coverage_id": ["coverage_a"],
    },
}


def _validate_table(tmp_path: Path, relation: str, table: Any) -> None:
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    store = ArtifactStore(tmp_path / ".dllab")
    reference = store.put_bytes("pack_demo", sink.getvalue().to_pybytes(), "application/x-parquet")
    raw = research_pack()
    raw["relations"][relation] = {
        "state": "present",
        "schema_id": RELATION_SCHEMA_IDS[relation],
        "row_count": table.num_rows,
        "artifact": reference.model_dump(mode="json"),
        "reason_code": None,
    }
    pack = ResearchPack.model_validate_json(json.dumps(raw))
    validate_pack_artifacts(pack, store)


def _large_string_table(relation: str) -> Any:
    table = pa.table(RELATION_COLUMNS[relation])
    for index, field in enumerate(table.schema):
        if pa.types.is_string(field.type):
            table = table.set_column(index, field.name, table.column(index).cast(pa.large_string()))
    return table


@pytest.mark.parametrize(
    ("relation", "optional_fields"),
    [
        ("coverage", ("expected_units",)),
        ("pr_episode", ("ready_at", "merged_at")),
        ("ci_attempt", ("completed_at",)),
    ],
)
def test_accepts_inferred_null_type_for_declared_optional_fields(
    tmp_path: Path, relation: str, optional_fields: tuple[str, ...]
) -> None:
    columns = {**RELATION_COLUMNS[relation], **{field: [None] for field in optional_fields}}
    table = pa.table(columns)
    assert all(pa.types.is_null(table.schema.field(field).type) for field in optional_fields)

    _validate_table(tmp_path, relation, table)


@pytest.mark.parametrize("relation", RELATION_COLUMNS)
def test_accepts_large_string_for_schema_string_fields(tmp_path: Path, relation: str) -> None:
    _validate_table(tmp_path, relation, _large_string_table(relation))


@pytest.mark.parametrize(
    ("relation", "field"),
    [("coverage", "coverage_id"), ("coverage", "observed_units"), ("repository_week", "value")],
)
def test_rejects_inferred_null_type_for_required_fields(
    tmp_path: Path, relation: str, field: str
) -> None:
    table = pa.table({**RELATION_COLUMNS[relation], field: [None]})

    with pytest.raises(ManifestError, match=f"relation {relation} field {field}.*type"):
        _validate_table(tmp_path, relation, table)


def test_rejects_null_values_in_required_large_string_field(tmp_path: Path) -> None:
    table = _large_string_table("coverage")
    table = table.set_column(0, "coverage_id", pa.array([None], type=pa.large_string()))

    with pytest.raises(ManifestError, match="coverage field coverage_id must not contain nulls"):
        _validate_table(tmp_path, "coverage", table)


@pytest.mark.parametrize(
    ("relation", "field", "array"),
    [
        ("coverage", "observed_units", pa.array([1], type=pa.int32())),
        ("coverage", "observed_units", pa.array([1], type=pa.uint64())),
        ("coverage", "observed_units", pa.array([1.0], type=pa.float64())),
        ("coverage", "expected_units", pa.array([None], type=pa.int32())),
        ("coverage", "expected_units", pa.array([None], type=pa.large_string())),
        ("repository_week", "value", pa.array([3.0], type=pa.float32())),
        ("repository_week", "value", pa.array([3], type=pa.int64())),
        ("pr_episode", "ready_at", pa.array([None], type=pa.binary())),
    ],
)
def test_rejects_other_physical_types_even_when_optional_values_are_null(
    tmp_path: Path, relation: str, field: str, array: Any
) -> None:
    table = pa.table(RELATION_COLUMNS[relation])
    table = table.set_column(table.schema.get_field_index(field), field, array)

    with pytest.raises(ManifestError, match=f"relation {relation} field {field}.*type"):
        _validate_table(tmp_path, relation, table)


@pytest.mark.parametrize(
    ("relation", "field", "value", "message"),
    [
        ("coverage", "observed_units", -1, "non-negative counts"),
        ("coverage", "expected_units", -1, "non-negative counts"),
        ("repository_week", "value", float("nan"), "finite numbers"),
        ("repository_week", "value", float("inf"), "finite numbers"),
        ("repository_week", "value", float("-inf"), "finite numbers"),
        ("coverage", "window_start", "2025-01-06T00:00:00+00:00", "canonical UTC"),
        ("pr_episode", "ready_at", "2025-02-30T00:00:00Z", "canonical UTC"),
        ("ci_attempt", "completed_at", "invented-invalid-time", "canonical UTC"),
    ],
)
def test_large_string_compatibility_preserves_value_checks(
    tmp_path: Path, relation: str, field: str, value: object, message: str
) -> None:
    table = _large_string_table(relation)
    index = table.schema.get_field_index(field)
    table = table.set_column(index, field, pa.array([value], type=table.schema.field(field).type))

    with pytest.raises(
        ManifestError, match=f"relation {relation} field {field}.*{message}"
    ) as error:
        _validate_table(tmp_path, relation, table)

    assert str(tmp_path) not in str(error.value)
    assert "invented-invalid-time" not in str(error.value)


@pytest.mark.parametrize("defect", ["missing", "extra", "reordered"])
def test_large_string_compatibility_preserves_exact_columns(tmp_path: Path, defect: str) -> None:
    table = _large_string_table("coverage")
    if defect == "missing":
        table = table.drop(["status"])
    elif defect == "extra":
        table = table.append_column("invented_extra", pa.array(["extra"], type=pa.large_string()))
    else:
        table = table.select(["status", "capability_code", "coverage_id", *table.column_names[3:]])

    with pytest.raises(ManifestError, match="relation coverage columns differ"):
        _validate_table(tmp_path, "coverage", table)
