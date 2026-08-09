"""Build and exercise the package wheel without touching repository state."""

from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import cast

PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS = 300
PACKAGE_SMOKE_DIAGNOSTIC_STREAM_LIMIT = 2_000
PACKAGE_SMOKE_DIAGNOSTIC_TRUNCATION_MARKER = "\n...[truncated]"
UV_VERSION_BOUNDS: tuple[tuple[int, int, int], tuple[int, int, int]] = (
    (0, 12, 2),
    (0, 13, 0),
)
_UV_VERSION_PATTERN = re.compile(r"^\s*uv\s+(?P<version>\d+\.\d+\.\d+)(?:\s|$)")


def _canonicalize_line_endings(value: str) -> str:
    """Use one line-ending representation for diagnostics and redaction values."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _environment_values_to_redact(environment: dict[str, str]) -> list[str]:
    """Return environment values that must not appear in failure diagnostics."""
    sensitive_names = (
        "auth",
        "credential",
        "cookie",
        "key",
        "pass",
        "password",
        "secret",
        "token",
    )
    values = {
        _canonicalize_line_endings(value)
        for name, value in environment.items()
        if value and (len(value) >= 4 or any(marker in name.lower() for marker in sensitive_names))
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
    for value in _environment_values_to_redact(environment):
        normalized = _replace_path(normalized, value, "<redacted>")
    cwd_path = str(cwd)
    normalized = _replace_path(normalized, cwd_path, "<task-cwd>")
    with contextlib.suppress(OSError):
        normalized = _replace_path(normalized, str(cwd.resolve()), "<task-cwd>")
    for argument in command:
        if Path(argument).is_absolute():
            normalized = _replace_path(normalized, argument, "<task-path>")
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
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        rendered = _render_command(command)
        raise RuntimeError(
            "package smoke command timed out after "
            f"{PACKAGE_SMOKE_COMMAND_TIMEOUT_SECONDS} seconds: {rendered}"
        ) from exc
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
        distribution_root = smoke_root / "dist"
        venv_root = smoke_root / "venv"
        run_root = smoke_root / "run"
        distribution_root.mkdir()
        run_root.mkdir()

        _run(
            [*uv, "build", "--sdist", "--wheel", "--out-dir", str(distribution_root)],
            cwd=root,
            environment=environment,
        )
        wheels = sorted(distribution_root.glob("*.whl"))
        sdists = sorted(distribution_root.glob("*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            raise RuntimeError("package build did not produce one wheel and one sdist")

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
