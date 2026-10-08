from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab.cli import app

from .test_finding_export import ROOT, RUN_ID, seed_store


def test_finding_command_reads_stored_artifacts_without_analysis(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _ = seed_store(tmp_path)
    monkeypatch.chdir(ROOT)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("finding export must not invoke analysis or replay")

    monkeypatch.setattr("developer_lens_lab.wbc1.runner.run_benchmark", forbidden)
    monkeypatch.setattr("developer_lens_lab.wbc1.runner.reproduce_run", forbidden)
    monkeypatch.setattr("developer_lens_lab.wbc1.export.compose_method_trial_view", forbidden)
    output = tmp_path / "finding.json"
    result = CliRunner().invoke(
        app,
        ["export", "finding", RUN_ID, "--out", str(output), "--artifact-root", str(store.root)],
    )
    assert result.exit_code == 0, result.output
    assert "bundle_hash=sha256:" in result.output
    assert output.is_file()


def test_finding_command_refuses_unknown_run_without_creating_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(ROOT)
    output = tmp_path / "absent/finding.json"
    result = CliRunner().invoke(
        app,
        [
            "export",
            "finding",
            "../private",
            "--out",
            str(output),
            "--artifact-root",
            str(tmp_path / "store"),
        ],
    )
    assert result.exit_code == 1
    assert "../private" not in result.output
    assert not output.parent.exists()
