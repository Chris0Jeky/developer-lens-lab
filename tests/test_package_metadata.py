from __future__ import annotations

import tomllib
from pathlib import Path

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
