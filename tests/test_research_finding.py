from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from developer_lens_lab.contracts.research_finding import (
    FindingError,
    derive_gates,
    finding_bundle_hash,
    load_finding_contract,
    validate_research_finding,
)
from developer_lens_lab.finding_canonical import stable_bytes

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor/developer-lens/research-finding/v1"


def fixture() -> dict[str, Any]:
    return json.loads((VENDOR / "wbc1.fixture.json").read_bytes())


def signed(value: dict[str, Any]) -> dict[str, Any]:
    value["provenance"]["bundle_hash"] = finding_bundle_hash(value)
    return value


def test_exact_producer_fixture_conformance() -> None:
    value = fixture()
    assert finding_bundle_hash(value) == (
        "sha256:070bf161dbd7fa5bcb858d484024de69f315550ce8692776b241899d54c4cf35"
    )
    assert validate_research_finding(value, root=ROOT) == value
    assert stable_bytes(value) == (VENDOR / "wbc1.fixture.json").read_bytes()
    assert load_finding_contract(ROOT)["schema"]["additionalProperties"] is False


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("classification",), "C1"),
        (("finding", "title"), " "),
        (("finding", "question"), "\t"),
        (("decision", "summary"), " "),
        (("decision", "retained_fallback"), "bocpd_gaussian"),
        (
            ("methods", "candidate"),
            {"method_code": "rolling_median_mad", "display_name": "Rolling median and MAD"},
        ),
        (
            ("methods", "candidate"),
            {"method_code": "pelt_offline", "display_name": "PELT descriptive marker"},
        ),
        (("generated_at",), "2026-02-30T00:00:00Z"),
        (("generated_at",), "2026-08-30T00:00:00+00:00"),
        (("finding", "title"), "Contact @invented"),
        (("finding", "title"), "Contact @_7"),
        (("finding", "title"), "invented@☀"),
        (("finding", "title"), "C:\\private\\invented"),
        (("finding", "question"), "owner/repository"),
        (("decision", "summary"), "Observed on 2026-08-30"),
        (("provenance", "public_url"), "https://example.invalid"),
        (("provenance", "unknown"), "private"),
    ],
)
def test_structural_semantic_and_privacy_refusals(
    path: tuple[str, ...], replacement: object
) -> None:
    value = fixture()
    parent = value
    for part in path[:-1]:
        parent = parent[part]
    parent[path[-1]] = replacement
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)


@pytest.mark.parametrize("index", range(7))
def test_gate_values_must_derive_from_carried_evidence(index: int) -> None:
    value = fixture()
    value["gates"][index]["passed"] = not value["gates"][index]["passed"]
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)


@pytest.mark.parametrize("name", ["metrics", "gates", "limitations", "unsupported_claims"])
def test_duplicate_codes_are_refused(name: str) -> None:
    value = fixture()
    value[name].append(copy.deepcopy(value[name][0]))
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)


def test_gate_order_and_transport_tampering_are_refused() -> None:
    value = fixture()
    value["gates"].reverse()
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)
    value = fixture()
    value["finding"]["title"] = "Changed title"
    with pytest.raises(FindingError):
        validate_research_finding(value, root=ROOT)


def test_missing_measurements_derive_null_gates_not_zero_or_false() -> None:
    value = fixture()
    value.pop("threshold_viability")
    value["limitations"] = value["limitations"][:-1]
    value["metrics"][0]["candidate"] = {"status": "unavailable"}
    value["metrics"][2]["candidate"] = {"status": "unavailable"}
    value["metrics"][3]["candidate"] = {"status": "unavailable"}
    value["gates"] = derive_gates(value)
    assert [gate["passed"] for gate in value["gates"]] == [
        None,
        None,
        None,
        None,
        False,
        None,
        None,
    ]
    validate_research_finding(signed(value), root=ROOT)


def test_false_alert_projection_is_weaker_than_source_preregistration() -> None:
    value = fixture()
    value["metrics"][1]["baseline"]["value"] = 3.0
    value["metrics"][1]["candidate"]["value"] = 2.9
    assert derive_gates(value)[4]["passed"] is True


@pytest.mark.parametrize("present", [True, False])
def test_nonviable_limitation_tracks_evidence_even_without_selection_gates(present: bool) -> None:
    value = fixture()
    value["gates"] = value["gates"][2:]
    if present:
        value["threshold_viability"]["candidate"] = True
    else:
        value["limitations"] = value["limitations"][:-1]
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)


@pytest.mark.parametrize("outcome", ["revise_once", "benchmarked"])
def test_nonreject_does_not_retain_fallback_or_assert_promotion(outcome: str) -> None:
    value = fixture()
    value["decision"]["outcome"] = outcome
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)
    value["decision"]["retained_fallback"] = None
    validate_research_finding(signed(value), root=ROOT)


def test_reject_requires_negative_metric_or_failed_gate() -> None:
    value = fixture()
    value["gates"] = []
    for metric in value["metrics"]:
        metric["candidate"] = copy.deepcopy(metric["baseline"])
    with pytest.raises(FindingError):
        validate_research_finding(signed(value), root=ROOT)


@pytest.mark.parametrize("name", ["schema.json", "wbc1.fixture.json", "provenance.json"])
def test_corrupt_vendor_bytes_are_refused(tmp_path: Path, name: str) -> None:
    destination = tmp_path / "vendor/developer-lens/research-finding/v1"
    destination.mkdir(parents=True)
    for source in VENDOR.glob("*.json"):
        (destination / source.name).write_bytes(source.read_bytes())
    (destination / name).write_text("{}", encoding="utf-8")
    with pytest.raises(FindingError):
        load_finding_contract(tmp_path)
