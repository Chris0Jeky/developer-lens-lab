from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pytest

from scripts.verify_package_smoke import (
    assert_doctor_report,
    build_smoke_environment,
    resolve_uv_command,
)

ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_declares_license_identity() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]

    assert metadata["name"] == "developer-lens-lab"
    assert metadata["license"] == "AGPL-3.0-only"
    assert metadata["license-files"] == ["LICENSE"]
    assert metadata["authors"] == [{"name": "Cristian Tcaci"}]
    assert metadata["urls"]["Repository"] == "https://github.com/Chris0Jeky/developer-lens-lab"

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Developer Lens Lab" in license_text.splitlines()[:1]
    assert "SPDX-License-Identifier: AGPL-3.0-only" in license_text
    assert "GNU AFFERO GENERAL PUBLIC LICENSE" in license_text


def test_package_smoke_accepts_only_a_healthy_offline_context() -> None:
    report = assert_doctor_report('{"failures": [], "network_collection": "disabled", "ok": true}')

    assert report["ok"] is True


def test_package_smoke_rejects_context_failures() -> None:
    with pytest.raises(RuntimeError, match="valid context"):
        assert_doctor_report(
            '{"failures": ["missing file"], "network_collection": "disabled", "ok": false}'
        )


def test_package_smoke_falls_back_to_current_python_for_missing_path_uv(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def missing_uv(_name: str) -> None:
        return None

    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", missing_uv)

    assert resolve_uv_command() == [sys.executable, "-m", "uv"]


def test_package_smoke_confines_uv_cache_and_temp_paths(tmp_path: Path) -> None:
    environment = build_smoke_environment(tmp_path)

    assert Path(environment["UV_CACHE_DIR"]).is_relative_to(tmp_path)
    assert Path(environment["TMP"]).is_relative_to(tmp_path)
    assert Path(environment["TEMP"]).is_relative_to(tmp_path)
    assert Path(environment["TMPDIR"]).is_relative_to(tmp_path)
    assert environment["UV_CONCURRENT_DOWNLOADS"] == "1"
