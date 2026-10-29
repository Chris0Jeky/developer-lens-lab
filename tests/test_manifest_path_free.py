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


@pytest.mark.parametrize(
    "value",
    [
        "~invented/out.parquet",
        r"~invented\out.parquet",
        "~invented_name/out.parquet",
        r"~invented-name\out.parquet",
        "~invented.name/",
        "~invented\\",
        "  ~invented/out.parquet  ",
        "\t~invented\\out.parquet\r\n",
    ],
)
def test_user_home_prefixes_are_rejected_without_echoing_values(value: str) -> None:
    for candidate in (value, {"note": value}, {"nested": [{"note": value}]}):
        with pytest.raises(ManifestError) as exc_info:
            assert_path_free_manifest(candidate)
        assert str(exc_info.value) == "manifest contains a local path"


@pytest.mark.parametrize(
    "value",
    [
        "~",
        "~invented",
        "  ~invented  ",
        "notes~invented/out.parquet",
        r"reports\~invented\out.parquet",
        "reports/~invented/out.parquet",
        "about ~invented/out.parquet",
        "~approximate value/ratio",
    ],
)
def test_embedded_tildes_and_bare_names_remain_path_free(value: str) -> None:
    for candidate in (value, {"note": value}, {"nested": [{"note": value}]}):
        assert_path_free_manifest(candidate)
