"""Build and exercise the package wheel without touching repository state."""

from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import unicodedata
from collections.abc import Callable
from pathlib import Path, PureWindowsPath
from typing import cast

PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS = 300
PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS = 10
PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT = 2_000
PACKAGE_SMOKE_DIAGNOSTIC_TRUNCATION_MARKER = "\n...[truncated]"
_PROCESS_TREE_CLEANUP_UNCONFIRMED = "package smoke process-tree cleanup could not be confirmed"
UV_VERSION_BOUNDS: tuple[tuple[int, int, int], tuple[int, int, int]] = (
    (0, 12, 2),
    (0, 13, 0),
)
_UV_VERSION_PATTERN = re.compile(r"^\s*uv\s+(?P<version>\d+\.\d+\.\d+)(?:\s|$)")


class ProcessTreeCleanupUnconfirmedError(RuntimeError):
    """Raised when a timed-out process tree could not be confirmed reaped.

    This is deliberately distinct from the generic failures a caller may treat as
    "this candidate did not work". It reports that supervision lost track of a live
    process tree, so every caller must fail closed and propagate it rather than fall
    back to another candidate and continue with an unreaped tree still running.
    """


def _canonicalize_line_endings(value: str) -> str:
    """Use one line-ending representation for diagnostics and redaction values."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _is_windows() -> bool:
    """Return whether package-smoke supervision is running on Windows."""
    return os.name == "nt"


def _environment_values_to_redact(environment: dict[str, str]) -> list[str]:
    """Return environment values that must not appear in failure diagnostics."""
    sensitive_names = (
        "auth",
        "credential",
        "cookie",
        "key",
        "password",
        "secret",
        "token",
    )
    short_secret_markers = {"pass", "pwd"}
    values = {
        _canonicalize_line_endings(value)
        for name, value in environment.items()
        if value
        and (
            len(value) >= 4
            or any(marker in name.lower() for marker in sensitive_names)
            or any(
                marker in re.split(r"[^a-z0-9]+", name.lower()) for marker in short_secret_markers
            )
        )
    }
    return sorted(values, key=lambda value: (-len(value), value))


def _replace_path(text: str, path: str, replacement: str) -> str:
    """Replace a path in either native or slash-normalized form."""
    variants = {path, path.replace("\\", "/"), path.replace("/", "\\")}
    for variant in sorted(variants, key=len, reverse=True):
        if not variant:
            continue
        windows_path = re.match(r"^[a-z]:[\\/]", variant, flags=re.IGNORECASE) is not None
        flags = re.IGNORECASE if os.name == "nt" or windows_path else 0
        text = re.sub(re.escape(variant), replacement, text, flags=flags)
    return text


def _escape_terminal_controls(value: str) -> str:
    """Render terminal/control characters visibly while preserving line breaks."""
    escaped: list[str] = []
    for character in value:
        if character == "\n":
            escaped.append(character)
        elif unicodedata.category(character) in {"Cc", "Cf"}:
            codepoint = ord(character)
            escaped.append(f"\\x{codepoint:02x}" if codepoint <= 0xFF else f"\\u{codepoint:04x}")
        else:
            escaped.append(character)
    return "".join(escaped)


def _bounded_diagnostic_stream(
    output: str, *, cwd: Path, command: list[str], environment: dict[str, str]
) -> str:
    """Normalize, redact, and cap one subprocess diagnostic stream."""
    normalized = _canonicalize_line_endings(output)
    replacements: list[tuple[str, str, int]] = [
        (value, "<redacted>", 0) for value in _environment_values_to_redact(environment)
    ]
    replacements.append((str(cwd), "<task-cwd>", 1))
    with contextlib.suppress(OSError):
        replacements.append((str(cwd.resolve()), "<task-cwd>", 1))
    replacements.extend(
        (argument, "<task-path>", 2) for argument in command if Path(argument).is_absolute()
    )
    for source, replacement, _ in sorted(
        replacements, key=lambda candidate: (-len(candidate[0]), candidate[2])
    ):
        normalized = _replace_path(normalized, source, replacement)
    normalized = _escape_terminal_controls(normalized).rstrip("\n")
    if len(normalized) <= PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT:
        return normalized
    limit = PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT - len(PACKAGE_SMOKE_DIAGNOSTIC_TRUNCATION_MARKER)
    return normalized[:limit] + PACKAGE_SMOKE_DIAGNOSTIC_TRUNCATION_MARKER


def _render_command(command: list[str]) -> str:
    """Render a command without exposing absolute task paths."""
    rendered_parts: list[str] = []
    for argument in command:
        if Path(argument).is_absolute():
            rendered_parts.append("<task-path>")
        else:
            rendered_parts.append(argument)
    return " ".join(rendered_parts)


def _format_failure_diagnostics(
    *, command: list[str], cwd: Path, environment: dict[str, str], stdout: str, stderr: str
) -> str:
    """Format deterministic bounded diagnostics for a failed subprocess."""
    stdout_text = _bounded_diagnostic_stream(
        stdout, cwd=cwd, command=command, environment=environment
    )
    stderr_text = _bounded_diagnostic_stream(
        stderr, cwd=cwd, command=command, environment=environment
    )
    return f"\nstdout:\n{stdout_text}\nstderr:\n{stderr_text}"


def _uv_version_requirement() -> str:
    minimum, maximum = UV_VERSION_BOUNDS
    minimum_text = ".".join(str(part) for part in minimum)
    maximum_text = ".".join(str(part) for part in maximum[:2])
    return f">={minimum_text},<{maximum_text}"


def _parse_uv_version(output: str) -> tuple[int, int, int] | None:
    match = _UV_VERSION_PATTERN.match(output)
    if match is None:
        return None
    parts = [int(part) for part in match.group("version").split(".")]
    return parts[0], parts[1], parts[2]


def _is_compatible_uv_version(version: tuple[int, int, int]) -> bool:
    minimum, maximum = UV_VERSION_BOUNDS
    return minimum <= version < maximum


def _probe_uv_command(command: list[str], *, cwd: Path, environment: dict[str, str]) -> bool:
    """Return whether a uv command reports a version in the required range."""
    try:
        result = _run([*command, "--version"], cwd=cwd, environment=environment)
    except ProcessTreeCleanupUnconfirmedError:
        # An unreaped process tree is not an unusable candidate. Let it escape the
        # candidate fallback so the smoke fails closed instead of starting the next
        # probe alongside a process tree that is still running.
        raise
    except (OSError, RuntimeError):
        return False
    version = _parse_uv_version(result.stdout)
    return version is not None and _is_compatible_uv_version(version)


def resolve_uv_command(*, cwd: Path, environment: dict[str, str]) -> list[str]:
    """Select a compatible PATH uv, then a compatible current-interpreter module."""
    candidates: list[list[str]] = []
    uv = shutil.which("uv")
    if uv:
        candidates.append([uv])
    candidates.append([sys.executable, "-m", "uv"])
    for candidate in candidates:
        if _probe_uv_command(candidate, cwd=cwd, environment=environment):
            return candidate
    raise RuntimeError(
        "no compatible uv command found; required uv version range is "
        f"{_uv_version_requirement()} (PATH uv and current-interpreter module were invalid)"
    )


def build_smoke_environment(smoke_root: Path) -> dict[str, str]:
    """Return an environment whose uv cache and temporary files stay in smoke_root."""
    cache_root = smoke_root / "uv-cache"
    temp_root = smoke_root / "tmp"
    cache_root.mkdir()
    temp_root.mkdir()
    environment = os.environ.copy()
    environment.update(
        {
            "TEMP": str(temp_root),
            "TMP": str(temp_root),
            "TMPDIR": str(temp_root),
            "UV_CACHE_DIR": str(cache_root),
            "UV_CONCURRENT_BUILDS": "1",
            "UV_CONCURRENT_DOWNLOADS": "1",
            "UV_CONCURRENT_INSTALLS": "1",
            "UV_NO_CONFIG": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    environment.pop("PYTHONPATH", None)
    return environment


def assert_doctor_report(output: str) -> dict[str, object]:
    """Validate the JSON contract emitted by the installed wheel's doctor command."""
    try:
        payload_raw = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError("dllab doctor --json did not emit JSON") from exc
    if not isinstance(payload_raw, dict):
        raise RuntimeError("dllab doctor --json emitted a non-object JSON value")
    payload = cast(dict[str, object], payload_raw)
    if payload.get("ok") is not True:
        raise RuntimeError("installed wheel doctor did not report a valid context")
    if payload.get("network_collection") != "disabled":
        raise RuntimeError("installed wheel doctor did not report disabled network collection")
    if payload.get("failures") != []:
        raise RuntimeError("installed wheel doctor reported context failures")
    return payload


