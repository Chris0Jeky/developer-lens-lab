# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import copy
import hashlib
import json
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from developer_lens_lab.artifacts import ArtifactError, ArtifactStore
from developer_lens_lab.contracts import ArtifactRef, EvaluationBundle
from developer_lens_lab.contracts.method_trial_view import validate_method_trial_view
from developer_lens_lab.contracts.research_finding import (
    FindingError,
    derive_gates,
    finding_bundle_hash,
    load_finding_contract,
    validate_research_finding,
)
from developer_lens_lab.finding_canonical import stable_bytes
from developer_lens_lab.finding_source import (
    validate_recorded_provenance,
    validate_snapshot,
    validate_study_identity,
)

_MAX_JSON_BYTES = 1_048_576
_METRIC_DOMAINS = {
    "detection_rate": "detection",
    "false_alerts_per_year": "primary",
    "median_detection_delay_weeks": "detection",
    "coverage_confound_false_alert_rate": "coverage",
}


@dataclass(frozen=True)
class FindingExportResult:
    output_path: Path
    sha256: str
    bundle_hash: str


def _digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise FindingError("stored JSON contains duplicate object keys")
        value[key] = item
    return value


def _json_object(payload: bytes) -> dict[str, Any]:
    if len(payload) > _MAX_JSON_BYTES:
        raise FindingError("stored evidence exceeds the JSON size bound")
    try:
        value = json.loads(payload, object_pairs_hook=_unique_object)
        if not isinstance(value, dict):
            raise ValueError("not an object")
        return cast(dict[str, Any], value)
    except (ValueError, RecursionError) as exc:
        raise FindingError("stored evidence is not a valid JSON object") from exc


def _source_bundle(payload: bytes) -> EvaluationBundle:
    value = _json_object(payload)
    try:
        return EvaluationBundle.model_validate_json(json.dumps(value, allow_nan=False))
    except (ValueError, RecursionError) as exc:
        raise FindingError("stored EvaluationBundle does not satisfy its contract") from exc


def _verified_producer_snapshots(root: Path) -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    for key, name, filenames in (
        ("method_trial_view", "method-trial-view", ("schema.json",)),
        ("research_pack", "research-pack", ("invented.fixture.json", "schema.json")),
    ):
        directory = root / "vendor/developer-lens" / name / "v1"
        provenance = _json_object(_read_confined(directory / "provenance.json", root))
        payloads = {
            filename: _read_confined(directory / filename, root) for filename in filenames
        }
        try:
            validate_snapshot(provenance, payloads)
        except (ArtifactError, ValueError) as exc:
            raise FindingError("source contract provenance does not match verified bytes") from exc
        snapshots[key] = provenance
    return snapshots


def _validated_view(
    source: object,
    bundle: EvaluationBundle,
    bundle_digest: str,
    product_commit: str,
    root: Path,
) -> dict[str, Any]:
    try:
        view = validate_method_trial_view(source, root=root)
    except (ValueError, OSError, RecursionError) as exc:
        raise FindingError("stored MethodTrialView does not satisfy its contract") from exc
    reproduction = view["reproducibility"]
    if (
        reproduction["run_id"] != bundle.run_manifest.run_id
        or reproduction["lab_commit"] != bundle.run_manifest.lab_commit
        or reproduction["product_contract_commit"] != product_commit
        or reproduction["digests"]["evaluation_bundle"] != bundle_digest
        or reproduction["digests"]["research_pack"] != bundle.research_pack_sha256
        or view["decision"]["outcome"] != bundle.decision.outcome
        or view["decision"]["reason_codes"] != list(bundle.decision.reason_codes)
    ):
        raise FindingError("stored MethodTrialView is not linked to the same bundle evidence")
    schema_root = root / "vendor/developer-lens/method-trial-view/v1"
    provenance = _json_object(_read_confined(schema_root / "provenance.json", root))
    schema_payload = _read_confined(schema_root / "schema.json", root)
    expected_files = [
        {
            "name": "schema.json",
            "sha256": _digest(schema_payload),
            "size_bytes": len(schema_payload),
        }
    ]
    if (
        provenance.get("product_commit") != product_commit
        or reproduction["digests"]["schema"] != _digest(schema_payload)
        or provenance.get("files") != expected_files
    ):
        raise FindingError("stored MethodTrialView schema provenance does not match its pin")
    dataset = view["dataset"]
    coverage = {item.status: item.count for item in bundle.dataset_card.coverage_counts}
    if (
        dataset["system_count"] != bundle.dataset_card.system_count
        or dataset["weekly_opportunity_count"] != bundle.dataset_card.observation_count
        or dataset["observed_count"] != coverage.get("present", 0)
        or dataset["absent_count"] != coverage.get("absent", 0)
    ):
        raise FindingError("stored MethodTrialView and bundle disagree on dataset coverage")
    return view


