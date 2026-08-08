# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pyarrow as pa
import pyarrow.parquet as pq

from developer_lens_lab.artifacts import ArtifactRef, ArtifactStore, canonical_json_bytes
from developer_lens_lab.contracts import EvaluationBundle, validate_method_trial_view
from developer_lens_lab.wbc1.evaluation import (
    evaluate_partition,
    prepare_evaluation,
    run_evaluation,
)
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


def _publish_export(path: Path, payload: bytes) -> None:
    """Atomically replace the named export without following a final symlink."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=".dllab-export-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


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


def load_provenance(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    method_path = root / "vendor" / "developer-lens" / "method-trial-view" / "v1"
    research_path = root / "vendor" / "developer-lens" / "research-pack" / "v1"
    method = cast(dict[str, Any], json.loads((method_path / "provenance.json").read_text()))
    research = cast(dict[str, Any], json.loads((research_path / "provenance.json").read_text()))
    for directory, provenance in ((method_path, method), (research_path, research)):
        for entry in cast(list[dict[str, Any]], provenance.get("files", [])):
            payload = (directory / str(entry["name"])).read_bytes()
            if entry.get("sha256") != _sha256(payload) or entry.get("size_bytes") != len(payload):
                raise ValueError("vendored contract provenance does not match file bytes")
    return method, research


def load_recorded_provenance(
    root: Path, manifest: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return the run's producer snapshots, refusing to trust a later vendor snapshot."""
    recorded = manifest.get("provenance")
    if not isinstance(recorded, dict):
        raise ValueError("run manifest lacks recorded producer provenance")
    method = recorded.get("method_trial_view")
    research = recorded.get("research_pack")
    if not isinstance(method, dict) or not isinstance(research, dict):
        raise ValueError("run manifest has incomplete recorded producer provenance")
    current_method, current_research = load_provenance(root)
    if canonical_json_bytes(current_method) != canonical_json_bytes(method):
        raise ValueError("vendored MethodTrialView provenance differs from recorded run")
    if canonical_json_bytes(current_research) != canonical_json_bytes(research):
        raise ValueError("vendored ResearchPack provenance differs from recorded run")
    if method.get("product_commit") != manifest.get("product_contract_commit"):
        raise ValueError("recorded MethodTrialView provenance does not match run manifest")
    if research.get("product_commit") != manifest.get("product_commit"):
        raise ValueError("recorded ResearchPack provenance does not match run manifest")
    return cast(dict[str, Any], method), cast(dict[str, Any], research)


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
            baseline_score = baseline_scores[index]
            candidate_score = candidate_scores[index]
            baseline_measured = bool(float(baseline_score) == float(baseline_score))
            candidate_measured = bool(float(candidate_score) == float(candidate_score))
            baseline = {
                "alert": index in baseline_alerts if baseline_measured else False,
                "score": _value(float(baseline_score))
                if baseline_measured
                else _unavailable("warmup"),
                "threshold": _value(baseline_threshold),
            }
            candidate = {
                "alert": index in candidate_alerts if candidate_measured else False,
                "probability": _value(float(candidate_score))
                if candidate_measured
                else _unavailable("warmup"),
                "threshold": _value(candidate_threshold),
            }
        else:
            reason = (
                "permission_gap"
                if series.confound_kind == "permission_shift"
                else "instrumentation_gap"
            )
            observed_value = {"state": "missing", "reason": reason}
            baseline = {
                "alert": False,
                "score": _unavailable(reason="missing_observation"),
                "threshold": _value(baseline_threshold),
            }
            candidate = {
                "alert": False,
                "probability": _unavailable(reason="missing_observation"),
                "threshold": _value(candidate_threshold),
            }
        marker = planted_marker if series.change_index == index else "none"
        points.append(
            {
                "relative_week_index": index - start,
                "relative_week_label": f"week-{index - start:03d}",
                "observed": observed_value,
                "planted_marker": marker,
                "confound_marker": confound_marker
                if bool(series.confound[index])
                and (index == 0 or not bool(series.confound[index - 1]))
                else "none",
                "baseline": baseline,
                "candidate": candidate,
                "pelt_marker": {
                    "evaluation_mode": "offline_descriptive",
                    "boundary": index in boundaries,
                },
            }
        )
    return points


