from __future__ import annotations

import json
from pathlib import Path

import pytest

from developer_lens_lab.wbc1 import runner
from developer_lens_lab.wbc1.runner import RunnerError, run_benchmark


def _allow_dirty_tree(_root: Path) -> None:
    pass


def _write_vendor(root: Path, *, schema_bytes: bytes, provenance_text: str) -> None:
    vendor = root / "vendor" / "developer-lens" / "research-pack" / "v1"
    vendor.mkdir(parents=True, exist_ok=True)
    (vendor / "invented.fixture.json").write_bytes(b"{}")
    (vendor / "schema.json").write_bytes(schema_bytes)
    (vendor / "provenance.json").write_text(provenance_text, encoding="utf-8")


def test_corrupt_schema_raises_runner_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_vendor(
        tmp_path,
        schema_bytes=b"{ {{",
        provenance_text=json.dumps({"files": []}),
    )
    monkeypatch.setattr(runner, "_ensure_reproducible_tree", _allow_dirty_tree)
    with pytest.raises(RunnerError):
        run_benchmark(root=tmp_path)


@pytest.mark.parametrize(
    "provenance_text",
    [
        json.dumps({"files": "x"}),
        json.dumps({"files": [{"name": "invented.fixture.json"}]}),
        json.dumps([]),
    ],
    ids=["files-is-string", "entry-missing-fields", "provenance-is-list"],
)
def test_bad_provenance_shape_raises_runner_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, provenance_text: str
) -> None:
    _write_vendor(
        tmp_path,
        schema_bytes=b"{}",
        provenance_text=provenance_text,
    )
    monkeypatch.setattr(runner, "_ensure_reproducible_tree", _allow_dirty_tree)
    with pytest.raises(RunnerError):
        run_benchmark(root=tmp_path)
