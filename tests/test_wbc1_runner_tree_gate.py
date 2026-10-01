# pyright: reportPrivateUsage=false
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from developer_lens_lab.wbc1 import runner
from developer_lens_lab.wbc1.runner import RunnerError


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], check=True, capture_output=True, text=True, cwd=repo)


def _commit(repo: Path) -> None:
    _git(
        repo,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "-q",
        "-m",
        "init",
    )


def _init_clean_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    (repo / "a.txt").write_text("alpha\n", encoding="utf-8")
    _git(repo, "add", "a.txt")
    _commit(repo)


def test_clean_committed_tree_passes(tmp_path: Path) -> None:
    _init_clean_repo(tmp_path)
    assert runner._ensure_reproducible_tree(tmp_path) is None


def test_untracked_file_rejected(tmp_path: Path) -> None:
    _init_clean_repo(tmp_path)
    (tmp_path / "b.txt").write_text("beta\n", encoding="utf-8")
    with pytest.raises(RunnerError, match="clean"):
        runner._ensure_reproducible_tree(tmp_path)


def test_modified_tracked_file_rejected(tmp_path: Path) -> None:
    _init_clean_repo(tmp_path)
    (tmp_path / "a.txt").write_text("alpha changed\n", encoding="utf-8")
    with pytest.raises(RunnerError, match="clean"):
        runner._ensure_reproducible_tree(tmp_path)


def test_gitignored_file_is_allowed(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore")
    _commit(tmp_path)
    (tmp_path / "ignored.txt").write_text("noise\n", encoding="utf-8")
    assert runner._ensure_reproducible_tree(tmp_path) is None


def test_non_git_directory_rejected(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    with pytest.raises(RunnerError, match="readable Git worktree"):
        runner._ensure_reproducible_tree(plain)
