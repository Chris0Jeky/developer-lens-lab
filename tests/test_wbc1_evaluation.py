from __future__ import annotations

import math

import numpy as np
import pytest
from numpy.typing import NDArray

import developer_lens_lab.wbc1.evaluation as evaluation_module
from developer_lens_lab.wbc1.evaluation import (
    DETECTION_DELAY_BUDGET,
    MethodCode,
    evaluate_partition,
    evaluate_pelt,
    prepare_evaluation,
    run_evaluation,
)
from developer_lens_lab.wbc1.generator import Partition, WeeklySeries, build_benchmark_dataset


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
