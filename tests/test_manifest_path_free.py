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
        "a\\.\\b",
        "reports/.",
        "reports\\.",
        "a/.\\b",
        "a\\./b",
        " reports/. ",
    ],
)
def test_dot_segments_rejected(value: str) -> None:
    with pytest.raises(ManifestError):
        assert_path_free_manifest(value)
    with pytest.raises(ManifestError):
        assert_path_free_manifest({"note": [value]})


@pytest.mark.parametrize(
    "value",
    [
        "out.parquet",
        "reports/out.parquet",
        "reports\\out.parquet",
        "my.file",
        "reports/.hidden",
        "reports\\.hidden",
        "release.v1/out.parquet",
    ],
)
def test_benign_names_pass_through(value: str) -> None:
    assert_path_free_manifest(value)
