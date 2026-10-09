from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from developer_lens_lab.validation import (
    MAX_MANIFEST_BYTES,
    ManifestError,
    _load_json,  # pyright: ignore[reportPrivateUsage]
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

    def small_stat(self: Path) -> _SmallStat:
        return _SmallStat()

    monkeypatch.setattr(Path, "stat", small_stat)

    with pytest.raises(ManifestError, match="exceeds"):
        _load_json(manifest)


@pytest.mark.parametrize("size", [MAX_MANIFEST_BYTES - 1, MAX_MANIFEST_BYTES])
def test_load_accepts_manifest_within_byte_limit(tmp_path: Path, size: int) -> None:
    manifest = tmp_path / "manifest.json"
    payload = b'{"ok": true}'
    manifest.write_bytes(payload + b" " * (size - len(payload)))
    assert _load_json(manifest) == {"ok": True}


def test_load_bounds_read_before_rejecting_oversize(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def read(size: int = -1) -> bytes:
        assert 0 <= size <= MAX_MANIFEST_BYTES + 1, "unbounded manifest read"
        return b"x" * size

    opened = MagicMock()
    opened.return_value.__enter__.return_value.read.side_effect = read
    monkeypatch.setattr(Path, "open", opened)
    with pytest.raises(ManifestError, match="exceeds"):
        _load_json(tmp_path / "manifest.json")
