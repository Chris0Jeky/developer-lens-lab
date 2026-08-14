from __future__ import annotations

import os
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Protocol, cast

import pytest

from scripts.verify_package_smoke import (
    PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS,
    PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT,
    ProcessTreeCleanupUnconfirmedError,
    _run,  # pyright: ignore[reportPrivateUsage] - direct timeout seam coverage
    _uv_version_requirement,  # pyright: ignore[reportPrivateUsage] - config parity coverage
    assert_doctor_report,
    build_smoke_environment,
    resolve_uv_command,
    run_package_smoke,
)

ROOT = Path(__file__).resolve().parents[1]


def _path_uv(_name: str) -> str:
    return "uv-on-path"


def _stub_uv_command(*, cwd: Path, environment: dict[str, str]) -> list[str]:
    del cwd, environment
    return ["uv"]


class _WindowsByteLocker(Protocol):
    LK_NBLCK: int
    LK_UNLCK: int

    def locking(self, file_descriptor: int, mode: int, length: int) -> None: ...


class _RecordingStream:
    """A minimal invented pipe that records whether supervision released it."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


class _CompletedPopen:
    def __init__(self, returncode: int | None, stdout: str = "", stderr: str = "") -> None:
        self.pid = 4312
        self.returncode: int | None = returncode
        self._stdout = stdout
        self._stderr = stderr
        # Real Popen exposes its pipes; supervision releases them on non-timeout exits.
        self.stdout: _RecordingStream | None = None
        self.stderr: _RecordingStream | None = None
        self.stdin: _RecordingStream | None = None

    def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
        del timeout
        return self._stdout, self._stderr


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


def test_package_smoke_uv_requirement_matches_pyproject() -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert _uv_version_requirement() == metadata["tool"]["uv"]["required-version"]


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
        "scripts.verify_package_smoke._run",
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
    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", _path_uv)
    calls: list[list[str]] = []

    def version_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        version = reported_version if command == [path_uv, "--version"] else "0.12.2"
        return subprocess.CompletedProcess(command, 0, stdout=f"uv {version}\n", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke._run", version_run)

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
    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", _path_uv)

    def version_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        if command == [path_uv, "--version"]:
            if failure == "malformed":
                return subprocess.CompletedProcess(command, 0, stdout="not uv\n", stderr="")
            if failure == "nonzero":
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="broken")
            raise RuntimeError("simulated package-smoke timeout")
        return subprocess.CompletedProcess(command, 0, stdout="uv 0.12.2\n", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke._run", version_run)

    assert resolve_uv_command(cwd=tmp_path, environment={}) == module_uv


def test_package_smoke_rejects_invalid_uv_candidates_with_actionable_range(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path_uv = "uv-on-path"
    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", _path_uv)
    calls: list[list[str]] = []

    def invalid_candidates_run(
        command: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="uv 0.13.0\n", stderr="")

    monkeypatch.setattr(
        "scripts.verify_package_smoke._run",
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


def test_package_smoke_builds_wheel_from_the_emitted_sdist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[list[str]] = []
    sdist_path: Path | None = None

    monkeypatch.setattr("scripts.verify_package_smoke.resolve_uv_command", _stub_uv_command)

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        nonlocal sdist_path
        calls.append(command)
        if command[1:3] == ["build", "--sdist"]:
            sdist_path = Path(command[-1]) / "developer_lens_lab-0.1.0.tar.gz"
            sdist_path.write_bytes(b"synthetic sdist")
        elif command[1] == "build" and command[3] == "--wheel":
            assert sdist_path is not None
            assert command[2] == str(sdist_path)
            assert command[2] != str(tmp_path)
            (Path(command[-1]) / "developer_lens_lab-0.1.0-py3-none-any.whl").write_bytes(
                b"synthetic wheel"
            )
        elif command[-2:] == ["doctor", "--json"]:
            return subprocess.CompletedProcess(
                command,
                0,
                stdout='{"failures": [], "network_collection": "disabled", "ok": true}',
                stderr="",
            )
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke._run", fake_run)

    run_package_smoke(tmp_path)

    assert len(calls) == 5
    sdist_command, wheel_command, venv_command, install_command, doctor_command = calls
    assert sdist_command[0:4] == ["uv", "build", "--sdist", "--out-dir"]
    assert Path(sdist_command[-1]).name == "sdist"
    selected_sdist = Path(sdist_command[-1]) / "developer_lens_lab-0.1.0.tar.gz"
    wheel_root = Path(wheel_command[-1])
    selected_wheel = wheel_root / "developer_lens_lab-0.1.0-py3-none-any.whl"
    venv_bin = "Scripts" if os.name == "nt" else "bin"
    python_name = "python.exe" if os.name == "nt" else "python"
    dllab_name = "dllab.exe" if os.name == "nt" else "dllab"
    assert wheel_command == [
        "uv",
        "build",
        str(selected_sdist),
        "--wheel",
        "--out-dir",
        str(wheel_root),
    ]
    assert Path(wheel_command[-1]).name == "wheel"
    venv_root = Path(venv_command[-1])
    assert venv_command == ["uv", "venv", "--python", sys.executable, str(venv_root)]
    python_executable = venv_root / venv_bin / python_name
    assert install_command == [
        "uv",
        "pip",
        "install",
        "--python",
        str(python_executable),
        str(selected_wheel),
    ]
    assert doctor_command == [
        str(venv_root / venv_bin / dllab_name),
        "doctor",
        "--json",
    ]


@pytest.mark.parametrize("wheel_names", [[], ["one.whl", "two.whl"]])
def test_package_smoke_rejects_zero_or_multiple_wheels(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, wheel_names: list[str]
) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr("scripts.verify_package_smoke.resolve_uv_command", _stub_uv_command)

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        if command[1:3] == ["build", "--sdist"]:
            output_root = Path(command[-1])
            (output_root / "developer_lens_lab-0.1.0.tar.gz").write_bytes(b"synthetic sdist")
        elif command[1] == "build" and command[3] == "--wheel":
            output_root = Path(command[-1])
            for name in wheel_names:
                (output_root / name).write_bytes(b"synthetic wheel")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke._run", fake_run)

    with pytest.raises(RuntimeError, match="wheel build did not produce exactly one wheel"):
        run_package_smoke(tmp_path)

    assert len(calls) == 2
    assert calls[0][0:4] == ["uv", "build", "--sdist", "--out-dir"]
    assert calls[1][0:4] == ["uv", "build", calls[1][2], "--wheel"]
    assert all(command[1:3] != ["venv", "--python"] for command in calls)
    assert all(command[1:3] != ["pip", "install"] for command in calls)
    assert all(command[-2:] != ["doctor", "--json"] for command in calls)


@pytest.mark.parametrize("sdist_names", [[], ["one.tar.gz", "two.tar.gz"]])
def test_package_smoke_rejects_zero_or_multiple_sdists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, sdist_names: list[str]
) -> None:
    calls: list[list[str]] = []

    monkeypatch.setattr("scripts.verify_package_smoke.resolve_uv_command", _stub_uv_command)

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(command)
        if command[1:3] == ["build", "--sdist"]:
            output_root = Path(command[-1])
            for name in sdist_names:
                (output_root / name).write_bytes(b"synthetic sdist")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke._run", fake_run)

    with pytest.raises(RuntimeError, match="exactly one sdist"):
        run_package_smoke(tmp_path)

    build_calls = [command for command in calls if len(command) > 1 and command[1] == "build"]
    assert len(build_calls) == 1
    assert build_calls[0][0:4] == ["uv", "build", "--sdist", "--out-dir"]


def test_package_smoke_confines_uv_cache_and_temp_paths(tmp_path: Path) -> None:
    environment = build_smoke_environment(tmp_path)

    assert Path(environment["UV_CACHE_DIR"]).is_relative_to(tmp_path)
    assert Path(environment["TMP"]).is_relative_to(tmp_path)
    assert Path(environment["TEMP"]).is_relative_to(tmp_path)
    assert Path(environment["TMPDIR"]).is_relative_to(tmp_path)
    assert environment["UV_CONCURRENT_DOWNLOADS"] == "1"


def test_package_smoke_run_supervises_with_named_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls: list[tuple[list[str], dict[str, object]]] = []

    def fake_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        calls.append((command, kwargs))
        return _CompletedPopen(0)

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", fake_popen)

    result = _run(["uv", "build", "--wheel"], cwd=tmp_path, environment={"SAFE": "yes"})

    assert result.returncode == 0
    assert calls == [
        (
            ["uv", "build", "--wheel"],
            {
                "cwd": tmp_path,
                "env": {"SAFE": "yes"},
                "stdout": subprocess.PIPE,
                "stderr": subprocess.PIPE,
                "text": True,
                "shell": False,
                "start_new_session": os.name != "nt",
            },
        )
    ]


def test_package_smoke_run_reports_timeout_without_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class TimeoutPopen(_CompletedPopen):
        def __init__(self) -> None:
            super().__init__(None)
            self.timeouts: list[float | None] = []

        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            self.timeouts.append(timeout)
            if len(self.timeouts) == 1:
                raise subprocess.TimeoutExpired(["uv"], timeout or 0)
            self.returncode = -9
            return super().communicate(timeout=timeout)

    processes: list[TimeoutPopen] = []

    def timeout_popen(*_args: object, **_kwargs: object) -> TimeoutPopen:
        process = TimeoutPopen()
        processes.append(process)
        return process

    def successful_taskkill(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0)

    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: True)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", timeout_popen)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", successful_taskkill)
    synthetic_root = r"C:\Windows"
    monkeypatch.setenv("SYSTEMROOT", synthetic_root)

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
    assert processes[0].timeouts == [300, PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS]
    assert processes[0].returncode == -9


def test_package_smoke_timeout_uses_taskkill_and_reaps_direct_child(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class TimeoutPopen(_CompletedPopen):
        def __init__(self) -> None:
            super().__init__(None)
            self.timeouts: list[float | None] = []

        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            self.timeouts.append(timeout)
            if len(self.timeouts) == 1:
                raise subprocess.TimeoutExpired(["synthetic-tool"], timeout or 0)
            self.returncode = -9
            return super().communicate(timeout=timeout)

    taskkill_calls: list[tuple[list[str], dict[str, object]]] = []
    processes: list[TimeoutPopen] = []

    def taskkill(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        taskkill_calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)

    def timeout_popen(*_args: object, **_kwargs: object) -> TimeoutPopen:
        process = TimeoutPopen()
        processes.append(process)
        return process

    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: True)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", timeout_popen)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", taskkill)
    synthetic_root = r"C:\Windows"
    expected_taskkill = str(Path(synthetic_root) / "System32" / "taskkill.exe")
    monkeypatch.setenv("SYSTEMROOT", synthetic_root)

    with pytest.raises(RuntimeError, match="timed out after 300 seconds") as exc_info:
        _run(["synthetic-tool"], cwd=tmp_path, environment={"SAFE": "yes"})

    assert exc_info.value.__cause__ is None
    assert processes[0].timeouts == [300, PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS]
    assert processes[0].returncode == -9
    assert taskkill_calls == [
        (
            [expected_taskkill, "/PID", "4312", "/T", "/F"],
            {
                "stdin": subprocess.DEVNULL,
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "shell": False,
                "check": False,
                "timeout": PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS,
            },
        )
    ]


def test_package_smoke_timeout_fails_closed_without_raw_cleanup_details(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class TimeoutPopen(_CompletedPopen):
        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            raise subprocess.TimeoutExpired(["synthetic-tool"], timeout or 0)

    secret = "invented-secret-value"
    raw_taskkill_output = "invented-taskkill-output"

    def timeout_popen(*_args: object, **_kwargs: object) -> TimeoutPopen:
        return TimeoutPopen(None)

    def failed_taskkill(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 1, stderr=raw_taskkill_output)

    synthetic_root = r"C:\Windows"
    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: True)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", timeout_popen)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", failed_taskkill)
    # Without this the cleanup returns early on the absent-SYSTEMROOT branch, and the
    # failed-taskkill assertions below never observe the failed cleanup they name.
    monkeypatch.setenv("SYSTEMROOT", synthetic_root)

    with pytest.raises(ProcessTreeCleanupUnconfirmedError) as exc_info:
        _run(["synthetic-tool"], cwd=tmp_path, environment={"SECRET_VALUE": secret})

    message = str(exc_info.value)
    assert message == "package smoke process-tree cleanup could not be confirmed"
    assert exc_info.value.__cause__ is None
    assert secret not in message
    assert str(tmp_path) not in message
    assert "4312" not in message
    assert raw_taskkill_output not in message


def test_package_smoke_timeout_fails_closed_when_system_root_is_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class TimeoutPopen(_CompletedPopen):
        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            raise subprocess.TimeoutExpired(["synthetic-tool"], timeout or 0)

    taskkill_calls: list[list[str]] = []

    def timeout_popen(*_args: object, **_kwargs: object) -> TimeoutPopen:
        return TimeoutPopen(None)

    def unexpected_taskkill(
        command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        taskkill_calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: True)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", timeout_popen)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", unexpected_taskkill)
    monkeypatch.delenv("SYSTEMROOT", raising=False)

    with pytest.raises(ProcessTreeCleanupUnconfirmedError) as exc_info:
        _run(["synthetic-tool"], cwd=tmp_path, environment={})

    assert str(exc_info.value) == "package smoke process-tree cleanup could not be confirmed"
    assert exc_info.value.__cause__ is None
    # No unqualified taskkill may be attempted when the system root is unknown.
    assert taskkill_calls == []


def test_package_smoke_timeout_fails_closed_when_bounded_reap_times_out(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class TimeoutPopen(_CompletedPopen):
        def __init__(self) -> None:
            super().__init__(None)
            self.timeouts: list[float | None] = []

        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            self.timeouts.append(timeout)
            raise subprocess.TimeoutExpired(["synthetic-tool"], timeout or 0)

    processes: list[TimeoutPopen] = []

    def timeout_popen(*_args: object, **_kwargs: object) -> TimeoutPopen:
        process = TimeoutPopen()
        processes.append(process)
        return process

    def successful_taskkill(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess([], 0)

    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: True)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", timeout_popen)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", successful_taskkill)
    synthetic_root = r"C:\Windows"
    monkeypatch.setenv("SYSTEMROOT", synthetic_root)

    with pytest.raises(
        RuntimeError, match=r"^package smoke process-tree cleanup could not be confirmed$"
    ):
        _run(["synthetic-tool"], cwd=tmp_path, environment={})

    assert processes[0].timeouts == [300, PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS]
    assert processes[0].returncode is None


def test_package_smoke_probe_propagates_unconfirmed_cleanup_instead_of_falling_back(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    probed: list[list[str]] = []

    def unconfirmed_cleanup(
        command: list[str], *, cwd: Path, environment: dict[str, str]
    ) -> subprocess.CompletedProcess[str]:
        del cwd, environment
        probed.append(command)
        raise ProcessTreeCleanupUnconfirmedError(
            "package smoke process-tree cleanup could not be confirmed"
        )

    monkeypatch.setattr("scripts.verify_package_smoke.shutil.which", _path_uv)
    monkeypatch.setattr("scripts.verify_package_smoke._run", unconfirmed_cleanup)

    with pytest.raises(ProcessTreeCleanupUnconfirmedError):
        resolve_uv_command(cwd=tmp_path, environment={})

    # The unreaped tree must stop candidate resolution outright. An ordinary invalid
    # candidate would instead be rejected and the interpreter-module candidate probed,
    # which is what test_package_smoke_rejects_invalid_uv_candidates... asserts.
    assert probed == [["uv-on-path", "--version"]]


def test_package_smoke_run_reaps_child_when_communicate_fails_without_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class InterruptedPopen(_CompletedPopen):
        def __init__(self) -> None:
            super().__init__(None)
            self.communicate_calls = 0
            self.stdout = _RecordingStream()
            self.stderr = _RecordingStream()

        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            del timeout
            self.communicate_calls += 1
            if self.communicate_calls == 1:
                raise KeyboardInterrupt
            self.returncode = -9
            return "", ""

    processes: list[InterruptedPopen] = []
    taskkill_calls: list[list[str]] = []

    def interrupted_popen(*_args: object, **_kwargs: object) -> InterruptedPopen:
        process = InterruptedPopen()
        processes.append(process)
        return process

    def successful_taskkill(
        command: list[str], **_kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        taskkill_calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    synthetic_root = r"C:\Windows"
    expected_taskkill = str(Path(synthetic_root) / "System32" / "taskkill.exe")
    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: True)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", interrupted_popen)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.run", successful_taskkill)
    monkeypatch.setenv("SYSTEMROOT", synthetic_root)

    with pytest.raises(KeyboardInterrupt):
        _run(["synthetic-tool"], cwd=tmp_path, environment={})

    # The original exception is re-raised unchanged, but only after the tree is reaped
    # and the pipes are released; without the catch-all both would leak.
    assert taskkill_calls == [[expected_taskkill, "/PID", "4312", "/T", "/F"]]
    assert processes[0].returncode == -9
    assert processes[0].stdout is not None
    assert processes[0].stderr is not None
    assert processes[0].stdout.closed
    assert processes[0].stderr.closed


def test_package_smoke_posix_timeout_kills_its_new_process_group(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class TimeoutPopen(_CompletedPopen):
        def __init__(self) -> None:
            super().__init__(None)
            self.timeouts: list[float | None] = []

        def communicate(self, *, timeout: float | None = None) -> tuple[str, str]:
            self.timeouts.append(timeout)
            if len(self.timeouts) == 1:
                raise subprocess.TimeoutExpired(["synthetic-tool"], timeout or 0)
            self.returncode = -9
            return super().communicate(timeout=timeout)

    calls: list[tuple[int, int]] = []
    processes: list[TimeoutPopen] = []

    def timeout_popen(*_args: object, **_kwargs: object) -> TimeoutPopen:
        process = TimeoutPopen()
        processes.append(process)
        return process

    def record_killpg(pid: int, received_signal: int) -> None:
        calls.append((pid, received_signal))

    monkeypatch.setattr("scripts.verify_package_smoke._is_windows", lambda: False)
    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", timeout_popen)
    monkeypatch.setattr(
        "scripts.verify_package_smoke.os.killpg",
        record_killpg,
        raising=False,
    )
    monkeypatch.setattr("scripts.verify_package_smoke.signal.SIGKILL", 9, raising=False)

    with pytest.raises(RuntimeError, match="timed out after 300 seconds"):
        _run(["synthetic-tool"], cwd=tmp_path, environment={})

    assert calls == [(4312, 9)]
    assert processes[0].timeouts == [300, PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS]
    assert processes[0].returncode == -9


@pytest.mark.skipif(os.name != "nt", reason="Windows taskkill proof")
def test_package_smoke_timeout_removes_invented_child_grandchild_lock(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    helper = ROOT / "tests" / "helpers" / "package_smoke_process_tree.py"
    lock_path = tmp_path / "invented.lock"
    ready_path = tmp_path / "ready"
    locker = cast(_WindowsByteLocker, __import__("msvcrt"))
    monkeypatch.setattr("scripts.verify_package_smoke.PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS", 2)

    with pytest.raises(RuntimeError, match="timed out after 2 seconds"):
        _run(
            [sys.executable, str(helper), str(lock_path), str(ready_path)],
            cwd=tmp_path,
            environment=os.environ.copy(),
        )

    assert ready_path.exists()
    with lock_path.open("r+b") as lock_file:
        lock_file.seek(0)
        locker.locking(lock_file.fileno(), locker.LK_NBLCK, 1)
        locker.locking(lock_file.fileno(), locker.LK_UNLCK, 1)


def test_package_smoke_run_reports_bounded_redacted_diagnostics(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    secret = "synthetic-package-secret"

    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(
            17,
            stdout=("stdout-detail " + secret + " " + "x" * 3_000),
            stderr=("stderr-detail " + secret + " " + "y" * 3_000),
        )

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

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

    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(2, stdout=output, stderr="diagnostic\r\n")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

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

    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(3, stdout=output, stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

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


def test_package_smoke_diagnostics_redact_environment_values_before_paths(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    command_path = tmp_path / "synthetic-tool.exe"
    environment_value = f"{command_path}-environment-suffix"
    output = f"value={environment_value}\r\n"

    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(5, stdout=output, stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "build", str(command_path)],
            cwd=tmp_path,
            environment={"PATH_VALUE": environment_value},
        )

    message = str(exc_info.value)
    assert environment_value not in message
    assert "environment-suffix" not in message
    assert "value=<redacted>" in message


def test_package_smoke_diagnostics_redact_cwd_before_short_environment_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    cwd = tmp_path / "synthetic-true-project"
    command_path = cwd / "synthetic-tool.exe"
    output = f"cwd={cwd}\r\npath={command_path}\r\n"

    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(7, stdout=output, stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "build", str(command_path)],
            cwd=cwd,
            environment={"CI": "true"},
        )

    message = str(exc_info.value)
    assert f"cwd={cwd}" not in message
    assert f"path={command_path}" not in message
    assert "synthetic-<redacted>-project" not in message
    assert "cwd=<task-cwd>" in message
    assert "path=<task-path>" in message


def test_package_smoke_diagnostics_redact_short_pass_values_but_not_safe_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(6, stdout="pass=abc safe=ok", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "build"],
            cwd=tmp_path,
            environment={"DB_PASS": "abc", "SAFE_SHORT": "ok"},
        )

    message = str(exc_info.value)
    assert "pass=<redacted> safe=ok" in message
    assert "abc" not in message


def test_package_smoke_diagnostics_redact_short_pwd_values_but_not_bypass_or_compass_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(8, stdout="pwd=xyz bypass=no compass=ok", stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

    with pytest.raises(RuntimeError) as exc_info:
        _run(
            ["uv", "build"],
            cwd=tmp_path,
            environment={
                "DB_PWD": "xyz",
                "BYPASS_MODE": "no",
                "COMPASS_ENABLED": "ok",
            },
        )

    message = str(exc_info.value)
    assert "pwd=<redacted> bypass=no compass=ok" in message
    assert "xyz" not in message


def test_package_smoke_diagnostics_escape_terminal_controls_and_keep_newlines(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    output = "\x1b[31mred\x1b[0m\x1b]0;synthetic-title\x07\x00\nnext-line"

    def failed_popen(command: list[str], **kwargs: object) -> _CompletedPopen:
        del command, kwargs
        return _CompletedPopen(4, stdout=output, stderr="")

    monkeypatch.setattr("scripts.verify_package_smoke.subprocess.Popen", failed_popen)

    with pytest.raises(RuntimeError) as exc_info:
        _run(["uv", "build"], cwd=tmp_path, environment={"SAFE": "ok"})

    message = str(exc_info.value)
    assert "\x1b" not in message
    assert "\x07" not in message
    assert "\x00" not in message
    assert r"\x1b[31mred\x1b[0m\x1b]0;synthetic-title\x07\x00" in message
    assert r"\x07" in message
    assert "\nnext-line" in message
