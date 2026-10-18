from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from developer_lens_lab.contracts import EvaluationBundle
from developer_lens_lab.contracts.evaluation_bundle import Preregistration, SplitPart

from .factories import TRAIN_END, TRAIN_START, evaluation_bundle


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
