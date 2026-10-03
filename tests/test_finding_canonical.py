from __future__ import annotations

import math

import pytest

from developer_lens_lab.finding_canonical import canonical_bytes, stable_bytes


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0.0, "0"),
        (-0.0, "0"),
        (1.0, "1"),
        (333333333.33333329, "333333333.3333333"),
        (1e30, "1e+30"),
        (4.50, "4.5"),
        (2e-3, "0.002"),
        (1e-6, "0.000001"),
        (1e-7, "1e-7"),
        (5e-324, "5e-324"),
        (1e20, "100000000000000000000"),
        (1e21, "1e+21"),
        (1.234e-5, "0.00001234"),
        (1.152921504606847e18, "1152921504606847000"),
    ],
)
def test_ecmascript_number_vectors(value: float, expected: str) -> None:
    assert canonical_bytes(value) == expected.encode()


def test_utf16_key_order_and_json_escaping() -> None:
    assert canonical_bytes({"\ue000": 1, "😀": '\n\t"\\', "a": [True, None]}) == (
        '{"a":[true,null],"😀":"\\n\\t\\"\\\\","\ue000":1}'.encode()
    )


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, b"bytes", {1: "key"}, "\ud800"])
def test_invalid_json_values_are_refused(value: object) -> None:
    with pytest.raises(ValueError):
        canonical_bytes(value)


def test_pretty_output_matches_producer_conventions() -> None:
    assert stable_bytes({"b": 1.0, "a": [False, 1e-7]}) == (
        b'{\n  "a": [\n    false,\n    1e-7\n  ],\n  "b": 1\n}\n'
    )
