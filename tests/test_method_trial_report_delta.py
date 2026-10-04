from __future__ import annotations

from typing import Any
from collections.abc import Mapping

from developer_lens_lab.wbc1.report import _false_alert_delta  # pyright: ignore[reportPrivateUsage]


def _view(baseline: float, candidate: float) -> Mapping[str, Any]:
    return {
        "scorecard": {
            "baseline": {"false_alerts_per_year": {"status": "measured", "value": baseline}},
            "candidate": {"false_alerts_per_year": {"status": "measured", "value": candidate}},
        }
    }


def test_improvement_uses_fewer_wording() -> None:
    result = _false_alert_delta(_view(2.0, 1.0))
    assert result == "-50.0% fewer false alerts"


def test_regression_uses_more_wording() -> None:
    result = _false_alert_delta(_view(1.0, 2.0))
    assert result == "100.0% more false alerts"
