from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal
from unittest.mock import Mock

import numpy as np
import pytest

from developer_lens_lab.wbc1 import evaluation, runner
from developer_lens_lab.wbc1.generator import (
    BenchmarkDataset,
    GeneratorConfig,
    Partition,
    WeeklySeries,
)

ROOT = Path(__file__).resolve().parents[1]


def _partition(
    code: Literal["train", "test", "final_holdout"], year: int, families: int
) -> Partition:
    start = datetime(year, 1, 1, tzinfo=UTC)
    seed_families = tuple(f"family_{code}_{index}" for index in range(families))
    series: list[WeeklySeries] = []
    for index, family in enumerate(seed_families):
        weeks = 52 + index * 13
        observed = np.ones(weeks, dtype=np.bool_)
        observed[0] = False
        series.append(
            WeeklySeries(
                system_alias=f"system_{code}_{index}",
                seed_family=family,
                scenario_code="no_change",
                noise_family="gaussian",
                week_starts=tuple(
                    (start + timedelta(weeks=week)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    for week in range(weeks)
                ),
                values=np.ones(weeks, dtype=np.float64),
                observed=observed,
                confound=np.zeros(weeks, dtype=np.bool_),
                change_index=None,
                change_kind=None,
                confound_kind=None,
                coverage_id=f"coverage_{code}_{index}",
            )
        )
    return Partition(
        code,
        start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        f"{year + 2}-01-01T00:00:00Z",
        tuple(series),
        seed_families,
    )


@pytest.mark.parametrize("families", [1, 2])
@pytest.mark.parametrize("viable", [False, True])
def test_benchmark_resources_count_every_evaluator_pass_and_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, families: int, viable: bool
) -> None:
    # Entirely fabricated partitions: no existing final-holdout observations are opened.
    def dataset(*, smoke: bool) -> BenchmarkDataset:
        return BenchmarkDataset(
            GeneratorConfig(families_per_partition=families),
            _partition("train", 2020, families),
            _partition("test", 2023, 1),
            lambda: _partition("final_holdout", 2026, 1),
            "sha256:" + "b" * 64,
        )

    points: list[tuple[evaluation.MethodCode, int]] = []

    def evaluate(
        partition: Partition, method: evaluation.MethodCode, threshold: float
    ) -> evaluation.AggregateMetrics:
        points.append((method, sum(len(series.values) for series in partition.series)))
        return evaluation.AggregateMetrics(
            method_code=method,
            threshold=threshold,
            eligible_series=len(partition.series),
            abstained_series=0,
            true_changes=1,
            detected_changes=int(viable),
            false_alerts=0,
            observed_weeks=52,
            false_alerts_per_year=0.0,
            detection_rate=float(viable),
            detection_delays=(1,) if viable else (),
            median_detection_delay=1.0 if viable else None,
            coverage_confound_false_alert_rate=0.0,
            calibration_brier=0.0 if method == "bocpd_gaussian" else None,
        )

    evaluator = Mock(side_effect=evaluate)
    monkeypatch.setattr(evaluation, "evaluate_partition", evaluator)
    monkeypatch.setattr(
        evaluation, "evaluate_pelt", Mock(return_value=evaluation.PeltSummary(0, 0, 0, ()))
    )
    monkeypatch.setattr(runner, "build_benchmark_dataset", dataset)
    monkeypatch.setattr(runner, "_ensure_reproducible_tree", Mock(return_value=None))
    monkeypatch.setattr(runner, "_git_commit", Mock(return_value="a" * 40))

    result = runner.run_benchmark(
        smoke=False, root=ROOT, artifact_root=tmp_path, run_id="wbc1_resource_replay"
    )
    assert evaluator.call_count == 28  # 6 thresholds x 2 train splits x 2 methods + 4 final passes
    assert result.bundle.resources.evaluation_points == sum(count for _, count in points)
    assert result.bundle.resources.candidate_steps == sum(
        count for method, count in points if method == "bocpd_gaussian"
    )

    first_passes = tuple(points)
    points.clear()
    assert runner.reproduce_run(result.manifest_path, root=ROOT)
    assert tuple(points) == first_passes
    assert runner.build_report(result.run_id, artifact_root=tmp_path) == (
        result.markdown_artifact,
        result.html_artifact,
    )
