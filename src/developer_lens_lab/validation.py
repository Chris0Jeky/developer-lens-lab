# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import cast

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import ValidationError

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.contracts import EvaluationBundle, ResearchPack
from developer_lens_lab.contracts.research_pack import RelationDescriptor

MAX_MANIFEST_BYTES = 1_000_000
FORBIDDEN_KEY_FRAGMENTS = {
    "command",
    "host_fingerprint",
    "local_path",
    "provider_id",
    "repository_name",
    "username",
}
FORBIDDEN_EXACT_KEYS = {"environment_name", "environment_value", "environment_variables"}
ABSOLUTE_PATH_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|/home/|/Users/|/var/|/tmp/)")

RELATION_COLUMNS: dict[str, tuple[str, ...]] = {
    "coverage": (
        "coverage_id",
        "capability_code",
        "status",
        "observed_units",
        "expected_units",
        "window_start",
        "window_end",
    ),
    "repository_week": (
        "repository_alias",
        "week_start",
        "metric_code",
        "value",
        "coverage_id",
    ),
    "pr_episode": (
        "episode_id",
        "repository_alias",
        "opened_at",
        "ready_at",
        "merged_at",
        "status",
        "coverage_id",
    ),
    "ci_attempt": (
        "attempt_id",
        "repository_alias",
        "started_at",
        "completed_at",
        "outcome_code",
        "coverage_id",
    ),
    "release_episode": (
        "release_id",
        "repository_alias",
        "week_start",
        "change_count",
        "coverage_id",
    ),
    "collection_probe": (
        "probe_id",
        "repository_alias",
        "observed_at",
        "status",
        "coverage_id",
    ),
    "system_event": (
        "event_id",
        "repository_alias",
        "occurred_at",
        "event_code",
        "coverage_id",
    ),
}


class ManifestError(ValueError):
    """A manifest failed its path-free or size boundary."""


def _load_json(path: Path) -> object:
    size = path.stat().st_size
    if size > MAX_MANIFEST_BYTES:
        raise ManifestError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    return json.loads(path.read_text(encoding="utf-8"))


def assert_path_free_manifest(value: object) -> None:
    def visit(node: object) -> None:
        if isinstance(node, dict):
            mapping = cast(dict[object, object], node)
            for raw_key, child in mapping.items():
                if not isinstance(raw_key, str):
                    raise ManifestError("manifest keys must be strings")
                lowered = raw_key.casefold()
                if lowered in FORBIDDEN_EXACT_KEYS or any(
                    fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS
                ):
                    raise ManifestError(f"forbidden manifest key: {raw_key}")
                visit(child)
        elif isinstance(node, list):
            for child in cast(list[object], node):
                visit(child)
        elif isinstance(node, str):
            if ABSOLUTE_PATH_RE.match(node) or "../" in node or "..\\" in node:
                raise ManifestError("manifest contains a local path")

    visit(value)


def validate_research_pack(path: Path) -> ResearchPack:
    raw = _load_json(path)
    assert_path_free_manifest(raw)
    pack = ResearchPack.model_validate_json(json.dumps(raw, separators=(",", ":")))
    if pack.classification != "C0":
        raise ManifestError("bootstrap validator accepts C0 invented packs only")
    return pack


def validate_evaluation_bundle(path: Path) -> EvaluationBundle:
    raw = _load_json(path)
    assert_path_free_manifest(raw)
    return EvaluationBundle.model_validate_json(json.dumps(raw, separators=(",", ":")))


def _relation_items(pack: ResearchPack) -> tuple[tuple[str, RelationDescriptor], ...]:
    return (
        ("coverage", pack.relations.coverage),
        ("repository_week", pack.relations.repository_week),
        ("pr_episode", pack.relations.pr_episode),
        ("ci_attempt", pack.relations.ci_attempt),
        ("release_episode", pack.relations.release_episode),
        ("collection_probe", pack.relations.collection_probe),
        ("system_event", pack.relations.system_event),
    )


def profile_research_pack(pack: ResearchPack) -> dict[str, object]:
    relation_states = Counter(descriptor.state for _, descriptor in _relation_items(pack))
    return {
        "schema_version": pack.schema_version,
        "classification": pack.classification,
        "relations": dict(sorted(relation_states.items())),
        "present_rows": sum(
            descriptor.row_count or 0
            for _, descriptor in _relation_items(pack)
            if descriptor.state == "present"
        ),
        "features": len(pack.feature_registry),
        "temporal_availability": {
            "event": pack.temporal_availability.event.state,
            "collection": pack.temporal_availability.collection.state,
            "feature": pack.temporal_availability.feature.state,
        },
    }


def validate_pack_artifacts(pack: ResearchPack, store: ArtifactStore) -> None:
    for relation_name, descriptor in _relation_items(pack):
        if descriptor.state != "present" or descriptor.artifact is None:
            continue
        payload = store.get_bytes(pack.pack_id, descriptor.artifact)
        if descriptor.artifact.media_type != "application/x-parquet":
            raise ManifestError(f"present relation {relation_name} must use Parquet")
        parquet = pq.ParquetFile(pa.BufferReader(payload))
        if parquet.metadata.num_rows != descriptor.row_count:
            raise ManifestError(f"relation {relation_name} row_count does not match Parquet")
        actual_columns = tuple(parquet.schema_arrow.names)
        if actual_columns != RELATION_COLUMNS[relation_name]:
            raise ManifestError(
                f"relation {relation_name} columns differ: expected "
                f"{RELATION_COLUMNS[relation_name]}, got {actual_columns}"
            )


def explain_validation_error(error: Exception) -> str:
    if isinstance(error, ValidationError):
        return json.dumps(error.errors(include_url=False), sort_keys=True)
    return str(error)
