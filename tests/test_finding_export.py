from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from developer_lens_lab.artifacts import ArtifactStore, canonical_json_bytes
from developer_lens_lab.contracts import ArtifactRef, EvaluationBundle
from developer_lens_lab.contracts.research_finding import FindingError
from developer_lens_lab.finding_canonical import stable_bytes
from developer_lens_lab.finding_export import compose_finding, export_finding

from .test_finding_source import registered_bundle, snapshots

ROOT = Path(__file__).resolve().parents[1]
VENDOR = ROOT / "vendor/developer-lens/research-finding/v1"
PIN = "b48fea579936671397a0486ae7a0342197ee6e4b"
RUN_ID = "wbc1_demo"


def custody_evidence(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "event": "final_holdout_custody",
        "run_id": bundle["run_manifest"]["run_id"],
        "generator_revision": "wbc1.generator.v1",
        "dataset_sha256": "sha256:" + "d" * 64,
        "evaluation_plan_sha256": "sha256:" + "e" * 64,
        "baseline_threshold": 2.5,
        "candidate_threshold": 0.05,
        "baseline_parameters_sha256": bundle["baseline_model_card"]["parameter_sha256"],
        "candidate_parameters_sha256": bundle["candidate_model_card"]["parameter_sha256"],
    }


def source_evidence() -> tuple[dict[str, Any], dict[str, Any]]:
    """Invent linked evidence; never claim to reconstruct historical bundle or receipt bytes."""
    view_path = ROOT / "release-assets/v0.1.0/method-trial-v1/method-trial-view.v1.json"
    view = json.loads(view_path.read_bytes())
    bundle = registered_bundle()
    bundle["bundle_id"] = RUN_ID
    bundle["created_at"] = "2026-08-30T00:00:00Z"
    bundle["run_manifest"]["run_id"] = RUN_ID
    bundle["run_manifest"]["lab_commit"] = view["reproducibility"]["lab_commit"]
    bundle["research_pack_sha256"] = view["reproducibility"]["digests"]["research_pack"]
    bundle["preregistration"]["primary_metric_code"] = "false_alerts_per_year"
    bundle["dataset_card"]["system_count"] = 54
    bundle["dataset_card"]["observation_count"] = 5616
    bundle["dataset_card"]["coverage_counts"] = [
        {"status": "present", "count": 5346},
        {"status": "absent", "count": 270},
    ]
    for side in ("baseline", "candidate"):
        bundle[f"{side}_results"]["metrics"] = [
            {
                "domain_code": domain,
                "metric_code": code,
                "state": "present",
                "value": view["scorecard"][side][code]["value"],
                "reason_code": None,
            }
            for code, domain in (
                ("false_alerts_per_year", "primary"),
                ("detection_rate", "detection"),
            )
        ]
    bundle["decision"] = {
        "outcome": "reject",
        "acceptance_gate_passed": False,
        "reason_codes": view["decision"]["reason_codes"],
    }
    payload = canonical_json_bytes(custody_evidence(bundle))
    receipt = ArtifactRef(
        sha256="sha256:" + hashlib.sha256(payload).hexdigest(),
        size_bytes=len(payload),
        media_type="application/json",
    )
    bundle["artifact_manifest"].append(receipt.model_dump(mode="json"))
    view["reproducibility"]["digests"]["custody"] = receipt.sha256
    EvaluationBundle.model_validate_json(json.dumps(bundle))
    link_view(bundle, view)
    return bundle, view


def link_view(bundle: dict[str, Any], view: dict[str, Any]) -> None:
    view["reproducibility"]["digests"]["evaluation_bundle"] = (
        "sha256:" + hashlib.sha256(canonical_json_bytes(bundle)).hexdigest()
    )


def compose(bundle: dict[str, Any], view: dict[str, Any] | None = None) -> dict[str, Any]:
    return compose_finding(
        canonical_json_bytes(bundle), root=ROOT, product_contract_commit=PIN, source_view=view
    )


