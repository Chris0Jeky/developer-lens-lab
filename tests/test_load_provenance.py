from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from developer_lens_lab.wbc1.export import load_provenance


def _vendor_dirs(root: Path) -> tuple[Path, Path]:
    method_dir = root / "vendor" / "developer-lens" / "method-trial-view" / "v1"
    research_dir = root / "vendor" / "developer-lens" / "research-pack" / "v1"
    method_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)
    return method_dir, research_dir


def _write_provenance(directory: Path, payload: dict[str, Any]) -> None:
    (directory / "provenance.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _descriptor(payload: bytes) -> dict[str, Any]:
    return {
        "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
        "size_bytes": len(payload),
    }


def test_happy_path_returns_both_dicts(tmp_path: Path) -> None:
    method_dir, research_dir = _vendor_dirs(tmp_path)
    payload = b'{"hello": "world"}'
    (method_dir / "contract.json").write_bytes(payload)
    method = {"files": [{"name": "contract.json", **_descriptor(payload)}]}
    research: dict[str, Any] = {"files": []}
    _write_provenance(method_dir, method)
    _write_provenance(research_dir, research)
    loaded_method, loaded_research = load_provenance(tmp_path)
    assert loaded_method == method
    assert loaded_research == research


def test_traversal_is_rejected(tmp_path: Path) -> None:
    method_dir, research_dir = _vendor_dirs(tmp_path)
    payload = b"outside"
    (tmp_path / "outside.json").write_bytes(payload)
    method = {"files": [{"name": "../../../../outside.json", **_descriptor(payload)}]}
    _write_provenance(method_dir, method)
    _write_provenance(research_dir, {"files": []})
    with pytest.raises(ValueError, match="unsafe file"):
        load_provenance(tmp_path)


@pytest.mark.parametrize(
    "bad_name",
    ["sub/x.json", "/absolute.json", "..", "", None],
    ids=["nested", "absolute", "dotdot", "empty", "missing"],
)
def test_unsafe_names_rejected(tmp_path: Path, bad_name: str | None) -> None:
    method_dir, research_dir = _vendor_dirs(tmp_path)
    if bad_name is None:
        entry: dict[str, Any] = {**_descriptor(b"x")}
    else:
        entry = {"name": bad_name, **_descriptor(b"x")}
    _write_provenance(method_dir, {"files": [entry]})
    _write_provenance(research_dir, {"files": []})
    with pytest.raises(ValueError, match="unsafe file"):
        load_provenance(tmp_path)


def test_provenance_decodes_utf8(tmp_path: Path) -> None:
    method_dir, research_dir = _vendor_dirs(tmp_path)
    method: dict[str, Any] = {"files": [], "note": "café"}
    _write_provenance(method_dir, method)
    _write_provenance(research_dir, {"files": []})
    loaded_method, _ = load_provenance(tmp_path)
    assert loaded_method == method
    assert loaded_method["note"] == "café"
