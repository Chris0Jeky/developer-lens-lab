# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError

from developer_lens_lab.finding_canonical import canonical_bytes

FINDING_VENDOR_ROOT = Path("vendor/developer-lens/research-finding/v1")
FINDING_CONTRACT_COMMIT = "d8961cdbe794edb40d2ca221a267fe2728ade5d6"
FINDING_PUBLIC_URL = "https://chris0jeky.github.io/developer-lens/?view=method-trial"
_PINNED_FILES = (
    ("schema.json", "7339ee2e85d5337f0fa1977396569aa866c4a7dc94cbdf324af05ec26f9b14ef", 29342),
    ("wbc1.fixture.json", "64f759894e92c72931bcdc19b726dfd0264aa1ddf2da3e9b328f2f266e47b84d", 4566),
)
_GATES = (
    ("baseline_selection", "Baseline selection is viable"),
    ("candidate_selection", "Candidate selection is viable"),
    ("detection_floor", "Candidate meets detection floor"),
    ("delay_budget", "Candidate meets delay budget"),
    ("false_alert_improvement", "Candidate false alerts are lower than baseline"),
    ("not_worse_detection", "Candidate detection is not worse"),
    ("confound_guard", "Candidate confound guard is measured"),
)
_DENIED_TOKEN = re.compile(
    r"@[^\s@]|(?:[A-Za-z]:\\|/|\\)[^\s\"']+|\b[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\b"
)
_DATE_TOKEN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")


class FindingError(ValueError):
    """Controlled refusal at the public finding boundary, without source-value disclosure."""


def _vendor_bytes(root: Path, name: str) -> bytes:
    root = root.resolve()
    path = root / FINDING_VENDOR_ROOT / name
    current = path
    while current != root:
        if current.is_symlink() or current.is_junction():
            raise FindingError("finding contract snapshot must not traverse links")
        current = current.parent
    try:
        with path.open("rb") as stream:
            payload = stream.read(65537)
    except OSError as exc:
        raise FindingError("finding contract snapshot is unavailable") from exc
    if len(payload) > 65536:
        raise FindingError("finding contract snapshot exceeds its size bound")
    return payload


def load_finding_contract(root: Path) -> dict[str, Any]:
    snapshots: dict[str, Any] = {}
    for name, digest, size in _PINNED_FILES:
        payload = _vendor_bytes(root, name)
        if len(payload) != size or hashlib.sha256(payload).hexdigest() != digest:
            raise FindingError("finding contract snapshot differs from the pinned producer")
        snapshots[name] = json.loads(payload)
    try:
        provenance = json.loads(_vendor_bytes(root, "provenance.json"))
    except ValueError as exc:
        raise FindingError("finding contract provenance is invalid") from exc
    expected = {
        "schema_version": "DeveloperLensContractSnapshot.v1",
        "product_commit": FINDING_CONTRACT_COMMIT,
        "files": [
            {"name": name, "sha256": "sha256:" + digest, "size_bytes": size}
            for name, digest, size in _PINNED_FILES
        ],
        "identity_semantics": "provenance_only_not_a_join_key",
    }
    if provenance != expected:
        raise FindingError("finding contract provenance differs from the pinned producer")
    return {"schema": snapshots["schema.json"], "fixture": snapshots["wbc1.fixture.json"]}


def finding_bundle_hash(value: dict[str, Any]) -> str:
    body = copy.deepcopy(value)
    try:
        body["provenance"].pop("bundle_hash", None)
        payload = canonical_bytes(body)
    except (KeyError, TypeError, AttributeError, ValueError) as exc:
        raise FindingError("finding body is not canonical JSON") from exc
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def derive_gates(value: dict[str, Any]) -> list[dict[str, Any]]:
    """Derive projection claims, not the source trial's stronger acceptance verdict."""
    metrics = {item["key"]: item for item in value["metrics"]}

    def measured(code: str, side: str) -> float | None:
        item = metrics.get(code, {}).get(side)
        return float(item["value"]) if item and item["status"] == "measured" else None

    selection = value.get("threshold_viability", {})
    detection = measured("detection_rate", "candidate")
    baseline_detection = measured("detection_rate", "baseline")
    delay = measured("median_detection_delay_weeks", "candidate")
    alerts = measured("false_alerts_per_year", "candidate")
    baseline_alerts = measured("false_alerts_per_year", "baseline")
    confound = measured("coverage_confound_false_alert_rate", "candidate")
    baseline_confound = measured("coverage_confound_false_alert_rate", "baseline")
    outcomes = [
        selection.get("baseline"),
        selection.get("candidate"),
        None if detection is None else detection >= 0.75,
        None if delay is None else delay <= 8,
        None if alerts is None or baseline_alerts is None else alerts < baseline_alerts,
        None
        if detection is None or baseline_detection is None
        else detection >= baseline_detection,
        None if confound is None or baseline_confound is None else confound <= baseline_confound,
    ]
    return [
        {"code": code, "label": label, "passed": outcomes[index]}
        for index, (code, label) in enumerate(_GATES)
    ]


