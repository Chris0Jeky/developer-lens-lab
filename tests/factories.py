from __future__ import annotations

from typing import Any

SHA_A = "sha256:" + "a" * 64
SHA_B = "sha256:" + "b" * 64
SHA_C = "sha256:" + "c" * 64
COMMIT = "d" * 40
START = "2025-01-06T00:00:00Z"
END = "2025-12-29T00:00:00Z"
TRAIN_START = "2023-01-02T00:00:00Z"
TRAIN_END = "2024-01-01T00:00:00Z"
TEST_START = "2024-01-01T00:00:00Z"
TEST_END = "2025-01-06T00:00:00Z"


def artifact(digest: str = SHA_A, size: int = 12) -> dict[str, object]:
    return {"sha256": digest, "size_bytes": size, "media_type": "application/x-parquet"}


def unavailable_relation(reason: str = "NOT_IN_FIXTURE") -> dict[str, object]:
    return {
        "state": "intentionally_omitted",
        "schema_id": None,
        "row_count": None,
        "artifact": None,
        "reason_code": reason,
    }


def research_pack(repository_week: dict[str, Any] | None = None) -> dict[str, Any]:
    relation = repository_week or unavailable_relation()
    return {
        "schema_version": "DeveloperLensResearchPack.v1",
        "pack_id": "pack_demo",
        "generated_at": "2026-08-06T12:00:00Z",
        "classification": "C0",
        "provenance": {
            "product_commit": COMMIT,
            "contract_sha256": SHA_C,
            "producer_code": "developer-lens.research-pack.v1",
            "fixture_revision": "invented.v1",
        },
        "temporal_availability": {
            name: {"state": "present", "window": {"start": START, "end": END}, "reason_code": None}
            for name in ("event", "collection", "feature")
        },
        "relations": {
            "coverage": unavailable_relation(),
            "repository_week": relation,
            "pr_episode": unavailable_relation(),
            "ci_attempt": unavailable_relation(),
            "release_episode": unavailable_relation(),
            "collection_probe": unavailable_relation(),
            "system_event": unavailable_relation(),
        },
        "feature_registry": [
            {
                "feature_id": "DL.WEEK.CHANGE_COUNT.v1",
                "relation": "repository_week",
                "value_kind": "count",
                "unit_code": "count",
                "evidence_layer": "deterministic",
                "prohibited_interpretation_codes": ["NOT_PRODUCTIVITY", "NOT_EFFORT"],
            }
        ],
    }


def evaluation_bundle() -> dict[str, Any]:
    baseline_artifact = artifact(SHA_A, 12)
    candidate_artifact = artifact(SHA_B, 18)

    def split(
        alias: str, seed_family: str, window_start: str, window_end: str
    ) -> dict[str, object]:
        return {
            "window": {"start": window_start, "end": window_end},
            "system_aliases": [alias],
            "seed_families": [seed_family],
        }

    def metric(code: str, value: float) -> dict[str, object]:
        return {
            "metric_code": code,
            "state": "present",
            "value": value,
            "reason_code": None,
        }

    return {
        "schema_version": "DeveloperLensEvaluationBundle.v1",
        "bundle_id": "bundle_demo",
        "created_at": "2026-08-06T12:05:00Z",
        "research_pack_sha256": SHA_C,
        "preregistration": {
            "question_code": "WB.C1.CHANGE_POINT",
            "baseline_method_code": "rolling_median_mad",
            "candidate_method_code": "bocpd_gaussian",
            "primary_metric_code": "event_f1",
            "acceptance_rule_code": "candidate_beats_baseline",
            "abstention_rule_code": "coverage_and_support_floor",
            "seed_families": [
                "seed_family_train",
                "seed_family_test",
                "seed_family_holdout",
            ],
        },
        "dataset_card": {
            "generator_code": "invented_weekly_series",
            "generator_revision": "v1",
            "classification": "C0",
            "observation_count": 156,
            "system_count": 3,
            "coverage_counts": [{"status": "present", "count": 156}],
        },
        "baseline_model_card": {
            "model_id": "model_baseline",
            "role": "baseline",
            "method_code": "rolling_median_mad",
            "method_revision": "v1",
            "deterministic": True,
            "parameter_sha256": SHA_A,
            "no_model_fallback_code": "same_as_baseline",
        },
        "candidate_model_card": {
            "model_id": "model_candidate",
            "role": "candidate",
            "method_code": "bocpd_gaussian",
            "method_revision": "v1",
            "deterministic": True,
            "parameter_sha256": SHA_B,
            "no_model_fallback_code": "rolling_median_mad",
        },
        "split_manifest": {
            "strategy": "repository_time_seed",
            "train": split("system_train", "seed_family_train", TRAIN_START, TRAIN_END),
            "test": split("system_test", "seed_family_test", TEST_START, TEST_END),
            "final_holdout": split("system_holdout", "seed_family_holdout", START, END),
        },
        "run_manifest": {
            "run_id": "run_demo",
            "lab_commit": COMMIT,
            "environment_sha256": SHA_C,
            "started_at": "2026-08-06T12:00:00Z",
            "completed_at": "2026-08-06T12:04:00Z",
            "seeds": [17, 29],
            "deterministic": True,
        },
        "baseline_results": {
            "model_id": "model_baseline",
            "metrics": [metric("event_f1", 0.61)],
            "artifact": baseline_artifact,
        },
        "candidate_results": {
            "model_id": "model_candidate",
            "metrics": [metric("event_f1", 0.74)],
            "artifact": candidate_artifact,
        },
        "calibration": {"status": "measured", "metrics": [metric("brier", 0.12)]},
        "abstention": {"eligible_count": 30, "abstained_count": 3, "reason_codes": ["LOW_SUPPORT"]},
        "leakage": [{"check_code": "future_window", "outcome": "pass", "detail_code": "NO_LEAK"}],
        "resources": {
            "evaluation_points": 468,
            "candidate_steps": 468,
            "offline_series": 3,
            "declared_wall_time_budget_ms": 5_000,
            "declared_peak_rss_budget_bytes": 256_000_000,
            "workload_sha256": SHA_C,
        },
        "decision": {
            "outcome": "benchmarked",
            "acceptance_gate_passed": True,
            "reason_codes": ["PRIMARY_GATE_PASSED"],
        },
        "artifact_manifest": [baseline_artifact, candidate_artifact],
    }
