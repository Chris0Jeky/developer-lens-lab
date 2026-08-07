from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from statistics import median
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from .generator import Partition, WeeklySeries
from .methods import (
    BaselineParameters,
    BocpdParameters,
    alerts_from_scores,
    bocpd_scores,
    pelt_segments,
    rolling_median_mad_scores,
)

FloatArray = NDArray[np.float64]
MethodCode = Literal["rolling_median_mad", "bocpd_gaussian"]
DETECTION_DELAY_BUDGET = 8


def _pairwise_sum(values: Sequence[float]) -> float:
    """Sum floats in one fixed tree so aggregate bytes do not depend on SIMD width."""
    size = len(values)
    if size == 0:
        return 0.0
    if size == 1:
        return float(values[0])
    midpoint = size // 2
    return _pairwise_sum(values[:midpoint]) + _pairwise_sum(values[midpoint:])


@dataclass(frozen=True)
class AggregateMetrics:
    method_code: MethodCode
    threshold: float
    eligible_series: int
    abstained_series: int
    true_changes: int
    detected_changes: int
    false_alerts: int
    observed_weeks: int
    false_alerts_per_year: float
    detection_rate: float | None
    detection_delays: tuple[int, ...]
    median_detection_delay: float | None
    coverage_confound_false_alert_rate: float | None
    calibration_brier: float | None


@dataclass(frozen=True)
class ThresholdSelection:
    method_code: MethodCode
    threshold: float
    training_metrics: AggregateMetrics
    viable: bool
    inner_validation_metrics: AggregateMetrics | None = None


@dataclass(frozen=True)
class PeltSummary:
    evaluated_series: int
    boundary_count: int
    localized_changes: int
    localization_errors: tuple[int, ...]


@dataclass(frozen=True)
class BenchmarkEvaluation:
    baseline_selection: ThresholdSelection
    candidate_selection: ThresholdSelection
    baseline_test: AggregateMetrics
    candidate_test: AggregateMetrics
    baseline_holdout: AggregateMetrics
    candidate_holdout: AggregateMetrics
    pelt: PeltSummary
    decision: Literal["reject", "benchmarked"]
    decision_reasons: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationPlan:
    baseline_selection: ThresholdSelection
    candidate_selection: ThresholdSelection


def _eligible(series: WeeklySeries) -> bool:
    return len(series.values) >= 52 and float(series.observed.mean()) >= 0.8


def _scores(series: WeeklySeries, method: MethodCode) -> FloatArray:
    if method == "rolling_median_mad":
        return rolling_median_mad_scores(series.values)
    return bocpd_scores(series.values).change_probability


def _cooldown(method: MethodCode) -> int:
    return (
        BaselineParameters().cooldown
        if method == "rolling_median_mad"
        else BocpdParameters().cooldown
    )