def _run(
    command: list[str], *, cwd: Path, environment: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    # Deliberately not a `with subprocess.Popen(...)` block: Popen.__exit__ ends in an
    # unbounded wait(), which would turn the fail-closed cleanup-unconfirmed path below
    # into an indefinite hang on the very tree that could not be reaped. The explicit
    # handlers here bound every exit path instead.
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        start_new_session=not _is_windows(),
    )
    try:
        stdout, stderr = process.communicate(timeout=PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        if not _terminate_process_tree(process):
            raise ProcessTreeCleanupUnconfirmedError(_PROCESS_TREE_CLEANUP_UNCONFIRMED) from None
        rendered = _render_command(command)
        raise RuntimeError(
            "package smoke command timed out after "
            f"{PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS} seconds: {rendered}"
        ) from None
    except BaseException as exc:
        # Any other exit from communicate — notably KeyboardInterrupt — would otherwise
        # leave the child detached and its pipes open. Reap the tree on a bounded budget
        # and release the pipes; the reap runs under try/finally so a second interrupt
        # arriving during it cannot skip the pipe release. The two exit classes then
        # diverge: an ordinary Exception whose tree was not confirmed reaped must not stay
        # an OSError/RuntimeError a caller's candidate fallback can swallow, so it is
        # reported as cleanup-unconfirmed with the original exception as its cause;
        # interrupt-only exits (KeyboardInterrupt, SystemExit) propagate unchanged rather
        # than being masked by a cleanup error.
        try:
            cleanup_confirmed = _terminate_process_tree(process)
        finally:
            _close_process_streams(process)
        if isinstance(exc, Exception) and not cleanup_confirmed:
            raise ProcessTreeCleanupUnconfirmedError(_PROCESS_TREE_CLEANUP_UNCONFIRMED) from exc
        raise
    result = subprocess.CompletedProcess(command, process.returncode, stdout=stdout, stderr=stderr)
    if result.returncode:
        rendered = _render_command(command)
        diagnostics = _format_failure_diagnostics(
            command=command,
            cwd=cwd,
            environment=environment,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        raise RuntimeError(
            f"package smoke command failed ({result.returncode}): {rendered}{diagnostics}"
        )
    return result


def _close_process_streams(process: subprocess.Popen[str]) -> None:
    """Release a supervised child's pipes without masking the failure in flight."""
    for stream in (process.stdout, process.stderr, process.stdin):
        if stream is not None:
            with contextlib.suppress(OSError):
                stream.close()


def _terminate_process_tree(process: subprocess.Popen[str]) -> bool:
    """Terminate an ordinary timed-out process tree and confirm the direct child was reaped."""
    if _is_windows():
        system_root = os.environ.get("SYSTEMROOT")
        if not system_root:
            return False
        # A relative system root would resolve taskkill.exe against the current working
        # directory, so the cleanup binary is only trusted from an absolute root. The
        # flavour must be explicit rather than host-derived: this branch is reached with
        # _is_windows() forced true by the mocked supervision tests, which run on POSIX CI
        # where a host-flavoured PosixPath(r"C:\Windows") is not absolute. The semantic
        # target is a Windows path on either host, so evaluate it as one.
        if not PureWindowsPath(system_root).is_absolute():
            return False
        taskkill = Path(system_root) / "System32" / "taskkill.exe"
        try:
            cleanup = subprocess.run(
                [str(taskkill), "/PID", str(process.pid), "/T", "/F"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False,
                check=False,
                timeout=PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.TimeoutExpired):
            return False
        # taskkill reports 128 when the PID is not found: the direct child already exited
        # between the communicate timeout and this cleanup, so fall through to the
        # confirming reap below, which still gates on that direct child. The claim stops
        # there and is narrower than the POSIX ProcessLookupError below, where killpg
        # targets the whole group and so implies no group member survived. Descendants
        # orphaned by an independently exited child inside this race window are past
        # taskkill's reach with no job-object backstop here — an accepted narrow residual
        # under issue #81 item 2's fail-direction analysis.
        if cleanup.returncode not in {0, 128}:
            return False
    else:
        killpg = cast(Callable[[int, int], None] | None, getattr(os, "killpg", None))
        sigkill = cast(int | None, getattr(signal, "SIGKILL", None))
        if killpg is None or sigkill is None:
            return False
        try:
            killpg(process.pid, sigkill)
        except ProcessLookupError:
            pass
        except OSError:
            return False
    try:
        process.communicate(timeout=PACKAGE_SMOKE_CLEANUP_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return process.returncode is not None


def run_package_smoke(root: Path) -> None:
    """Build sdist/wheel and prove the wheel's CLI in an isolated environment."""
    disposable_root = root / ".package-smoke"
    disposable_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="run-", dir=disposable_root, ignore_cleanup_errors=True
    ) as temporary:
        smoke_root = Path(temporary)
        environment = build_smoke_environment(smoke_root)
        uv = resolve_uv_command(cwd=root, environment=environment)
        sdist_root = smoke_root / "sdist"
        wheel_root = smoke_root / "wheel"
        venv_root = smoke_root / "venv"
        run_root = smoke_root / "run"
        sdist_root.mkdir()
        wheel_root.mkdir()
        run_root.mkdir()

        _run(
            [*uv, "build", "--sdist", "--out-dir", str(sdist_root)],
            cwd=root,
            environment=environment,
        )
        sdists = sorted(sdist_root.glob("*.tar.gz"))
        if len(sdists) != 1:
            raise RuntimeError("source distribution build did not produce exactly one sdist")

        _run(
            [*uv, "build", str(sdists[0]), "--wheel", "--out-dir", str(wheel_root)],
            cwd=root,
            environment=environment,
        )
        wheels = sorted(wheel_root.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("wheel build did not produce exactly one wheel")

        _run(
            [*uv, "venv", "--python", sys.executable, str(venv_root)],
            cwd=root,
            environment=environment,
        )
        python_name = "python.exe" if os.name == "nt" else "python"
        python_executable = venv_root / ("Scripts" if os.name == "nt" else "bin") / python_name
        _run(
            [*uv, "pip", "install", "--python", str(python_executable), str(wheels[0])],
            cwd=root,
            environment=environment,
        )
        dllab_name = "dllab.exe" if os.name == "nt" else "dllab"
        dllab_executable = venv_root / ("Scripts" if os.name == "nt" else "bin") / dllab_name
        result = _run(
            [str(dllab_executable), "doctor", "--json"],
            cwd=run_root,
            environment=environment,
        )
        assert_doctor_report(result.stdout)


def main() -> int:
    run_package_smoke(Path(__file__).resolve().parents[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
