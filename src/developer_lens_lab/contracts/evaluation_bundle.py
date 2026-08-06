from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from .common import (
    ArtifactRef,
    CanonicalUtc,
    Code,
    CommitSha,
    MetricValue,
    OpaqueId,
    Sha256,
    StrictModel,
    TimeWindow,
)


class Preregistration(StrictModel):
    question_code: Code
    baseline_method_code: Code
    candidate_method_code: Code
    primary_metric_code: Code
    acceptance_rule_code: Code
    abstention_rule_code: Code
    seed_families: Annotated[tuple[Code, ...], Field(min_length=1, max_length=32)]


class CoverageCount(StrictModel):
    status: Literal["present", "absent", "unsupported", "intentionally_omitted"]
    count: Annotated[int, Field(ge=0, le=100_000_000)]


class DatasetCard(StrictModel):
    generator_code: Code
    generator_revision: Code
    classification: Literal["C0"]
    observation_count: Annotated[int, Field(ge=1, le=100_000_000)]
    system_count: Annotated[int, Field(ge=1, le=1_000_000)]
    coverage_counts: Annotated[tuple[CoverageCount, ...], Field(min_length=1, max_length=4)]

    @model_validator(mode="after")
    def unique_coverage_states(self) -> Self:
        states = [entry.status for entry in self.coverage_counts]
        if len(states) != len(set(states)):
            raise ValueError("coverage_counts contains duplicate states")
        if sum(entry.count for entry in self.coverage_counts) != self.observation_count:
            raise ValueError("coverage_counts must sum to observation_count")
        return self


class ModelCard(StrictModel):
    model_id: OpaqueId
    role: Literal["baseline", "candidate"]
    method_code: Code
    method_revision: Code
    deterministic: bool
    parameter_sha256: Sha256
    no_model_fallback_code: Code


class SplitPart(StrictModel):
    window: TimeWindow
    system_aliases: Annotated[tuple[OpaqueId, ...], Field(min_length=1, max_length=10_000)]
    seed_families: Annotated[tuple[Code, ...], Field(min_length=1, max_length=32)]

    @model_validator(mode="after")
    def entries_are_unique(self) -> Self:
        if len(self.system_aliases) != len(set(self.system_aliases)):
            raise ValueError("split part contains duplicate system_aliases")
        if len(self.seed_families) != len(set(self.seed_families)):
            raise ValueError("split part contains duplicate seed_families")
        return self


class SplitManifest(StrictModel):
    strategy: Literal["repository_time_seed"]
    train: SplitPart
    test: SplitPart
    final_holdout: SplitPart

    @model_validator(mode="after")
    def partitions_are_disjoint(self) -> Self:
        system_parts = [
            set(self.train.system_aliases),
            set(self.test.system_aliases),
            set(self.final_holdout.system_aliases),
        ]
        if (
            system_parts[0] & system_parts[1]
            or system_parts[0] & system_parts[2]
            or system_parts[1] & system_parts[2]
        ):
            raise ValueError("split system_aliases must be disjoint")
        seed_parts = [
            set(self.train.seed_families),
            set(self.test.seed_families),
            set(self.final_holdout.seed_families),
        ]
        if (
            seed_parts[0] & seed_parts[1]
            or seed_parts[0] & seed_parts[2]
            or seed_parts[1] & seed_parts[2]
        ):
            raise ValueError("split seed_families must be disjoint")
        train_end = datetime.fromisoformat(self.train.window.end.removesuffix("Z") + "+00:00")
        test_start = datetime.fromisoformat(self.test.window.start.removesuffix("Z") + "+00:00")
        test_end = datetime.fromisoformat(self.test.window.end.removesuffix("Z") + "+00:00")
        holdout_start = datetime.fromisoformat(
            self.final_holdout.window.start.removesuffix("Z") + "+00:00"
        )
        if not (train_end <= test_start and test_end <= holdout_start):
            raise ValueError("split windows must be ordered and non-overlapping")
        return self


class RunManifest(StrictModel):
    run_id: OpaqueId
    lab_commit: CommitSha
    environment_sha256: Sha256
    started_at: CanonicalUtc
    completed_at: CanonicalUtc
    seeds: Annotated[tuple[int, ...], Field(min_length=1, max_length=128)]
    deterministic: bool

    @model_validator(mode="after")
    def ordered(self) -> Self:
        start = datetime.fromisoformat(self.started_at.removesuffix("Z") + "+00:00")
        end = datetime.fromisoformat(self.completed_at.removesuffix("Z") + "+00:00")
        if start > end:
            raise ValueError("run completed_at must not precede started_at")
        if len(self.seeds) != len(set(self.seeds)) or any(
            seed < 0 or seed > 4_294_967_295 for seed in self.seeds
        ):
            raise ValueError("run seeds must be unique unsigned 32-bit integers")
        return self