def _select_series(
    series: tuple[WeeklySeries, ...], scenario_codes: tuple[str, ...]
) -> WeeklySeries:
    """Select the lexical-lowest eligible final-holdout series for a role."""
    for scenario_code in scenario_codes:
        eligible = sorted(
            (
                item
                for item in series
                if item.scenario_code == scenario_code
                and len(item.values) >= 52
                and float(item.observed.mean()) >= 0.8
            ),
            key=lambda item: item.system_alias,
        )
        if eligible:
            return eligible[0]
    raise ValueError(f"missing eligible representative role: {scenario_codes[0]}")


def _build_cases(
    dataset: Any,
    values: dict[tuple[str, str], float],
    baseline_threshold: float,
    candidate_threshold: float,
) -> list[dict[str, Any]]:
    series = dataset.final_holdout_metadata.series
    # The MethodTrialView v1 contract pins each representative case's scenario_code to a
    # const (case[1]=level, case[2]=parser_shift), so the representative selection must
    # resolve to the canonical scenario or fail-export. A non-canonical fallback (e.g. a
    # slope series when level is ineligible) would emit a case whose const scenario_code
    # contradicts the underlying series -- the faithfulness bug this fixes. Narrowing each
    # role to its single canonical code makes _select_series raise its missing-role
    # ValueError instead of silently substituting an unrepresentable scenario.
    no_change = _select_series(series, ("no_change",))
    planted = _select_series(series, ("level",))
    confound = _select_series(series, ("parser_shift",))
    return [
        {
            "order": 1,
            "role": "no_change_control",
            "scenario_code": "no_change",
            "selection_rule": {
                "code": "fixed_first_window",
                "label": "Lexical-lowest eligible no-change series across the final holdout",
                "deterministic": True,
            },
            "title": "No-change control",
            "summary": (
                "The full 104-week holdout series checks ordinary variation without a planted "
                "change."
            ),
            "points": _case_points(
                no_change, values, baseline_threshold, candidate_threshold, 0, 104, "none", "none"
            ),
        },
        {
            "order": 2,
            "role": "planted_change",
            "scenario_code": "level",
            "selection_rule": {
                "code": "fixed_change_window",
                "label": "Lexical-lowest eligible preferred planted-change series",
                "deterministic": True,
            },
            "title": "Planted level change",
            "summary": "The full 104-week holdout series includes the known level-change boundary.",
            "points": _case_points(
                planted,
                values,
                baseline_threshold,
                candidate_threshold,
                0,
                104,
                "level",
                "none",
            ),
        },
        {
            "order": 3,
            "role": "instrumentation_confound",
            "scenario_code": "parser_shift",
            "selection_rule": {
                "code": "fixed_confound_window",
                "label": "Lexical-lowest eligible preferred instrumentation-confound series",
                "deterministic": True,
            },
            "title": "Instrumentation confound",
            "summary": "The full 104-week holdout series exposes an instrument shift explicitly.",
            "points": _case_points(
                confound,
                values,
                baseline_threshold,
                candidate_threshold,
                0,
                104,
                "none",
                "parser_shift",
            ),
        },
    ]


