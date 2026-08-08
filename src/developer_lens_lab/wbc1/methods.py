# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass

import numpy as np
import ruptures as rpt
from numpy.typing import NDArray
from scipy.special import gammaln

FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class BaselineParameters:
    window: int = 12
    minimum_history: int = 8
    minimum_scale: float = 0.25
    cooldown: int = 6


@dataclass(frozen=True)
class BocpdParameters:
    # `expected_run_length` -- and therefore the constant hazard
    # `1 / expected_run_length` -- is denominated in OBSERVED SAMPLES, not
    # calendar weeks.  Missing/non-finite weeks are intentionally skipped (see
    # bocpd_scores) and do not advance the run-length/hazard posterior.  This is
    # the canonical Adams--MacKay run-length-in-observations semantics -- a
    # post-hoc characterization of the already-run behavior, NOT a preregistration
    # (docs/EXPERIMENT_LEDGER.md).  The method must not be used for calendar-time /
    # real-time run-length claims without a separate preregistration AND a newly
    # reserved, untouched holdout with its own custody event.
    expected_run_length: float = 52.0
    warmup: int = 12
    recent_run_lengths: int = 3
    maximum_run_length: int = 104
    cooldown: int = 6
    # Fixed Normal-Inverse-Gamma prior; these are deliberately independent of
    # the observations so the first samples are not used once to set a prior
    # and again as likelihood evidence.
    prior_mean: float = 20.0
    prior_kappa: float = 1.0
    prior_alpha: float = 2.0
    prior_beta: float = 4.0


@dataclass(frozen=True)
class BocpdOutput:
    change_probability: FloatArray
    surprise: FloatArray


DEFAULT_BASELINE_PARAMETERS = BaselineParameters()
DEFAULT_BOCPD_PARAMETERS = BocpdParameters()


def parameters_sha256(value: BaselineParameters | BocpdParameters) -> str:
    payload = json.dumps(asdict(value), separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def rolling_median_mad_scores(
    values: FloatArray, parameters: BaselineParameters = DEFAULT_BASELINE_PARAMETERS
) -> FloatArray:
    scores = np.zeros(len(values), dtype=np.float64)
    for index in range(len(values)):
        value = values[index]
        if np.isnan(value):
            continue
        start = max(0, index - parameters.window)
        history = values[start:index]
        finite = history[np.isfinite(history)]
        if len(finite) < parameters.minimum_history:
            continue
        median = float(np.median(finite))
        mad = float(np.median(np.abs(finite - median)))
        scale = max(1.4826 * mad, parameters.minimum_scale)
        scores[index] = abs(float(value) - median) / scale
    return scores


def _student_t_pdf(
    value: float, location: FloatArray, scale: FloatArray, degrees: FloatArray
) -> FloatArray:
    safe_scale = np.maximum(scale, 1e-9)
    standardized = (value - location) / safe_scale
    log_density = (
        gammaln((degrees + 1.0) / 2.0)
        - gammaln(degrees / 2.0)
        - 0.5 * np.log(degrees * np.pi)
        - np.log(safe_scale)
        - ((degrees + 1.0) / 2.0) * np.log1p((standardized**2) / degrees)
    )
    return np.asarray(np.exp(log_density), dtype=np.float64)


def bocpd_scores(
    values: FloatArray, parameters: BocpdParameters = DEFAULT_BOCPD_PARAMETERS
) -> BocpdOutput:
    # Adams--MacKay Algorithm 1.  State arrays describe the posterior
    # sufficient statistics for each run length *before* the current value.
    # The r=0 state is always the fixed prior; only grown states incorporate
    # the current observation.
    prior_mean = float(parameters.prior_mean)
    prior_kappa = float(parameters.prior_kappa)
    prior_alpha = float(parameters.prior_alpha)
    prior_beta = float(parameters.prior_beta)
    hazard = 1.0 / parameters.expected_run_length

    probabilities = np.asarray([1.0], dtype=np.float64)
    means = np.asarray([prior_mean], dtype=np.float64)
    kappas = np.asarray([prior_kappa], dtype=np.float64)
    alphas = np.asarray([prior_alpha], dtype=np.float64)
    betas = np.asarray([prior_beta], dtype=np.float64)
    change_probability = np.zeros(len(values), dtype=np.float64)
    surprise = np.zeros(len(values), dtype=np.float64)

    for index, raw_value in enumerate(values):
        if not np.isfinite(raw_value):
            # Observed-sample semantics: a censored week is equivalent to
            # deleting that sample, so the run-length/hazard posterior does not
            # advance here.  This skip is intentional, not an oversight.
            continue
        value = float(raw_value)
        degrees = 2.0 * alphas
        scales = np.sqrt(betas * (kappas + 1.0) / (alphas * kappas))
        predictive = _student_t_pdf(value, means, scales, degrees)
        growth = probabilities * (1.0 - hazard) * predictive
        # A changepoint has the same predictive term as every other run
        # length, then resets to the fixed prior at r=0.
        changepoint = float(np.sum(probabilities * hazard * predictive))
        updated_probabilities = np.concatenate((np.asarray([changepoint]), growth))
        evidence = float(updated_probabilities.sum())
        if not np.isfinite(evidence) or evidence <= 0.0:
            updated_probabilities = np.asarray([1.0], dtype=np.float64)
        else:
            updated_probabilities /= evidence
        updated_probabilities = updated_probabilities[: parameters.maximum_run_length + 1]
        updated_probabilities /= float(updated_probabilities.sum())

        grown_kappas = kappas + 1.0
        grown_means = (kappas * means + value) / grown_kappas
        grown_alphas = alphas + 0.5
        grown_betas = betas + kappas * (value - means) ** 2 / (2.0 * grown_kappas)
        means = np.concatenate((np.asarray([prior_mean]), grown_means))[
            : len(updated_probabilities)
        ]
        kappas = np.concatenate((np.asarray([prior_kappa]), grown_kappas))[
            : len(updated_probabilities)
        ]
        alphas = np.concatenate((np.asarray([prior_alpha]), grown_alphas))[
            : len(updated_probabilities)
        ]
        betas = np.concatenate((np.asarray([prior_beta]), grown_betas))[
            : len(updated_probabilities)
        ]
        probabilities = updated_probabilities
        if index >= parameters.warmup:
            recent = min(parameters.recent_run_lengths, len(probabilities))
            change_probability[index] = float(probabilities[:recent].sum())
            surprise[index] = float(-np.log(max(evidence, 1e-300)))
    return BocpdOutput(change_probability, surprise)


def alerts_from_scores(
    scores: FloatArray,
    threshold: float,
    cooldown: int,
    observed: NDArray[np.bool_],
) -> tuple[int, ...]:
    alerts: list[int] = []
    next_allowed = 0
    for index, score in enumerate(scores):
        if index < next_allowed or not bool(observed[index]) or not np.isfinite(score):
            continue
        if float(score) >= threshold:
            alerts.append(index)
            next_allowed = index + cooldown
    return tuple(alerts)


def pelt_segments(values: FloatArray, penalty: float = 8.0) -> tuple[int, ...]:
    finite = np.isfinite(values)
    # PELT is an offline descriptive arm; never interpolate a censored series.
    if int(finite.sum()) < 12 or not bool(finite.all()):
        return ()
    boundaries = (
        rpt.Pelt(model="rbf", min_size=4, jump=1).fit(values.reshape(-1, 1)).predict(pen=penalty)
    )
    return tuple(int(boundary) for boundary in boundaries if boundary < len(values))
