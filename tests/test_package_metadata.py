from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from scripts.verify_package_smoke import (
    PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS,
    PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT,
    _run,  # pyright: ignore[reportPrivateUsage] - direct timeout seam coverage
    assert_doctor_report,
    build_smoke_environment,
    resolve_uv_command,
    run_package_smoke,
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
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def missing_uv(_name: str) -> None:
        return None

    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", missing_uv)

    def valid_module_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 0, stdout="uv 0.12.2\n", stderr="")

    monkeypatch.setattr(
        "scripts.verify_package_smoke.subprocess.run",
        valid_module_run,
    )

    assert resolve_uv_command(cwd=tmp_path, environment={}) == [sys.executable, "-m", "uv"]


@pytest.mark.parametrize(
    ("reported_version", "compatible"),
    [("0.12.2", True), ("0.12.4", True), ("0.12.1", False), ("0.13.0", False)],
)
def test_package_smoke_validates_uv_version_bounds(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    reported_version: str,
    compatible: bool,
) -> None:
    path_uv = "uv-on-path"
    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", lambda _name: path_uv)
    calls: list[list[str]] = []

    def version_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        version = reported_version if command == [path_uv, "--version"] else "0.12.2"
        return subprocess.CompletedProcess(command, 0, stdout=f"uv {version}\n", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", version_run)

    result = resolve_uv_command(cwd=tmp_path, environment={})

    expected = [path_uv] if compatible else [sys.executable, "-m", "uv"]
    assert result == expected
    assert calls == [
        [path_uv, "--version"],
        *([] if compatible else [[sys.executable, "-m", "uv", "--version"]]),
    ]


@pytest.mark.parametrize("failure", ["malformed", "nonzero", "timeout"])
def test_package_smoke_invalid_path_uv_uses_valid_module_fallback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, failure: str
) -> None:
    path_uv = "uv-on-path"
    module_uv = [sys.executable, "-m", "uv"]
    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", lambda _name: path_uv)

    def version_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        if command == [path_uv, "--version"]:
            if failure == "malformed":
                return subprocess.CompletedProcess(command, 0, stdout="not uv\n", stderr="")
            if failure == "nonzero":
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="broken")
            raise subprocess.TimeoutExpired(command, 300)
        return subprocess.CompletedProcess(command, 0, stdout="uv 0.12.2\n", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", version_run)

    assert resolve_uv_command(cwd=tmp_path, environment={}) == module_uv


def test_package_smoke_rejects_invalid_uv_candidates_with_actionable_range(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path_uv = "uv-on-path"
    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", lambda _name: path_uv)
    calls: list[list[str]] = []

    def invalid_candidates_run(
        command: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="uv 0.13.0\n", stderr="")

    monkeypatch.setattr(
        "scripts.verify_package_smoke.subprocess.run",
        invalid_candidates_run,
    )

    with pytest.raises(RuntimeError, match=r">=0\.12\.2,<0\.13"):
        resolve_uv_command(cwd=tmp_path, environment={})
    assert calls == [[path_uv, "--version"], [sys.executable, "-m", "uv", "--version"]]


def test_package_smoke_validates_uv_before_build(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []

    def unavailable_uv(*, cwd: Path, environment: dict[str, str]) -> list[str]:
        del cwd, environment
        raise RuntimeError("no compatible uv command found")

    monkeypatch.setattr("scripts.verify_package_smoke.resolve_uv_command", unavailable_uv)

    def unexpected_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr(
        "scripts.verify_package_smoke._run",
        unexpected_run,
    )

    with pytest.raises(RuntimeError, match="no compatible uv command"):
        run_package_smoke(tmp_path)

    assert calls == []


def test_package_smoke_confines_uv_cache_and_temp_paths(tmp_path: Path) -> None:
    environment = build_smoke_environment(tmp_path)

    assert Path(environment["UV_CACHE_DIR"]).is_relative_to(tmp_path)
    assert Path(environment["TMP"]).is_relative_to(tmp_path)
    assert Path(environment["TEMP"]).is_relative_to(tmp_path)
    assert Path(environment["TMPDIR"]).is_relative_to(tmp_path)
    assert environment["UV_CONCURRENT_DOWNLOADS"] == "1"


def test_package_smoke_run_passes_named_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", fake_run)

    result = _run(["uv", "build", "--wheel"], cwd=tmp_path, environment={"SAFE": "yes"})

    assert result.returncode == 0
    assert calls == [
        (
            ["uv", "build", "--wheel"],
            {
                "cwd": tmp_path,
                "env": {"SAFE": "yes"},
                "capture_output": True,
                "text": True,
                "check": False,
                "timeout": PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS,
            },
        )
    ]


def test_package_smoke_run_reports_timeout_without_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def timeout_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        raise subprocess.TimeoutExpired(command, PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS)

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", timeout_run)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "pip", "install", "package.whl"],
            cwd=tmp_path,
            environment={"SECRET_VALUE": "must-not-appear"},
        )

    message = str(exc_info.value)
    assert (
        message == "package smoke command timed out after 300 seconds: uv pip install package.whl"
    )
    assert "must-not-appear" not in message


def test_package_smoke_run_reports_bounded_redacted_diagnostics(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    secret = "synthetic-package-secret"

    def failed_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(
            command,
            17,
            stdout=("stdout-detail " + secret + " " + "x" * 3_000),
            stderr=("stderr-detail " + secret + " " + "y" * 3_000),
        )

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", failed_run)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "build", str(tmp_path / "package.whl")],
            cwd=tmp_path,
            environment={"SECRET_VALUE": secret, "SAFE_VALUE": "synthetic-safe"},
        )

    message = str(exc_info.value)
    assert message.startswith("package smoke command failed (17): uv build <task-path>")
    assert "stdout:\nstdout-detail <redacted>" in message
    assert "stderr:\nstderr-detail <redacted>" in message
    assert secret not in message
    assert str(tmp_path) not in message
    assert "x" * 3_000 not in message
    assert "y" * 3_000 not in message
    assert len(message.split("stdout:\n", 1)[1].split("\nstderr:\n", 1)[0]) <= (
        PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT
    )
    assert len(message.split("\nstderr:\n", 1)[1]) <= PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT


def test_package_smoke_failure_diagnostics_are_deterministic(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    command = ["uv", "build"]
    output = f"failed in {tmp_path}\r\n"

    def failed_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 2, stdout=output, stderr="diagnostic\r\n")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", failed_run)

    def failure_message(environment: dict[str, str]) -> str:
        with pytest.raises(RuntimeError) as exc_info:
            _run(command, cwd=tmp_path, environment=environment)
        return str(exc_info.value)

    first = failure_message({"SECOND": "synthetic-second", "FIRST": "synthetic-first"})
    second = failure_message({"FIRST": "synthetic-first", "SECOND": "synthetic-second"})

    assert first == second
    assert first == (
        "package smoke command failed (2): uv build\n"
        "stdout:\nfailed in <task-cwd>\n"
        "stderr:\ndiagnostic"
    )


def test_package_smoke_diagnostics_redact_canonical_multiline_path_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    native_path = r"C:\Synthetic\secret-root"
    slash_swapped_path = native_path.replace("\\", "/")
    multiline_secret = "synthetic-line-one\r\nsynthetic-line-two"
    output = f"path={slash_swapped_path}\r\nvalue={multiline_secret}\r\n"

    def failed_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 3, stdout=output, stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", failed_run)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "build"],
            cwd=tmp_path,
            environment={"SECRET_PATH": native_path, "MULTILINE_TOKEN": multiline_secret},
        )

    message = str(exc_info.value)
    assert native_path not in message
    assert slash_swapped_path not in message
    assert "synthetic-line-one\r\nsynthetic-line-two" not in message
    assert "path=<redacted>\nvalue=<redacted>" in message


def test_package_smoke_diagnostics_escape_terminal_controls_and_keep_newlines(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    output = "\x1b[31mred\x1b[0m\x1b]0;synthetic-title\x07\x00\nnext-line"

    def failed_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 4, stdout=output, stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", failed_run)

    with pytest.raises(RuntimeError) as exc_info:
        _run(["uv", "build"], cwd=tmp_path, environment={"SAFE": "ok"})

    message = str(exc_info.value)
    assert "\x1b" not in message
    assert "\x07" not in message
    assert "\x00" not in message
    assert r"\x1b[31mred\x1b[0m\x1b]0;synthetic-title\x07\x00" in message
    assert r"\x07" in message
    assert "\nnext-line" in message
