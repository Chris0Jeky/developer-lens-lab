from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from .common import (
    JSON_INTEGER_COERCION,
    ArtifactRef,
    AvailabilityState,
    CanonicalUtc,
    Code,
    CommitSha,
    OpaqueId,
    Sha256,
    StrictModel,
    TemporalAvailability,
)

RelationName = Literal[
    "coverage",
    "repository_week",
    "pr_episode",
    "ci_attempt",
    "release_episode",
    "collection_probe",
    "system_event",
]
RELATION_SCHEMA_IDS = {
    "coverage": "developer-lens.coverage.v1",
    "repository_week": "developer-lens.repository-week.v1",
    "pr_episode": "developer-lens.pr-episode.v1",
    "ci_attempt": "developer-lens.ci-attempt.v1",
    "release_episode": "developer-lens.release-episode.v1",
    "collection_probe": "developer-lens.collection-probe.v1",
    "system_event": "developer-lens.system-event.v1",
}
CANONICAL_PERSON_SUBJECT_TERMS = (
    "person",
    "people",
    "individual",
    "contributor",
    "developer",
    "author",
    "committer",
    "reviewer",
    "employee",
    "engineer",
    "teammate",
    "team_member",
    "username",
    "user_login",
    "headcount",
    "seniority",
)
PROHIBITED_PERFORMANCE_TERMS = (
    "productiv",
    "performance",
    "effort",
    "attendance",
    "hours_worked",
    "availability",
    "diligence",
    "quality",
    "worth",
    "personality",
    "sentiment",
    "burnout",
    "surveillance",
    "bus_factor",
    "individual_output",
)
PROHIBITED_FEATURE_TERMS = CANONICAL_PERSON_SUBJECT_TERMS + PROHIBITED_PERFORMANCE_TERMS


def _casefold_pattern(term: str, *, prefix: bool = False) -> str:
    parts = term.split("_")
    core = r"[._-]+".join(
        "".join(f"[{char.lower()}{char.upper()}]" if char.isalpha() else char for char in part)
        for part in parts
    )
    suffix = "[A-Za-z0-9]*" if prefix else ""
    return rf"(?:^|[._-]){core}{suffix}(?:$|[._-])"


PROHIBITED_FEATURE_RE = re.compile(
    "|".join(
        _casefold_pattern(term, prefix=term == "productiv") for term in PROHIBITED_FEATURE_TERMS
    ),
    re.IGNORECASE,
)


FEATURE_ID_PATTERN = (
    r"^(?!.*(?:"
    + "|".join(
        _casefold_pattern(term, prefix=term == "productiv") for term in PROHIBITED_FEATURE_TERMS
    )
    + r"))[A-Za-z][A-Za-z0-9_.-]{0,95}$"
)

InterpretationCode = Literal["NOT_PERSON_MEASURE", "NOT_PRODUCTIVITY", "NOT_EFFORT"]
REQUIRED_NO_PERSON_INTERPRETATION = "NOT_PERSON_MEASURE"


class ResearchPackProvenance(StrictModel):
    product_commit: CommitSha
    contract_sha256: Sha256
    producer_code: Literal["developer-lens.research-pack.v1"]
    fixture_revision: Code | None


class RelationDescriptor(StrictModel):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {"properties": {"state": {"const": "present"}}},
                    "then": {
                        "properties": {
                            "schema_id": {"not": {"type": "null"}},
                            "row_count": {"not": {"type": "null"}},
                            "artifact": {"not": {"type": "null"}},
                            "reason_code": {"type": "null"},
                        }
                    },
                    "else": {
                        "properties": {
                            "schema_id": {"type": "null"},
                            "row_count": {"type": "null"},
                            "artifact": {"type": "null"},
                            "reason_code": {"not": {"type": "null"}},
                        }
                    },
                }
            ]
        }
    )

    state: AvailabilityState
    schema_id: Code | None
    row_count: (
        Annotated[
            int,
            Field(ge=0, le=100_000_000),
            JSON_INTEGER_COERCION,
        ]
        | None
    )
    artifact: ArtifactRef | None
    reason_code: Code | None

    @model_validator(mode="after")
    def state_matches_artifact(self) -> Self:
        values = (self.schema_id, self.row_count, self.artifact)
        if self.state == "present":
            if any(value is None for value in values) or self.reason_code is not None:
                raise ValueError(
                    "present relation requires schema_id, row_count, artifact, and no reason_code"
                )
            if self.artifact is not None and self.artifact.media_type != "application/x-parquet":
                raise ValueError("present relation artifact must use Parquet")
        elif any(value is not None for value in values) or self.reason_code is None:
            raise ValueError(
                "non-present relation requires reason_code and no schema, count, or artifact"
            )
        return self


