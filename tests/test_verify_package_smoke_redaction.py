"""Redaction boundary coverage for package-smoke diagnostics."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.verify_package_smoke import (
    _bounded_diagnostic_stream,  # pyright: ignore[reportPrivateUsage] - diagnostic seam coverage
    _environment_values_to_redact,  # pyright: ignore[reportPrivateUsage] - redaction seam coverage
)


def test_sensitive_name_matches_on_token_boundaries() -> None:
    assert _environment_values_to_redact({"KEYBOARD": "ab"}) == []
    assert _environment_values_to_redact({"API_KEY": "ab"}) == ["ab"]


@pytest.mark.parametrize(
    "name", ["APIKEY", "PASSWORD2", "API_KEY2", "CREDENTIALS", "SECRETKEY", "MYKEY", "TOKEN2"]
)
def test_affixed_sensitive_names_redact_short_values(name: str, tmp_path: Path) -> None:
    assert (
        _bounded_diagnostic_stream(
            "value=ab", cwd=tmp_path, command=["synthetic"], environment={name: "ab"}
        )
        == "value=<redacted>"
    )


@pytest.mark.parametrize("name", ["MYPASS", "MYPWD", "PWD2", "DB_PASS"])
def test_short_secret_markers_redact_affixed_names(name: str, tmp_path: Path) -> None:
    assert _environment_values_to_redact({name: "ab"}) == ["ab"]
    assert (
        _bounded_diagnostic_stream(
            "value=ab", cwd=tmp_path, command=["synthetic"], environment={name: "ab"}
        )
        == "value=<redacted>"
    )
