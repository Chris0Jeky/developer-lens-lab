from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, cast

import pytest

from developer_lens_lab import finding_export
from developer_lens_lab.contracts.research_finding import (
    FindingError,
    finding_bundle_hash,
    validate_research_finding,
)
from developer_lens_lab.finding_canonical import stable_bytes

from .test_finding_export import ROOT, RUN_ID, VENDOR, seed_store


def _payload_with_title(title: str) -> bytes:
    value = json.loads((VENDOR / "wbc1.fixture.json").read_bytes())
    value["finding"]["title"] = title
    value["provenance"]["bundle_hash"] = finding_bundle_hash(value)
    return stable_bytes(value)


def _store_bytes(root: Path) -> dict[Path, bytes]:
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


@pytest.mark.parametrize("existing_output", [False, True])
def test_denied_serialized_bytes_are_refused_before_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, existing_output: bool
) -> None:
    store, _ = seed_store(tmp_path)
    before = _store_bytes(store.root)
    destination = tmp_path / "published/finding.json"
    destination.parent.mkdir()
    if existing_output:
        destination.write_bytes(b"previous output")
    denied = _payload_with_title("Invented finding in /home/invented/private.csv")

    def serialize_denied_token(_value: object) -> bytes:
        return denied

    monkeypatch.setattr(finding_export, "stable_bytes", serialize_denied_token)

    with pytest.raises(FindingError, match="denied identity, date, or path token") as error:
        finding_export.export_finding(
            RUN_ID, root=ROOT, output=destination, artifact_root=store.root
        )

    assert "private.csv" not in str(error.value)
    assert _store_bytes(store.root) == before
    assert list(destination.parent.iterdir()) == ([destination] if existing_output else [])
    if existing_output:
        assert destination.read_bytes() == b"previous output"


@pytest.mark.parametrize("defect", ["changed_value", "whitespace", "oversized", "invalid_json"])
def test_changed_temporary_file_bytes_are_refused_and_cleaned_up(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, defect: str
) -> None:
    store, _ = seed_store(tmp_path)
    before = _store_bytes(store.root)
    destination = tmp_path / "published/finding.json"
    destination.parent.mkdir()
    destination.write_bytes(b"previous output")
    replacement = {
        "changed_value": _payload_with_title("Another invented result"),
        "whitespace": (VENDOR / "wbc1.fixture.json").read_bytes() + b" ",
        "oversized": b" " * 1_048_577,
        "invalid_json": b"{",
    }[defect]
    if defect == "changed_value":
        validate_research_finding(json.loads(replacement), root=ROOT)
    original_fdopen = os.fdopen

    @contextmanager
    def alter_written_file(descriptor: int, mode: str) -> Generator[BinaryIO, None, None]:
        with original_fdopen(descriptor, mode) as stream:
            yield cast(BinaryIO, stream)
            stream.seek(0)
            stream.write(replacement)
            stream.truncate()
            stream.flush()

    monkeypatch.setattr(os, "fdopen", alter_written_file)
    expected = {
        "changed_value": "canonical payload",
        "whitespace": "canonical payload",
        "oversized": "JSON size bound",
        "invalid_json": "valid JSON object",
    }[defect]
    with pytest.raises(FindingError, match=expected):
        finding_export.export_finding(
            RUN_ID, root=ROOT, output=destination, artifact_root=store.root
        )

    assert destination.read_bytes() == b"previous output"
    assert list(destination.parent.iterdir()) == [destination]
    assert _store_bytes(store.root) == before


def test_noncanonical_serialized_bytes_are_refused_even_when_unchanged_on_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _ = seed_store(tmp_path)
    destination = tmp_path / "published/finding.json"
    destination.parent.mkdir()
    destination.write_bytes(b"previous output")
    calls = 0

    def drift_first_serialization(value: object) -> bytes:
        nonlocal calls
        calls += 1
        payload = stable_bytes(value)
        return payload.rstrip(b"\n") if calls == 1 else payload

    monkeypatch.setattr(finding_export, "stable_bytes", drift_first_serialization)
    with pytest.raises(FindingError, match="canonical payload"):
        finding_export.export_finding(
            RUN_ID, root=ROOT, output=destination, artifact_root=store.root
        )

    assert destination.read_bytes() == b"previous output"
    assert list(destination.parent.iterdir()) == [destination]


def test_actual_written_finding_is_validated_before_atomic_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, _ = seed_store(tmp_path)
    before = _store_bytes(store.root)
    destination = tmp_path / "published/finding.json"
    destination.parent.mkdir()
    destination.write_bytes(b"previous output")
    validated_written_bytes: list[bytes] = []

    def observe_validation(value: object, *, root: Path) -> dict[str, Any]:
        temporary = [path for path in destination.parent.iterdir() if path != destination]
        if temporary:
            assert len(temporary) == 1
            payload = temporary[0].read_bytes()
            assert json.loads(payload) == value
            assert destination.read_bytes() == b"previous output"
            validated_written_bytes.append(payload)
        return validate_research_finding(value, root=root)

    monkeypatch.setattr(finding_export, "validate_research_finding", observe_validation)
    result = finding_export.export_finding(
        RUN_ID, root=ROOT, output=destination, artifact_root=store.root
    )

    payload = destination.read_bytes()
    assert validated_written_bytes == [payload]
    assert payload == (VENDOR / "wbc1.fixture.json").read_bytes()
    assert result.sha256 == "sha256:" + hashlib.sha256(payload).hexdigest()
    assert list(destination.parent.iterdir()) == [destination]
    assert _store_bytes(store.root) == before
