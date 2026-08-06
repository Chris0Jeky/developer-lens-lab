from __future__ import annotations

import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from developer_lens_lab.contracts import EvaluationBundle, ResearchPack
from developer_lens_lab.contracts.common import UTC_PATTERN

from .factories import evaluation_bundle, research_pack


def test_strict_contracts_accept_invented_examples() -> None:
    pack = ResearchPack.model_validate_json(json.dumps(research_pack()))
    bundle = EvaluationBundle.model_validate_json(json.dumps(evaluation_bundle()))

    assert pack.relations.repository_week.state == "intentionally_omitted"
    assert bundle.decision.outcome == "benchmarked"


def test_research_pack_rejects_unknown_fields_and_non_z_timestamps() -> None:
    extra = research_pack()
    extra["repository_name"] = "invented-but-still-prohibited"
    with pytest.raises(ValidationError):
        ResearchPack.model_validate_json(json.dumps(extra))

    offset = research_pack()
    offset["generated_at"] = "2026-08-06T13:00:00+01:00"
    with pytest.raises(ValidationError, match="pattern"):
        ResearchPack.model_validate_json(json.dumps(offset))

    schema = ResearchPack.model_json_schema(mode="validation")
    assert schema["properties"]["generated_at"]["pattern"] == UTC_PATTERN
    assert schema["$defs"]["TimeWindow"]["properties"]["start"]["pattern"] == UTC_PATTERN
    assert schema["$defs"]["RelationDescriptor"]["allOf"]


def test_missing_relation_cannot_be_encoded_as_zero() -> None:
    invalid = research_pack()
    invalid["relations"]["repository_week"] = {
        "state": "absent",
        "schema_id": None,
        "row_count": 0,
        "artifact": None,
        "reason_code": "NO_OBSERVATION",
    }
    with pytest.raises(ValidationError, match="no schema, count, or artifact"):
        ResearchPack.model_validate_json(json.dumps(invalid))

    missing_null = research_pack()
    del missing_null["relations"]["repository_week"]["row_count"]
    with pytest.raises(ValidationError, match="Field required"):
        ResearchPack.model_validate_json(json.dumps(missing_null))


def test_evaluation_bundle_rejects_ship_and_split_leakage() -> None:
    ship = evaluation_bundle()
    ship["decision"]["outcome"] = "ship"
    with pytest.raises(ValidationError):
        EvaluationBundle.model_validate_json(json.dumps(ship))

    leaked = deepcopy(evaluation_bundle())
    leaked["split_manifest"]["test"]["system_aliases"] = ["system_train"]
    with pytest.raises(ValidationError, match="must be disjoint"):
        EvaluationBundle.model_validate_json(json.dumps(leaked))


def test_failed_leakage_and_shared_model_ids_block_benchmarked_decision() -> None:
    leakage = evaluation_bundle()
    leakage["leakage"][0]["outcome"] = "fail"
    with pytest.raises(ValidationError, match="failed leakage"):
        EvaluationBundle.model_validate_json(json.dumps(leakage))

    shared_id = evaluation_bundle()
    shared_id["candidate_model_card"]["model_id"] = "model_baseline"
    shared_id["candidate_results"]["model_id"] = "model_baseline"
    with pytest.raises(ValidationError, match="model_id values must differ"):
        EvaluationBundle.model_validate_json(json.dumps(shared_id))
