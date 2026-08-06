from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .common import (
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


class ResearchPackProvenance(StrictModel):
    product_commit: CommitSha
    contract_sha256: Sha256
    producer_code: Literal["developer-lens.research-pack.v1"]
    fixture_revision: Code | None


class RelationDescriptor(StrictModel):
    state: AvailabilityState
    schema_id: Code | None
    row_count: Annotated[int, Field(ge=0, le=100_000_000)] | None
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
    feature_id: Code
    relation: RelationName
    value_kind: Literal["count", "duration_hours", "ratio", "category", "boolean"]
    unit_code: Code
    evidence_layer: Literal["observed", "deterministic"]
    prohibited_interpretation_codes: Annotated[tuple[Code, ...], Field(min_length=1, max_length=12)]


class ResearchPack(StrictModel):
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
