"""Manifest presence contract for the MethodTrialView export."""

from __future__ import annotations

from pathlib import Path

import pytest

from developer_lens_lab.wbc1.export import (
    _read_series_values,  # pyright: ignore[reportPrivateUsage] - missing-field seam coverage
    compose_method_trial_view,
)


def _ref() -> dict[str, object]:
    return {
        "sha256": "sha256:" + "0" * 64,
        "size_bytes": 10,
        "media_type": "application/json",
    }


def _manifest_without_repository_week() -> dict[str, object]:
    return {
        "bundle": _ref(),
        "baseline": _ref(),
        "candidate": _ref(),
        "pelt": _ref(),
        "custody": _ref(),
        "research_pack": _ref(),
        "research_pack_coverage": _ref(),
    }


def test_empty_manifest_raises_value_error_naming_bundle(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="bundle"):
        compose_method_trial_view("missing-manifest-run", root=tmp_path, manifest={})


def test_manifest_missing_repository_week_raises_value_error(tmp_path: Path) -> None:
    manifest = _manifest_without_repository_week()
    with pytest.raises(ValueError, match="research_pack_repository_week"):
        compose_method_trial_view(
            "missing-week-run",
            root=tmp_path,
            manifest=manifest,  # type: ignore[arg-type]
        )


def test_read_series_values_missing_repository_week_raises_value_error(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="research_pack_repository_week"):
        _read_series_values(None, "missing-week-run", None, {})  # type: ignore[arg-type]
