from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from developer_lens_lab.contracts import EvaluationBundle
from developer_lens_lab.contracts.evaluation_bundle import Preregistration, SplitPart

from .factories import TRAIN_END, TRAIN_START, evaluation_bundle


@pytest.mark.parametrize(
    "result_name, manifest_index", [("baseline_results", 0), ("candidate_results", 1)]
)
@pytest.mark.parametrize(
    "changes",
    [
        {"size_bytes": 999},
        {"media_type": "text/html"},
        {"size_bytes": 999, "media_type": "text/html"},
    ],
    ids=["size", "media-type", "size-and-media-type"],
)
def test_result_artifact_metadata_must_match_manifest(
    result_name: str, manifest_index: int, changes: dict[str, int | str]
) -> None:
    bundle = evaluation_bundle()
    result_artifact = bundle[result_name]["artifact"].copy()
    bundle["artifact_manifest"][manifest_index] = {
        **bundle["artifact_manifest"][manifest_index],
        **changes,
    }
    assert bundle[result_name]["artifact"] == result_artifact

    with pytest.raises(
        ValidationError, match="result artifact references must match artifact_manifest"
    ):
        EvaluationBundle.model_validate_json(json.dumps(bundle))


@pytest.mark.parametrize("result_name", ["baseline_results", "candidate_results"])
def test_missing_result_artifact_rejected(result_name: str) -> None:
    bundle = evaluation_bundle()
    bundle[result_name]["artifact"] = {
        **bundle[result_name]["artifact"],
        "sha256": "sha256:" + "c" * 64,
    }
    with pytest.raises(
        ValidationError, match="result artifacts must be present in artifact_manifest"
    ):
        EvaluationBundle.model_validate_json(json.dumps(bundle))


def test_duplicate_manifest_digest_rejected() -> None:
    bundle = evaluation_bundle()
    bundle["artifact_manifest"].append({**bundle["artifact_manifest"][0], "size_bytes": 999})
    with pytest.raises(ValidationError, match="artifact_manifest contains duplicate digests"):
        EvaluationBundle.model_validate_json(json.dumps(bundle))


def test_matching_artifact_references_accept_reordered_manifest() -> None:
    raw = evaluation_bundle()
    raw["artifact_manifest"].reverse()
    bundle = EvaluationBundle.model_validate_json(json.dumps(raw))
    assert bundle.baseline_results.artifact == bundle.artifact_manifest[1]
    assert bundle.candidate_results.artifact == bundle.artifact_manifest[0]


def test_duplicated_preregistration_seeds_rejected() -> None:
    duplicated = evaluation_bundle()
    duplicated["preregistration"]["seed_families"] = [
        "seed_family_train",
        "seed_family_train",
        "seed_family_test",
        "seed_family_holdout",
    ]
    with pytest.raises(ValidationError, match="duplicate seed_families"):
        EvaluationBundle.model_validate_json(json.dumps(duplicated))

    with pytest.raises(ValidationError, match="duplicate seed_families"):
        Preregistration.model_validate_json(json.dumps(duplicated["preregistration"]))


def test_distinct_matching_seeds_still_pass() -> None:
    bundle = EvaluationBundle.model_validate_json(json.dumps(evaluation_bundle()))
    assert list(bundle.preregistration.seed_families) == [
        "seed_family_train",
        "seed_family_test",
        "seed_family_holdout",
    ]


def test_split_part_duplicate_behavior_unchanged() -> None:
    with pytest.raises(ValidationError, match="duplicate seed_families"):
        SplitPart.model_validate_json(
            json.dumps(
                {
                    "window": {"start": TRAIN_START, "end": TRAIN_END},
                    "system_aliases": ["system_train"],
                    "seed_families": ["dl_seed_a", "dl_seed_a"],
                }
            )
        )
