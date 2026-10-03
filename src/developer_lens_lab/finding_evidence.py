"""Consistency checks for stored WB-C1 evidence; never execute a method or holdout."""

from __future__ import annotations

import math
import re
from typing import Any, cast

from developer_lens_lab.contracts import ArtifactRef, EvaluationBundle

_REASONS = (
    "PRIMARY_DOMAIN_METRICS_PRESENT",
    "BASELINE_SELECTION_VIABLE",
    "CANDIDATE_SELECTION_VIABLE",
    "CANDIDATE_DETECTION_FLOOR",
    "CANDIDATE_DELAY_BUDGET",
    "CANDIDATE_FALSE_ALERT_IMPROVEMENT",
    "CANDIDATE_NOT_WORSE_DETECTION",
    "CANDIDATE_CONFOUND_GUARD",
)
_DOMAINS = {
    "detection_rate": "detection",
    "false_alerts_per_year": "primary",
    "median_detection_delay_weeks": "detection",
    "coverage_confound_false_alert_rate": "coverage",
}


def validate_decision_evidence(bundle: EvaluationBundle, view: dict[str, Any] | None) -> None:
    """Check the recorded source verdict, not the weaker public projection gates.

    The caller validates and links a supplied view first. Without one, only a
    rejection fully explained by measured bundle rules can be carried. Missing
    selection evidence cannot establish a positive decision or a failed selection.
    """

    def measured(side: str, code: str) -> float | None:
        if view is not None:
            item = view["scorecard"][side][code]
            return float(item["value"]) if item["status"] == "measured" else None
        result = bundle.baseline_results if side == "baseline" else bundle.candidate_results
        for item in result.metrics:
            if item.metric_code == code and item.domain_code == _DOMAINS[code]:
                return item.value if item.state == "present" else None
        return None

    baseline_detection = measured("baseline", "detection_rate")
    detection = measured("candidate", "detection_rate")
    delay = measured("candidate", "median_detection_delay_weeks")
    baseline_alerts = measured("baseline", "false_alerts_per_year")
    alerts = measured("candidate", "false_alerts_per_year")
    baseline_confound = measured("baseline", "coverage_confound_false_alert_rate")
    confound = measured("candidate", "coverage_confound_false_alert_rate")
    selection: dict[str, Any] = {} if view is None else view["scorecard"]["threshold_selection"]
    outcomes: tuple[bool | None, ...] = (
        baseline_detection is not None and detection is not None,
        None if view is None else bool(selection["baseline"]["viable"]),
        None if view is None else bool(selection["candidate"]["viable"]),
        None if detection is None else detection >= 0.75,
        None if delay is None else delay <= 8,
        None
        if alerts is None or baseline_alerts is None
        else baseline_alerts > 0.0 and alerts <= baseline_alerts * 0.8,
        None
        if detection is None or baseline_detection is None
        else detection >= baseline_detection,
        None if confound is None or baseline_confound is None else confound <= baseline_confound,
    )
    reasons = tuple(bundle.decision.reason_codes)
    if bundle.decision.outcome == "benchmarked":
        if not all(outcome is True for outcome in outcomes) or reasons != (
            "ALL_PREREGISTERED_GATES_PASSED",
        ):
            raise ValueError("stored benchmarked decision lacks complete passing gate evidence")
        return
    if bundle.decision.outcome != "reject":
        raise ValueError("no WB-C1 revision-decision evidence recipe is registered")
    failed = tuple(
        code for code, outcome in zip(_REASONS, outcomes, strict=True) if outcome is False
    )
    if not failed or reasons != failed:
        raise ValueError("stored rejection reasons are unsupported or contradict gate evidence")


def validate_view_lineage(
    bundle: EvaluationBundle,
    reproduction: dict[str, Any],
    research_commit: str,
    custody: ArtifactRef | None = None,
) -> None:
    """Match the view receipt to a bundle-owned JSON reference and optional manifest ref."""
    if reproduction["product_research_pack_commit"] != research_commit:
        raise ValueError("stored view declares a different ResearchPack producer")
    digest = reproduction["digests"]["custody"]
    reference = next((ref for ref in bundle.artifact_manifest if ref.sha256 == digest), None)
    if (
        reference is None
        or reference.media_type != "application/json"
        or (custody is not None and custody != reference)
    ):
        raise ValueError("stored view custody differs from its recorded bundle receipt")


def validate_custody_record(
    bundle: EvaluationBundle, manifest: dict[str, Any], receipt: dict[str, Any]
) -> None:
    """Check the existing receipt only. Reading it does not open its held-out data."""
    expected = {
        "event": "final_holdout_custody",
        "run_id": bundle.run_manifest.run_id,
        "generator_revision": bundle.dataset_card.generator_revision,
        "dataset_sha256": manifest.get("dataset_sha256"),
        "baseline_parameters_sha256": bundle.baseline_model_card.parameter_sha256,
        "candidate_parameters_sha256": bundle.candidate_model_card.parameter_sha256,
    }
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError("stored custody receipt is not bound to the recorded run")
    for key in ("dataset_sha256", "evaluation_plan_sha256"):
        value = receipt.get(key)
        if not isinstance(value, str) or re.fullmatch(r"sha256:[0-9a-f]{64}", value) is None:
            raise ValueError("stored custody receipt lacks an immutable evidence digest")
    for key in ("baseline_threshold", "candidate_threshold"):
        value = receipt.get(key)
        threshold = cast(int | float, value)
        if type(value) not in (int, float) or not math.isfinite(threshold) or threshold < 0:
            raise ValueError("stored custody receipt contains an invalid selected threshold")
