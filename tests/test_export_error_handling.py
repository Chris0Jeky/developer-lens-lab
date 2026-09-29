"""Export error contract: missing/corrupt artifacts must yield ERROR + exit 1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

import developer_lens_lab.cli as cli_module
from developer_lens_lab.cli import app

RUN_ID = "missing_artifact_run"


def _missing_artifact_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a fake repo root with a scope whose bundle object is absent."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'fake'\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# fake\n", encoding="utf-8")
    scope_dir = tmp_path / ".dllab" / "scopes" / RUN_ID
    scope_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "bundle": {
            "sha256": "sha256:" + "0" * 64,
            "size_bytes": 10,
            "media_type": "application/json",
        }
    }
    (scope_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(cli_module, "_repo_root", lambda: tmp_path)
    return tmp_path


def test_export_method_trial_missing_artifact_reports_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _missing_artifact_root(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(app, ["export", "method-trial", RUN_ID])
    assert result.exit_code == 1
    assert result.output.startswith("ERROR:")
    assert "Traceback" not in result.output


def test_demo_export_missing_artifact_reports_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _missing_artifact_root(tmp_path, monkeypatch)
    runner = CliRunner()
    result = runner.invoke(app, ["demo", "export", RUN_ID, "--output", str(tmp_path / "view.json")])
    assert result.exit_code == 1
    assert result.output.startswith("ERROR:")
    assert "Traceback" not in result.output
