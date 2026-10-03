from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from developer_lens_lab.contracts import EvaluationBundle
from developer_lens_lab.finding_source import (
    validate_recorded_provenance,
    validate_snapshot,
    validate_study_identity,
)

from .factories import evaluation_bundle

ROOT = Path(__file__).resolve().parents[1]
BASELINE_PARAMETERS = "sha256:72aa597050c5199c88208a5d021f9a50a439079d4d0d03b1d0afc6677bfeb88c"
CANDIDATE_PARAMETERS = "sha256:2ec6875a7ee96a825c3227a1b262076a45f46d29f32467a358a0940a171cb5be"


def registered_bundle() -> dict[str, Any]:
    value = evaluation_bundle()
    value["bundle_id"] = value["run_manifest"]["run_id"]
    value["preregistration"]["primary_metric_code"] = "false_alerts_per_year"
    value["dataset_card"]["generator_revision"] = "wbc1.generator.v1"
    for side, digest in (("baseline", BASELINE_PARAMETERS), ("candidate", CANDIDATE_PARAMETERS)):
        value[f"{side}_results"]["metrics"][0]["metric_code"] = "false_alerts_per_year"
        value[f"{side}_model_card"].update(
            method_revision="wbc1.methods.v1", parameter_sha256=digest
        )
    return value


def snapshots() -> dict[str, dict[str, Any]]:
    return {
        key: json.loads((ROOT / "vendor/developer-lens" / name / "v1/provenance.json").read_bytes())
        for key, name in (
            ("method_trial_view", "method-trial-view"),
            ("research_pack", "research-pack"),
        )
    }


def test_registered_study_is_accepted() -> None:
    validate_study_identity(EvaluationBundle.model_validate_json(json.dumps(registered_bundle())))


@pytest.mark.parametrize(
    ("section", "field", "replacement"),
    [
        ("preregistration", "acceptance_rule_code", "different_acceptance"),
        ("preregistration", "abstention_rule_code", "different_abstention"),
        ("dataset_card", "generator_code", "different_generator"),
        ("dataset_card", "generator_revision", "wbc1.generator.v2"),
        ("baseline_model_card", "method_revision", "wbc1.methods.v2"),
        ("candidate_model_card", "method_revision", "wbc1.methods.v2"),
        ("baseline_model_card", "parameter_sha256", "sha256:" + "a" * 64),
        ("candidate_model_card", "parameter_sha256", "sha256:" + "a" * 64),
        ("baseline_model_card", "no_model_fallback_code", "different_fallback"),
        ("candidate_model_card", "no_model_fallback_code", "different_fallback"),
    ],
)
def test_unregistered_protocol_is_refused(section: str, field: str, replacement: str) -> None:
    value = registered_bundle()
    value[section][field] = replacement
    bundle = EvaluationBundle.model_validate_json(json.dumps(value))
    with pytest.raises(ValueError, match="study semantics"):
        validate_study_identity(bundle)


def test_bundle_identity_must_equal_run_identity() -> None:
    value = registered_bundle()
    value["bundle_id"] = "another_bundle"
    with pytest.raises(ValueError, match="identity"):
        validate_study_identity(EvaluationBundle.model_validate_json(json.dumps(value)))


def test_registered_parameters_match_wbc1_defaults() -> None:
    from developer_lens_lab.wbc1.methods import (
        DEFAULT_BASELINE_PARAMETERS,
        DEFAULT_BOCPD_PARAMETERS,
        parameters_sha256,
    )

    assert parameters_sha256(DEFAULT_BASELINE_PARAMETERS) == BASELINE_PARAMETERS
    assert parameters_sha256(DEFAULT_BOCPD_PARAMETERS) == CANDIDATE_PARAMETERS


@pytest.mark.parametrize("name", ["research-pack", "method-trial-view"])
def test_snapshot_is_validated_against_fixed_file_bytes(name: str) -> None:
    directory = ROOT / "vendor/developer-lens" / name / "v1"
    provenance = json.loads((directory / "provenance.json").read_bytes())
    names = (
        ("schema.json",) if name == "method-trial-view" else ("invented.fixture.json", "schema.json")
    )
    payloads = {filename: (directory / filename).read_bytes() for filename in names}
    validate_snapshot(provenance, payloads)
    payloads["schema.json"] += b" "
    with pytest.raises(ValueError):
        validate_snapshot(provenance, payloads)


@pytest.mark.parametrize("defect", ["missing", "extra", "commit", "identity", "version", "file"])
def test_snapshot_refuses_incomplete_or_untrusted_metadata(defect: str) -> None:
    provenance = snapshots()["method_trial_view"]
    directory = ROOT / "vendor/developer-lens/method-trial-view/v1"
    if defect == "missing":
        provenance["files"] = []
    elif defect == "extra":
        provenance["unknown"] = "private"
    elif defect == "commit":
        provenance["product_commit"] = "main"
    elif defect == "identity":
        provenance["identity_semantics"] = "join_key"
    elif defect == "version":
        provenance["schema_version"] = "unknown"
    else:
        provenance["files"][0]["name"] = "../../private"
    with pytest.raises(ValueError):
        validate_snapshot(provenance, {"schema.json": (directory / "schema.json").read_bytes()})


@pytest.mark.parametrize(
    "defect",
    [
        "none",
        "record_missing",
        "method_missing",
        "research_missing",
        "method_changed",
        "research_changed",
        "method_commit",
        "research_commit",
        "schema_digest",
    ],
)
def test_recorded_provenance_is_required_even_without_view(defect: str) -> None:
    verified = snapshots()
    manifest: dict[str, Any] = {
        "provenance": copy.deepcopy(verified),
        "product_contract_commit": verified["method_trial_view"]["product_commit"],
        "product_commit": verified["research_pack"]["product_commit"],
        "producer_schema_sha256": next(
            item["sha256"]
            for item in verified["research_pack"]["files"]
            if item["name"] == "schema.json"
        ),
    }
    if defect == "none":
        assert (
            validate_recorded_provenance(manifest, verified) == manifest["product_contract_commit"]
        )
        return
    if defect == "record_missing":
        manifest.pop("provenance")
    elif defect.endswith("_missing"):
        key = "method_trial_view" if defect == "method_missing" else "research_pack"
        manifest["provenance"].pop(key)
    elif defect.endswith("_changed"):
        key = "method_trial_view" if defect == "method_changed" else "research_pack"
        manifest["provenance"][key]["product_commit"] = "a" * 40
    else:
        field = {
            "method_commit": "product_contract_commit",
            "research_commit": "product_commit",
            "schema_digest": "producer_schema_sha256",
        }[defect]
        manifest[field] = "sha256:" + "a" * 64 if defect == "schema_digest" else "a" * 40
    with pytest.raises(ValueError):
        validate_recorded_provenance(manifest, verified)