def compose_method_trial_view(
    run_id: str,
    *,
    root: Path | None = None,
    artifact_root: Path | None = None,
    bundle: EvaluationBundle | None = None,
    manifest: dict[str, Any] | None = None,
    store: ArtifactStore | None = None,
) -> dict[str, Any]:
    """Compose the canonical MethodTrialView from verified source artifacts.

    The returned mapping is pure and may be rendered or persisted by callers.  When
    ``bundle`` and ``manifest`` are omitted this function loads and integrity-checks a
    recorded run, retaining a convenient compatibility seam for the CLI/export helper.
    """
    root = _root(root)
    store = store or ArtifactStore(artifact_root or (root / ".dllab"))
    if manifest is None:
        manifest_path = store.scope_root(run_id) / "run.json"
        if not manifest_path.is_file():
            raise ValueError(f"run manifest not found for {run_id}")
        manifest = cast(dict[str, Any], json.loads(manifest_path.read_text(encoding="utf-8")))
    if bundle is None:
        bundle_ref = ArtifactRef.model_validate(manifest["bundle"])
        bundle = EvaluationBundle.model_validate_json(store.get_bytes(run_id, bundle_ref))
    bundle_ref = ArtifactRef.model_validate(manifest["bundle"])
    if bundle.research_pack_sha256 != str(manifest["research_pack"]["sha256"]):
        raise ValueError("EvaluationBundle ResearchPack reference differs from run manifest")
    declared = {ref.sha256 for ref in bundle.artifact_manifest}
    for name in (
        "baseline",
        "candidate",
        "pelt",
        "custody",
        "research_pack",
        "research_pack_coverage",
        "research_pack_repository_week",
    ):
        ref = ArtifactRef.model_validate(manifest[name])
        store.get_bytes(run_id, ref)
        if ref.sha256 not in declared:
            raise ValueError(f"EvaluationBundle artifact_manifest omits {name}")
    values = _read_series_values(store, run_id, bundle, manifest)
    custody_ref = ArtifactRef.model_validate(manifest["custody"])
    custody = cast(dict[str, Any], json.loads(store.get_bytes(run_id, custody_ref)))
    dataset = build_benchmark_dataset(smoke=bool(manifest.get("smoke", True)))
    dataset.replay_final_holdout(str(custody["dataset_sha256"]))
    if str(custody.get("run_id")) != run_id:
        raise ValueError("custody run_id does not match requested run")
    method_provenance, research_provenance = load_recorded_provenance(root, manifest)
    schema_file = next(item for item in method_provenance["files"] if item["name"] == "schema.json")
    baseline_threshold = float(custody["baseline_threshold"])
    candidate_threshold = float(custody["candidate_threshold"])
    plan = prepare_evaluation(dataset.train)
    if (
        plan.baseline_selection.threshold != baseline_threshold
        or plan.candidate_selection.threshold != candidate_threshold
        or plan.baseline_selection.viable
        or plan.candidate_selection.viable
    ):
        raise ValueError("custody thresholds or viability differ from the frozen evaluation plan")
    full_evaluation = run_evaluation(
        dataset.train, dataset.test, dataset.final_holdout_metadata, plan
    )
    if (
        bundle.decision.outcome != full_evaluation.decision
        or tuple(bundle.decision.reason_codes) != full_evaluation.decision_reasons
    ):
        raise ValueError("EvaluationBundle decision differs from recomputed evaluation")
    baseline_eval = evaluate_partition(
        dataset.final_holdout_metadata, "rolling_median_mad", baseline_threshold
    )
    candidate_eval = evaluate_partition(
        dataset.final_holdout_metadata, "bocpd_gaussian", candidate_threshold
    )
    baseline_false = baseline_eval.false_alerts_per_year
    baseline_detection = baseline_eval.detection_rate or 0.0
    baseline_delay = baseline_eval.median_detection_delay
    baseline_confound = baseline_eval.coverage_confound_false_alert_rate
    candidate_false = candidate_eval.false_alerts_per_year
    candidate_detection = candidate_eval.detection_rate or 0.0
    candidate_delay = candidate_eval.median_detection_delay
    candidate_confound = candidate_eval.coverage_confound_false_alert_rate
    candidate_brier = candidate_eval.calibration_brier
    if _metric(bundle, "baseline", "false_alerts_per_year") != baseline_false:
        raise ValueError("baseline metric differs from recomputed final holdout")
    if _metric(bundle, "baseline", "detection_rate") != baseline_detection:
        raise ValueError("baseline detection differs from recomputed final holdout")
    if _metric(bundle, "candidate", "false_alerts_per_year") != candidate_false:
        raise ValueError("candidate metric differs from recomputed final holdout")
    if _metric(bundle, "candidate", "detection_rate") != candidate_detection:
        raise ValueError("candidate detection differs from recomputed final holdout")
    bundle_brier = next(
        float(metric.value)
        for metric in bundle.calibration.metrics
        if metric.metric_code == "brier" and metric.value is not None
    )
    if bundle_brier != candidate_brier:
        raise ValueError("candidate calibration differs from recomputed final holdout")
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
            "scenario_codes": [
                "no_change",
                "level",
                "variance",
                "slope",
                "seasonal_amplitude",
                "heavy_tailed_no_change",
                "coverage_gap",
                "permission_shift",
                "parser_shift",
            ],
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
                "method_code": "bocpd_gaussian",
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
                "median_detection_delay_weeks": _value(baseline_delay)
                if baseline_delay is not None
                else _unavailable(),
                "coverage_confound_false_alert_rate": _value(baseline_confound)
                if baseline_confound is not None
                else _unavailable(),
                "calibration_brier": _unavailable("not_applicable"),
            },
            "candidate": {
                "false_alerts_per_year": _value(candidate_false),
                "detection_rate": _value(candidate_detection),
                "median_detection_delay_weeks": _value(candidate_delay)
                if candidate_delay is not None
                else _unavailable(),
                "coverage_confound_false_alert_rate": _value(candidate_confound)
                if candidate_confound is not None
                else _unavailable(),
                "calibration_brier": _value(candidate_brier)
                if candidate_brier is not None
                else _unavailable(),
            },
            "threshold_selection": {
                "baseline": {
                    "viable": False,
                    "selected_value": _value(baseline_threshold),
                    "reason_code": "frozen_best_available",
                    "summary": (
                        "Training and validation did not yield a viable stable baseline threshold."
                    ),
                },
                "candidate": {
                    "viable": False,
                    "selected_value": _value(candidate_threshold),
                    "reason_code": "frozen_best_available",
                    "summary": (
                        "Training and validation did not yield a viable stable candidate threshold."
                    ),
                },
            },
        },
        "acceptance_gates": [
            {
                "order": 1,
                "code": "baseline_selection",
                "label": "Baseline selection is viable",
                "outcome": "fail",
                "reason_code": "BASELINE_SELECTION_VIABLE",
                "reason": "Baseline train and validation selection is nonviable.",
            },
            {
                "order": 2,
                "code": "candidate_selection",
                "label": "Candidate selection is viable",
                "outcome": "fail",
                "reason_code": "CANDIDATE_SELECTION_VIABLE",
                "reason": "Candidate train and validation selection is nonviable.",
            },
            {
                "order": 3,
                "code": "detection_floor",
                "label": "Candidate meets detection floor",
                "outcome": "pass",
                "reason_code": "CANDIDATE_DETECTION_FLOOR",
                "reason": "Candidate detection meets the preregistered floor.",
                "relevant_values": {
                    "baseline": _value(baseline_detection),
                    "candidate": _value(candidate_detection),
                },
            },
            {
                "order": 4,
                "code": "delay_budget",
                "label": "Candidate meets delay budget",
                "outcome": "pass",
                "reason_code": "CANDIDATE_DELAY_BUDGET",
                "reason": "Candidate median detection delay meets the preregistered budget.",
                "relevant_values": {
                    "baseline": _value(baseline_delay or 0.0),
                    "candidate": _value(candidate_delay or 0.0),
                },
            },
            {
                "order": 5,
                "code": "false_alert_improvement",
                "label": "Candidate false alerts improve",
                "outcome": "fail",
                "reason_code": "CANDIDATE_FALSE_ALERT_IMPROVEMENT",
                "reason": "Candidate false alerts per year exceed the baseline.",
                "relevant_values": {
                    "baseline": _value(baseline_false),
                    "candidate": _value(candidate_false),
                },
            },
            {
                "order": 6,
                "code": "not_worse_detection",
                "label": "Candidate detection is not worse",
                "outcome": "pass",
                "reason_code": "CANDIDATE_NOT_WORSE_DETECTION",
                "reason": "Candidate and baseline detection rates are equal.",
                "relevant_values": {
                    "baseline": _value(baseline_detection),
                    "candidate": _value(candidate_detection),
                },
            },
            {
                "order": 7,
                "code": "confound_guard",
                "label": "Candidate confound guard is measured",
                "outcome": "pass",
                "reason_code": "CANDIDATE_CONFOUND_GUARD",
                "reason": "Candidate confound false-alert rate is measured within the guard.",
                "relevant_values": {
                    "baseline": _value(baseline_confound or 0.0),
                    "candidate": _value(candidate_confound or 0.0),
                },
            },
        ],
        "decision": {
            "outcome": "reject",
            "candidate_promoted": False,
            "fallback": {"method_code": "rolling_median_mad", "retained": True},
            "reason_codes": list(bundle.decision.reason_codes),
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
                {
                    "code": "online_pelt_performance",
                    "display_text": "Offline PELT markers do not establish online performance.",
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
        "representative_selection": {
            "version": "wbc1-final-holdout-v1",
            "partition": "final_holdout",
            "planted_preference": ["level", "slope", "variance", "seasonal_amplitude"],
            "confound_preference": ["parser_shift", "coverage_gap", "permission_shift"],
            "tie_break": "lexicographically_lowest_stable_opaque_alias",
            "missing_role_policy": "fail_export",
            "aliases_not_exposed": True,
        },
        "deferred_caveats": [
            {
                "code": "missingness_confound_observability",
                "display_text": "Confound observability remains a deferred measurement refinement.",
            },
            {
                "code": "validation_artifact_lifecycle",
                "display_text": "Run-owned artifact lifecycle hardening remains deferred.",
            },
            {
                "code": "threshold_selection_workload_counts",
                "display_text": "Threshold-selection workload counts remain a deferred refinement.",
            },
            {
                "code": "corrupt_manifest_failure",
                "display_text": "Corrupt-manifest failure reporting remains a deferred refinement.",
            },
            {
                "code": "primary_domain_metric_enforcement",
                "display_text": "Primary-domain metric enforcement remains a deferred refinement.",
            },
            {
                "code": "zero_delay_fallback_ordering",
                "display_text": "Zero-delay fallback ordering remains a deferred refinement.",
            },
        ],
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
                "research_pack": manifest["research_pack"]["sha256"],
            },
            "commands": {
                "benchmark": f"uv run dllab benchmark wb-c1 --smoke --run-id {run_id}",
                "reproduce": f"uv run dllab run reproduce {run_id}",
                "export": f"uv run dllab export method-trial {run_id}",
                "report": f"uv run dllab report build {run_id}",
            },
            "verification": {
                "local": "not_run",
                "product_hosted": "not_run",
                "lab_hosted": "not_run",
            },
        },
    }
    validate_method_trial_view(payload, root=root)
    return payload


def export_method_trial(
    run_id: str,
    *,
    output: Path | None = None,
    root: Path | None = None,
    artifact_root: Path | None = None,
) -> MethodTrialExport:
    """Export a validated canonical view as JSON plus one LF for compatibility."""
    root = _root(root)
    view = compose_method_trial_view(run_id, root=root, artifact_root=artifact_root)
    data = canonical_json_bytes(view) + b"\n"
    requested_output = output or (root / "method-trial-view.json")
    output_path = requested_output.parent.resolve() / requested_output.name
    _publish_export(output_path, data)
    return MethodTrialExport(run_id, data, output_path, _sha256(data))
