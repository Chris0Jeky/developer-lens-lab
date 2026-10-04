from __future__ import annotations

import pytest

from developer_lens_lab.validation import ManifestError, assert_path_free_manifest


@pytest.mark.parametrize(
    "value",
    [
        ".",
        "./reports/out.parquet",
        ".\\reports\\out.parquet",
        "a/./b",
    ],
)
def test_dot_segments_rejected(value: str) -> None:
    with pytest.raises(ManifestError):
        assert_path_free_manifest(value)


@pytest.mark.parametrize(
    "value",
    [
        "out.parquet",
        "reports/out.parquet",
        "reports\\out.parquet",
        "my.file",
    ],
)
def test_benign_names_pass_through(value: str) -> None:
    assert_path_free_manifest(value) is None
