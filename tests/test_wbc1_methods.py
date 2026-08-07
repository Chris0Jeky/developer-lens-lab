from __future__ import annotations

import numpy as np
from scipy.special import gammaln

from developer_lens_lab.wbc1.generator import build_benchmark_dataset
from developer_lens_lab.wbc1.methods import (
    BocpdParameters,
    bocpd_scores,
    parameters_sha256,
    rolling_median_mad_scores,
)


def test_online_methods_are_prefix_causal_and_finite() -> None:
    dataset = build_benchmark_dataset(smoke=True)
    series = next(series for series in dataset.train.series if series.scenario_code == "level")
    assert series.change_index is not None
    changed_suffix = series.values.copy()
    changed_suffix[80:] += 100.0

    baseline = rolling_median_mad_scores(series.values)
    baseline_changed = rolling_median_mad_scores(changed_suffix)
    candidate = bocpd_scores(series.values).change_probability
    candidate_changed = bocpd_scores(changed_suffix).change_probability

    np.testing.assert_allclose(baseline[:80], baseline_changed[:80])
    np.testing.assert_allclose(candidate[:80], candidate_changed[:80])
    assert np.isfinite(candidate).all()
    assert bool(((candidate >= 0.0) & (candidate <= 1.0)).all())
    assert float(candidate[series.change_index : series.change_index + 9].max()) > float(
        np.median(candidate[12 : series.change_index])
    )


def test_bocpd_matches_adams_mackay_reference_vector() -> None:
    parameters = BocpdParameters(
        expected_run_length=4.0,
        warmup=0,
        recent_run_lengths=1,
        maximum_run_length=16,
        prior_mean=0.0,
        prior_kappa=1.0,
        prior_alpha=2.0,
        prior_beta=1.0,
    )
    values = np.asarray([0.5, 0.75, -0.25], dtype=np.float64)

    # Independent implementation of Algorithm 1's predictive/growth and
    # changepoint recurrence, kept deliberately small for a formula-level
    # regression against the vectorized production code.
    probabilities = np.asarray([1.0], dtype=np.float64)
    means = np.asarray([parameters.prior_mean], dtype=np.float64)
    kappas = np.asarray([parameters.prior_kappa], dtype=np.float64)
    alphas = np.asarray([parameters.prior_alpha], dtype=np.float64)
    betas = np.asarray([parameters.prior_beta], dtype=np.float64)
    expected: list[float] = []
    hazard = 1.0 / parameters.expected_run_length
    for value in values:
        degrees = 2.0 * alphas
        scales = np.sqrt(betas * (kappas + 1.0) / (alphas * kappas))
        standardized = (value - means) / scales
        log_density = (
            gammaln((degrees + 1.0) / 2.0)
            - gammaln(degrees / 2.0)
            - 0.5 * np.log(degrees * np.pi)
            - np.log(scales)
            - ((degrees + 1.0) / 2.0) * np.log1p((standardized**2) / degrees)
        )
        predictive = np.asarray(np.exp(log_density), dtype=np.float64)
        updated = np.concatenate(
            (
                np.asarray([float(np.sum(probabilities * hazard * predictive))], dtype=np.float64),
                probabilities * (1.0 - hazard) * predictive,
            )
        )
        evidence = float(updated.sum())
        updated /= evidence
        assert np.isclose(float(updated.sum()), 1.0)
        expected.append(float(updated[0]))
        grown_kappas = kappas + 1.0
        grown_means = (kappas * means + value) / grown_kappas
        grown_alphas = alphas + 0.5
        grown_betas = betas + kappas * (value - means) ** 2 / (2.0 * grown_kappas)
        probabilities = updated
        means = np.concatenate(([parameters.prior_mean], grown_means))
        kappas = np.concatenate(([parameters.prior_kappa], grown_kappas))
        alphas = np.concatenate(([parameters.prior_alpha], grown_alphas))
        betas = np.concatenate(([parameters.prior_beta], grown_betas))

    actual = bocpd_scores(values, parameters).change_probability
    np.testing.assert_allclose(actual, np.asarray(expected), rtol=1e-12, atol=1e-12)


def test_bocpd_missing_observation_is_causal_and_prior_is_hashed() -> None:
    parameters = BocpdParameters(warmup=0, recent_run_lengths=1, prior_mean=0.0)
    values = np.asarray([0.1, 0.2, 0.3, 0.4], dtype=np.float64)
    missing = values.copy()
    missing[2] = np.nan
    observed = bocpd_scores(values, parameters).change_probability
    censored = bocpd_scores(missing, parameters).change_probability
    np.testing.assert_allclose(observed[:2], censored[:2])
    assert censored[2] == 0.0
    np.testing.assert_allclose(
        censored[3], bocpd_scores(values[[0, 1, 3]], parameters).change_probability[2]
    )
    assert np.isfinite(censored).all()
    assert parameters_sha256(parameters) != parameters_sha256(
        BocpdParameters(warmup=0, recent_run_lengths=1, prior_mean=1.0)
    )


def test_bocpd_missing_block_is_observed_sample_equivalent() -> None:
    # Characterization lock for the preregistered observed-sample semantics: a
    # contiguous block of missing weeks is equivalent to deleting those samples
    # (the run-length/hazard posterior does not advance across the gap), so the
    # post-gap scores must equal those of the gap-deleted series at the
    # compacted indices.  Must be GREEN on current code by construction.
    parameters = BocpdParameters(warmup=12)
    rng = np.random.default_rng(20260807)
    pre = rng.normal(20.0, 1.0, size=24)
    # Level shift after the gap keeps the post-gap change probabilities
    # non-trivial relative to the quiet pre-gap history.
    post = rng.normal(28.0, 1.0, size=18)
    deleted_series = np.concatenate((pre, post)).astype(np.float64)

    gap = 4
    gap_start = len(pre)
    series = np.concatenate((pre, np.full(gap, np.nan), post)).astype(np.float64)

    full = bocpd_scores(series, parameters).change_probability
    deleted = bocpd_scores(deleted_series, parameters).change_probability

    # Each censored week scores exactly 0.0.
    for index in range(gap_start, gap_start + gap):
        assert full[index] == 0.0
    # Post-gap scores equal the gap-deleted series at the compacted indices.
    np.testing.assert_allclose(full[gap_start + gap :], deleted[gap_start:])
    assert np.isfinite(full).all()
    assert np.isfinite(deleted).all()
    # Non-trivial: the post-gap window carries real changepoint mass.
    assert float(full[gap_start + gap :].max()) > float(
        np.median(full[parameters.warmup : gap_start])
    )