def seed_store(tmp_path: Path, *, with_view: bool = True) -> tuple[ArtifactStore, dict[str, Any]]:
    bundle, view = source_evidence()
    store = ArtifactStore(tmp_path / "store")
    bundle_ref = store.put_json(RUN_ID, bundle)
    custody = custody_evidence(bundle)
    custody_ref = store.put_json(RUN_ID, custody)
    provenance = snapshots()
    manifest = {
        "schema_version": "DeveloperLensWbc1Run.v1",
        "run_id": RUN_ID,
        "lab_commit": bundle["run_manifest"]["lab_commit"],
        "product_contract_commit": PIN,
        "product_commit": provenance["research_pack"]["product_commit"],
        "producer_schema_sha256": next(
            item["sha256"]
            for item in provenance["research_pack"]["files"]
            if item["name"] == "schema.json"
        ),
        "provenance": provenance,
        "bundle": bundle_ref.model_dump(mode="json"),
        "custody": custody_ref.model_dump(mode="json"),
        "dataset_sha256": custody["dataset_sha256"],
        "deterministic_bundle_sha256": bundle_ref.sha256,
    }
    if with_view:
        manifest["method_trial_view"] = store.put_json(RUN_ID, view).model_dump(mode="json")
    store.write_scope_file(RUN_ID, "run.json", canonical_json_bytes(manifest))
    return store, manifest


def test_projection_matches_pinned_fixture_and_preserves_sources() -> None:
    bundle, view = source_evidence()
    before = copy.deepcopy((bundle, view))
    assert stable_bytes(compose(bundle, view)) == (VENDOR / "wbc1.fixture.json").read_bytes()
    assert (bundle, view) == before


def test_bundle_only_export_does_not_invent_delay_confound_or_selection() -> None:
    bundle, _ = source_evidence()
    bundle["decision"]["reason_codes"] = ["CANDIDATE_FALSE_ALERT_IMPROVEMENT"]
    value = compose(bundle)
    assert "threshold_viability" not in value
    assert "public_url" not in value["provenance"]
    assert value["metrics"][2]["candidate"] == {"status": "unavailable"}
    assert value["metrics"][3]["baseline"] == {"status": "unavailable"}
    assert [gate["passed"] for gate in value["gates"]] == [
        None,
        None,
        True,
        None,
        False,
        True,
        None,
    ]
    assert [item["code"] for item in value["limitations"]] == ["c0_synthetic_only"]


@pytest.mark.parametrize(
    "defect",
    ["bundle_hash", "run_id", "lab_commit", "product_commit", "pack_hash", "dataset"],
)
def test_linked_view_must_belong_to_the_same_evidence(defect: str) -> None:
    bundle, view = source_evidence()
    if defect == "bundle_hash":
        view["reproducibility"]["digests"]["evaluation_bundle"] = "sha256:" + "a" * 64
    elif defect == "pack_hash":
        view["reproducibility"]["digests"]["research_pack"] = "sha256:" + "a" * 64
    elif defect == "dataset":
        bundle["dataset_card"]["system_count"] = 53
        link_view(bundle, view)
    else:
        key = "product_contract_commit" if defect == "product_commit" else defect
        view["reproducibility"][key] = "different_run" if key == "run_id" else "a" * 40
    with pytest.raises(FindingError):
        compose(bundle, view)


@pytest.mark.parametrize(
    "defect",
    ["wrong_domain", "conflicting_value", "explicit_missing", "unknown_study", "unknown_method"],
)
def test_source_incompatibility_is_refused_not_repaired(defect: str) -> None:
    bundle, view = source_evidence()
    if defect == "wrong_domain":
        bundle["baseline_results"]["metrics"][0]["domain_code"] = "other"
    elif defect == "conflicting_value":
        bundle["baseline_results"]["metrics"][1]["value"] = 0.5
    elif defect == "explicit_missing":
        bundle["baseline_results"]["metrics"][1].update(
            state="absent", value=None, reason_code="NO_SUPPORT"
        )
    elif defect == "unknown_study":
        bundle["preregistration"]["question_code"] = "UNKNOWN.STUDY"
    else:
        bundle["preregistration"]["candidate_method_code"] = "unknown"
        bundle["candidate_model_card"]["method_code"] = "unknown"
    link_view(bundle, view)
    with pytest.raises(FindingError):
        compose(bundle, view)