def evaluate_partition(
    partition: Partition,
    method: MethodCode,
    threshold: float,
) -> AggregateMetrics:
    eligible_series = 0
    abstained_series = 0
    true_changes = 0
    detected_changes = 0
    false_alerts = 0
    observed_weeks = 0
    non_event_observed_weeks = 0
    delays: list[int] = []
    confound_series = 0
    confound_series_alerted = 0
    calibration_squared_errors: list[float] = []

    for series in partition.series:
        if not _eligible(series):
            abstained_series += 1
            continue
        eligible_series += 1
        scores = _scores(series, method)
        alerts = alerts_from_scores(scores, threshold, _cooldown(method), series.observed)
        observed_weeks += int(series.observed.sum())
        event_window = np.zeros(len(series.values), dtype=np.bool_)
        if series.change_index is not None:
            event_window[series.change_index : series.change_index + DETECTION_DELAY_BUDGET + 1] = (
                True
            )
        non_event_observed_weeks += int(np.logical_and(series.observed, ~event_window).sum())
        matched_alert: int | None = None
        if series.change_index is not None:
            true_changes += 1
            candidates = [
                alert
                for alert in alerts
                if series.change_index <= alert <= series.change_index + DETECTION_DELAY_BUDGET
            ]
            if candidates:
                matched_alert = min(candidates)
                detected_changes += 1
                delays.append(matched_alert - series.change_index)
        false_alerts += sum(
            1
            for alert in alerts
            if not (
                series.change_index is not None
                and series.change_index <= alert <= series.change_index + DETECTION_DELAY_BUDGET
            )
        )
        if series.confound_kind is not None:
            confound_series += 1
            if any(bool(series.confound[alert]) for alert in alerts):
                confound_series_alerted += 1
        if method == "bocpd_gaussian":
            labels = np.zeros(len(series.values), dtype=np.float64)
            if series.change_index is not None:
                labels[series.change_index : series.change_index + 3] = 1.0
            mask = series.observed
            calibration_squared_errors.extend(((scores[mask] - labels[mask]) ** 2).tolist())

    years = non_event_observed_weeks / 52.0
    detection_rate = detected_changes / true_changes if true_changes else None
    confound_rate = confound_series_alerted / confound_series if confound_series else None
    brier = (
        _pairwise_sum(calibration_squared_errors) / len(calibration_squared_errors)
        if calibration_squared_errors
        else None
    )
    return AggregateMetrics(
        method_code=method,
        threshold=threshold,
        eligible_series=eligible_series,
        abstained_series=abstained_series,
        true_changes=true_changes,
        detected_changes=detected_changes,
        false_alerts=false_alerts,
        observed_weeks=observed_weeks,
        false_alerts_per_year=false_alerts / years if years else 0.0,
        detection_rate=detection_rate,
        detection_delays=tuple(delays),
        median_detection_delay=float(median(delays)) if delays else None,
        coverage_confound_false_alert_rate=confound_rate,
        calibration_brier=brier,
    )


def _is_viable(metrics: AggregateMetrics) -> bool:
    return bool(
        metrics.detection_rate is not None
        and metrics.detection_rate >= 0.75
        and metrics.median_detection_delay is not None
        and metrics.median_detection_delay <= DETECTION_DELAY_BUDGET
    )


def select_threshold(partition: Partition, method: MethodCode) -> ThresholdSelection:
    thresholds = (
        (2.5, 3.0, 3.5, 4.0, 5.0, 6.0)
        if method == "rolling_median_mad"
        else (0.05, 0.1, 0.2, 0.35, 0.5, 0.7)
    )
    families = partition.seed_families
    validation_family = families[-1:] if len(families) > 1 else families
    validation_series = tuple(
        series for series in partition.series if series.seed_family in validation_family
    )
    fit_series = tuple(
        series for series in partition.series if series.seed_family not in validation_family
    )
    fit_partition = Partition(
        partition.code,
        partition.start,
        partition.end,
        fit_series or validation_series,
        tuple(families[:-1]) or tuple(validation_family),
    )
    validation_partition = Partition(
        partition.code, partition.start, partition.end, validation_series, tuple(validation_family)
    )
    candidates = [
        (
            evaluate_partition(fit_partition, method, threshold),
            evaluate_partition(validation_partition, method, threshold),
        )
        for threshold in thresholds
    ]
    viable = [
        (fit_metrics, validation_metrics)
        for fit_metrics, validation_metrics in candidates
        if _is_viable(fit_metrics) and _is_viable(validation_metrics)
    ]
    if viable:
        fit_selected, validation_selected = min(
            viable,
            key=lambda metrics: (
                metrics[1].false_alerts_per_year,
                metrics[1].coverage_confound_false_alert_rate or 0.0,
                -metrics[1].threshold,
            ),
        )
        return ThresholdSelection(
            method,
            validation_selected.threshold,
            fit_selected,
            True,
            validation_selected,
        )
    fit_selected, validation_selected = min(
        candidates,
        key=lambda metrics: (
            -(metrics[1].detection_rate or 0.0),
            metrics[1].false_alerts_per_year,
            # A genuine median detection delay of 0 (instant detection) is the
            # best possible tie-break, not a missing value.  `x or inf` would
            # collapse a real 0.0 to the worst rank; only a true `None` (no
            # detections at all) may be treated as absent.
            metrics[1].median_detection_delay
            if metrics[1].median_detection_delay is not None
            else float("inf"),
        ),
    )
    return ThresholdSelection(
        method,
        validation_selected.threshold,
        fit_selected,
        False,
        validation_selected,
    )


