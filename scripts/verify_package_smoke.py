"""Build and exercise the package wheel without touching repository state."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import cast


def resolve_uv_command() -> list[str]:
    """Use PATH uv in CI, or the current interpreter's uv module locally."""
    uv = shutil.which("uv")
    return [uv] if uv else [sys.executable, "-m", "uv"]


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
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        rendered = " ".join(command)
        raise RuntimeError(f"package smoke command failed ({result.returncode}): {rendered}")
    return result


def run_package_smoke(root: Path) -> None:
    """Build sdist/wheel and prove the wheel's CLI in an isolated environment."""
    disposable_root = root / ".package-smoke"
    disposable_root.mkdir(exist_ok=True)
    uv = resolve_uv_command()
    with tempfile.TemporaryDirectory(
        prefix="run-", dir=disposable_root, ignore_cleanup_errors=True
    ) as temporary:
        smoke_root = Path(temporary)
        environment = build_smoke_environment(smoke_root)
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