def _validate_privacy(value: object, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, str):
        if path == ("provenance", "public_url") and value == FINDING_PUBLIC_URL:
            return
        if _DENIED_TOKEN.search(value) or (
            path != ("generated_at",) and _DATE_TOKEN.search(value)
        ):
            raise FindingError("finding contains a denied identity, date, or path token")
    elif isinstance(value, list):
        for item in cast(list[Any], value):
            _validate_privacy(item, path)
    elif isinstance(value, dict):
        for key, item in cast(dict[str, Any], value).items():
            _validate_privacy(item, (*path, key))


def _validate_semantics(value: dict[str, Any]) -> None:
    if value["classification"] != "C0":
        raise FindingError("the Lab finding producer supports invented C0 evidence only")
    try:
        datetime.fromisoformat(value["generated_at"].removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise FindingError("finding timestamp must be a real canonical UTC instant") from exc
    texts = (value["finding"]["title"], value["finding"]["question"], value["decision"]["summary"])
    if any(not text.strip() for text in texts):
        raise FindingError("finding text must not be blank")
    methods = value["methods"]
    baseline = methods["baseline"]["method_code"]
    candidate = methods["candidate"]["method_code"]
    if baseline == candidate or "pelt_offline" in (baseline, candidate):
        raise FindingError("finding requires distinct supported online methods")
    for name, key in (
        ("metrics", "key"),
        ("gates", "code"),
        ("limitations", "code"),
        ("unsupported_claims", "code"),
    ):
        codes = [item[key] for item in value.get(name, [])]
        if len(codes) != len(set(codes)):
            raise FindingError("finding registry entries must be unique")
    expected_gates = {gate["code"]: gate for gate in derive_gates(value)}
    gate_codes = [gate["code"] for gate in value.get("gates", [])]
    if gate_codes != sorted(gate_codes, key=list(expected_gates).index):
        raise FindingError("finding gates must use registry order")
    for gate in value.get("gates", []):
        if gate["passed"] is not expected_gates[gate["code"]]["passed"]:
            raise FindingError("finding gate must derive from its carried evidence")
    selection = value.get("threshold_viability")
    nonviable = selection is not None and not selection["baseline"] and not selection["candidate"]
    has_limitation = any(item["code"] == "thresholds_nonviable" for item in value["limitations"])
    if nonviable != has_limitation:
        raise FindingError("nonviable limitation must match both threshold selections")
    decision = value["decision"]
    if decision["outcome"] == "reject":
        worse = any(
            item["baseline"]["status"] == "measured"
            and item["candidate"]["status"] == "measured"
            and (
                item["candidate"]["value"] < item["baseline"]["value"]
                if item["better_when"] == "higher"
                else item["candidate"]["value"] > item["baseline"]["value"]
            )
            for item in value["metrics"]
        )
        failed = any(gate["passed"] is False for gate in value.get("gates", []))
        if decision["retained_fallback"] != baseline or not (worse or failed):
            raise FindingError("rejection requires negative evidence and the baseline fallback")
    elif decision["retained_fallback"] is not None:
        raise FindingError("non-reject findings must not retain a fallback")


def validate_research_finding(value: object, *, root: Path) -> dict[str, Any]:
    contract = load_finding_contract(root)
    try:
        canonical_bytes(value)
        Draft202012Validator(contract["schema"]).validate(value)
    except (ValueError, ValidationError) as exc:
        raise FindingError("finding does not satisfy the pinned structural contract") from exc
    validated = cast(dict[str, Any], value)
    _validate_semantics(validated)
    _validate_privacy(validated)
    if validated["provenance"]["bundle_hash"] != finding_bundle_hash(validated):
        raise FindingError("finding transport hash does not match its canonical body")
    return validated
