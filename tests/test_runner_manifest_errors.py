"""Stored run-manifest failures stay controlled and cannot publish reports."""

from __future__ import annotations

import traceback
from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab.artifacts import ArtifactError, ArtifactStore
from developer_lens_lab.cli import app
from developer_lens_lab.wbc1 import runner

RUN_ID = "manifest_error_run"
CANARY = "invented-private-manifest-content"
FAILURES = (
    "malformed_json",
    "invalid_utf8",
    "integer_limit",
    "nesting_limit",
    "non_object",
    "missing",
    "directory",
    "unreadable",
)


def _stored_manifest(root: Path, monkeypatch: pytest.MonkeyPatch, failure: str) -> Path:
    store = ArtifactStore(root)
    path = store.scope_root(RUN_ID) / "run.json"
    if failure == "missing":
        return path
    if failure == "directory":
        path.mkdir(parents=True)
        return path
    payloads = {
        "malformed_json": f'{{"note":"{CANARY}",'.encode(),
        "invalid_utf8": CANARY.encode() + b"\xff",
        "integer_limit": b'{"unused":' + b"1" * 5_000 + b"}",
        "nesting_limit": b'{"unused":' + b"[" * 10_000 + b"0" + b"]" * 10_000 + b"}",
        "non_object": f'"{CANARY}"'.encode(),
        "unreadable": b"{}",
    }
    store.write_scope_file_once(RUN_ID, "run.json", payloads[failure])
    if failure == "unreadable":
        read_text = Path.read_text

        def fail_read(self: Path, *, encoding: str) -> str:
            if self == path:
                raise PermissionError(13, CANARY, str(path))
            return read_text(self, encoding=encoding)

        monkeypatch.setattr(Path, "read_text", fail_read)
    return path


def _files(root: Path) -> dict[Path, bytes]:
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.mark.parametrize("operation", ["report", "reproduce"])
@pytest.mark.parametrize("failure", FAILURES)
def test_stored_manifest_failure_is_controlled_and_does_not_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, operation: str, failure: str
) -> None:
    manifest_path = _stored_manifest(tmp_path, monkeypatch, failure)
    before = _files(tmp_path)

    with pytest.raises(runner.RunnerError, match="run manifest") as caught:
        if operation == "report":
            runner.build_report(RUN_ID, artifact_root=tmp_path)
        else:
            runner.reproduce_run(manifest_path, root=tmp_path)

    diagnostic = "".join(traceback.format_exception(caught.value))
    assert str(tmp_path) not in diagnostic
    assert CANARY not in diagnostic
    assert "ValueError:" not in diagnostic
    assert "RecursionError:" not in diagnostic
    assert _files(tmp_path) == before


@pytest.mark.parametrize("failure", FAILURES)
def test_report_cli_manifest_failure_has_sanitized_diagnostic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    _stored_manifest(tmp_path, monkeypatch, failure)
    before = _files(tmp_path)

    result = CliRunner().invoke(app, ["report", "build", RUN_ID, "--artifact-root", str(tmp_path)])

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "ERROR: report build failed: run manifest" in result.stderr
    assert str(tmp_path) not in result.output
    assert CANARY not in result.output
    assert "Traceback" not in result.output
    assert _files(tmp_path) == before


@pytest.mark.parametrize("failure", ["malformed_json", "integer_limit", "nesting_limit"])
def test_corrupt_manifest_cannot_overwrite_existing_reports_with_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    manifest_path = _stored_manifest(tmp_path, monkeypatch, failure)
    (manifest_path.parent / "report.md").write_bytes(b"existing markdown\n")
    (manifest_path.parent / "report.html").write_bytes(b"existing html\n")
    before = _files(tmp_path)

    with pytest.raises(runner.RunnerError, match="run manifest"):
        runner.build_report(RUN_ID, artifact_root=tmp_path, force=True)

    assert _files(tmp_path) == before


def test_report_preserves_artifact_scope_errors(tmp_path: Path) -> None:
    with pytest.raises(ArtifactError, match="opaque lowercase identifier"):
        runner.build_report("invalid/scope", artifact_root=tmp_path)

    assert _files(tmp_path) == {}
