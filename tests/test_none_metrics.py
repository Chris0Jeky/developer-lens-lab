# pyright: reportPrivateUsage=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""None metrics propagate as unavailable instead of 0.0."""

from __future__ import annotations

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from developer_lens_lab.wbc1 import runner as runner_mod
from developer_lens_lab.wbc1.evaluation import (
    AggregateMetrics,
    BenchmarkEvaluation,
    EvaluationPlan,
    PeltSummary,
    ThresholdSelection,
    decide_benchmark,
    evaluate_partition,
)
from developer_lens_lab.wbc1.export import _acceptance_gates, _maybe_value, _unavailable
from developer_lens_lab.wbc1.generator import Partition, WeeklySeries


def _no_change_partition() -> Partition:
    week_starts = tuple(f"2021-01-{index + 1:02d}" for index in range(52))
    values = np.asarray([10.0 + (index % 7) * 0.1 for index in range(52)], dtype=np.float64)
    observed = np.ones(52, dtype=np.bool_)
    one = WeeklySeries(
        system_alias="system_no_change",
        seed_family="family_00",
        scenario_code="no_change",
        noise_family="gaussian",
        week_starts=week_starts,
        values=values,
        observed=observed,
        confound=np.zeros(52, dtype=np.bool_),
        change_index=None,
        change_kind=None,
        confound_kind=None,
        coverage_id="coverage_00",
    )
    return Partition(
        code="final_holdout",
        start=week_starts[0],
        end=week_starts[-1],
        series=(one,),
        seed_families=("family_00",),
    )


def test_no_change_partition_yields_none_rate_and_delay() -> None:
    metrics = evaluate_partition(_no_change_partition(), "bocpd_gaussian", 0.5)
    assert metrics.detection_rate is None
    assert metrics.median_detection_delay is None


def test_absent_rate_exports_as_unavailable() -> None:
    assert _maybe_value(None) == {"status": "unavailable", "reason": "not_measured"}
    # A genuine 0.0 measurement must stay measured, not collapse to unavailable.
    assert _maybe_value(0.0) == {"status": "measured", "value": 0.0}
    assert _maybe_value(0.2)["status"] == "measured"


def test_absent_brier_exports_as_unavailable() -> None:
    assert _maybe_value(None) == _unavailable()
    assert _maybe_value(0.0) == {"status": "measured", "value": 0.0}


def _holdout_evaluation() -> BenchmarkEvaluation:
    baseline, candidate, plan = _metrics_with_none()
    return BenchmarkEvaluation(
        plan.baseline_selection,
        plan.candidate_selection,
        baseline,
        candidate,
        baseline,
        candidate,
        PeltSummary(0, 0, 0, ()),
        "reject",
        ("CANDIDATE_DETECTION_FLOOR",),
    )


def test_gates_do_not_pass_on_absent_detection() -> None:
    gates = _acceptance_gates(
        _holdout_evaluation(),
        1.0,
        None,
        None,
        None,
        1.0,
        None,
        None,
        None,
    )
    by_code = {gate["code"]: gate for gate in gates}
    assert by_code["detection_floor"]["outcome"] == "not_applicable"
    assert by_code["not_worse_detection"]["outcome"] == "not_applicable"
    assert by_code["detection_floor"]["relevant_values"]["candidate"] == _unavailable()
    assert by_code["detection_floor"]["relevant_values"]["baseline"] == _unavailable()
    assert by_code["not_worse_detection"]["relevant_values"]["candidate"] == _unavailable()
    assert by_code["delay_budget"]["outcome"] != "pass"
    assert by_code["delay_budget"]["relevant_values"]["candidate"] == _unavailable()
    assert by_code["confound_guard"]["outcome"] != "pass"


def _metrics_with_none() -> tuple[AggregateMetrics, AggregateMetrics, EvaluationPlan]:
    base = AggregateMetrics(
        method_code="rolling_median_mad",
        threshold=3.0,
        eligible_series=1,
        abstained_series=0,
        true_changes=0,
        detected_changes=0,
        false_alerts=0,
        observed_weeks=52,
        false_alerts_per_year=0.0,
        detection_rate=None,
        detection_delays=(),
        median_detection_delay=None,
        coverage_confound_false_alert_rate=None,
        calibration_brier=None,
    )
    cand = AggregateMetrics(
        method_code="bocpd_gaussian",
        threshold=0.5,
        eligible_series=1,
        abstained_series=0,
        true_changes=0,
        detected_changes=0,
        false_alerts=0,
        observed_weeks=52,
        false_alerts_per_year=0.0,
        detection_rate=None,
        detection_delays=(),
        median_detection_delay=None,
        coverage_confound_false_alert_rate=None,
        calibration_brier=None,
    )
    plan = EvaluationPlan(
        ThresholdSelection("rolling_median_mad", 3.0, base, False, base),
        ThresholdSelection("bocpd_gaussian", 0.5, cand, False, cand),
    )
    return base, cand, plan


def test_decision_guards_do_not_pass_on_absent_data() -> None:
    baseline, candidate, plan = _metrics_with_none()
    outcome, reasons = decide_benchmark(baseline, candidate, plan)
    assert outcome != "benchmarked"
    assert "CANDIDATE_NOT_WORSE_DETECTION" in reasons
    assert "CANDIDATE_CONFOUND_GUARD" in reasons
    assert "CANDIDATE_DETECTION_FLOOR" in reasons


def test_runner_bundle_storage_preserves_none() -> None:
    metric = runner_mod._metric("detection_rate", None, "detection")  # pyright: ignore[reportPrivateUsage]
    assert metric["value"] is None
    assert metric["state"] != "present"
    measured = runner_mod._metric("detection_rate", 0.0, "detection")  # pyright: ignore[reportPrivateUsage]
    assert measured == {
        "metric_code": "detection_rate",
        "domain_code": "detection",
        "state": "present",
        "value": 0.0,
        "reason_code": None,
    }


def test_runner_parquet_preserves_none_rate() -> None:
    baseline, _, _ = _metrics_with_none()
    payload = runner_mod._result_parquet_bytes(baseline)  # pyright: ignore[reportPrivateUsage]
    rows = pq.read_table(pa.BufferReader(payload)).to_pylist()
    by_code = {row["metric_code"]: row["value"] for row in rows}
    assert by_code["detection_rate"] is None


@pytest.mark.parametrize(
    ("baseline", "candidate", "floor", "not_worse"),
    [
        (None, 0.8, "pass", "not_applicable"),
        (0.8, None, "not_applicable", "not_applicable"),
        (0.0, 0.0, "fail", "pass"),
        (0.8, 0.0, "fail", "fail"),
    ],
)
def test_none_metrics_detection_gates(
    baseline: float | None, candidate: float | None, floor: str, not_worse: str
) -> None:
    gates = _acceptance_gates(
        _holdout_evaluation(), 1.0, baseline, None, None, 1.0, candidate, None, None
    )
    by_code = {gate["code"]: gate for gate in gates}
    assert by_code["detection_floor"]["outcome"] == floor
    assert by_code["not_worse_detection"]["outcome"] == not_worse
