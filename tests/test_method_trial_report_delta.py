from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest

from developer_lens_lab.wbc1.report import _false_alert_delta  # pyright: ignore[reportPrivateUsage]


def _view(baseline: float | None, candidate: float | None) -> Mapping[str, Any]:
    return {
        "scorecard": {
            "baseline": {"false_alerts_per_year": {"status": "measured", "value": baseline}},
            "candidate": {"false_alerts_per_year": {"status": "measured", "value": candidate}},
        }
    }


@pytest.mark.parametrize(("candidate", "magnitude"), [(1.0, "50.0"), (0.0, "100.0")])
def test_improvement_uses_fewer_wording(candidate: float, magnitude: str) -> None:
    result = _false_alert_delta(_view(2.0, candidate))
    assert result == f"{magnitude}% fewer false alerts"


def test_regression_uses_more_wording() -> None:
    result = _false_alert_delta(_view(1.0, 2.0))
    assert result == "100.0% more false alerts"


def test_equal_values_use_no_change_wording() -> None:
    assert _false_alert_delta(_view(2.0, 2.0)) == "no change in false alerts"


@pytest.mark.parametrize(
    ("baseline", "candidate"),
    [(0.0, 0.0), (0.0, 1.0), (None, 1.0), (1.0, None), (None, None)],
)
def test_undefined_delta_stays_unavailable(
    baseline: float | None, candidate: float | None
) -> None:
    assert _false_alert_delta(_view(baseline, candidate)) == "unavailable"


@pytest.mark.parametrize("side", ["baseline", "candidate"])
@pytest.mark.parametrize(
    "metrics",
    [
        {},
        {"false_alerts_per_year": {"status": "measured"}},
        {"false_alerts_per_year": {"status": "unavailable", "reason": "not_applicable"}},
    ],
)
def test_missing_or_unavailable_metric_stays_unavailable(
    side: str, metrics: dict[str, Any]
) -> None:
    view = dict(_view(2.0, 1.0))
    view["scorecard"][side] = metrics
    assert _false_alert_delta(view) == "unavailable"
