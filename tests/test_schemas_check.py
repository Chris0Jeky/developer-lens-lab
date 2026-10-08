from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from developer_lens_lab import cli
from developer_lens_lab.schemas import check_schemas, render_schemas


def test_check_schemas_reports_missing_without_traceback(tmp_path: Path) -> None:
    failures = check_schemas(tmp_path)

    assert failures
    assert any(str(Path("schemas/research-pack/v1/consumer.schema.json")) in f for f in failures)
    assert any("missing/unreadable" in f for f in failures)


def test_check_schemas_reports_unreadable_without_traceback(tmp_path: Path) -> None:
    render_schemas(tmp_path)
    consumer = tmp_path / "schemas/research-pack/v1/consumer.schema.json"
    consumer.write_bytes(b"\xff\xfe\xfd not valid utf-8 \x80")

    failures = check_schemas(tmp_path)

    assert any("consumer.schema.json" in f for f in failures)
    assert any("missing/unreadable" in f for f in failures)


@pytest.mark.parametrize("command", [["contracts", "check"], ["doctor"], ["context", "verify"]])
@pytest.mark.parametrize("broken", ["missing", "invalid_utf8", "directory"])
def test_cli_schema_failure_exits_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, command: list[str], broken: str
) -> None:
    render_schemas(tmp_path)
    consumer = tmp_path / "schemas/research-pack/v1/consumer.schema.json"
    if broken == "invalid_utf8":
        consumer.write_bytes(b"\xff")
    else:
        consumer.unlink()
        if broken == "directory":
            consumer.mkdir()
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    result = CliRunner().invoke(cli.app, command)

    assert result.exit_code == 1
    assert "ERROR" in result.stderr
    assert "missing/unreadable" in result.stderr
    assert "consumer.schema.json" in result.stderr
    assert "Traceback" not in result.output
    assert not isinstance(result.exception, (OSError, UnicodeDecodeError))


def test_check_schemas_current_and_drifted(tmp_path: Path) -> None:
    render_schemas(tmp_path)
    assert check_schemas(tmp_path) == ()
    consumer = tmp_path / "schemas/research-pack/v1/consumer.schema.json"
    consumer.write_text("{}", encoding="utf-8")
    assert check_schemas(tmp_path) == (
        f"drifted generated schema: {consumer.relative_to(tmp_path)}",
    )
