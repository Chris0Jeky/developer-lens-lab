from __future__ import annotations

import numpy as np

from developer_lens_lab.wbc1.generator import build_benchmark_dataset
from developer_lens_lab.wbc1.methods import bocpd_scores, rolling_median_mad_scores


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
