# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

METHOD_TRIAL_SCHEMA_VERSION = "DeveloperLensMethodTrialView.v1"
METHOD_TRIAL_VENDOR_ROOT = Path("vendor/developer-lens/method-trial-view/v1")


class MethodTrialViewError(ValueError):
    """Raised when a MethodTrialView does not satisfy the pinned product schema."""


_GATE_CODES = (
    "baseline_selection",
    "candidate_selection",
    "detection_floor",
    "delay_budget",
    "false_alert_improvement",
    "not_worse_detection",
    "confound_guard",
)
_GATE_REASONS = (
    "BASELINE_SELECTION_VIABLE",
    "CANDIDATE_SELECTION_VIABLE",
    "CANDIDATE_DETECTION_FLOOR",
    "CANDIDATE_DELAY_BUDGET",
    "CANDIDATE_FALSE_ALERT_IMPROVEMENT",
    "CANDIDATE_NOT_WORSE_DETECTION",
    "CANDIDATE_CONFOUND_GUARD",
)
_CASE_IDENTITIES = (
    ("no_change_control", "no_change", "fixed_first_window"),
    ("planted_change", "level", "fixed_change_window"),
    ("instrumentation_confound", "parser_shift", "fixed_confound_window"),
)


def _mapping(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value)


def _sequence(value: object) -> list[Any]:
    return cast(list[Any], value)


def _semantic_error(code: str) -> None:
    raise MethodTrialViewError(f"MethodTrialView semantic validation failed: {code}")


def _measurement_value(value: object) -> float | None:
    measurement = _mapping(value)
    return float(measurement["value"]) if measurement["status"] == "measured" else None