def compose_finding(
    bundle_payload: bytes,
    *,
    root: Path,
    product_contract_commit: str,
    source_view: object | None = None,
) -> dict[str, Any]:
    """Project stored evidence only. No generator, method, runner, or holdout is invoked."""
    bundle = _source_bundle(bundle_payload)
    try:
        validate_study_identity(bundle)
    except ValueError as exc:
        raise FindingError(
            "no finding adapter is registered for these source study semantics"
        ) from exc
    snapshots = _verified_producer_snapshots(root)
    if product_contract_commit != snapshots["method_trial_view"]["product_commit"]:
        raise FindingError("finding source contract commit differs from its verified pin")
    view = (
        None
        if source_view is None
        else _validated_view(
            source_view, bundle, _digest(bundle_payload), product_contract_commit, root
        )
    )
    value = copy.deepcopy(load_finding_contract(root)["fixture"])
    value["generated_at"] = bundle.created_at
    value["provenance"]["source_lab_commit"] = bundle.run_manifest.lab_commit
    value["provenance"]["source_product_contract_commit"] = product_contract_commit
    outcome = bundle.decision.outcome
    summaries = {
        "reject": "The candidate is rejected; the deterministic baseline is retained.",
        "revise_once": "The stored trial permits one revision; no method is promoted.",
        "benchmarked": "The stored trial is benchmarked; this does not promote a model.",
    }
    value["decision"] = {
        "outcome": outcome,
        "retained_fallback": "rolling_median_mad" if outcome == "reject" else None,
        "summary": summaries[outcome],
    }
    if outcome != "reject":
        value["finding"]["title"] = "WB-C1 stored method trial"
    for side, results in (
        ("baseline", bundle.baseline_results),
        ("candidate", bundle.candidate_results),
    ):
        recorded: dict[str, dict[str, Any]] = {}
        for metric in results.metrics:
            if metric.metric_code not in _METRIC_DOMAINS:
                continue
            if (
                metric.domain_code != _METRIC_DOMAINS[metric.metric_code]
                or metric.metric_code in recorded
            ):
                raise FindingError("finding metric has an ambiguous or unsupported source domain")
            recorded[metric.metric_code] = (
                {"status": "measured", "value": metric.value}
                if metric.state == "present"
                else {"status": "unavailable"}
            )
        for metric in value["metrics"]:
            code = metric["key"]
            source_measurement = None
            if view is not None:
                measurement = view["scorecard"][side][code]
                source_measurement = (
                    {"status": "measured", "value": measurement["value"]}
                    if measurement["status"] == "measured"
                    else {"status": "unavailable"}
                )
                if code in recorded and recorded[code] != source_measurement:
                    raise FindingError("stored bundle and view contain conflicting metric evidence")
            metric[side] = recorded.get(code, source_measurement or {"status": "unavailable"})
    if view is None:
        value.pop("threshold_viability", None)
        value["provenance"].pop("public_url", None)
        value["limitations"] = value["limitations"][:1]
    else:
        selection = view["scorecard"]["threshold_selection"]
        value["threshold_viability"] = {
            side: selection[side]["viable"] for side in ("baseline", "candidate")
        }
        value["decision"]["summary"] = view["decision"]["summary"]
        if any(value["threshold_viability"].values()):
            value["limitations"] = [
                item for item in value["limitations"] if item["code"] != "thresholds_nonviable"
            ]
    value["gates"] = derive_gates(value)
    value["provenance"]["bundle_hash"] = finding_bundle_hash(value)
    return validate_research_finding(value, root=root)


