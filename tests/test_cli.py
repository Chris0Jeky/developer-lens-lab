from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab.cli import app

ROOT = Path(__file__).resolve().parents[1]


def test_doctor_is_non_mutating(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    artifact_root = ROOT / ".dllab"
    assert not artifact_root.exists()
    result = CliRunner().invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.output
    assert '"network_collection": "disabled"' in result.output
    assert not artifact_root.exists()
