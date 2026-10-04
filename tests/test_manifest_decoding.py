from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from developer_lens_lab.validation import (
    ManifestError,
    validate_evaluation_bundle,
    validate_research_pack,
)


def test_non_utf8_pack_manifest_raises_manifest_error(tmp_path: Path) -> None:
    path = tmp_path / "pack.json"
    path.write_bytes(b"\xff\xfe{}")
    with pytest.raises(ManifestError, match="not valid UTF-8"):
        validate_research_pack(path)


def test_non_utf8_bundle_manifest_raises_manifest_error(tmp_path: Path) -> None:
    path = tmp_path / "bundle.json"
    path.write_bytes(b"\xff\xfe{}")
    with pytest.raises(ManifestError, match="not valid UTF-8"):
        validate_evaluation_bundle(path)


def test_non_utf8_error_names_the_file(tmp_path: Path) -> None:
    path = tmp_path / "pack.json"
    path.write_bytes(b"\xff\xfe{}")
    with pytest.raises(ManifestError) as excinfo:
        validate_research_pack(path)
    assert path.name in str(excinfo.value)


@pytest.mark.parametrize("validator", [validate_research_pack, validate_evaluation_bundle])
def test_non_utf8_error_omits_parent_path(
    tmp_path: Path, validator: Callable[[Path], object]
) -> None:
    path = tmp_path / "invented-private-directory" / "manifest.json"
    path.parent.mkdir()
    path.write_bytes(b"\xff\xfe{}")
    with pytest.raises(ManifestError) as excinfo:
        validator(path)
    assert str(path.parent) not in str(excinfo.value)
