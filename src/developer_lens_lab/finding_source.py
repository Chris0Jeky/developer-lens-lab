"""Closed WB-C1 protocol and recorded producer-pin validation, without analysis imports."""

from __future__ import annotations

import hashlib
import re
from typing import Any, cast

from developer_lens_lab.artifacts import canonical_json_bytes
from developer_lens_lab.contracts import EvaluationBundle

_COMMIT = re.compile(r"[0-9a-f]{40}")
_BASELINE_PARAMETERS = "sha256:72aa597050c5199c88208a5d021f9a50a439079d4d0d03b1d0afc6677bfeb88c"
_CANDIDATE_PARAMETERS = "sha256:2ec6875a7ee96a825c3227a1b262076a45f46d29f32467a358a0940a171cb5be"


def validate_study_identity(bundle: EvaluationBundle) -> None:
    """Refuse protocol drift rather than label a different experiment as WB-C1."""
    if bundle.bundle_id != bundle.run_manifest.run_id:
        raise ValueError("stored bundle and run identity disagree")
    prereg = bundle.preregistration
    baseline = bundle.baseline_model_card
    candidate = bundle.candidate_model_card
    if (
        prereg.question_code != "WB.C1.CHANGE_POINT"
        or prereg.primary_metric_code != "false_alerts_per_year"
        or prereg.baseline_method_code != "rolling_median_mad"
        or prereg.candidate_method_code != "bocpd_gaussian"
        or prereg.acceptance_rule_code != "candidate_beats_baseline"
        or prereg.abstention_rule_code != "coverage_and_support_floor"
        or bundle.dataset_card.generator_code != "invented_weekly_series"
        or bundle.dataset_card.generator_revision != "wbc1.generator.v1"
        or baseline.method_code != "rolling_median_mad"
        or candidate.method_code != "bocpd_gaussian"
        or baseline.method_revision != "wbc1.methods.v1"
        or candidate.method_revision != "wbc1.methods.v1"
        or baseline.parameter_sha256 != _BASELINE_PARAMETERS
        or candidate.parameter_sha256 != _CANDIDATE_PARAMETERS
        or baseline.no_model_fallback_code != "same_as_baseline"
        or candidate.no_model_fallback_code != "rolling_median_mad"
        or not bundle.run_manifest.deterministic
        or not baseline.deterministic
        or not candidate.deterministic
    ):
        raise ValueError("no finding adapter is registered for these source study semantics")


def validate_snapshot(provenance: dict[str, Any], payloads: dict[str, bytes]) -> None:
    """Validate declarations against caller-selected fixed filenames, never declared paths."""
    commit = provenance.get("product_commit")
    if not isinstance(commit, str) or not _COMMIT.fullmatch(commit):
        raise ValueError("source contract snapshot lacks an immutable producer pin")
    expected = {
        "schema_version": "DeveloperLensContractSnapshot.v1",
        "product_commit": commit,
        "identity_semantics": "provenance_only_not_a_join_key",
        "files": [
            {
                "name": name,
                "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
            }
            for name, payload in sorted(payloads.items())
        ],
    }
    if canonical_json_bytes(provenance) != canonical_json_bytes(expected):
        raise ValueError("source contract snapshot provenance does not match verified bytes")


def validate_recorded_provenance(
    manifest: dict[str, Any], snapshots: dict[str, dict[str, Any]]
) -> str:
    """Require both recorded snapshots and their manifest bindings on every export path."""
    recorded = manifest.get("provenance")
    if not isinstance(recorded, dict):
        raise ValueError("stored run manifest lacks recorded producer provenance")
    recorded = cast(dict[str, Any], recorded)
    for key in ("method_trial_view", "research_pack"):
        if canonical_json_bytes(recorded.get(key)) != canonical_json_bytes(snapshots[key]):
            raise ValueError("stored producer provenance differs from the verified snapshot")
    method = snapshots["method_trial_view"]
    research = snapshots["research_pack"]
    if (
        manifest.get("product_contract_commit") != method["product_commit"]
        or manifest.get("product_commit") != research["product_commit"]
        or manifest.get("producer_schema_sha256")
        != next(item["sha256"] for item in research["files"] if item["name"] == "schema.json")
    ):
        raise ValueError("stored run manifest disagrees with its recorded producer pins")
    return str(method["product_commit"])
