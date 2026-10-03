from __future__ import annotations

from typing import Any

import pytest

from developer_lens_lab.contracts.research_finding import FindingError, finding_bundle_hash
from developer_lens_lab.finding_canonical import canonical_bytes, stable_bytes


@pytest.mark.parametrize(
    "value",
    ["x" * 65537, [None] * 4097, {"x" * 65537: None}, ["x" * 1024] * 65],
    ids=["large_string", "wide_array", "large_key", "aggregate_text"],
)
def test_transport_refuses_excessive_width_and_text(value: object) -> None:
    with pytest.raises(ValueError):
        canonical_bytes(value)
    with pytest.raises(ValueError):
        stable_bytes(value)


def test_hash_refuses_large_unknown_fields_before_copying(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    value: dict[str, Any] = {"provenance": {}, "unknown": [None] * 4097}

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("unbounded input reached deepcopy")

    monkeypatch.setattr("developer_lens_lab.contracts.research_finding.copy.deepcopy", forbidden)
    with pytest.raises(FindingError):
        finding_bundle_hash(value)


def test_cyclic_input_fails_without_unbounded_traversal() -> None:
    value: list[Any] = []
    value.append(value)
    with pytest.raises(ValueError):
        canonical_bytes(value)
