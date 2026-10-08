from __future__ import annotations

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab import cli
from developer_lens_lab.schemas import check_schemas, render_schemas, rendered_schemas


def _targets(root: Path) -> list[Path]:
    return [
        root / "schemas/research-pack/v1/consumer.schema.json",
        root / "schemas/evaluation-bundle/v1/schema.json",
    ]


def test_render_writes_both_schemas_current(tmp_path: Path) -> None:
    render_schemas(tmp_path)

    for target in _targets(tmp_path):
        assert target.is_file()
    assert check_schemas(tmp_path) == ()
    assert set(rendered_schemas(tmp_path)) == set(_targets(tmp_path))


def test_render_is_atomic_when_second_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    render_schemas(tmp_path)
    before = {target: target.read_bytes() for target in _targets(tmp_path)}
    real_replace = os.replace

    def fail_second(src: str | Path, dst: str | Path) -> None:
        if "evaluation-bundle" in str(dst):
            raise OSError("injected write fault")
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", fail_second)
    with pytest.raises(OSError, match="injected write fault"):
        render_schemas(tmp_path)

    for target in _targets(tmp_path):
        assert target.read_bytes() == before[target]
    assert list(tmp_path.rglob("*.tmp")) == []


def test_contracts_render_reports_write_fault_without_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    render_schemas(tmp_path)
    before = {target: target.read_bytes() for target in _targets(tmp_path)}
    real_replace = os.replace

    def fail_second(src: str | Path, dst: str | Path) -> None:
        if "evaluation-bundle" in str(dst):
            raise OSError("injected write fault")
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", fail_second)
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    result = CliRunner().invoke(cli.app, ["contracts", "render"])

    assert result.exit_code == 1
    assert "ERROR" in result.stderr
    assert "Traceback" not in result.output
    assert not isinstance(result.exception, OSError)
    for target in _targets(tmp_path):
        assert target.read_bytes() == before[target]


def test_render_aborts_when_existing_schema_snapshot_is_unreadable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    render_schemas(tmp_path)
    targets = _targets(tmp_path)
    targets[0].write_bytes(b"original schema requiring preservation")
    before = {target: target.read_bytes() for target in targets}
    real_read = Path.read_bytes
    real_replace = os.replace

    def fail_snapshot(path: Path) -> bytes:
        if path == targets[0]:
            raise PermissionError("injected snapshot fault")
        return real_read(path)

    def fail_second(src: str | Path, dst: str | Path) -> None:
        if dst == targets[1]:
            raise OSError("injected replacement fault")
        real_replace(src, dst)

    monkeypatch.setattr(Path, "read_bytes", fail_snapshot)
    monkeypatch.setattr(os, "replace", fail_second)
    with pytest.raises(PermissionError, match="injected snapshot fault"):
        render_schemas(tmp_path)

    for target in targets:
        assert real_read(target) == before[target]
    assert list(tmp_path.rglob("*.tmp")) == []
