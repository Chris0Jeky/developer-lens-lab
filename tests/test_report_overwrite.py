# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
"""Refuse silent report overwrite unless --force is passed."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab.cli import app
from developer_lens_lab.wbc1.runner import RunnerError, build_report, run_benchmark

ROOT = Path(__file__).resolve().parents[1]


def _permit_test_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    def permit(_root: Path) -> None:
        return None

    def fixed_commit(_root: Path) -> str:
        return "a" * 40

    monkeypatch.setattr("developer_lens_lab.wbc1.runner._ensure_reproducible_tree", permit)
    monkeypatch.setattr("developer_lens_lab.wbc1.runner._git_commit", fixed_commit)


def test_second_build_without_force_fails_and_preserves_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="wbc1_overwrite")
    build_report(result.run_id, artifact_root=tmp_path)

    scope = tmp_path / "scopes" / result.scope
    before_md = (scope / "report.md").read_bytes()
    before_html = (scope / "report.html").read_bytes()

    with pytest.raises(RunnerError, match=r"report\.md"):
        build_report(result.run_id, artifact_root=tmp_path)
    with pytest.raises(RunnerError, match=r"report\.html"):
        build_report(result.run_id, artifact_root=tmp_path)
    with pytest.raises(RunnerError, match="--force"):
        build_report(result.run_id, artifact_root=tmp_path)

    assert (scope / "report.md").read_bytes() == before_md
    assert (scope / "report.html").read_bytes() == before_html


def test_rebuild_with_force_succeeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="wbc1_overwrite_force")
    first = build_report(result.run_id, artifact_root=tmp_path)

    scope = tmp_path / "scopes" / result.scope
    before_md = (scope / "report.md").read_bytes()
    before_html = (scope / "report.html").read_bytes()

    with pytest.raises(RunnerError, match="already exist"):
        build_report(result.run_id, artifact_root=tmp_path)

    second = build_report(result.run_id, artifact_root=tmp_path, force=True)

    assert second == first
    assert (scope / "report.md").read_bytes() == before_md
    assert (scope / "report.html").read_bytes() == before_html


def test_cli_second_build_requires_force(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="wbc1_overwrite_cli")
    runner = CliRunner()

    first = runner.invoke(app, ["report", "build", result.run_id, "--artifact-root", str(tmp_path)])
    assert first.exit_code == 0, first.output

    scope = tmp_path / "scopes" / result.scope
    before_md = (scope / "report.md").read_bytes()
    before_html = (scope / "report.html").read_bytes()

    second = runner.invoke(
        app, ["report", "build", result.run_id, "--artifact-root", str(tmp_path)]
    )
    assert second.exit_code != 0
    assert "report.md" in second.output or "report.md" in getattr(second, "stderr", "")
    assert (scope / "report.md").read_bytes() == before_md
    assert (scope / "report.html").read_bytes() == before_html

    third = runner.invoke(
        app,
        ["report", "build", result.run_id, "--artifact-root", str(tmp_path), "--force"],
    )
    assert third.exit_code == 0, third.output
    assert (scope / "report.md").read_bytes() == before_md
    assert (scope / "report.html").read_bytes() == before_html


@pytest.mark.parametrize("name", ["report.md", "report.html"])
def test_concurrent_report_creation_preserves_writer_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    from developer_lens_lab.artifacts import ArtifactError, ArtifactRef, ArtifactStore

    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="wbc1_race")
    original = ArtifactStore.get_bytes
    sentinel = b"concurrent writer sentinel"

    def create_before_write(self: ArtifactStore, scope_id: str, reference: ArtifactRef) -> bytes:
        payload = original(self, scope_id, reference)
        if scope_id == result.scope and reference.media_type in ("text/markdown", "text/html"):
            (self.scope_root(scope_id) / name).write_bytes(sentinel)
        return payload

    monkeypatch.setattr(ArtifactStore, "get_bytes", create_before_write)
    with pytest.raises(ArtifactError, match="already exists"):
        build_report(result.run_id, artifact_root=tmp_path)
    assert (tmp_path / "scopes" / result.scope / name).read_bytes() == sentinel
