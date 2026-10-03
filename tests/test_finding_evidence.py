from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from developer_lens_lab.artifacts import canonical_json_bytes
from developer_lens_lab.contracts import ArtifactRef, EvaluationBundle
from developer_lens_lab.finding_evidence import (
    validate_custody_record,
    validate_decision_evidence,
    validate_view_lineage,
)

from .factories import evaluation_bundle

ROOT = Path(__file__).resolve().parents[1]


def evidence() -> tuple[EvaluationBundle, dict[str, Any], ArtifactRef, dict[str, Any]]:
    view = json.loads(
        (ROOT / "release-assets/v0.1.0/method-trial-v1/method-trial-view.v1.json").read_bytes()
    )
    raw = evaluation_bundle()
    raw["preregistration"]["primary_metric_code"] = "false_alerts_per_year"
    raw["dataset_card"]["generator_revision"] = "wbc1.generator.v1"
    for side in ("baseline", "candidate"):
        raw[f"{side}_results"]["metrics"] = [
            {
                "domain_code": domain,
                "metric_code": code,
                "state": "present",
                "value": view["scorecard"][side][code]["value"],
                "reason_code": None,
            }
            for code, domain in (
                ("false_alerts_per_year", "primary"),
                ("detection_rate", "detection"),
            )
        ]
    raw["decision"] = {
        "outcome": "reject",
        "acceptance_gate_passed": False,
        "reason_codes": view["decision"]["reason_codes"],
    }
    receipt = {
        "event": "final_holdout_custody",
        "run_id": raw["run_manifest"]["run_id"],
        "generator_revision": raw["dataset_card"]["generator_revision"],
        "dataset_sha256": "sha256:" + "d" * 64,
        "evaluation_plan_sha256": "sha256:" + "e" * 64,
        "baseline_threshold": 2.0,
        "candidate_threshold": 0.5,
        "baseline_parameters_sha256": raw["baseline_model_card"]["parameter_sha256"],
        "candidate_parameters_sha256": raw["candidate_model_card"]["parameter_sha256"],
    }
    payload = canonical_json_bytes(receipt)
    ref = ArtifactRef(
        sha256="sha256:" + hashlib.sha256(payload).hexdigest(),
        size_bytes=len(payload),
        media_type="application/json",
    )
    raw["artifact_manifest"].append(ref.model_dump(mode="json"))
    view["reproducibility"]["digests"]["custody"] = ref.sha256
    return EvaluationBundle.model_validate_json(json.dumps(raw)), view, ref, receipt


def change_decision(bundle: EvaluationBundle, outcome: str, reasons: list[str]) -> EvaluationBundle:
    raw = bundle.model_dump(mode="json")
    raw["decision"] = {
        "outcome": outcome,
        "acceptance_gate_passed": outcome == "benchmarked",
        "reason_codes": reasons,
    }
    return EvaluationBundle.model_validate_json(json.dumps(raw))


def test_frozen_view_rejection_has_supported_reasons() -> None:
    bundle, view, _, _ = evidence()
    validate_decision_evidence(bundle, view)


@pytest.mark.parametrize("outcome", ["benchmarked", "revise_once"])
def test_losing_bundle_cannot_gain_a_positive_or_revision_decision(outcome: str) -> None:
    bundle, _, _, _ = evidence()
    changed = change_decision(bundle, outcome, ["ALL_PREREGISTERED_GATES_PASSED"])
    with pytest.raises(ValueError):
        validate_decision_evidence(changed, None)


def test_bundle_only_rejection_uses_only_supported_recorded_reasons() -> None:
    bundle, _, _, _ = evidence()
    changed = change_decision(bundle, "reject", ["CANDIDATE_FALSE_ALERT_IMPROVEMENT"])
    validate_decision_evidence(changed, None)


