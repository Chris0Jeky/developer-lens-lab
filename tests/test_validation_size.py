from __future__ import annotations

from pathlib import Path

import pytest

from developer_lens_lab.validation import (
    MAX_MANIFEST_BYTES,
    ManifestError,
    _load_json,
)


def _oversize_payload() -> bytes:
    return b'{"data": "' + b"x" * MAX_MANIFEST_BYTES + b'"}'


def test_oversize_at_read_rejected_when_stat_reports_small(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(_oversize_payload())
    assert manifest.stat().st_size > MAX_MANIFEST_BYTES

    class _SmallStat:
        st_size = 2

    monkeypatch.setattr(Path, "stat", lambda self: _SmallStat())

    with pytest.raises(ManifestError, match="exceeds"):
        _load_json(manifest)


def test_load_does_not_trust_stat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = tmp_path / "manifest.json"
    manifest.write_bytes(b'{"ok": true}')

    def _forbidden_stat(self: Path):  # pragma: no cover
        raise AssertionError("stat must not be consulted")

    monkeypatch.setattr(Path, "stat", _forbidden_stat)

    assert _load_json(manifest) == {"ok": True}
