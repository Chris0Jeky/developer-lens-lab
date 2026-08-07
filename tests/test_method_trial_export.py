# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownLambdaType=false

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from developer_lens_lab.contracts.method_trial_view import (
    MethodTrialViewError,
    validate_method_trial_view,
)
from developer_lens_lab.wbc1.export import export_method_trial
from developer_lens_lab.wbc1.runner import run_benchmark

ROOT = Path(__file__).resolve().parents[1]


def _permit_test_tree(monkeypatch) -> None:
    monkeypatch.setattr(
        "developer_lens_lab.wbc1.runner._ensure_reproducible_tree", lambda _root: None
    )
    monkeypatch.setattr("developer_lens_lab.wbc1.runner._git_commit", lambda _root: "a" * 40)


def test_method_trial_export_is_deterministic_and_schema_valid(tmp_path: Path, monkeypatch) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="method_trial_export")
    first = export_method_trial(
        result.run_id, root=ROOT, artifact_root=tmp_path, output=tmp_path / "view.json"
    )
    second = export_method_trial(
        result.run_id, root=ROOT, artifact_root=tmp_path, output=tmp_path / "view-2.json"
    )
    assert first.payload == second.payload
    assert first.sha256 == "sha256:" + hashlib.sha256(first.payload).hexdigest()
    payload = json.loads(first.payload)
    schema = json.loads(
        (ROOT / "vendor/developer-lens/method-trial-view/v1/schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(payload)
    assert payload["scorecard"]["baseline"]["false_alerts_per_year"]["value"] == 2.966666666666667
    assert payload["scorecard"]["candidate"]["false_alerts_per_year"]["value"] == 4.2
    assert payload["scorecard"]["candidate"]["calibration_brier"]["value"] == 0.017341137335170863
    assert payload["decision"]["outcome"] == "reject"
    assert [gate["outcome"] for gate in payload["acceptance_gates"]] == [
        "fail",
        "fail",
        "pass",
        "pass",
        "fail",
        "pass",
        "pass",
    ]
    assert payload["representative_selection"]["version"] == "wbc1-final-holdout-v1"
    assert [case["role"] for case in payload["representative_cases"]] == [
        "no_change_control",
        "planted_change",
        "instrumentation_confound",
    ]
    assert [case["scenario_code"] for case in payload["representative_cases"]] == [
        "no_change",
        "level",
        "parser_shift",
    ]
    assert all(52 <= len(case["points"]) <= 104 for case in payload["representative_cases"])
    assert all(
        "threshold" in point["baseline"] and "threshold" in point["candidate"]
        for case in payload["representative_cases"]
        for point in case["points"]
    )
    assert [
        point["planted_marker"]
        for point in payload["representative_cases"][1]["points"]
        if point["planted_marker"] != "none"
    ] == ["level"]
    assert [
        point["confound_marker"]
        for point in payload["representative_cases"][2]["points"]
        if point["confound_marker"] != "none"
    ] == ["parser_shift"]
    flattened = json.dumps(payload, sort_keys=True)
    assert all(value not in flattened for value in ("http://", "https://", "@", "C:\\"))


def test_method_trial_vendor_snapshot_is_pinned() -> None:
    root = ROOT / "vendor/developer-lens/method-trial-view/v1"
    provenance = json.loads((root / "provenance.json").read_text(encoding="utf-8"))
    schema = (root / "schema.json").read_bytes()
    assert provenance["product_commit"] == "b48fea579936671397a0486ae7a0342197ee6e4b"
    assert provenance["files"] == [
        {
            "name": "schema.json",
            "sha256": "sha256:634b0cc7a0c3dbcefe8b9cf258e157695beae06d08cc9d02bb781a4267f633ef",
            "size_bytes": len(schema),
        }
    ]


def test_method_trial_semantics_reject_structural_only_mutations(
    tmp_path: Path, monkeypatch
) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="method_trial_semantics")
    payload = json.loads(
        export_method_trial(result.run_id, root=ROOT, artifact_root=tmp_path).payload
    )
    schema = json.loads(
        (ROOT / "vendor/developer-lens/method-trial-view/v1/schema.json").read_text(
            encoding="utf-8"
        )
    )
    validator = Draft202012Validator(schema)

    mismatched_command = deepcopy(payload)
    mismatched_command["reproducibility"]["commands"]["export"] = (
        "uv run dllab export method-trial wbc1_other"
    )

    mismatched_gate = deepcopy(payload)
    mismatched_gate["acceptance_gates"][5]["outcome"] = "fail"

    mismatched_relevant_value = deepcopy(payload)
    mismatched_relevant_value["acceptance_gates"][4]["relevant_values"]["candidate"] = {
        "status": "measured",
        "value": 1,
    }

    mismatched_decision = deepcopy(payload)
    mismatched_decision["decision"]["reason_codes"] = ["CANDIDATE_FALSE_ALERT_IMPROVEMENT"]

    unavailable_viable_threshold = deepcopy(payload)
    unavailable_viable_threshold["scorecard"]["threshold_selection"]["candidate"]["viable"] = True
    unavailable_viable_threshold["scorecard"]["threshold_selection"]["candidate"][
        "selected_value"
    ] = {"status": "unavailable", "reason": "not_measured"}

    mismatched_week = deepcopy(payload)
    mismatched_week["representative_cases"][0]["points"][0]["relative_week_label"] = "week-001"

    nonsequential_week = deepcopy(payload)
    nonsequential_week["representative_cases"][0]["points"][1]["relative_week_index"] = 2

    marked_control = deepcopy(payload)
    marked_control["representative_cases"][0]["points"][0]["planted_marker"] = "level"

    simultaneous_markers = deepcopy(payload)
    planted_point = next(
        point
        for point in simultaneous_markers["representative_cases"][1]["points"]
        if point["planted_marker"] != "none"
    )
    planted_point["confound_marker"] = "parser_shift"

    missing_planted_marker = deepcopy(payload)
    for point in missing_planted_marker["representative_cases"][1]["points"]:
        point["planted_marker"] = "none"

    missing_confound_marker = deepcopy(payload)
    for point in missing_confound_marker["representative_cases"][2]["points"]:
        point["confound_marker"] = "none"

    for mutated in (
        mismatched_command,
        mismatched_gate,
        mismatched_relevant_value,
        mismatched_decision,
        unavailable_viable_threshold,
        mismatched_week,
        nonsequential_week,
        marked_control,
        simultaneous_markers,
        missing_planted_marker,
        missing_confound_marker,
    ):
        validator.validate(mutated)
        with pytest.raises(MethodTrialViewError, match="semantic validation failed"):
            validate_method_trial_view(mutated, root=ROOT)


def test_method_trial_export_uses_recorded_provenance_and_fails_closed_on_drift(
    tmp_path: Path, monkeypatch
) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="method_trial_provenance")
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    view = json.loads(export_method_trial(result.run_id, root=ROOT, artifact_root=tmp_path).payload)
    assert (
        view["reproducibility"]["product_contract_commit"]
        == manifest["provenance"]["method_trial_view"]["product_commit"]
    )
    path = ROOT / "vendor/developer-lens/method-trial-view/v1/provenance.json"
    original = path.read_bytes()
    altered = json.loads(original)
    altered["product_commit"] = "f" * 40
    path.write_text(json.dumps(altered, indent=2) + "\n", encoding="utf-8")
    try:
        with pytest.raises(ValueError, match="MethodTrialView provenance differs"):
            export_method_trial(result.run_id, root=ROOT, artifact_root=tmp_path)
    finally:
        path.write_bytes(original)