@pytest.mark.parametrize(
    "reasons",
    [
        ["BASELINE_SELECTION_VIABLE"],
        ["CANDIDATE_DETECTION_FLOOR"],
        ["UNKNOWN_GATE"],
        ["ALL_PREREGISTERED_GATES_PASSED"],
        ["CANDIDATE_FALSE_ALERT_IMPROVEMENT", "CANDIDATE_FALSE_ALERT_IMPROVEMENT"],
    ],
)
def test_bundle_only_rejection_refuses_unmeasured_or_false_reasons(reasons: list[str]) -> None:
    bundle, _, _, _ = evidence()
    with pytest.raises(ValueError):
        validate_decision_evidence(change_decision(bundle, "reject", reasons), None)


def test_source_rule_keeps_preregistered_twenty_percent_threshold() -> None:
    bundle, _, _, _ = evidence()
    raw = bundle.model_dump(mode="json")
    raw["candidate_results"]["metrics"][0]["value"] = 2.9
    changed = EvaluationBundle.model_validate_json(json.dumps(raw))
    changed = change_decision(changed, "reject", ["CANDIDATE_FALSE_ALERT_IMPROVEMENT"])
    validate_decision_evidence(changed, None)


def test_benchmarked_requires_all_gate_evidence_not_just_better_bundle_metrics() -> None:
    bundle, _, _, _ = evidence()
    raw = bundle.model_dump(mode="json")
    raw["candidate_results"]["metrics"][0]["value"] = 0.1
    changed = EvaluationBundle.model_validate_json(json.dumps(raw))
    changed = change_decision(changed, "benchmarked", ["ALL_PREREGISTERED_GATES_PASSED"])
    with pytest.raises(ValueError):
        validate_decision_evidence(changed, None)


def test_supported_benchmarked_helper_has_no_failed_or_missing_gates() -> None:
    bundle, view, _, _ = evidence()
    view["scorecard"]["baseline"]["false_alerts_per_year"]["value"] = 3.0
    view["scorecard"]["candidate"]["false_alerts_per_year"]["value"] = 1.0
    for side in ("baseline", "candidate"):
        view["scorecard"]["threshold_selection"][side]["viable"] = True
    changed = change_decision(bundle, "benchmarked", ["ALL_PREREGISTERED_GATES_PASSED"])
    validate_decision_evidence(changed, view)


@pytest.mark.parametrize("field", ["product_research_pack_commit", "custody"])
def test_view_lineage_refuses_altered_producer_or_custody(field: str) -> None:
    bundle, view, ref, _ = evidence()
    reproduction = copy.deepcopy(view["reproducibility"])
    commit = reproduction["product_research_pack_commit"]
    if field == "custody":
        reproduction["digests"]["custody"] = "sha256:" + "f" * 64
    else:
        reproduction[field] = "f" * 40
    with pytest.raises(ValueError):
        validate_view_lineage(bundle, reproduction, commit, ref)


def test_view_lineage_accepts_only_a_bundle_owned_json_receipt() -> None:
    bundle, view, ref, _ = evidence()
    reproduction = view["reproducibility"]
    validate_view_lineage(bundle, reproduction, reproduction["product_research_pack_commit"], ref)
    changed = ref.model_copy(update={"size_bytes": ref.size_bytes + 1})
    with pytest.raises(ValueError):
        validate_view_lineage(
            bundle, reproduction, reproduction["product_research_pack_commit"], changed
        )


@pytest.mark.parametrize(
    "field",
    [
        "event",
        "run_id",
        "generator_revision",
        "dataset_sha256",
        "baseline_parameters_sha256",
        "candidate_parameters_sha256",
    ],
)
def test_custody_record_is_bound_to_the_run(field: str) -> None:
    bundle, _, _, receipt = evidence()
    manifest = {"run_id": bundle.run_manifest.run_id, "dataset_sha256": receipt["dataset_sha256"]}
    receipt[field] = "other"
    with pytest.raises(ValueError):
        validate_custody_record(bundle, manifest, receipt)


def test_custody_record_accepts_original_receipt() -> None:
    bundle, _, _, receipt = evidence()
    validate_custody_record(bundle, {"dataset_sha256": receipt["dataset_sha256"]}, receipt)
