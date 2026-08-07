from __future__ import annotations

import numpy as np
import pytest

from developer_lens_lab.wbc1.generator import (
    SCENARIOS,
    HoldoutAlreadyOpenedError,
    build_benchmark_dataset,
)


def test_invented_generator_is_deterministic_and_split_clean() -> None:
    first = build_benchmark_dataset(smoke=True)
    second = build_benchmark_dataset(smoke=True)

    assert first.dataset_sha256 == second.dataset_sha256
    assert {series.scenario_code for series in first.train.series} == {
        scenario.code for scenario in SCENARIOS
    }
    assert {series.noise_family for series in first.train.series} == {
        "gaussian",
        "heavy_tailed",
    }
    for left, right in zip(first.train.series, second.train.series, strict=True):
        np.testing.assert_equal(left.values, right.values)
    assert set(first.train.seed_families).isdisjoint(first.test.seed_families)
    assert first.train.end == first.test.start


def test_missingness_is_not_zero_and_holdout_opens_once() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    missing = next(
        series for series in dataset.train.series if series.scenario_code == "coverage_gap"
    )

    assert np.isnan(missing.values[~missing.observed]).all()
    custody_states: list[bool] = []
    holdout = dataset.open_final_holdout(
        lambda _checksum: custody_states.append(dataset.holdout_opened)
    )
    assert holdout.code == "final_holdout"
    assert custody_states == [False]
    assert dataset.holdout_opened
    with pytest.raises(HoldoutAlreadyOpenedError):
        dataset.open_final_holdout()
