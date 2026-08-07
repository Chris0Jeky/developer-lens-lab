# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
"""Execution and byte-for-byte reproduction for the WB-C1 smoke benchmark."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal, cast

import pyarrow as pa
import pyarrow.parquet as pq
from jsonschema import Draft202012Validator

from developer_lens_lab.artifacts import ArtifactError, ArtifactStore, canonical_json_bytes
from developer_lens_lab.contracts import ArtifactRef, EvaluationBundle, ResearchPack
from developer_lens_lab.contracts.common import MetricValue, TimeWindow
from developer_lens_lab.contracts.evaluation_bundle import (
    AbstentionReport,
    CalibrationReport,
    CoverageCount,
    DatasetCard,
    DecisionReport,
    LeakageCheck,
    ModelCard,
    Preregistration,
    ResourceReport,
    ResultSet,
    RunManifest,
    SplitManifest,
    SplitPart,
)
from developer_lens_lab.validation import validate_pack_artifacts, validate_research_pack

from .evaluation import BenchmarkEvaluation, EvaluationPlan, prepare_evaluation, run_evaluation
from .generator import BenchmarkDataset, Partition, build_benchmark_dataset
from .methods import DEFAULT_BASELINE_PARAMETERS, DEFAULT_BOCPD_PARAMETERS, parameters_sha256
from .report import (
    build_html,
    build_markdown,
    build_method_trial_html,
    build_method_trial_markdown,
)


class RunnerError(RuntimeError):
    """Raised when a benchmark cannot produce a reproducible run."""


@dataclass(frozen=True)
class BenchmarkRun:
    run_id: str
    scope: str
    bundle: EvaluationBundle
    bundle_artifact: ArtifactRef
    method_trial_view_artifact: ArtifactRef | None
    markdown_artifact: ArtifactRef
    html_artifact: ArtifactRef
    manifest_path: Path


@dataclass(frozen=True)
class MaterializedResearchPack:
    manifest_bytes: bytes
    coverage_bytes: bytes
    repository_week_bytes: bytes
    pack: ResearchPack


MediaType = Literal["application/json", "application/x-parquet", "text/markdown", "text/html"]


LOGICAL_RUN_TIME = "2026-01-01T00:00:00Z"
CUSTODY_RECORD_NAME = "custody.json"


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _root() -> Path:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise RunnerError("run from inside a developer-lens-lab checkout")


def _vendor_root(root: Path) -> Path:
    return root / "vendor" / "developer-lens" / "research-pack" / "v1"


def _load_vendor_snapshot(
    root: Path,
) -> tuple[dict[str, Any], dict[str, Any], ResearchPack]:
    vendor = _vendor_root(root)
    fixture_path = vendor / "invented.fixture.json"
    if not fixture_path.is_file():
        raise RunnerError(
            "vendor producer snapshot absent: run `dllab contracts sync --from <checkout> "
            "--ref <40-hex-commit>` before benchmarking"
        )
    provenance_path = vendor / "provenance.json"
    if not provenance_path.is_file():
        raise RunnerError("vendor producer snapshot is missing provenance.json")
    fixture_bytes = fixture_path.read_bytes()
    schema_path = vendor / "schema.json"
    if not schema_path.is_file():
        raise RunnerError("vendor producer snapshot is missing schema.json")
    schema_bytes = schema_path.read_bytes()
    schema = cast(dict[str, Any], json.loads(schema_bytes))
    provenance = cast(dict[str, Any], json.loads(provenance_path.read_text(encoding="utf-8")))
    declared_files = {
        str(entry["name"]): entry
        for entry in cast(list[dict[str, Any]], provenance.get("files", []))
    }
    for name, payload in (("invented.fixture.json", fixture_bytes), ("schema.json", schema_bytes)):
        declaration = declared_files.get(name)
        if declaration is None:
            raise RunnerError(f"vendor provenance does not declare {name}")
        if declaration.get("sha256") != _sha256(payload) or declaration.get("size_bytes") != len(
            payload
        ):
            raise RunnerError(f"vendor provenance does not match {name}")
    try:
        Draft202012Validator(schema).validate(json.loads(fixture_bytes))
    except Exception as exc:
        raise RunnerError(f"vendor ResearchPack fails producer schema: {exc}") from exc
    pack = validate_research_pack(fixture_path)
    return schema, provenance, pack


def _parquet_bytes(rows: list[dict[str, Any]]) -> bytes:
    table = pa.Table.from_pylist(rows)
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink)
    return sink.getvalue().to_pybytes()


def _materialize_research_pack(
    dataset: BenchmarkDataset,
    fixture: ResearchPack,
    provenance: dict[str, Any],
    producer_schema: dict[str, Any],
) -> MaterializedResearchPack:
    repository_week_rows: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    partitions = (dataset.train, dataset.test, dataset.final_holdout_metadata)
    for partition in partitions:
        for series in partition.series:
            coverage_rows.append(
                {
                    "coverage_id": series.coverage_id,
                    "capability_code": "invented.wbc1",
                    "status": "present" if bool(series.observed.all()) else "partial",
                    "observed_units": int(series.observed.sum()),
                    "expected_units": len(series.observed),
                    "window_start": series.week_starts[0],
                    "window_end": partition.end,
                }
            )
            for week, value, observed in zip(
                series.week_starts, series.values.tolist(), series.observed.tolist(), strict=True
            ):
                if observed:
                    repository_week_rows.append(
                        {
                            "repository_alias": series.system_alias,
                            "week_start": week,
                            "metric_code": "DL.WEEK.SYSTEM_SIGNAL_INDEX.v1",
                            "value": float(value),
                            "coverage_id": series.coverage_id,
                        }
                    )
    coverage_bytes = _parquet_bytes(coverage_rows)
    repository_week_bytes = _parquet_bytes(repository_week_rows)
    schema_digest = next(
        entry["sha256"]
        for entry in cast(list[dict[str, str]], provenance["files"])
        if entry["name"] == "schema.json"
    )
    raw = fixture.model_dump(mode="json")
    raw["pack_id"] = "wbc1_research_pack"
    raw["generated_at"] = LOGICAL_RUN_TIME
    raw["provenance"]["product_commit"] = provenance["product_commit"]
    raw["provenance"]["contract_sha256"] = schema_digest
    raw["provenance"]["fixture_revision"] = "wbc1.generator.v1"
    raw["relations"]["coverage"] = {
        "state": "present",
        "schema_id": "developer-lens.coverage.v1",
        "row_count": len(coverage_rows),
        "artifact": {
            "sha256": _sha256(coverage_bytes),
            "size_bytes": len(coverage_bytes),
            "media_type": "application/x-parquet",
        },
        "reason_code": None,
    }
    raw["relations"]["repository_week"] = {
        "state": "present",
        "schema_id": "developer-lens.repository-week.v1",
        "row_count": len(repository_week_rows),
        "artifact": {
            "sha256": _sha256(repository_week_bytes),
            "size_bytes": len(repository_week_bytes),
            "media_type": "application/x-parquet",
        },
        "reason_code": None,
    }
    temporal_window = {"start": dataset.train.start, "end": dataset.final_holdout_metadata.end}
    raw["temporal_availability"] = {
        name: {"state": "present", "window": temporal_window, "reason_code": None}
        for name in ("event", "collection", "feature")
    }
    raw["feature_registry"] = [
        {
            "feature_id": "DL.WEEK.SYSTEM_SIGNAL_INDEX.v1",
            "relation": "repository_week",
            "value_kind": "ratio",
            "unit_code": "synthetic_index",
            "evidence_layer": "deterministic",
            "prohibited_interpretation_codes": [
                "NOT_PRODUCTIVITY",
                "NOT_EFFORT",
                "NOT_PERSON_MEASURE",
            ],
        }
    ]
    try:
        Draft202012Validator(producer_schema).validate(raw)
    except Exception as exc:
        raise RunnerError(f"WB-C1 ResearchPack fails pinned producer schema: {exc}") from exc
    manifest_bytes = canonical_json_bytes(raw)
    return MaterializedResearchPack(
        manifest_bytes,
        coverage_bytes,
        repository_week_bytes,
        ResearchPack.model_validate_json(manifest_bytes),
    )


def _store_research_pack(
    materialized: MaterializedResearchPack, scope: str, store: ArtifactStore
) -> tuple[ArtifactRef, ArtifactRef]:
    references: list[ArtifactRef] = []
    for relation_name, payload in (
        ("coverage", materialized.coverage_bytes),
        ("repository_week", materialized.repository_week_bytes),
    ):
        descriptor = getattr(materialized.pack.relations, relation_name)
        if descriptor.state != "present" or descriptor.artifact is None:
            raise RunnerError(f"WB-C1 ResearchPack must contain present {relation_name}")
        reference = store.put_bytes(scope, payload, "application/x-parquet")
        if (
            reference.sha256 != descriptor.artifact.sha256
            or reference.size_bytes != descriptor.artifact.size_bytes
        ):
            raise RunnerError(f"{relation_name} Parquet does not match ResearchPack artifact")
        store.put_bytes(materialized.pack.pack_id, payload, "application/x-parquet")
        references.append(reference)
    validate_pack_artifacts(materialized.pack, store)
    return references[0], references[1]


def _reference(payload: bytes, media_type: MediaType) -> ArtifactRef:
    return ArtifactRef(sha256=_sha256(payload), size_bytes=len(payload), media_type=media_type)


def _git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _ensure_reproducible_tree(root: Path) -> None:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RunnerError("benchmark requires a readable Git worktree")
    material = tuple(result.stdout.splitlines())
    if material:
        raise RunnerError("benchmark requires a clean tracked/unignored worktree")


def _recipe_seeds(dataset: BenchmarkDataset) -> tuple[int, ...]:
    series = dataset.train.series + dataset.test.series + dataset.final_holdout_metadata.series
    return tuple(
        int.from_bytes(
            hashlib.sha256(f"{item.seed_family}:{item.scenario_code}".encode()).digest()[:4],
            "big",
        )
        for item in series
    )


def _partition_part(partition: Partition) -> SplitPart:
    return SplitPart(
        window=TimeWindow(start=partition.start, end=partition.end),
        system_aliases=tuple(series.system_alias for series in partition.series),
        seed_families=partition.seed_families,
    )


def _metric(code: str, value: float | None, domain: str = "primary") -> dict[str, Any]:
    return {
        "metric_code": code,
        "domain_code": domain,
        "state": "present",
        "value": value,
        "reason_code": None,
    }


def _result_parquet_bytes(metrics: Any) -> bytes:
    return _parquet_bytes(
        [
            {
                "metric_code": "false_alerts_per_year",
                "value": metrics.false_alerts_per_year,
            },
            {"metric_code": "detection_rate", "value": metrics.detection_rate or 0.0},
        ]
    )


def _pelt_bytes(evaluation: BenchmarkEvaluation) -> bytes:
    return canonical_json_bytes(
        {
            "method": "pelt",
            "role": "offline_descriptive_only",
            "summary": {
                "evaluated_series": evaluation.pelt.evaluated_series,
                "boundary_count": evaluation.pelt.boundary_count,
                "localized_changes": evaluation.pelt.localized_changes,
                "localization_errors": evaluation.pelt.localization_errors,
            },
        }
    )


def _evaluation_artifacts(
    scope: str, store: ArtifactStore, evaluation: BenchmarkEvaluation
) -> tuple[ArtifactRef, ArtifactRef, ArtifactRef]:
    baseline = store.put_bytes(
        scope, _result_parquet_bytes(evaluation.baseline_holdout), "application/x-parquet"
    )
    candidate = store.put_bytes(
        scope, _result_parquet_bytes(evaluation.candidate_holdout), "application/x-parquet"
    )
    pelt = store.put_bytes(scope, _pelt_bytes(evaluation), "application/json")
    return baseline, candidate, pelt


def _unique_refs(references: tuple[ArtifactRef, ...]) -> tuple[ArtifactRef, ...]:
    by_digest: dict[str, ArtifactRef] = {}
    for reference in references:
        by_digest.setdefault(reference.sha256, reference)
    return tuple(by_digest.values())


def _custody_bytes(run_id: str, dataset_sha256: str, plan: EvaluationPlan) -> bytes:
    plan_sha256 = _sha256(canonical_json_bytes(asdict(plan)))
    return canonical_json_bytes(
        {
            "event": "final_holdout_custody",
            "run_id": run_id,
            "generator_revision": "wbc1.generator.v1",
            "dataset_sha256": dataset_sha256,
            "evaluation_plan_sha256": plan_sha256,
            "baseline_threshold": plan.baseline_selection.threshold,
            "candidate_threshold": plan.candidate_selection.threshold,
            "baseline_parameters_sha256": parameters_sha256(DEFAULT_BASELINE_PARAMETERS),
            "candidate_parameters_sha256": parameters_sha256(DEFAULT_BOCPD_PARAMETERS),
        }
    )


def _build_bundle(
    root: Path,
    run_id: str,
    dataset: BenchmarkDataset,
    evaluation: BenchmarkEvaluation,
    pack: ResearchPack,
    research_pack_sha256: str,
    bundle_refs: tuple[ArtifactRef, ...],
    custody_ref: ArtifactRef,
    pelt_ref: ArtifactRef,
    pack_ref: ArtifactRef,
    pack_parquet_refs: tuple[ArtifactRef, ArtifactRef],
) -> EvaluationBundle:
    required_refs = _unique_refs(
        (*bundle_refs, custody_ref, pelt_ref, pack_ref, *pack_parquet_refs)
    )
    if len(bundle_refs) != 2:
        raise RunnerError("EvaluationBundle requires baseline and candidate result artifacts")
    if (
        bundle_refs[0].media_type != "application/x-parquet"
        or bundle_refs[1].media_type != "application/x-parquet"
    ):
        raise RunnerError("EvaluationBundle result artifacts must be Parquet")
    if custody_ref.media_type != "application/json" or pelt_ref.media_type != "application/json":
        raise RunnerError("EvaluationBundle requires JSON custody and PELT artifacts")
    if pack_ref.media_type != "application/json" or any(
        ref.media_type != "application/x-parquet" for ref in pack_parquet_refs
    ):
        raise RunnerError("EvaluationBundle requires its ResearchPack manifest and Parquet data")
    if pack_ref.sha256 != research_pack_sha256:
        raise RunnerError("EvaluationBundle ResearchPack checksum must match its manifest artifact")
    pack_relation_digests = {
        descriptor.artifact.sha256
        for descriptor in (pack.relations.coverage, pack.relations.repository_week)
        if descriptor.artifact is not None
    }
    if pack_relation_digests != {ref.sha256 for ref in pack_parquet_refs}:
        raise RunnerError("EvaluationBundle ResearchPack relation artifacts do not match the pack")
    baseline = evaluation.baseline_holdout
    candidate = evaluation.candidate_holdout
    prereg = Preregistration(
        question_code="WB.C1.CHANGE_POINT",
        baseline_method_code="rolling_median_mad",
        candidate_method_code="bocpd_gaussian",
        primary_metric_code="false_alerts_per_year",
        acceptance_rule_code="candidate_beats_baseline",
        abstention_rule_code="coverage_and_support_floor",
        seed_families=dataset.train.seed_families
        + dataset.test.seed_families
        + dataset.opened_seed_families,
    )
    all_series = dataset.train.series + dataset.test.series + dataset.final_holdout_metadata.series
    expected_observations = sum(len(series.values) for series in all_series)
    observed_observations = sum(int(series.observed.sum()) for series in all_series)
    dataset_card = DatasetCard(
        generator_code="invented_weekly_series",
        generator_revision="wbc1.generator.v1",
        classification="C0",
        observation_count=expected_observations,
        system_count=len(all_series),
        coverage_counts=(
            CoverageCount(status="present", count=observed_observations),
            CoverageCount(status="absent", count=expected_observations - observed_observations),
        ),
    )
    baseline_card = ModelCard(
        model_id="wbc1_baseline",
        role="baseline",
        method_code="rolling_median_mad",
        method_revision="wbc1.methods.v1",
        deterministic=True,
        parameter_sha256=parameters_sha256(DEFAULT_BASELINE_PARAMETERS),
        no_model_fallback_code="same_as_baseline",
    )
    candidate_card = ModelCard(
        model_id="wbc1_candidate",
        role="candidate",
        method_code="bocpd_gaussian",
        method_revision="wbc1.methods.v1",
        deterministic=True,
        parameter_sha256=parameters_sha256(DEFAULT_BOCPD_PARAMETERS),
        no_model_fallback_code="rolling_median_mad",
    )
    baseline_results = ResultSet(
        model_id=baseline_card.model_id,
        metrics=(
            MetricValue.model_validate(
                _metric("false_alerts_per_year", baseline.false_alerts_per_year)
            ),
            MetricValue.model_validate(
                _metric("detection_rate", baseline.detection_rate or 0.0, "detection")
            ),
        ),
        artifact=bundle_refs[0],
    )
    candidate_results = ResultSet(
        model_id=candidate_card.model_id,
        metrics=(
            MetricValue.model_validate(
                _metric("false_alerts_per_year", candidate.false_alerts_per_year)
            ),
            MetricValue.model_validate(
                _metric("detection_rate", candidate.detection_rate or 0.0, "detection")
            ),
        ),
        artifact=bundle_refs[1],
    )
    run_manifest = RunManifest(
        run_id=run_id,
        lab_commit=_git_commit(root),
        environment_sha256=_sha256((root / "uv.lock").read_bytes()),
        started_at=LOGICAL_RUN_TIME,
        completed_at=LOGICAL_RUN_TIME,
        seeds=_recipe_seeds(dataset),
        deterministic=True,
    )
    refs = required_refs
    return EvaluationBundle(
        schema_version="DeveloperLensEvaluationBundle.v1",
        bundle_id=run_id,
        created_at=LOGICAL_RUN_TIME,
        research_pack_sha256=research_pack_sha256,
        preregistration=prereg,
        dataset_card=dataset_card,
        baseline_model_card=baseline_card,
        candidate_model_card=candidate_card,
        split_manifest=SplitManifest(
            strategy="repository_time_seed",
            train=_partition_part(dataset.train),
            test=_partition_part(dataset.test),
            final_holdout=_partition_part(dataset.final_holdout_metadata),
        ),
        run_manifest=run_manifest,
        baseline_results=baseline_results,
        candidate_results=candidate_results,
        calibration=CalibrationReport(
            status="measured",
            metrics=(
                MetricValue.model_validate(
                    _metric("brier", candidate.calibration_brier or 0.0, "calibration")
                ),
            ),
        ),
        abstention=AbstentionReport(
            eligible_count=baseline.eligible_series,
            abstained_count=baseline.abstained_series,
            reason_codes=("COVERAGE_GAP",),
        ),
        leakage=(
            LeakageCheck(
                check_code="holdout_custody", outcome="pass", detail_code="RECEIPT_BEFORE_OPEN"
            ),
        ),
        resources=ResourceReport(
            evaluation_points=expected_observations * 2,
            candidate_steps=expected_observations,
            offline_series=evaluation.pelt.evaluated_series,
            declared_wall_time_budget_ms=120_000,
            declared_peak_rss_budget_bytes=1_000_000_000,
            workload_sha256=_sha256(
                canonical_json_bytes({"dataset": dataset.dataset_sha256, "method": "wbc1.v1"})
            ),
        ),
        decision=DecisionReport(
            outcome=evaluation.decision,
            acceptance_gate_passed=evaluation.decision == "benchmarked",
            reason_codes=evaluation.decision_reasons,
        ),
        artifact_manifest=refs,
    )


def run_benchmark(
    *,
    smoke: bool = True,
    root: Path | None = None,
    artifact_root: Path | None = None,
    run_id: str | None = None,
) -> BenchmarkRun:
    root = (root or _root()).resolve()
    run_id = run_id or ("wbc1_smoke" if smoke else "wbc1_full")
    _ensure_reproducible_tree(root)
    producer_schema, provenance, vendor_pack = _load_vendor_snapshot(root)
    dataset = build_benchmark_dataset(smoke=smoke)
    plan = prepare_evaluation(dataset.train)
    scope = run_id
    store = ArtifactStore(artifact_root or (root / ".dllab"))
    try:
        store.reserve_scope(scope)
    except ArtifactError as exc:
        raise RunnerError(f"run identity is single-use and already exists: {run_id}") from exc
    receipt_holder: list[ArtifactRef] = []

    def write_receipt(dataset_sha256: str) -> None:
        if receipt_holder:
            raise RunnerError("holdout custody receipt may be written only once")
        receipt_bytes = _custody_bytes(run_id, dataset_sha256, plan)
        store.write_scope_file_once(scope, CUSTODY_RECORD_NAME, receipt_bytes + b"\n")
        receipt_holder.append(store.put_bytes(scope, receipt_bytes, "application/json"))

    final_holdout = dataset.open_final_holdout(write_receipt)
    if not receipt_holder:
        raise RunnerError("holdout custody receipt was not written before materialization")
    receipt_ref = receipt_holder[0]
    materialized = _materialize_research_pack(dataset, vendor_pack, provenance, producer_schema)
    coverage_ref, repository_week_ref = _store_research_pack(materialized, scope, store)
    pack = materialized.pack
    evaluation = run_evaluation(dataset.train, dataset.test, final_holdout, plan)
    baseline_ref, candidate_ref, pelt_ref = _evaluation_artifacts(scope, store, evaluation)
    pack_ref = store.put_bytes(scope, materialized.manifest_bytes, "application/json")
    provisional_refs = (baseline_ref, candidate_ref)
    bundle = _build_bundle(
        root,
        run_id,
        dataset,
        evaluation,
        pack,
        _sha256(materialized.manifest_bytes),
        provisional_refs,
        receipt_ref,
        pelt_ref,
        pack_ref,
        (coverage_ref, repository_week_ref),
    )
    bundle_ref = store.put_json(scope, bundle.model_dump(mode="json"))
    from .export import load_provenance

    method_provenance, research_provenance = load_provenance(root)
    source_manifest = {
        "bundle": bundle_ref.model_dump(mode="json"),
        "custody": receipt_ref.model_dump(mode="json"),
        "baseline": baseline_ref.model_dump(mode="json"),
        "candidate": candidate_ref.model_dump(mode="json"),
        "pelt": pelt_ref.model_dump(mode="json"),
        "research_pack": pack_ref.model_dump(mode="json"),
        "research_pack_coverage": coverage_ref.model_dump(mode="json"),
        "research_pack_repository_week": repository_week_ref.model_dump(mode="json"),
        "smoke": smoke,
        "product_commit": research_provenance["product_commit"],
        "product_contract_commit": method_provenance["product_commit"],
        "provenance": {
            "method_trial_view": method_provenance,
            "research_pack": research_provenance,
        },
    }
    view_ref: ArtifactRef | None = None
    if smoke:
        from .export import compose_method_trial_view

        view = compose_method_trial_view(
            run_id,
            root=root,
            store=store,
            bundle=bundle,
            manifest=source_manifest,
        )
        view_ref = store.put_json(scope, view)
        markdown_ref = store.put_text(scope, build_method_trial_markdown(view), "text/markdown")
        html_ref = store.put_text(scope, build_method_trial_html(view), "text/html")
    else:
        markdown_ref = store.put_text(scope, build_markdown(bundle), "text/markdown")
        html_ref = store.put_text(scope, build_html(bundle), "text/html")
    manifest = {
        "schema_version": "DeveloperLensWbc1Run.v1",
        "run_id": run_id,
        "smoke": smoke,
        "bundle": bundle_ref.model_dump(mode="json"),
        "markdown": markdown_ref.model_dump(mode="json"),
        "html": html_ref.model_dump(mode="json"),
        "custody": receipt_ref.model_dump(mode="json"),
        "baseline": baseline_ref.model_dump(mode="json"),
        "candidate": candidate_ref.model_dump(mode="json"),
        "pelt": pelt_ref.model_dump(mode="json"),
        "research_pack": pack_ref.model_dump(mode="json"),
        "research_pack_coverage": coverage_ref.model_dump(mode="json"),
        "research_pack_repository_week": repository_week_ref.model_dump(mode="json"),
        "dataset_sha256": dataset.dataset_sha256,
        "product_commit": provenance["product_commit"],
        "product_contract_commit": method_provenance["product_commit"],
        "producer_schema_sha256": pack.provenance.contract_sha256,
        "provenance": {
            "method_trial_view": method_provenance,
            "research_pack": research_provenance,
        },
        "lab_commit": bundle.run_manifest.lab_commit,
        "environment_sha256": bundle.run_manifest.environment_sha256,
        "deterministic_bundle_sha256": _sha256(
            canonical_json_bytes(bundle.model_dump(mode="json"))
        ),
    }
    if view_ref is not None:
        manifest["method_trial_view"] = view_ref.model_dump(mode="json")
    manifest_path = store.write_scope_file_once(
        scope, "run.json", canonical_json_bytes(manifest) + b"\n"
    )
    presentation_refs = (view_ref,) if view_ref is not None else ()
    store.write_scope_manifest(
        scope,
        (*tuple(bundle.artifact_manifest), bundle_ref, *presentation_refs, markdown_ref, html_ref),
    )
    return BenchmarkRun(
        run_id, scope, bundle, bundle_ref, view_ref, markdown_ref, html_ref, manifest_path
    )


def _assert_reproduced_reference(
    name: str, payload: bytes, media_type: MediaType, recorded: object
) -> ArtifactRef:
    expected = ArtifactRef.model_validate(recorded)
    actual = _reference(payload, media_type)
    if actual != expected:
        raise RunnerError(f"reproduced {name} bytes differ from the recorded artifact")
    return actual


def reproduce_run(manifest_path: Path, *, root: Path | None = None) -> bool:
    """Recompute a run from recorded inputs and compare deterministic bundle bytes."""
    root = (root or _root()).resolve()
    manifest = cast(dict[str, Any], json.loads(manifest_path.read_text(encoding="utf-8")))
    if manifest.get("schema_version") != "DeveloperLensWbc1Run.v1":
        raise RunnerError("unsupported WB-C1 run manifest")
    smoke = manifest.get("smoke")
    if not isinstance(smoke, bool):
        raise RunnerError("run manifest smoke flag must be Boolean")
    scope = str(manifest["run_id"])
    artifact_root = manifest_path.parents[2]
    store = ArtifactStore(artifact_root)
    if manifest_path.resolve() != (store.scope_root(scope) / "run.json").resolve():
        raise RunnerError("run manifest is outside its declared artifact scope")
    bundle_ref = ArtifactRef.model_validate(manifest["bundle"])
    expected = store.get_bytes(scope, bundle_ref)
    expected_digest = str(manifest["deterministic_bundle_sha256"])
    if _sha256(expected) != expected_digest:
        raise RunnerError("recorded bundle digest does not match stored bundle")
    reference_names = (
        "custody",
        "baseline",
        "candidate",
        "pelt",
        "markdown",
        "html",
        "research_pack",
        "research_pack_coverage",
        "research_pack_repository_week",
    )
    if smoke:
        reference_names = (*reference_names, "method_trial_view")
    for name in reference_names:
        store.get_bytes(scope, ArtifactRef.model_validate(manifest[name]))
    if _git_commit(root) != manifest.get("lab_commit"):
        raise RunnerError("current lab commit differs from the recorded run")
    if _sha256((root / "uv.lock").read_bytes()) != manifest.get("environment_sha256"):
        raise RunnerError("current uv.lock differs from the recorded run")
    producer_schema, provenance, vendor_pack = _load_vendor_snapshot(root)
    from .export import load_recorded_provenance

    try:
        method_provenance, research_provenance = load_recorded_provenance(root, manifest)
    except ValueError as exc:
        raise RunnerError(str(exc)) from exc
    if provenance.get("product_commit") != manifest.get("product_commit"):
        raise RunnerError("pinned product commit differs from the recorded run")
    if research_provenance != provenance:
        raise RunnerError("pinned ResearchPack provenance differs from the recorded run")
    if method_provenance.get("product_commit") != manifest.get("product_contract_commit"):
        raise RunnerError("pinned MethodTrialView provenance differs from the recorded run")
    schema_digest = next(
        entry["sha256"]
        for entry in cast(list[dict[str, str]], provenance["files"])
        if entry["name"] == "schema.json"
    )
    if schema_digest != manifest.get("producer_schema_sha256"):
        raise RunnerError("pinned producer schema differs from the recorded run")

    dataset = build_benchmark_dataset(smoke=smoke)
    if dataset.dataset_sha256 != manifest.get("dataset_sha256"):
        raise RunnerError("reproduced dataset recipe differs from the recorded run")
    plan = prepare_evaluation(dataset.train)
    custody_bytes = _custody_bytes(scope, dataset.dataset_sha256, plan)
    custody_path = store.scope_root(scope) / CUSTODY_RECORD_NAME
    try:
        recorded_custody = custody_path.read_bytes()
    except FileNotFoundError as exc:
        raise RunnerError("append-only holdout custody record is missing") from exc
    if recorded_custody != custody_bytes + b"\n":
        raise RunnerError("append-only holdout custody record differs from the reproduced plan")
    custody_ref = _assert_reproduced_reference(
        "custody", custody_bytes, "application/json", manifest["custody"]
    )
    custody = cast(dict[str, Any], json.loads(custody_bytes))
    holdout = dataset.replay_final_holdout(str(custody["dataset_sha256"]))
    materialized = _materialize_research_pack(dataset, vendor_pack, provenance, producer_schema)
    pack_ref = _assert_reproduced_reference(
        "ResearchPack manifest",
        materialized.manifest_bytes,
        "application/json",
        manifest["research_pack"],
    )
    coverage_ref = _assert_reproduced_reference(
        "ResearchPack coverage",
        materialized.coverage_bytes,
        "application/x-parquet",
        manifest["research_pack_coverage"],
    )
    repository_week_ref = _assert_reproduced_reference(
        "ResearchPack repository_week",
        materialized.repository_week_bytes,
        "application/x-parquet",
        manifest["research_pack_repository_week"],
    )
    evaluation = run_evaluation(dataset.train, dataset.test, holdout, plan)
    baseline_bytes = _result_parquet_bytes(evaluation.baseline_holdout)
    candidate_bytes = _result_parquet_bytes(evaluation.candidate_holdout)
    pelt_bytes = _pelt_bytes(evaluation)
    baseline_ref = _assert_reproduced_reference(
        "baseline results", baseline_bytes, "application/x-parquet", manifest["baseline"]
    )
    candidate_ref = _assert_reproduced_reference(
        "candidate results", candidate_bytes, "application/x-parquet", manifest["candidate"]
    )
    pelt_ref = _assert_reproduced_reference(
        "PELT summary", pelt_bytes, "application/json", manifest["pelt"]
    )
    bundle = _build_bundle(
        root,
        scope,
        dataset,
        evaluation,
        materialized.pack,
        _sha256(materialized.manifest_bytes),
        (baseline_ref, candidate_ref),
        custody_ref,
        pelt_ref,
        pack_ref,
        (coverage_ref, repository_week_ref),
    )
    if smoke:
        from .export import compose_method_trial_view

        view = compose_method_trial_view(
            scope,
            root=root,
            store=store,
            bundle=bundle,
            manifest=manifest,
        )
        view_bytes = canonical_json_bytes(view)
        _assert_reproduced_reference(
            "MethodTrial view", view_bytes, "application/json", manifest["method_trial_view"]
        )
        markdown_bytes = build_method_trial_markdown(view).encode("utf-8")
        html_bytes = build_method_trial_html(view).encode("utf-8")
    else:
        markdown_bytes = build_markdown(bundle).encode("utf-8")
        html_bytes = build_html(bundle).encode("utf-8")
    _assert_reproduced_reference(
        "Markdown report", markdown_bytes, "text/markdown", manifest["markdown"]
    )
    _assert_reproduced_reference("HTML report", html_bytes, "text/html", manifest["html"])
    reproduced = canonical_json_bytes(bundle.model_dump(mode="json"))
    if _reference(reproduced, "application/json") != bundle_ref:
        raise RunnerError("reproduced EvaluationBundle bytes differ from the recorded artifact")
    return reproduced == expected and _sha256(reproduced) == expected_digest


def build_report(run_id: str, *, artifact_root: Path) -> tuple[ArtifactRef, ArtifactRef]:
    store = ArtifactStore(artifact_root)
    manifest_path = store.scope_root(run_id) / "run.json"
    if not manifest_path.is_file():
        raise RunnerError(f"run manifest not found for {run_id}")
    manifest = cast(dict[str, Any], json.loads(manifest_path.read_text(encoding="utf-8")))
    smoke = manifest.get("smoke")
    if not isinstance(smoke, bool):
        raise RunnerError("run manifest smoke flag must be Boolean")
    if smoke:
        from .export import compose_method_trial_view

        view_ref = ArtifactRef.model_validate(manifest["method_trial_view"])
        view_bytes = store.get_bytes(run_id, view_ref)
        view = json.loads(view_bytes)
        recomposed = compose_method_trial_view(run_id, root=_root(), store=store, manifest=manifest)
        if canonical_json_bytes(recomposed) != view_bytes:
            raise RunnerError("stored MethodTrialView differs from recomposed canonical projection")
        markdown_text = build_method_trial_markdown(view)
        html_text = build_method_trial_html(view)
    else:
        bundle_ref = ArtifactRef.model_validate(manifest["bundle"])
        bundle = EvaluationBundle.model_validate_json(store.get_bytes(run_id, bundle_ref))
        markdown_text = build_markdown(bundle)
        html_text = build_html(bundle)
    markdown = store.put_text(run_id, markdown_text, "text/markdown")
    html_ref = store.put_text(run_id, html_text, "text/html")
    if (
        markdown.model_dump(mode="json") != manifest["markdown"]
        or html_ref.model_dump(mode="json") != manifest["html"]
    ):
        raise RunnerError("report bytes differ from the recorded deterministic report")
    store.write_scope_file(run_id, "report.md", store.get_bytes(run_id, markdown))
    store.write_scope_file(run_id, "report.html", store.get_bytes(run_id, html_ref))
    return markdown, html_ref