def _read_confined(path: Path, root: Path) -> bytes:
    if not path.is_relative_to(root):
        raise FindingError("stored evidence escaped its artifact root")
    current = path
    while True:
        if current.is_symlink() or current.is_junction():
            raise FindingError("stored evidence must not traverse links")
        if current == root:
            break
        current = current.parent
    try:
        if not stat.S_ISREG(path.stat().st_mode):
            raise FindingError("stored evidence must be a regular file")
        with path.open("rb") as stream:
            payload = stream.read(_MAX_JSON_BYTES + 1)
    except OSError as exc:
        raise FindingError("stored evidence is unavailable") from exc
    if len(payload) > _MAX_JSON_BYTES:
        raise FindingError("stored evidence exceeds the JSON size bound")
    return payload


def _artifact_json(store: ArtifactStore, run_id: str, raw_ref: object) -> bytes:
    try:
        reference = ArtifactRef.model_validate_json(json.dumps(raw_ref))
    except ValueError as exc:
        raise FindingError("stored evidence reference is invalid") from exc
    if reference.media_type != "application/json" or reference.size_bytes > _MAX_JSON_BYTES:
        raise FindingError("finding source must be a bounded JSON artifact")
    digest = reference.sha256.removeprefix("sha256:")
    path = store.scope_root(run_id) / "objects" / digest[:2] / digest
    payload = _read_confined(path, store.root)
    if len(payload) != reference.size_bytes or _digest(payload) != reference.sha256:
        raise FindingError("stored evidence failed digest or size verification")
    return payload


def export_finding(
    run_id: str,
    *,
    root: Path,
    output: Path | None = None,
    artifact_root: Path | None = None,
) -> FindingExportResult:
    """Atomically publish a validated projection without modifying source run artifacts."""
    root = root.resolve()
    try:
        store = ArtifactStore(artifact_root if artifact_root is not None else root / ".dllab")
        manifest_path = store.scope_root(run_id) / "run.json"
        manifest = _json_object(_read_confined(manifest_path, store.root))
        if (
            manifest.get("schema_version") != "DeveloperLensWbc1Run.v1"
            or manifest.get("run_id") != run_id
        ):
            raise FindingError("stored run manifest has an unsupported identity")
        bundle_payload = _artifact_json(store, run_id, manifest.get("bundle"))
        bundle = _source_bundle(bundle_payload)
        if (
            bundle.bundle_id != run_id
            or bundle.run_manifest.run_id != run_id
            or manifest.get("lab_commit") != bundle.run_manifest.lab_commit
            or manifest.get("deterministic_bundle_sha256") != _digest(bundle_payload)
        ):
            raise FindingError("stored run manifest and bundle provenance disagree")
        product_commit = validate_recorded_provenance(manifest, _verified_producer_snapshots(root))
        view = None
        if "method_trial_view" in manifest:
            view = _json_object(_artifact_json(store, run_id, manifest["method_trial_view"]))
        value = compose_finding(
            bundle_payload, root=root, product_contract_commit=product_commit, source_view=view
        )
        destination = output if output is not None else root / "research-finding.json"
        # Resolve the parent only: replacing a final symlink must not overwrite its target.
        destination = destination.parent.resolve() / destination.name
        if destination.is_relative_to(store.root):
            raise FindingError("finding output must not overwrite the source artifact store")
        payload = stable_bytes(value)
        # Reuse the store's same-directory temporary-file and atomic-replace publisher.
        ArtifactStore._atomic_write(destination, payload)  # pyright: ignore[reportPrivateUsage]
    except FindingError:
        raise
    except (ArtifactError, OSError, ValueError, RecursionError) as exc:
        raise FindingError("finding export could not validate or publish its evidence") from exc
    return FindingExportResult(destination, _digest(payload), value["provenance"]["bundle_hash"])
