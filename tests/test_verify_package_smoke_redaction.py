"""Redaction boundary coverage for package-smoke diagnostics."""

from __future__ import annotations

from scripts.verify_package_smoke import (  # pyright: ignore[reportPrivateUsage] - direct redaction seam coverage
    _environment_values_to_redact,
)


def test_sensitive_name_matches_on_token_boundaries() -> None:
    assert _environment_values_to_redact({"KEYBOARD": "ab"}) == []
    assert _environment_values_to_redact({"API_KEY": "ab"}) == ["ab"]
