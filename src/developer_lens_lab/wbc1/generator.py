from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]
NoiseFamily = Literal["gaussian", "heavy_tailed"]


@dataclass(frozen=True)
class Scenario:
    code: str
    noise_family: NoiseFamily
    change_kind: str | None
    confound_kind: str | None = None


SCENARIOS = (
    Scenario("no_change", "gaussian", None),
    Scenario("level", "gaussian", "level"),
    Scenario("variance", "gaussian", "variance"),
    Scenario("slope", "heavy_tailed", "slope"),
    Scenario("seasonal_amplitude", "gaussian", "seasonal_amplitude"),
    Scenario("heavy_tailed_no_change", "heavy_tailed", None),
    Scenario("coverage_gap", "gaussian", None, "coverage_gap"),
    Scenario("permission_shift", "gaussian", None, "permission_shift"),
    Scenario("parser_shift", "gaussian", None, "parser_shift"),
)


@dataclass(frozen=True)
class GeneratorConfig:
    weeks: int = 104
    change_index: int = 60
    baseline_level: float = 20.0
    trend_per_week: float = 0.015
    seasonal_amplitude: float = 2.0
    noise_scale: float = 1.0
    robust_effect: float = 3.0
    families_per_partition: int = 1


@dataclass(frozen=True)
class WeeklySeries:
    system_alias: str
    seed_family: str
    scenario_code: str
    noise_family: NoiseFamily
    week_starts: tuple[str, ...]
    values: FloatArray
    observed: BoolArray
    confound: BoolArray
    change_index: int | None
    change_kind: str | None
    confound_kind: str | None
    coverage_id: str


@dataclass(frozen=True)
class Partition:
    code: Literal["train", "test", "final_holdout"]
    start: str
    end: str
    series: tuple[WeeklySeries, ...]
    seed_families: tuple[str, ...]


class HoldoutAlreadyOpenedError(RuntimeError):
    """Raised when final holdout custody is opened more than once."""


class BenchmarkDataset:
    def __init__(
        self,
        config: GeneratorConfig,
        train: Partition,
        test: Partition,
        final_holdout_factory: Callable[[], Partition],
        dataset_sha256: str,
    ) -> None:
        self.config = config
        self.train = train
        self.test = test
        self._final_holdout_factory = final_holdout_factory
        self.dataset_sha256 = dataset_sha256
        self._holdout_opened = False
        self._final_holdout: Partition | None = None

    @property
    def holdout_opened(self) -> bool:
        return self._holdout_opened

    def open_final_holdout(self, receipt_writer: Callable[[str], None] | None = None) -> Partition:
        """Open the frozen final partition exactly once after method selection."""
        if self._holdout_opened:
            raise HoldoutAlreadyOpenedError("final holdout has already been opened")
        if receipt_writer is not None:
            receipt_writer(self.dataset_sha256)
        self._holdout_opened = True
        self._final_holdout = self._final_holdout_factory()
        return self._final_holdout

    def replay_final_holdout(self, receipt_dataset_sha256: str) -> Partition:
        """Materialize deterministic holdout rows only after verifying a prior custody receipt."""
        if receipt_dataset_sha256 != self.dataset_sha256:
            raise ValueError("holdout custody receipt does not match the frozen dataset")
        self._final_holdout = self._final_holdout_factory()
        return self._final_holdout

    @property
    def final_holdout_metadata(self) -> Partition:
        if self._final_holdout is None:
            raise HoldoutAlreadyOpenedError("final holdout has not been opened")
        return self._final_holdout

    @property
    def opened_seed_families(self) -> tuple[str, ...]:
        return self.final_holdout_metadata.seed_families


def _canonical_week(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:4], "big")


def _noise(rng: np.random.Generator, family: NoiseFamily, length: int) -> FloatArray:
    if family == "gaussian":
        return np.asarray(rng.normal(0.0, 1.0, length), dtype=np.float64)
    # Student-t(df=3) has variance 3, so normalize to unit variance.
    return np.asarray(rng.standard_t(3, length) / np.sqrt(3.0), dtype=np.float64)