@pytest.mark.parametrize("outcome", ["revise_once", "benchmarked"])
def test_nonreject_states_without_supporting_evidence_are_refused(outcome: str) -> None:
    bundle, _ = source_evidence()
    bundle["decision"].update(outcome=outcome, acceptance_gate_passed=outcome == "benchmarked")
    with pytest.raises(FindingError, match="supporting gate evidence"):
        compose(bundle)


def test_atomic_export_is_repeatable_and_does_not_change_stored_evidence(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path)
    before = {
        p.relative_to(store.root): p.read_bytes() for p in store.root.rglob("*") if p.is_file()
    }
    destination = tmp_path / "published/finding.json"
    first = export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    payload = destination.read_bytes()
    second = export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert first == second
    assert payload == destination.read_bytes() == (VENDOR / "wbc1.fixture.json").read_bytes()
    assert before == {
        p.relative_to(store.root): p.read_bytes() for p in store.root.rglob("*") if p.is_file()
    }
    assert list(destination.parent.iterdir()) == [destination]


@pytest.mark.parametrize(
    "defect",
    ["digest", "size", "media", "manifest_id", "manifest_commit", "manifest_hash", "json"],
)
def test_source_refusal_preserves_existing_output(tmp_path: Path, defect: str) -> None:
    store, manifest = seed_store(tmp_path)
    if defect == "digest":
        manifest["bundle"]["sha256"] = "sha256:" + "a" * 64
    elif defect == "size":
        manifest["bundle"]["size_bytes"] += 1
    elif defect == "media":
        manifest["bundle"]["media_type"] = "application/x-parquet"
    elif defect == "manifest_id":
        manifest["run_id"] = "different_run"
    elif defect == "manifest_commit":
        manifest["lab_commit"] = "a" * 40
    elif defect == "manifest_hash":
        manifest["deterministic_bundle_sha256"] = "sha256:" + "a" * 64
    store.write_scope_file(
        RUN_ID, "run.json", b"{" if defect == "json" else canonical_json_bytes(manifest)
    )
    destination = tmp_path / "existing.json"
    destination.write_bytes(b"untouched")
    with pytest.raises(FindingError):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert destination.read_bytes() == b"untouched"


def test_output_cannot_overwrite_source_manifest(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path)
    destination = store.scope_root(RUN_ID) / "run.json"
    before = destination.read_bytes()
    with pytest.raises(FindingError):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert destination.read_bytes() == before


def test_final_output_symlink_is_replaced_without_following_target(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path)
    target = tmp_path / "keep.txt"
    target.write_bytes(b"untouched")
    destination = tmp_path / "finding.json"
    destination.symlink_to(target)
    export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert not destination.is_symlink()
    assert target.read_bytes() == b"untouched"


def test_manifest_symlink_and_oversized_json_are_refused_without_output(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path)
    manifest = store.scope_root(RUN_ID) / "run.json"
    moved = tmp_path / "moved.json"
    manifest.rename(moved)
    manifest.symlink_to(moved)
    destination = tmp_path / "absent/finding.json"
    with pytest.raises(FindingError):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert not destination.parent.exists()
    with pytest.raises(FindingError):
        compose_finding(b" " * 1_048_577, root=ROOT, product_contract_commit=PIN)


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
    ],
)
def test_composer_enforces_full_study_identity(section: str, field: str, replacement: str) -> None:
    bundle, _ = source_evidence()
    bundle[section][field] = replacement
    with pytest.raises(FindingError, match="study semantics"):
        compose(bundle)


def test_bundle_identity_mismatch_refuses_a_rehashed_artifact(tmp_path: Path) -> None:
    store, manifest = seed_store(tmp_path, with_view=False)
    bundle, _ = source_evidence()
    bundle["bundle_id"] = "another_bundle"
    reference = store.put_json(RUN_ID, bundle)
    manifest["bundle"] = reference.model_dump(mode="json")
    manifest["deterministic_bundle_sha256"] = reference.sha256
    store.write_scope_file(RUN_ID, "run.json", canonical_json_bytes(manifest))
    destination = tmp_path / "absent/finding.json"
    with pytest.raises(FindingError, match="provenance disagree"):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert not destination.parent.exists()


