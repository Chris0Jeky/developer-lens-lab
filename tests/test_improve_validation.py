# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.contracts import ResearchPack
from developer_lens_lab.validation import (
    ManifestError,
    assert_path_free_manifest,
    validate_evaluation_bundle,
    validate_pack_artifacts,
    validate_research_pack,
)

from .factories import evaluation_bundle, research_pack

SCOPE = "run_scope"


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
    raw["relations"]["coverage"] = {
        "state": "present",
        "schema_id": "developer-lens.coverage.v1",
        "row_count": row_count,
        "artifact": reference,
        "reason_code": None,
    }
    return ResearchPack.model_validate_json(json.dumps(raw))


def test_rejects_non_c0_research_pack(tmp_path: Path) -> None:
    # Mutants M7 (drop the C0 gate) and M8 (flip `!=` to `==`): a C1 pack
    # must be refused by the bootstrap validator.
    raw = research_pack(classification="C1", generated_at="2026-08-03T00:00:00Z")
    manifest = tmp_path / "pack.json"
    manifest.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ManifestError, match="C0"):
        validate_research_pack(manifest)


def test_research_pack_validation_screens_forbidden_keys_first(tmp_path: Path) -> None:
    # Mutant M9: drop the assert_path_free_manifest call in validate_research_pack
    # (the contract would raise ValidationError instead of ManifestError).
    raw = research_pack()
    raw["environment_name"] = "plain text"
    manifest = tmp_path / "pack.json"
    manifest.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ManifestError, match="forbidden manifest key"):
        validate_research_pack(manifest)


def test_evaluation_bundle_validation_screens_forbidden_keys_first(tmp_path: Path) -> None:
    # Mutant M10: drop the assert_path_free_manifest call in
    # validate_evaluation_bundle.
    raw = evaluation_bundle()
    raw["environment_name"] = "plain text"
    manifest = tmp_path / "bundle.json"
    manifest.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ManifestError, match="forbidden manifest key"):
        validate_evaluation_bundle(manifest)


def test_rejects_exact_forbidden_manifest_key() -> None:
    # Mutant M11: drop the FORBIDDEN_EXACT_KEYS disjunct ("environment_name"
    # contains no forbidden fragment, so only the exact set catches it).
    with pytest.raises(ManifestError, match="forbidden manifest key"):
        assert_path_free_manifest({"environment_name": "plain text"})


def test_rejects_forbidden_key_fragment_substring() -> None:
    # Mutant M12: compare fragments with `==` instead of `in`.
    with pytest.raises(ManifestError, match="forbidden manifest key"):
        assert_path_free_manifest({"job_command": "plain text"})


def test_forbidden_key_match_is_case_insensitive() -> None:
    # Mutant M13: match against the raw key instead of its casefold.
    with pytest.raises(ManifestError, match="forbidden manifest key"):
        assert_path_free_manifest({"COMMAND_LOG": "plain text"})


def test_rejects_non_string_manifest_key() -> None:
    # Mutant M14: drop the non-string-key guard.
    with pytest.raises(ManifestError, match="keys must be strings"):
        assert_path_free_manifest({1: "plain text"})


def test_rejects_file_url_manifest_value() -> None:
    # Mutant M15: drop the `file://` alternative from ABSOLUTE_PATH_RE.
    with pytest.raises(ManifestError, match="local path"):
        assert_path_free_manifest({"note": "file://server/share"})


def test_reads_artifacts_from_explicit_scope(tmp_path: Path) -> None:
    # Mutant M16: ignore the explicit scope and always read pack.pack_id.
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _coverage_parquet_bytes(_valid_coverage_columns())
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 1)
    assert pack.pack_id != SCOPE
    validate_pack_artifacts(pack, store, SCOPE)


def test_rejects_extra_parquet_rows(tmp_path: Path) -> None:
    # Mutant M17: weaken `num_rows != row_count` to `num_rows < row_count`,
    # which lets a two-row file pass a one-row descriptor.
    columns = _valid_coverage_columns()
    doubled = {name: values * 2 for name, values in columns.items()}
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _coverage_parquet_bytes(doubled)
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 1)
    with pytest.raises(ManifestError, match="row_count"):
        validate_pack_artifacts(pack, store, SCOPE)


def test_accepts_zero_counts(tmp_path: Path) -> None:
    # Mutant M18: tighten `value < 0` to `value <= 0`, rejecting zero counts.
    columns = _valid_coverage_columns()
    columns["observed_units"] = [0]
    columns["expected_units"] = [0]
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _coverage_parquet_bytes(columns)
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 1)
    validate_pack_artifacts(pack, store, SCOPE)


def test_rejects_reordered_columns(tmp_path: Path) -> None:
    # Mutant M19: compare columns as an order-insensitive set. The swapped
    # pair shares one Arrow type, so only the order check can catch it.
    columns = _valid_coverage_columns()
    reordered = {
        "coverage_id": columns["coverage_id"],
        "status": columns["status"],
        "capability_code": columns["capability_code"],
        "observed_units": columns["observed_units"],
        "expected_units": columns["expected_units"],
        "window_start": columns["window_start"],
        "window_end": columns["window_end"],
    }
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _coverage_parquet_bytes(reordered)
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 1)
    with pytest.raises(ManifestError, match="columns differ"):
        validate_pack_artifacts(pack, store, SCOPE)


def test_rejects_non_parquet_media_type(tmp_path: Path) -> None:
    # Mutant M20: drop the media_type guard (the contract blocks this input,
    # so the pack is forged with model_copy, bypassing contract validation).
    store = ArtifactStore(tmp_path / ".dllab")
    payload = _coverage_parquet_bytes(_valid_coverage_columns())
    reference = store.put_bytes(SCOPE, payload, "application/x-parquet")
    pack = _pack_with_coverage(reference.model_dump(mode="json"), 1)
    forged_artifact = reference.model_copy(update={"media_type": "application/json"})
    forged_coverage = pack.relations.coverage.model_copy(update={"artifact": forged_artifact})
    forged_relations = pack.relations.model_copy(update={"coverage": forged_coverage})
    forged = pack.model_copy(update={"relations": forged_relations})
    with pytest.raises(ManifestError, match="must use Parquet"):
        validate_pack_artifacts(forged, store, SCOPE)
