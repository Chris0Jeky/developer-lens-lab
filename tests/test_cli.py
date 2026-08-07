import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from developer_lens_lab.cli import app

ROOT = Path(__file__).resolve().parents[1]


def _artifact_snapshot(root: Path) -> tuple[tuple[str, str], ...] | None:
    if not root.exists():
        return None
    return tuple(
        (path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
        for path in sorted(root.rglob("*"))
        if path.is_file()
    )


def test_doctor_is_non_mutating(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    artifact_root = ROOT / ".dllab"
    before = _artifact_snapshot(artifact_root)
    result = CliRunner().invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0, result.output
    assert '"network_collection": "disabled"' in result.output
    assert _artifact_snapshot(artifact_root) == before


def test_demo_export_uses_explicit_output_and_content_free_result(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    output = tmp_path / "view.json"

    def fake_export(run_id: str, *, output: Path, root: Path) -> SimpleNamespace:
        assert run_id == "run-demo-01"
        output.write_bytes(b"{}\n")
        return SimpleNamespace(output_path=output, sha256="sha256:" + "a" * 64)

    monkeypatch.setattr("developer_lens_lab.cli.export_method_trial", fake_export)
    monkeypatch.chdir(ROOT)
    result = CliRunner().invoke(app, ["demo", "export", "run-demo-01", "--output", str(output)])
    assert result.exit_code == 0, result.output
    assert f"path={output}" in result.output
    assert "sha256:" + "a" * 64 in result.output
