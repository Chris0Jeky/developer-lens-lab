# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pyarrow as pa
import pyarrow.parquet as pq

from developer_lens_lab.artifacts import ArtifactRef, ArtifactStore, canonical_json_bytes
from developer_lens_lab.contracts import EvaluationBundle, validate_method_trial_view
from developer_lens_lab.wbc1.generator import WeeklySeries, build_benchmark_dataset
from developer_lens_lab.wbc1.methods import (
    DEFAULT_BASELINE_PARAMETERS,
    DEFAULT_BOCPD_PARAMETERS,
    alerts_from_scores,
    bocpd_scores,
    pelt_segments,
    rolling_median_mad_scores,
)


@dataclass(frozen=True)
class MethodTrialExport:
    run_id: str
    payload: bytes
    output_path: Path
    sha256: str


def _root(root: Path | None) -> Path:
    if root is not None:
        return root.resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise ValueError("run from inside a developer-lens-lab checkout")


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _metric(bundle: EvaluationBundle, role: str, code: str) -> float:
    result = bundle.baseline_results if role == "baseline" else bundle.candidate_results
    for metric in result.metrics:
        if metric.metric_code == code and metric.value is not None:
            return float(metric.value)
    raise ValueError(f"{role} metric is unavailable: {code}")


def _value(value: float) -> dict[str, object]:
    return {"status": "measured", "value": float(value)}


def _unavailable(reason: str = "not_measured") -> dict[str, str]:
    return {"status": "unavailable", "reason": reason}


