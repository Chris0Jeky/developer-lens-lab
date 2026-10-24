from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab import cli
from developer_lens_lab.contract_sync import ContractSyncError
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


def _seed_distinct_originals(root: Path) -> dict[Path, bytes]:
    originals = {
        target: f"original {index} {target.name}\n".encode()
        for index, target in enumerate(_targets(root))
    }
    for target, content in originals.items():
        target.parent.mkdir(parents=True)
        target.write_bytes(content)
    return originals


def test_render_replaces_distinct_originals_byte_identically(tmp_path: Path) -> None:
    _seed_distinct_originals(tmp_path)

    render_schemas(tmp_path)

    for target, expected in rendered_schemas(tmp_path).items():
        assert target.read_bytes() == expected.encode()
    assert check_schemas(tmp_path) == ()


def test_second_replace_failure_restores_both_distinct_originals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    originals = _seed_distinct_originals(tmp_path)
    first, second = _targets(tmp_path)
    real_replace = os.replace
    first_replaced: list[bool] = []

    def fail_second(src: str | Path, dst: str | Path) -> None:
        if Path(dst) == second:
            raise OSError("injected second replacement fault")
        real_replace(src, dst)
        first_replaced.append(Path(dst) == first)

    monkeypatch.setattr(os, "replace", fail_second)
    with pytest.raises(OSError, match="injected second replacement fault"):
        render_schemas(tmp_path)

    assert any(first_replaced)  # the first schema really was updated, then rolled back
    for target, content in originals.items():
        assert target.read_bytes() == content
    assert list(tmp_path.rglob("*.tmp")) == []


def _link(path: Path, target: Path, kind: str) -> None:
    if kind == "junction":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(path), str(target)],
            capture_output=True,
            check=False,
        )
        if result.returncode:
            pytest.skip("directory junctions are unavailable on this host")
        assert path.is_junction()
        return
    try:
        path.symlink_to(target, target_is_directory=target.is_dir())
    except OSError:
        pytest.skip("symlinks are unavailable on this host")


def test_render_refuses_linked_destination(tmp_path: Path) -> None:
    root = tmp_path / "root"
    originals = _seed_distinct_originals(root)
    first, second = _targets(root)
    outside = tmp_path / "outside.json"
    outside.write_bytes(b"outside bytes")
    second.unlink()
    _link(second, outside, "symlink")

    with pytest.raises(ContractSyncError, match=r"symlink|junction"):
        render_schemas(root)

    assert outside.read_bytes() == b"outside bytes"
    assert first.read_bytes() == originals[first]
    assert list(root.rglob("*.tmp")) == []


@pytest.mark.parametrize(
    "kind",
    [
        "symlink",
        pytest.param("junction", marks=pytest.mark.skipif(os.name != "nt", reason="Windows")),
    ],
)
def test_render_refuses_linked_parent_without_outside_writes(tmp_path: Path, kind: str) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "schemas").mkdir(parents=True)
    _link(root / "schemas/evaluation-bundle", outside, kind)

    with pytest.raises(ContractSyncError, match=r"symlink|junction"):
        render_schemas(root)

    assert list(outside.iterdir()) == []
    assert not _targets(root)[0].exists()


def test_render_refuses_destination_reported_as_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    originals = _seed_distinct_originals(tmp_path)
    linked = _targets(tmp_path)[1]
    real_is_symlink = Path.is_symlink

    def is_symlink(path: Path) -> bool:
        return path == linked or real_is_symlink(path)

    monkeypatch.setattr(Path, "is_symlink", is_symlink)

    with pytest.raises(ContractSyncError, match=r"symlink|junction"):
        render_schemas(tmp_path)

    for target, content in originals.items():
        assert target.read_bytes() == content
