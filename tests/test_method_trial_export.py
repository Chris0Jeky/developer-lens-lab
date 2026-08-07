# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownLambdaType=false

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

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
    assert provenance["product_commit"] == "3ac919f6129374acae564883ef9196c1d4aaf54c"
    assert provenance["files"] == [
        {
            "name": "schema.json",
            "sha256": "sha256:86cf53a48660967c07329f02be01c05d773c16ac96c28ddcd8110aed3b827fdc",
            "size_bytes": len(schema),
        }
    ]