def _generate_series(
    partition_code: str,
    start: datetime,
    family_index: int,
    scenario_index: int,
    scenario: Scenario,
    config: GeneratorConfig,
) -> WeeklySeries:
    seed_family = f"seed_family_{partition_code}_{family_index:02d}"
    system_alias = f"system_{partition_code}_{family_index:02d}_{scenario_index:02d}"
    rng = np.random.default_rng(_seed(f"{seed_family}:{scenario.code}"))
    index = np.arange(config.weeks, dtype=np.float64)
    seasonal = config.seasonal_amplitude * np.sin(2.0 * np.pi * index / 52.0)
    underlying = config.baseline_level + config.trend_per_week * index + seasonal
    noise = _noise(rng, scenario.noise_family, config.weeks) * config.noise_scale
    change = config.change_index

    if scenario.code == "level":
        underlying[change:] += config.robust_effect
    elif scenario.code == "variance":
        noise[change:] *= config.robust_effect
    elif scenario.code == "slope":
        underlying[change:] += config.robust_effect * 0.06 * (index[change:] - change)
    elif scenario.code == "seasonal_amplitude":
        underlying[change:] += config.robust_effect * np.sin(2.0 * np.pi * index[change:] / 52.0)

    values = np.asarray(underlying + noise, dtype=np.float64)
    observed = np.ones(config.weeks, dtype=np.bool_)
    confound = np.zeros(config.weeks, dtype=np.bool_)
    if scenario.code == "coverage_gap":
        observed[change - 8 : change + 8] = False
        confound[change - 8 : change + 8] = True
    elif scenario.code == "permission_shift":
        shifted = np.arange(change, config.weeks)
        missing = shifted[(shifted - change) % 3 != 0]
        observed[missing] = False
        confound[change:] = True
    elif scenario.code == "parser_shift":
        # The system is unchanged; the measurement instrument changes.
        values[change:] += config.robust_effect
        confound[change:] = True
    values = values.copy()
    values[~observed] = np.nan
    weeks = tuple(
        _canonical_week(start + timedelta(weeks=offset)) for offset in range(config.weeks)
    )
    return WeeklySeries(
        system_alias=system_alias,
        seed_family=seed_family,
        scenario_code=scenario.code,
        noise_family=scenario.noise_family,
        week_starts=weeks,
        values=values,
        observed=observed,
        confound=confound,
        change_index=change if scenario.change_kind is not None else None,
        change_kind=scenario.change_kind,
        confound_kind=scenario.confound_kind,
        coverage_id=f"coverage_{partition_code}_{family_index:02d}_{scenario_index:02d}",
    )


def _partition(
    code: Literal["train", "test", "final_holdout"],
    start: datetime,
    config: GeneratorConfig,
) -> Partition:
    series = tuple(
        _generate_series(code, start, family, scenario_index, scenario, config)
        for family in range(config.families_per_partition)
        for scenario_index, scenario in enumerate(SCENARIOS)
    )
    seed_families = tuple(
        f"seed_family_{code}_{family:02d}" for family in range(config.families_per_partition)
    )
    end = start + timedelta(weeks=config.weeks)
    return Partition(code, _canonical_week(start), _canonical_week(end), series, seed_families)


def build_benchmark_dataset(smoke: bool = True) -> BenchmarkDataset:
    config = GeneratorConfig(
        weeks=104 if smoke else 208,
        change_index=60 if smoke else 120,
        families_per_partition=2 if smoke else 6,
    )
    train = _partition("train", datetime(2020, 1, 6, tzinfo=UTC), config)
    test_start = datetime(2020, 1, 6, tzinfo=UTC) + timedelta(weeks=config.weeks)
    holdout_start = test_start + timedelta(weeks=config.weeks)
    test = _partition("test", test_start, config)
    frozen = {
        "schema_version": "DeveloperLensWbc1Dataset.v1",
        "generator_revision": "wbc1.generator.v1",
        "config": asdict(config),
        "scenarios": [asdict(scenario) for scenario in SCENARIOS],
        "partitions": {
            "train": {"start": train.start, "seed_families": train.seed_families},
            "test": {"start": test.start, "seed_families": test.seed_families},
            "final_holdout": {
                "start": _canonical_week(holdout_start),
                "seed_families": tuple(
                    f"seed_family_final_holdout_{family:02d}"
                    for family in range(config.families_per_partition)
                ),
            },
        },
    }
    canonical = json.dumps(frozen, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
        "utf-8"
    )
    checksum = "sha256:" + hashlib.sha256(canonical).hexdigest()
    return BenchmarkDataset(
        config,
        train,
        test,
        lambda: _partition("final_holdout", holdout_start, config),
        checksum,
    )