class ResearchRelations(StrictModel):
    coverage: RelationDescriptor
    repository_week: RelationDescriptor
    pr_episode: RelationDescriptor
    ci_attempt: RelationDescriptor
    release_episode: RelationDescriptor
    collection_probe: RelationDescriptor
    system_event: RelationDescriptor


class FeatureDefinition(StrictModel):
    feature_id: Code = Field(
        json_schema_extra={
            "pattern": FEATURE_ID_PATTERN,
            "$comment": (
                "Runtime validator rejects person, productivity, performance, effort, "
                "and surveillance feature identifiers."
            ),
        }
    )
    relation: RelationName
    value_kind: Literal["count", "duration_hours", "ratio", "category", "boolean"]
    unit_code: Code
    evidence_layer: Literal["observed", "deterministic"]
    prohibited_interpretation_codes: Annotated[
        tuple[InterpretationCode, ...],
        Field(
            min_length=1,
            max_length=12,
            json_schema_extra={"contains": {"const": REQUIRED_NO_PERSON_INTERPRETATION}},
        ),
    ]

    @field_validator("feature_id")
    @classmethod
    def feature_is_system_shaped(cls, value: str) -> str:
        if PROHIBITED_FEATURE_RE.search(value):
            raise ValueError("person-scoring and productivity feature identifiers are prohibited")
        return value

    @model_validator(mode="after")
    def requires_no_person_interpretation(self) -> Self:
        if REQUIRED_NO_PERSON_INTERPRETATION not in self.prohibited_interpretation_codes:
            raise ValueError(f"{REQUIRED_NO_PERSON_INTERPRETATION} is required")
        return self


class ResearchPack(StrictModel):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {"properties": {"classification": {"const": "C1"}}},
                    "then": {
                        "properties": {
                            "generated_at": {"pattern": r"^\d{4}-\d{2}-\d{2}T00:00:00Z$"}
                        }
                    },
                }
            ]
        }
    )

    schema_version: Literal["DeveloperLensResearchPack.v1"]
    pack_id: OpaqueId
    generated_at: CanonicalUtc
    classification: Literal["C0", "C1"]
    provenance: ResearchPackProvenance
    temporal_availability: TemporalAvailability
    relations: ResearchRelations
    feature_registry: Annotated[tuple[FeatureDefinition, ...], Field(max_length=128)]

    @model_validator(mode="after")
    def unique_features(self) -> Self:
        if self.classification == "C1":
            generated_at = datetime.fromisoformat(self.generated_at.removesuffix("Z") + "+00:00")
            if (
                generated_at.weekday() != 0
                or generated_at.hour != 0
                or generated_at.minute != 0
                or generated_at.second != 0
                or generated_at.microsecond != 0
            ):
                raise ValueError("C1 generated_at must be the UTC Monday start of an ISO week")
        feature_ids = [feature.feature_id for feature in self.feature_registry]
        if len(feature_ids) != len(set(feature_ids)):
            raise ValueError("feature_registry contains duplicate feature_id values")
        relation_items = (
            ("coverage", self.relations.coverage),
            ("repository_week", self.relations.repository_week),
            ("pr_episode", self.relations.pr_episode),
            ("ci_attempt", self.relations.ci_attempt),
            ("release_episode", self.relations.release_episode),
            ("collection_probe", self.relations.collection_probe),
            ("system_event", self.relations.system_event),
        )
        present_digests: list[str] = []
        for relation_name, descriptor in relation_items:
            if descriptor.state != "present":
                continue
            if descriptor.schema_id != RELATION_SCHEMA_IDS[relation_name]:
                raise ValueError(f"{relation_name} has the wrong schema_id")
            if descriptor.artifact is not None:
                present_digests.append(descriptor.artifact.sha256)
        if len(present_digests) != len(set(present_digests)):
            raise ValueError("present relations must not share one artifact digest")
        return self