@pytest.mark.parametrize("with_view", [False, True])
@pytest.mark.parametrize("defect", ["missing", "contract_pin", "recorded_pin", "schema_digest"])
def test_recorded_provenance_is_checked_on_both_export_paths(
    tmp_path: Path, with_view: bool, defect: str
) -> None:
    store, manifest = seed_store(tmp_path, with_view=with_view)
    if defect == "missing":
        manifest.pop("provenance")
    elif defect == "contract_pin":
        manifest["product_contract_commit"] = "a" * 40
    elif defect == "recorded_pin":
        manifest["provenance"]["research_pack"]["product_commit"] = "a" * 40
    else:
        manifest["producer_schema_sha256"] = "sha256:" + "a" * 64
    store.write_scope_file(RUN_ID, "run.json", canonical_json_bytes(manifest))
    destination = tmp_path / "existing.json"
    destination.write_bytes(b"untouched")
    with pytest.raises(FindingError):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert destination.read_bytes() == b"untouched"


def test_bundle_only_composition_refuses_an_unverified_contract_pin() -> None:
    bundle, _ = source_evidence()
    with pytest.raises(FindingError, match="verified pin"):
        compose_finding(canonical_json_bytes(bundle), root=ROOT, product_contract_commit="a" * 40)


@pytest.mark.parametrize("field", ["product_research_pack_commit", "custody"])
def test_rehashed_view_cannot_change_producer_or_custody(tmp_path: Path, field: str) -> None:
    store, manifest = seed_store(tmp_path)
    _, view = source_evidence()
    if field == "custody":
        view["reproducibility"]["digests"]["custody"] = "sha256:" + "a" * 64
    else:
        view["reproducibility"][field] = "a" * 40
    manifest["method_trial_view"] = store.put_json(RUN_ID, view).model_dump(mode="json")
    store.write_scope_file(RUN_ID, "run.json", canonical_json_bytes(manifest))
    destination = tmp_path / "existing.json"
    destination.write_bytes(b"untouched")
    with pytest.raises(FindingError):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert destination.read_bytes() == b"untouched"


@pytest.mark.parametrize("defect", ["missing", "different_ref", "missing_object", "dataset"])
def test_recorded_custody_is_verified_before_publication(tmp_path: Path, defect: str) -> None:
    store, manifest = seed_store(tmp_path)
    if defect == "missing":
        manifest.pop("custody")
    elif defect == "different_ref":
        manifest["custody"] = store.put_json(RUN_ID, {"event": "other"}).model_dump(mode="json")
    elif defect == "missing_object":
        digest = manifest["custody"]["sha256"].removeprefix("sha256:")
        (store.scope_root(RUN_ID) / "objects" / digest[:2] / digest).unlink()
    else:
        manifest["dataset_sha256"] = "sha256:" + "a" * 64
    store.write_scope_file(RUN_ID, "run.json", canonical_json_bytes(manifest))
    destination = tmp_path / "absent/finding.json"
    with pytest.raises(FindingError):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert not destination.parent.exists()


def test_rehashed_losing_bundle_cannot_claim_benchmarked(tmp_path: Path) -> None:
    store, manifest = seed_store(tmp_path, with_view=False)
    bundle, _ = source_evidence()
    bundle["decision"] = {
        "outcome": "benchmarked",
        "acceptance_gate_passed": True,
        "reason_codes": ["ALL_PREREGISTERED_GATES_PASSED"],
    }
    ref = store.put_json(RUN_ID, bundle)
    manifest["bundle"] = ref.model_dump(mode="json")
    manifest["deterministic_bundle_sha256"] = ref.sha256
    store.write_scope_file(RUN_ID, "run.json", canonical_json_bytes(manifest))
    destination = tmp_path / "absent/finding.json"
    with pytest.raises(FindingError, match="supporting gate evidence"):
        export_finding(RUN_ID, root=ROOT, output=destination, artifact_root=store.root)
    assert not destination.parent.exists()
