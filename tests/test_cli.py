import hashlib
from pathlib import Path

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
