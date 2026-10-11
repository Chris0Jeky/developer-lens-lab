# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownLambdaType=false, reportPrivateUsage=false

"""Regression tests: MethodTrialView gates must follow recomputed metrics.

A hardcoded ``acceptance_gates`` literal (and a fixed ``reject`` verdict) stays
unchanged when the final-holdout metrics are crafted so the candidate improves
false alerts or misses the detection floor. These tests craft both situations
and require the exported gates and decision reasons to track the recomputed
evaluation instead.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any

from developer_lens_lab.wbc1 import export as export_module
from developer_lens_lab.wbc1.evaluation import (
    EvaluationPlan,
    MethodCode,
    decide_benchmark,
    prepare_evaluation,
    run_evaluation,
)
from developer_lens_lab.wbc1.export import compose_method_trial_view
from developer_lens_lab.wbc1.generator import build_benchmark_dataset
from developer_lens_lab.wbc1.runner import run_benchmark

ROOT = Path(__file__).resolve().parents[1]


def _permit_test_tree(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        "developer_lens_lab.wbc1.runner._ensure_reproducible_tree", lambda _root: None
    )
    monkeypatch.setattr("developer_lens_lab.wbc1.runner._git_commit", lambda _root: "a" * 40)


def _with_metric(results: Any, metric_code: str, value: float) -> Any:
    metrics = tuple(
        metric.model_copy(update={"value": value}) if metric.metric_code == metric_code else metric
        for metric in results.metrics
    )
    return results.model_copy(update={"metrics": metrics})


def _crafted_view(
    monkeypatch: Any,
    tmp_path: Path,
    run_id: str,
    *,
    candidate_false_factor: float | None = None,
    detection: float | None = None,
) -> dict[str, Any]:
    """Compose a view whose final-holdout metrics are crafted deterministically.

    The crafted bundle, the patched ``run_evaluation`` and the patched
    ``evaluate_partition`` all apply the same transform to the real smoke-run
    values, so the export's bundle cross-checks still hold while the gates see
    the crafted regime.
    """
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id=run_id)
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    dataset = build_benchmark_dataset(smoke=bool(manifest.get("smoke", True)))
    plan = prepare_evaluation(dataset.train)
    dataset.open_final_holdout()
    evaluation = run_evaluation(dataset.train, dataset.test, dataset.final_holdout_metadata, plan)
    baseline_holdout = evaluation.baseline_holdout
    candidate_holdout = evaluation.candidate_holdout
    target_false: float | None = None
    if candidate_false_factor is not None:
        target_false = baseline_holdout.false_alerts_per_year * candidate_false_factor
        candidate_holdout = dataclasses.replace(
            candidate_holdout, false_alerts_per_year=target_false
        )
    if detection is not None:
        baseline_holdout = dataclasses.replace(baseline_holdout, detection_rate=detection)
        candidate_holdout = dataclasses.replace(candidate_holdout, detection_rate=detection)
    decision, reasons = decide_benchmark(
        baseline_holdout,
        candidate_holdout,
        EvaluationPlan(
            baseline_selection=evaluation.baseline_selection,
            candidate_selection=evaluation.candidate_selection,
        ),
    )
    crafted_evaluation = dataclasses.replace(
        evaluation,
        baseline_holdout=baseline_holdout,
        candidate_holdout=candidate_holdout,
        decision=decision,
        decision_reasons=reasons,
    )
    bundle = result.bundle
    if target_false is not None:
        bundle = bundle.model_copy(
            update={
                "candidate_results": _with_metric(
                    bundle.candidate_results, "false_alerts_per_year", target_false
                )
            }
        )
    if detection is not None:
        bundle = bundle.model_copy(
            update={
                "baseline_results": _with_metric(
                    bundle.baseline_results, "detection_rate", detection
                )
            }
        )
        bundle = bundle.model_copy(
            update={
                "candidate_results": _with_metric(
                    bundle.candidate_results, "detection_rate", detection
                )
            }
        )
    bundle = bundle.model_copy(
        update={
            "decision": bundle.decision.model_copy(
                update={
                    "outcome": decision,
                    "acceptance_gate_passed": decision == "benchmarked",
                    "reason_codes": tuple(reasons),
                }
            )
        }
    )

    real_evaluate_partition = export_module.evaluate_partition

    def _fake_run_evaluation(train: Any, test: Any, holdout: Any, plan: Any = None) -> Any:
        return crafted_evaluation

    def _fake_evaluate_partition(partition: Any, method: MethodCode, threshold: float) -> Any:
        metrics = real_evaluate_partition(partition, method, threshold)
        if method == "bocpd_gaussian":
            if target_false is not None:
                metrics = dataclasses.replace(metrics, false_alerts_per_year=target_false)
            if detection is not None:
                metrics = dataclasses.replace(metrics, detection_rate=detection)
        elif method == "rolling_median_mad" and detection is not None:
            metrics = dataclasses.replace(metrics, detection_rate=detection)
        return metrics

    monkeypatch.setattr(export_module, "run_evaluation", _fake_run_evaluation)
    monkeypatch.setattr(export_module, "evaluate_partition", _fake_evaluate_partition)
    return compose_method_trial_view(
        result.run_id,
        root=ROOT,
        artifact_root=tmp_path,
        bundle=bundle,
        manifest=manifest,
    )


def test_gate5_passes_when_candidate_false_alerts_improve(tmp_path: Path, monkeypatch: Any) -> None:
    view = _crafted_view(monkeypatch, tmp_path, "method_trial_gate5", candidate_false_factor=0.5)
    gates = view["acceptance_gates"]
    assert [gate["outcome"] for gate in gates] == [
        "fail",
        "fail",
        "pass",
        "pass",
        "pass",
        "pass",
        "pass",
    ]
    assert gates[4]["code"] == "false_alert_improvement"
    assert gates[4]["outcome"] == "pass"
    assert view["decision"]["outcome"] == "reject"
    assert "CANDIDATE_FALSE_ALERT_IMPROVEMENT" not in view["decision"]["reason_codes"]


def test_gate3_fails_when_candidate_misses_detection_floor(
    tmp_path: Path, monkeypatch: Any
) -> None:
    view = _crafted_view(monkeypatch, tmp_path, "method_trial_gate3", detection=0.5)
    gates = view["acceptance_gates"]
    assert [gate["outcome"] for gate in gates] == [
        "fail",
        "fail",
        "fail",
        "pass",
        "fail",
        "pass",
        "pass",
    ]
    assert gates[2]["code"] == "detection_floor"
    assert gates[2]["outcome"] == "fail"
    assert view["decision"]["outcome"] == "reject"
    assert "CANDIDATE_DETECTION_FLOOR" in view["decision"]["reason_codes"]
