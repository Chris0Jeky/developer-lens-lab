# pyright: reportPrivateUsage=false
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from developer_lens_lab.wbc1 import runner
from developer_lens_lab.wbc1.runner import RunnerError


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True, text=True, cwd=repo)


def test_headless_checkout_raises_runner_error(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.txt").write_text("alpha\n", encoding="utf-8")
    _git(tmp_path, "add", "a.txt")
    # No commit: git status succeeds but git rev-parse HEAD exits nonzero.
    with pytest.raises(RunnerError, match="readable Git commit"):
        runner._git_commit(tmp_path)


def test_rev_parse_failure_raises_runner_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _fail(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.CalledProcessError(128, ["git", "rev-parse", "HEAD"])

    monkeypatch.setattr(runner.subprocess, "run", _fail)
    with pytest.raises(RunnerError, match="readable Git commit"):
        runner._git_commit(tmp_path)


def test_git_executable_missing_raises_runner_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _missing(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        raise OSError("git executable not found")

    monkeypatch.setattr(runner.subprocess, "run", _missing)
    with pytest.raises(RunnerError, match="readable Git commit"):
        runner._git_commit(tmp_path)
