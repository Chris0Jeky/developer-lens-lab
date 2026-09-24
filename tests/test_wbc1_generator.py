from __future__ import annotations

import numpy as np
import pytest

from developer_lens_lab.wbc1.generator import (
    BenchmarkDataset,
    HoldoutAlreadyOpenedError,
    SCENARIOS,
    WeeklySeries,
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


def _first_series_with_code(dataset: BenchmarkDataset, code: str) -> WeeklySeries:
    return next(series for series in dataset.train.series if series.scenario_code == code)


def test_replay_final_holdout_rejects_mismatched_receipt() -> None:
    dataset = build_benchmark_dataset(smoke=True)

    with pytest.raises(
        ValueError, match="holdout custody receipt does not match the frozen dataset"
    ):
        dataset.replay_final_holdout("sha256:" + "0" * 64)
    with pytest.raises(
        ValueError, match="holdout custody receipt does not match the frozen dataset"
    ):
        dataset.replay_final_holdout("")


def test_replay_final_holdout_matches_open_on_identical_dataset() -> None:
    first = build_benchmark_dataset(smoke=True)
    opened = first.open_final_holdout()
    second = build_benchmark_dataset(smoke=True)

    assert first.dataset_sha256 == second.dataset_sha256
    replayed = second.replay_final_holdout(second.dataset_sha256)

    assert replayed.code == "final_holdout"
    assert [series.system_alias for series in replayed.series] == [
        series.system_alias for series in opened.series
    ]
    for left, right in zip(opened.series, replayed.series, strict=True):
        assert left.system_alias == right.system_alias
        assert left.seed_family == right.seed_family
        assert np.array_equal(left.values, right.values, equal_nan=True)
    assert not second.holdout_opened


def test_final_holdout_metadata_raises_before_open_or_replay() -> None:
    dataset = build_benchmark_dataset(smoke=True)

    with pytest.raises(HoldoutAlreadyOpenedError, match="final holdout has not been opened"):
        _ = dataset.final_holdout_metadata
    with pytest.raises(HoldoutAlreadyOpenedError, match="final holdout has not been opened"):
        _ = dataset.opened_seed_families


def test_opened_seed_families_available_after_open() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    holdout = dataset.open_final_holdout()

    assert dataset.final_holdout_metadata is holdout
    assert dataset.opened_seed_families == holdout.seed_families
    assert dataset.opened_seed_families == (
        "seed_family_final_holdout_00",
        "seed_family_final_holdout_01",
    )


def test_open_final_holdout_calls_receipt_writer_once_with_sha_before_return() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    calls: list[str] = []
    seen_opened: list[bool] = []

    def writer(checksum: str) -> None:
        calls.append(checksum)
        seen_opened.append(dataset.holdout_opened)

    holdout = dataset.open_final_holdout(writer)

    assert calls == [dataset.dataset_sha256]
    assert seen_opened == [False]
    assert holdout.code == "final_holdout"


def test_open_final_holdout_second_open_raises_and_does_not_rewrite_receipt() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    calls: list[str] = []
    dataset.open_final_holdout(calls.append)

    with pytest.raises(HoldoutAlreadyOpenedError, match="final holdout has already been opened"):
        dataset.open_final_holdout(calls.append)

    assert calls == [dataset.dataset_sha256]


def test_planted_level_shift_exceeds_noise() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = _first_series_with_code(dataset, "level")
    change = dataset.config.change_index

    assert series.change_index == change
    assert series.change_kind == "level"
    pre_mean = float(np.nanmean(series.values[:change]))
    post_mean = float(np.nanmean(series.values[change:]))

    assert post_mean - pre_mean > dataset.config.noise_scale


def test_planted_slope_shift_exceeds_noise() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = _first_series_with_code(dataset, "slope")
    change = dataset.config.change_index

    assert series.change_index == change
    assert series.change_kind == "slope"
    pre_mean = float(np.nanmean(series.values[:change]))
    post_mean = float(np.nanmean(series.values[change:]))

    assert post_mean - pre_mean > dataset.config.noise_scale


def test_planted_parser_shift_exceeds_noise() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = _first_series_with_code(dataset, "parser_shift")
    change = dataset.config.change_index

    assert series.change_kind is None
    pre_mean = float(np.nanmean(series.values[:change]))
    post_mean = float(np.nanmean(series.values[change:]))

    assert post_mean - pre_mean > dataset.config.noise_scale


def test_planted_variance_change_inflates_post_variance() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = _first_series_with_code(dataset, "variance")
    change = dataset.config.change_index

    assert series.change_index == change
    assert series.change_kind == "variance"
    pre_var = float(np.nanvar(series.values[:change]))
    post_var = float(np.nanvar(series.values[change:]))

    assert post_var > 2.0 * pre_var


def test_no_change_series_carries_no_change_marker() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = _first_series_with_code(dataset, "no_change")

    assert series.change_index is None
    assert series.change_kind is None