def evaluate_pelt(partition: Partition) -> PeltSummary:
    boundary_count = 0
    localized = 0
    errors: list[int] = []
    evaluated = 0
    for series in partition.series:
        if (
            not _eligible(series)
            or not bool(series.observed.all())
            or not bool(np.isfinite(series.values).all())
        ):
            continue
        evaluated += 1
        boundaries = pelt_segments(series.values)
        boundary_count += len(boundaries)
        if series.change_index is None or not boundaries:
            continue
        error = min(abs(boundary - series.change_index) for boundary in boundaries)
        errors.append(error)
        if error <= 4:
            localized += 1
    return PeltSummary(evaluated, boundary_count, localized, tuple(errors))


def decide_benchmark(
    baseline: AggregateMetrics,
    candidate: AggregateMetrics,
    plan: EvaluationPlan,
) -> tuple[Literal["reject", "benchmarked"], tuple[str, ...]]:
    gates: tuple[tuple[str, Callable[[], bool]], ...] = (
        (
            # A `benchmarked` verdict must rest on primary-domain evidence that
            # was actually measured for BOTH methods.  When a partition planted
            # no true changes, detection_rate is None (absent), and every gate
            # that coerces it via `or 0.0` would otherwise let an unmeasured
            # comparison be declared benchmarked.  Require presence explicitly.
            "PRIMARY_DOMAIN_METRICS_PRESENT",
            lambda: baseline.detection_rate is not None and candidate.detection_rate is not None,
        ),
        (
            "BASELINE_SELECTION_VIABLE",
            lambda: plan.baseline_selection.viable,
        ),
        (
            "CANDIDATE_SELECTION_VIABLE",
            lambda: plan.candidate_selection.viable,
        ),
        ("CANDIDATE_DETECTION_FLOOR", lambda: (candidate.detection_rate or 0.0) >= 0.75),
        (
            "CANDIDATE_DELAY_BUDGET",
            lambda: (
                candidate.median_detection_delay is not None
                and candidate.median_detection_delay <= DETECTION_DELAY_BUDGET
            ),
        ),
        (
            "CANDIDATE_FALSE_ALERT_IMPROVEMENT",
            lambda: (
                baseline.false_alerts_per_year > 0.0
                and candidate.false_alerts_per_year <= baseline.false_alerts_per_year * 0.8
            ),
        ),
        (
            "CANDIDATE_NOT_WORSE_DETECTION",
            lambda: (candidate.detection_rate or 0.0) >= (baseline.detection_rate or 0.0),
        ),
        (
            "CANDIDATE_CONFOUND_GUARD",
            lambda: (
                (candidate.coverage_confound_false_alert_rate or 0.0)
                <= (baseline.coverage_confound_false_alert_rate or 0.0)
            ),
        ),
    )
    failed = tuple(code for code, predicate in gates if not predicate())
    return (
        ("benchmarked", ("ALL_PREREGISTERED_GATES_PASSED",)) if not failed else ("reject", failed)
    )


def prepare_evaluation(train: Partition) -> EvaluationPlan:
    """Tune thresholds on train's nested inner validation split before custody opens."""
    return EvaluationPlan(
        select_threshold(train, "rolling_median_mad"),
        select_threshold(train, "bocpd_gaussian"),
    )


def run_evaluation(
    train: Partition,
    test: Partition,
    holdout: Partition,
    plan: EvaluationPlan | None = None,
) -> BenchmarkEvaluation:
    frozen = plan or prepare_evaluation(train)
    baseline_selection = frozen.baseline_selection
    candidate_selection = frozen.candidate_selection
    baseline_test = evaluate_partition(test, "rolling_median_mad", baseline_selection.threshold)
    candidate_test = evaluate_partition(test, "bocpd_gaussian", candidate_selection.threshold)
    baseline_holdout = evaluate_partition(
        holdout, "rolling_median_mad", baseline_selection.threshold
    )
    candidate_holdout = evaluate_partition(holdout, "bocpd_gaussian", candidate_selection.threshold)
    pelt = evaluate_pelt(holdout)
    decision, reasons = decide_benchmark(baseline_holdout, candidate_holdout, frozen)
    return BenchmarkEvaluation(
        baseline_selection,
        candidate_selection,
        baseline_test,
        candidate_test,
        baseline_holdout,
        candidate_holdout,
        pelt,
        decision,
        reasons,
    )