def _validate_method_trial_view_semantics(value: dict[str, Any]) -> None:
    dataset = _mapping(value["dataset"])
    if (
        dataset["system_count"] != 54
        or dataset["weekly_opportunity_count"] != 5616
        or dataset["observed_count"] != 5346
        or dataset["absent_count"] != 270
        or dataset["observed_count"] + dataset["absent_count"]
        != dataset["weekly_opportunity_count"]
    ):
        _semantic_error("DATASET_COUNTS")

    methods = _mapping(value["methods"])
    expected_methods = {
        "baseline": ("baseline", "rolling_median_mad"),
        "candidate": ("candidate", "bocpd_gaussian"),
        "offline_pelt": ("offline_descriptive", "pelt"),
    }
    for key, (role, method_code) in expected_methods.items():
        method = _mapping(methods[key])
        if (
            method["role"] != role
            or method["method_code"] != method_code
            or method["deterministic"] is not True
        ):
            _semantic_error("METHOD_IDENTITY")

    scorecard = _mapping(value["scorecard"])
    selections = _mapping(scorecard["threshold_selection"])
    for key in ("baseline", "candidate"):
        selection = _mapping(selections[key])
        selected_value = _mapping(selection["selected_value"])
        if selection["viable"] is True and selected_value["status"] != "measured":
            _semantic_error("THRESHOLD_VIABILITY")
        if selection["viable"] is False and selection["reason_code"] == "selected":
            _semantic_error("THRESHOLD_REASON")

    reproducibility = _mapping(value["reproducibility"])
    run_id = str(reproducibility["run_id"])
    expected_commands = {
        "benchmark": f"uv run dllab benchmark wb-c1 --smoke --run-id {run_id}",
        "reproduce": f"uv run dllab run reproduce {run_id}",
        "export": f"uv run dllab export method-trial {run_id}",
        "report": f"uv run dllab report build {run_id}",
    }
    if _mapping(reproducibility["commands"]) != expected_commands:
        _semantic_error("COMMAND_RUN_ID")

    representative_cases = _sequence(value["representative_cases"])
    for case_index, case_value in enumerate(representative_cases):
        case = _mapping(case_value)
        role, scenario_code, selection_code = _CASE_IDENTITIES[case_index]
        selection_rule = _mapping(case["selection_rule"])
        if (
            case["order"] != case_index + 1
            or case["role"] != role
            or case["scenario_code"] != scenario_code
            or selection_rule["code"] != selection_code
        ):
            _semantic_error("CASE_IDENTITY")
        planted = False
        confounded = False
        for point_index, point_value in enumerate(_sequence(case["points"])):
            point = _mapping(point_value)
            if (
                point["relative_week_index"] != point_index
                or point["relative_week_label"] != f"week-{point_index:03d}"
            ):
                _semantic_error("TIMELINE_SEQUENCE")
            planted_marker = point["planted_marker"]
            confound_marker = point["confound_marker"]
            if planted_marker != "none" and confound_marker != "none":
                _semantic_error("POINT_MARKER_EXCLUSIVITY")
            planted = planted or planted_marker != "none"
            confounded = confounded or confound_marker != "none"
            observed = _mapping(point["observed"])
            if observed["state"] == "missing":
                baseline_point = _mapping(point["baseline"])
                candidate_point = _mapping(point["candidate"])
                if (
                    baseline_point["alert"] is True
                    or candidate_point["alert"] is True
                    or _mapping(baseline_point["score"])["status"] == "measured"
                    or _mapping(candidate_point["probability"])["status"] == "measured"
                ):
                    _semantic_error("MISSING_POINT_EVIDENCE")
        if role == "no_change_control" and (planted or confounded):
            _semantic_error("CONTROL_MARKERS")
        if role == "planted_change" and not planted:
            _semantic_error("PLANTED_MARKER_REQUIRED")
        if role == "instrumentation_confound" and not confounded:
            _semantic_error("CONFOUND_MARKER_REQUIRED")

    gates = _sequence(value["acceptance_gates"])
    expected_outcomes = [
        "pass" if _mapping(selections["baseline"])["viable"] is True else "fail",
        "pass" if _mapping(selections["candidate"])["viable"] is True else "fail",
    ]
    baseline = _mapping(scorecard["baseline"])
    candidate = _mapping(scorecard["candidate"])
    metric_pairs = (
        ("detection_rate", False),
        ("median_detection_delay_weeks", False),
        ("false_alerts_per_year", True),
        ("detection_rate", True),
        ("coverage_confound_false_alert_rate", True),
    )
    for metric_index, (metric_name, requires_baseline) in enumerate(metric_pairs):
        baseline_measurement = _mapping(baseline[metric_name])
        candidate_measurement = _mapping(candidate[metric_name])
        baseline_value = _measurement_value(baseline_measurement)
        candidate_value = _measurement_value(candidate_measurement)
        if candidate_value is None or (requires_baseline and baseline_value is None):
            outcome = "not_applicable"
        elif metric_index == 0:
            outcome = "pass" if candidate_value >= 0.75 else "fail"
        elif metric_index == 1:
            outcome = "pass" if candidate_value <= 8 else "fail"
        elif metric_index == 2:
            outcome = "pass" if candidate_value <= cast(float, baseline_value) * 0.8 else "fail"
        elif metric_index == 3:
            outcome = "pass" if candidate_value >= cast(float, baseline_value) else "fail"
        else:
            outcome = "pass" if candidate_value <= cast(float, baseline_value) else "fail"
        expected_outcomes.append(outcome)
        gate = _mapping(gates[metric_index + 2])
        relevant_values = _mapping(gate.get("relevant_values"))
        if (
            relevant_values.get("baseline") != baseline_measurement
            or relevant_values.get("candidate") != candidate_measurement
        ):
            _semantic_error("GATE_RELEVANT_VALUES")

    for index, gate_value in enumerate(gates):
        gate = _mapping(gate_value)
        if (
            gate["order"] != index + 1
            or gate["code"] != _GATE_CODES[index]
            or gate["reason_code"] != _GATE_REASONS[index]
            or gate["outcome"] != expected_outcomes[index]
        ):
            _semantic_error("GATE_DERIVATION")

    expected_reasons = [
        _GATE_REASONS[index] for index, outcome in enumerate(expected_outcomes) if outcome == "fail"
    ]
    decision = _mapping(value["decision"])
    if decision["reason_codes"] != expected_reasons:
        _semantic_error("DECISION_REASONS")


def method_trial_schema(root: Path) -> dict[str, Any]:
    path = root / METHOD_TRIAL_VENDOR_ROOT / "schema.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MethodTrialViewError(f"MethodTrialView schema is unavailable: {path.name}") from exc
    if not isinstance(value, dict):
        raise MethodTrialViewError("MethodTrialView schema must be an object")
    return cast(dict[str, Any], value)


def validate_method_trial_view(value: object, *, root: Path) -> dict[str, Any]:
    schema = method_trial_schema(root)
    try:
        Draft202012Validator(schema).validate(value)
    except Exception as exc:  # jsonschema exceptions vary by version
        raise MethodTrialViewError(str(exc)) from exc
    if not isinstance(value, dict) or value.get("schema_version") != METHOD_TRIAL_SCHEMA_VERSION:
        raise MethodTrialViewError("unsupported MethodTrialView schema version")
    validated = cast(dict[str, Any], value)
    _validate_method_trial_view_semantics(validated)
    return validated