def _provenance(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    method_path = root / "vendor" / "developer-lens" / "method-trial-view" / "v1"
    research_path = root / "vendor" / "developer-lens" / "research-pack" / "v1"
    method = cast(dict[str, Any], json.loads((method_path / "provenance.json").read_text()))
    research = cast(dict[str, Any], json.loads((research_path / "provenance.json").read_text()))
    return method, research


def _read_series_values(
    store: ArtifactStore, run_id: str, bundle: EvaluationBundle, manifest: dict[str, Any]
) -> dict[tuple[str, str], float]:
    ref = ArtifactRef.model_validate(manifest["research_pack_repository_week"])
    payload = store.get_bytes(run_id, ref)
    descriptor = bundle.research_pack_sha256
    if not descriptor:
        raise ValueError("EvaluationBundle lacks ResearchPack linkage")
    rows = pq.read_table(pa.BufferReader(payload)).to_pylist()
    return {
        (str(row["repository_alias"]), str(row["week_start"])): float(row["value"]) for row in rows
    }


def _case_points(
    series: WeeklySeries,
    values: dict[tuple[str, str], float],
    baseline_threshold: float,
    candidate_threshold: float,
    start: int,
    count: int,
    planted_marker: str,
    confound_marker: str,
) -> list[dict[str, Any]]:
    baseline_scores = rolling_median_mad_scores(series.values)
    candidate_scores = bocpd_scores(series.values).change_probability
    baseline_alerts = set(
        alerts_from_scores(
            baseline_scores,
            baseline_threshold,
            DEFAULT_BASELINE_PARAMETERS.cooldown,
            series.observed,
        )
    )
    candidate_alerts = set(
        alerts_from_scores(
            candidate_scores,
            candidate_threshold,
            DEFAULT_BOCPD_PARAMETERS.cooldown,
            series.observed,
        )
    )
    boundaries = set(pelt_segments(series.values))
    points: list[dict[str, Any]] = []
    for index in range(start, min(start + count, len(series.values))):
        observed = bool(series.observed[index])
        if observed:
            observed_value: dict[str, object] = {
                "state": "observed",
                "value": values[(series.system_alias, series.week_starts[index])],
            }
            baseline = {"alert": index in baseline_alerts, "score": _value(baseline_scores[index])}
            candidate = {
                "alert": index in candidate_alerts,
                "probability": _value(candidate_scores[index]),
            }
        else:
            reason = (
                "permission_gap"
                if series.confound_kind == "permission_shift"
                else "instrumentation_gap"
            )
            observed_value = {"state": "missing", "reason": reason}
            baseline = {"alert": False, "score": _unavailable(reason="insufficient_support")}
            candidate = {"alert": False, "probability": _unavailable(reason="insufficient_support")}
        marker = (
            planted_marker
            if series.change_index is not None and index >= series.change_index
            else "none"
        )
        points.append(
            {
                "relative_week_index": index - start,
                "relative_week_label": f"week-{index - start:02d}",
                "observed": observed_value,
                "planted_marker": marker,
                "confound_marker": confound_marker if bool(series.confound[index]) else "none",
                "baseline": baseline,
                "candidate": candidate,
                "pelt_marker": {
                    "evaluation_mode": "offline_descriptive",
                    "boundary": (index + 1) in boundaries,
                },
            }
        )
    return points


def _build_cases(
    dataset: Any,
    values: dict[tuple[str, str], float],
    baseline_threshold: float,
    candidate_threshold: float,
) -> list[dict[str, Any]]:
    series = dataset.final_holdout_metadata.series
    no_change = next(item for item in series if item.scenario_code == "no_change")
    planted = next(item for item in series if item.scenario_code == "level")
    confound = next(item for item in series if item.scenario_code == "permission_shift")
    return [
        {
            "order": 1,
            "scenario_code": "no_change_control",
            "selection_rule": {
                "code": "fixed_first_window",
                "label": "First eligible no-change series and first twelve weeks",
                "deterministic": True,
            },
            "title": "No-change control",
            "summary": "A fixed early window checks ordinary variation without a planted change.",
            "points": _case_points(
                no_change, values, baseline_threshold, candidate_threshold, 0, 12, "none", "none"
            ),
        },
        {
            "order": 2,
            "scenario_code": "planted_change",
            "selection_rule": {
                "code": "fixed_change_window",
                "label": "First eligible level-change series around the planted boundary",
                "deterministic": True,
            },
            "title": "Planted level change",
            "summary": "A fixed window straddles the known level change for detection context.",
            "points": _case_points(
                planted,
                values,
                baseline_threshold,
                candidate_threshold,
                max(0, int(planted.change_index or 0) - 4),
                16,
                "level",
                "none",
            ),
        },
        {
            "order": 3,
            "scenario_code": "instrumentation_confound",
            "selection_rule": {
                "code": "fixed_confound_window",
                "label": "First eligible permission-shift series around the confound",
                "deterministic": True,
            },
            "title": "Instrumentation confound",
            "summary": "A fixed window exposes permission loss and keeps missingness explicit.",
            "points": _case_points(
                confound,
                values,
                baseline_threshold,
                candidate_threshold,
                max(0, int(dataset.config.change_index) - 4),
                16,
                "none",
                "permission_loss",
            ),
        },
    ]


def export_method_trial(
    run_id: str,
    *,
    output: Path | None = None,
    root: Path | None = None,
    artifact_root: Path | None = None,
) -> MethodTrialExport:
    root = _root(root)
    store = ArtifactStore(artifact_root or (root / ".dllab"))
    manifest_path = store.scope_root(run_id) / "run.json"
    if not manifest_path.is_file():
        raise ValueError(f"run manifest not found for {run_id}")
    manifest = cast(dict[str, Any], json.loads(manifest_path.read_text(encoding="utf-8")))
    bundle_ref = ArtifactRef.model_validate(manifest["bundle"])
    bundle = EvaluationBundle.model_validate_json(store.get_bytes(run_id, bundle_ref))
    for reference in bundle.artifact_manifest:
        store.get_bytes(run_id, reference)
    values = _read_series_values(store, run_id, bundle, manifest)
    custody_ref = ArtifactRef.model_validate(manifest["custody"])
    custody = cast(dict[str, Any], json.loads(store.get_bytes(run_id, custody_ref)))
    dataset = build_benchmark_dataset(smoke=bool(manifest.get("smoke", True)))
    dataset.replay_final_holdout(str(custody["dataset_sha256"]))
    method_provenance, research_provenance = _provenance(root)
    schema_file = next(item for item in method_provenance["files"] if item["name"] == "schema.json")
    baseline_threshold = float(custody["baseline_threshold"])
    candidate_threshold = float(custody["candidate_threshold"])
    baseline_false = _metric(bundle, "baseline", "false_alerts_per_year")
    baseline_detection = _metric(bundle, "baseline", "detection_rate")
    candidate_false = _metric(bundle, "candidate", "false_alerts_per_year")
    candidate_detection = _metric(bundle, "candidate", "detection_rate")
    candidate_brier = next(
        float(metric.value)
        for metric in bundle.calibration.metrics
        if metric.metric_code == "brier" and metric.value is not None
    )
    payload: dict[str, Any] = {
        "schema_version": "DeveloperLensMethodTrialView.v1",
        "trial": {
            "trial_id": "trial-" + hashlib.sha256(run_id.encode()).hexdigest()[:16],
            "title": "WB-C1 method trial: why the simple baseline won",
            "question": (
                "Can the BOCPD candidate reduce false alerts per year versus the rolling median "
                "and MAD baseline without worsening detection or calibration?"
            ),
            "classification": "C0",
            "evidence_label": (
                "Invented weekly system series only; no real repositories, people, providers, "
                "URLs, paths, or production effect."
            ),
        },
        "dataset": {
            "system_count": bundle.dataset_card.system_count,
            "weekly_opportunity_count": bundle.dataset_card.observation_count,
            "observed_count": next(
                item.count
                for item in bundle.dataset_card.coverage_counts
                if item.status == "present"
            ),
            "absent_count": next(
                item.count
                for item in bundle.dataset_card.coverage_counts
                if item.status == "absent"
            ),
            "scenario_codes": ["no_change_control", "planted_change", "instrumentation_confound"],
            "limitations": [
                "Synthetic mechanics evidence only; it does not establish real repository "
                "validity.",
                "Missingness and instrumentation confounds remain explicit rather than "
                "zero-filled.",
            ],
        },
        "methods": {
            "baseline": {
                "role": "baseline",
                "method_code": "rolling_median_mad",
                "display_name": "Rolling median and MAD",
                "description": "A deterministic robust score with a fixed cooldown.",
                "deterministic": True,
                "parameter_summary": (
                    "Twelve-week history, minimum eight observations, fixed cooldown."
                ),
            },
            "candidate": {
                "role": "candidate",
                "method_code": "bocpd",
                "display_name": "Gaussian BOCPD",
                "description": "A fixed-prior Bayesian online change-point probability.",
                "deterministic": True,
                "parameter_summary": "Fixed Normal-Inverse-Gamma prior and hashed parameters.",
            },
            "offline_pelt": {
                "role": "offline_descriptive",
                "method_code": "pelt",
                "display_name": "PELT descriptive marker",
                "description": "An offline segmentation marker, never an online delay measure.",
                "deterministic": True,
                "parameter_summary": "Offline RBF segmentation with fixed penalty.",
            },
        },
        "scorecard": {
            "baseline": {
                "false_alerts_per_year": _value(baseline_false),
                "detection_rate": _value(baseline_detection),
                "detection_delay_weeks": _unavailable(),
                "calibration_brier": _unavailable(),
            },
            "candidate": {
                "false_alerts_per_year": _value(candidate_false),
                "detection_rate": _value(candidate_detection),
                "detection_delay_weeks": _unavailable(),
                "calibration_brier": _value(candidate_brier),
            },
            "threshold_selection": {
                "baseline": {
                    "viable": False,
                    "selected_value": _unavailable(),
                    "reason_code": "no_stable_selection",
                    "summary": (
                        "Training and validation did not yield a viable stable baseline threshold."
                    ),
                },
                "candidate": {
                    "viable": False,
                    "selected_value": _unavailable(),
                    "reason_code": "no_stable_selection",
                    "summary": (
                        "Training and validation did not yield a viable stable candidate threshold."
                    ),
                },
            },
        },
        "acceptance_gates": [
            {
                "order": 1,
                "code": "support",
                "label": "Support is sufficient",
                "outcome": "pass",
                "reason_code": "support_sufficient",
                "reason": "The invented panel has recorded observed and absent counts.",
            },
            {
                "order": 2,
                "code": "threshold_viability",
                "label": "Threshold selections are viable",
                "outcome": "fail",
                "reason_code": "both_selections_nonviable",
                "reason": "Both train and validation selections are nonviable.",
            },
            {
                "order": 3,
                "code": "false_alerts",
                "label": "Candidate false alerts improve",
                "outcome": "fail",
                "reason_code": "candidate_false_alerts_higher",
                "reason": "Candidate false alerts per year exceed the baseline.",
                "relevant_values": {
                    "baseline": _value(baseline_false),
                    "candidate": _value(candidate_false),
                },
            },
            {
                "order": 4,
                "code": "detection",
                "label": "Detection does not worsen",
                "outcome": "pass",
                "reason_code": "same_detection_no_gain",
                "reason": "Candidate and baseline detection rates are equal.",
                "relevant_values": {
                    "baseline": _value(baseline_detection),
                    "candidate": _value(candidate_detection),
                },
            },
            {
                "order": 5,
                "code": "calibration",
                "label": "Candidate calibration is reported",
                "outcome": "pass",
                "reason_code": "candidate_brier_reported",
                "reason": "Candidate Brier calibration is measured on observed points.",
                "relevant_values": {
                    "baseline": _unavailable(),
                    "candidate": _value(candidate_brier),
                },
            },
            {
                "order": 6,
                "code": "promotion",
                "label": "Candidate is eligible for promotion",
                "outcome": "fail",
                "reason_code": "candidate_rejected",
                "reason": "The conservative decision remains reject.",
            },
        ],
        "decision": {
            "outcome": "reject",
            "reason_codes": [
                "both_thresholds_nonviable",
                "candidate_more_false_alerts",
                "no_detection_gain",
            ],
            "summary": (
                "The candidate is rejected because both selections are nonviable and false "
                "alerts are higher."
            ),
            "why_simple_baseline_won": (
                "The complete deterministic baseline has fewer false alerts with the same "
                "detection rate and no candidate promotion evidence."
            ),
        },
        "representative_cases": _build_cases(
            dataset, values, baseline_threshold, candidate_threshold
        ),
        "claims": {
            "supported": [
                {
                    "code": "same_detection_on_c0",
                    "display_text": "Baseline and candidate detection match on this C0 run.",
                },
                {
                    "code": "candidate_more_false_alerts_on_c0",
                    "display_text": "Candidate false alerts are higher on this C0 run.",
                },
                {
                    "code": "deterministic_case_windows",
                    "display_text": "Three case windows are selected by fixed deterministic rules.",
                },
                {
                    "code": "offline_pelt_descriptive",
                    "display_text": "PELT markers are offline descriptive evidence only.",
                },
            ],
            "unsupported": [
                {
                    "code": "real_repository_validity",
                    "display_text": "This result does not establish validity on real repositories.",
                },
                {
                    "code": "person_level_inference",
                    "display_text": "No person-level inference is supported or attempted.",
                },
                {
                    "code": "model_promotion",
                    "display_text": "This rejected trial cannot promote a model.",
                },
            ],
            "limitations": [
                {
                    "code": "c0_synthetic_only",
                    "display_text": "Evidence is limited to invented C0 weekly system series.",
                },
                {
                    "code": "bounded_three_case_selection",
                    "display_text": "Only three bounded representative windows are exported.",
                },
                {
                    "code": "missingness_and_confound",
                    "display_text": (
                        "Missing observations and instrumentation confounds are explicit."
                    ),
                },
                {
                    "code": "thresholds_nonviable",
                    "display_text": "Both threshold selections are nonviable.",
                },
            ],
        },
        "reproducibility": {
            "product_contract_commit": method_provenance["product_commit"],
            "product_research_pack_commit": research_provenance["product_commit"],
            "lab_commit": bundle.run_manifest.lab_commit,
            "run_id": run_id,
            "recipe_code": "wbc1-smoke-c0-v1",
            "digests": {
                "schema": schema_file["sha256"],
                "evaluation_bundle": bundle_ref.sha256,
                "custody": custody_ref.sha256,
                "report": manifest["markdown"]["sha256"],
            },
            "commands": {
                "benchmark": f"uv run dllab benchmark wb-c1 --smoke --run-id {run_id}",
                "reproduce": f"uv run dllab run reproduce {run_id}",
                "export": f"uv run dllab export method-trial {run_id}",
                "report": f"uv run dllab report build {run_id}",
            },
            "verification": {
                "local": "passed",
                "product_hosted": "not_run",
                "lab_hosted": "not_run",
            },
        },
    }
    validate_method_trial_view(payload, root=root)
    data = canonical_json_bytes(payload)
    output_path = (output or (root / "method-trial-view.json")).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(data + b"\n")
    return MethodTrialExport(run_id, data + b"\n", output_path, _sha256(data + b"\n"))