class ResultSet(StrictModel):
    model_id: OpaqueId
    metrics: Annotated[tuple[MetricValue, ...], Field(min_length=1, max_length=64)]
    artifact: ArtifactRef


class CalibrationReport(StrictModel):
    status: Literal["measured", "not_applicable", "insufficient_support"]
    metrics: Annotated[tuple[MetricValue, ...], Field(max_length=32)]


class AbstentionReport(StrictModel):
    eligible_count: Annotated[int, Field(ge=0, le=100_000_000)]
    abstained_count: Annotated[int, Field(ge=0, le=100_000_000)]
    reason_codes: Annotated[tuple[Code, ...], Field(max_length=32)]

    @model_validator(mode="after")
    def abstention_is_bounded(self) -> Self:
        if self.abstained_count > self.eligible_count:
            raise ValueError("abstained_count cannot exceed eligible_count")
        return self


class LeakageCheck(StrictModel):
    check_code: Code
    outcome: Literal["pass", "fail", "not_applicable"]
    detail_code: Code


class ResourceReport(StrictModel):
    evaluation_points: Annotated[int, Field(ge=1, le=1_000_000_000)]
    candidate_steps: Annotated[int, Field(ge=1, le=1_000_000_000)]
    offline_series: Annotated[int, Field(ge=0, le=1_000_000)]
    declared_wall_time_budget_ms: Annotated[int, Field(ge=1, le=86_400_000)]
    declared_peak_rss_budget_bytes: Annotated[int, Field(ge=1, le=1_000_000_000_000)]
    workload_sha256: Sha256


class DecisionReport(StrictModel):
    outcome: Literal["reject", "revise_once", "benchmarked"]
    acceptance_gate_passed: bool
    reason_codes: Annotated[tuple[Code, ...], Field(min_length=1, max_length=16)]

    @model_validator(mode="after")
    def gate_matches_outcome(self) -> Self:
        if self.acceptance_gate_passed != (self.outcome == "benchmarked"):
            raise ValueError("only benchmarked may record a passed acceptance gate")
        return self


class EvaluationBundle(StrictModel):
    schema_version: Literal["DeveloperLensEvaluationBundle.v1"]
    bundle_id: OpaqueId
    created_at: CanonicalUtc
    research_pack_sha256: Sha256
    preregistration: Preregistration
    dataset_card: DatasetCard
    baseline_model_card: ModelCard
    candidate_model_card: ModelCard
    split_manifest: SplitManifest
    run_manifest: RunManifest
    baseline_results: ResultSet
    candidate_results: ResultSet
    calibration: CalibrationReport
    abstention: AbstentionReport
    leakage: Annotated[tuple[LeakageCheck, ...], Field(min_length=1, max_length=32)]
    resources: ResourceReport
    decision: DecisionReport
    artifact_manifest: Annotated[tuple[ArtifactRef, ...], Field(min_length=2, max_length=128)]

    @model_validator(mode="after")
    def roles_and_artifacts_match(self) -> Self:
        if self.baseline_model_card.role != "baseline":
            raise ValueError("baseline_model_card must have baseline role")
        if self.candidate_model_card.role != "candidate":
            raise ValueError("candidate_model_card must have candidate role")
        if self.baseline_model_card.model_id == self.candidate_model_card.model_id:
            raise ValueError("baseline and candidate model_id values must differ")
        if self.preregistration.baseline_method_code != self.baseline_model_card.method_code:
            raise ValueError("preregistered baseline method does not match its model card")
        if self.preregistration.candidate_method_code != self.candidate_model_card.method_code:
            raise ValueError("preregistered candidate method does not match its model card")
        if self.baseline_results.model_id != self.baseline_model_card.model_id:
            raise ValueError("baseline result model_id does not match its model card")
        if self.candidate_results.model_id != self.candidate_model_card.model_id:
            raise ValueError("candidate result model_id does not match its model card")
        declared = {artifact.sha256 for artifact in self.artifact_manifest}
        required = {self.baseline_results.artifact.sha256, self.candidate_results.artifact.sha256}
        if not required <= declared:
            raise ValueError("result artifacts must be present in artifact_manifest")
        if len(declared) != len(self.artifact_manifest):
            raise ValueError("artifact_manifest contains duplicate digests")
        split_seed_families = {
            *self.split_manifest.train.seed_families,
            *self.split_manifest.test.seed_families,
            *self.split_manifest.final_holdout.seed_families,
        }
        if split_seed_families != set(self.preregistration.seed_families):
            raise ValueError("preregistered seed_families must match the split manifest")
        if self.decision.outcome == "benchmarked" and any(
            check.outcome == "fail" for check in self.leakage
        ):
            raise ValueError("a failed leakage check blocks a benchmarked decision")
        return self
