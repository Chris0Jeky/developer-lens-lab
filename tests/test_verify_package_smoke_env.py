"""Smoke environment reuse coverage.

Calling build_smoke_environment twice on the same path must never leak a raw
FileExistsError: the second call either reuses the existing directories or
fails closed with a RuntimeError stating the smoke root is already
initialised.
"""

from __future__ import annotations

from pathlib import Path

from scripts.verify_package_smoke import build_smoke_environment


def test_build_smoke_environment_second_call_reuses_or_raises_runtime_error(
    tmp_path: Path,
) -> None:
    first = build_smoke_environment(tmp_path)

    try:
        second = build_smoke_environment(tmp_path)
    except FileExistsError:
        raise AssertionError(
            "second build_smoke_environment call raised raw FileExistsError"
        ) from None
    except RuntimeError as exc:
        assert "already initi" in str(exc).lower()
        return

    assert Path(second["UV_CACHE_DIR"]) == Path(first["UV_CACHE_DIR"])
    assert Path(second["TMP"]) == Path(first["TMP"])
    assert Path(second["UV_CACHE_DIR"]).is_dir()
    assert Path(second["TMP"]).is_dir()
