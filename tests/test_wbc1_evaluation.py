from __future__ import annotations

import math

import numpy as np
import pytest
from numpy.typing import NDArray

import developer_lens_lab.wbc1.evaluation as evaluation_module
from developer_lens_lab.wbc1.evaluation import (
    DETECTION_DELAY_BUDGET,
    AggregateMetrics,
    EvaluationPlan,
    MethodCode,
    ThresholdSelection,
    decide_benchmark,
    evaluate_partition,
    evaluate_pelt,
    prepare_evaluation,
    run_evaluation,
)
from developer_lens_lab.wbc1.generator import Partition, WeeklySeries, build_benchmark_dataset


def _metrics(method: MethodCode, false_alerts_per_year: float) -> AggregateMetrics:
    return AggregateMetrics(
        method_code=method,
        threshold=0.5,
        eligible_series=1,
        abstained_series=0,
        true_changes=1,
        detected_changes=1,
        false_alerts=0,
        observed_weeks=52,
        false_alerts_per_year=false_alerts_per_year,
        detection_rate=1.0,
        detection_delays=(1,),
        median_detection_delay=1.0,
        coverage_confound_false_alert_rate=0.0,
        calibration_brier=0.0,
    )


def _plan(*, baseline_viable: bool, candidate_viable: bool) -> EvaluationPlan:
    baseline_metrics = _metrics("rolling_median_mad", 0.0)
    candidate_metrics = _metrics("bocpd_gaussian", 0.0)
    return EvaluationPlan(
        ThresholdSelection("rolling_median_mad", 2.5, baseline_metrics, baseline_viable),
        ThresholdSelection("bocpd_gaussian", 0.5, candidate_metrics, candidate_viable),
    )


def test_smoke_evaluation_freezes_thresholds_before_holdout() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    holdout = dataset.open_final_holdout()
    result = run_evaluation(dataset.train, dataset.test, holdout)

    assert result.baseline_selection.threshold > 0
    assert result.candidate_selection.threshold > 0
    expected_changes = 4 * dataset.config.families_per_partition
    assert result.baseline_holdout.true_changes == expected_changes
    assert result.candidate_holdout.true_changes == expected_changes
    assert all(
        delay <= DETECTION_DELAY_BUDGET for delay in result.candidate_holdout.detection_delays
    )
    assert result.decision in {"reject", "benchmarked"}
    assert result.pelt.evaluated_series > 0


def test_thresholds_are_frozen_before_test_and_holdout() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    plan = prepare_evaluation(dataset.train)
    changed_holdout = dataset.open_final_holdout()
    changed_holdout.series[0].values[:] = -10_000.0
    replayed = run_evaluation(dataset.train, dataset.test, changed_holdout, plan)
    assert replayed.baseline_selection.threshold == plan.baseline_selection.threshold
    assert replayed.candidate_selection.threshold == plan.candidate_selection.threshold


def test_pelt_abstains_on_incomplete_series() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    complete = dataset.train.series[0]
    incomplete_values = complete.values.copy()
    incomplete_values[20] = float("nan")
    incomplete = complete.__class__(
        system_alias=complete.system_alias,
        seed_family=complete.seed_family,
        scenario_code=complete.scenario_code,
        noise_family=complete.noise_family,
        week_starts=complete.week_starts,
        values=incomplete_values,
        observed=complete.observed.copy(),
        confound=complete.confound.copy(),
        change_index=complete.change_index,
        change_kind=complete.change_kind,
        confound_kind=complete.confound_kind,
        coverage_id=complete.coverage_id,
    )
    partition = Partition(
        dataset.train.code,
        dataset.train.start,
        dataset.train.end,
        (incomplete,),
        (incomplete.seed_family,),
    )
    summary = evaluate_pelt(partition)
    assert summary.evaluated_series == 0


def test_false_alert_rate_uses_non_event_risk_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = next(item for item in dataset.train.series if item.scenario_code == "level")
    assert series.change_index is not None
    scores = np.zeros(len(series.values), dtype=np.float64)
    scores[series.change_index] = 1.0
    scores[series.change_index + 6] = 1.0
    scores[series.change_index + 12] = 1.0

    def fake_scores(_series: WeeklySeries, _method: MethodCode) -> NDArray[np.float64]:
        return scores

    monkeypatch.setattr(evaluation_module, "_scores", fake_scores)
    partition = Partition(
        dataset.train.code,
        dataset.train.start,
        dataset.train.end,
        (series,),
        (series.seed_family,),
    )

    metrics = evaluate_partition(partition, "rolling_median_mad", 0.5)

    non_event_weeks = len(series.values) - DETECTION_DELAY_BUDGET - 1
    assert metrics.false_alerts == 1
    assert math.isclose(metrics.false_alerts_per_year, 52 / non_event_weeks)


def test_decision_rejects_nonviable_threshold_selection_even_with_good_holdout() -> None:
    baseline = _metrics("rolling_median_mad", 1.0)
    candidate = _metrics("bocpd_gaussian", 0.5)
    decision, reasons = decide_benchmark(
        baseline, candidate, _plan(baseline_viable=False, candidate_viable=True)
    )
    assert decision == "reject"
    assert reasons == ("BASELINE_SELECTION_VIABLE",)


@pytest.mark.parametrize("candidate_rate", [0.0, 0.1])
def test_decision_requires_real_false_alert_improvement_when_baseline_is_zero(
    candidate_rate: float,
) -> None:
    baseline = _metrics("rolling_median_mad", 0.0)
    candidate = _metrics("bocpd_gaussian", candidate_rate)
    decision, reasons = decide_benchmark(
        baseline, candidate, _plan(baseline_viable=True, candidate_viable=True)
    )
    assert decision == "reject"
    assert "CANDIDATE_FALSE_ALERT_IMPROVEMENT" in reasons
