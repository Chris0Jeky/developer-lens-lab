# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import cast

import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import TypeAdapter, ValidationError

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.contracts import EvaluationBundle, ResearchPack
from developer_lens_lab.contracts.common import CanonicalUtc
from developer_lens_lab.contracts.research_pack import RELATION_SCHEMA_IDS, RelationDescriptor

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
ABSOLUTE_PATH_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\|/|~[\\/]|file://)", re.IGNORECASE)
ROOTED_PATH_RE = re.compile(r"^\\(?!\\)")
LETTER_COLON_RE = re.compile(r"^[A-Za-z]:")

RELATION_SCHEMAS: dict[str, pa.Schema] = {
    "developer-lens.coverage.v1": pa.schema(
        [
            pa.field("coverage_id", pa.string(), nullable=False),
            pa.field("capability_code", pa.string(), nullable=False),
            pa.field("status", pa.string(), nullable=False),
            pa.field("observed_units", pa.int64(), nullable=False),
            pa.field("expected_units", pa.int64()),
            pa.field("window_start", pa.string(), nullable=False),
            pa.field("window_end", pa.string(), nullable=False),
        ]
    ),
    "developer-lens.repository-week.v1": pa.schema(
        [
            pa.field("repository_alias", pa.string(), nullable=False),
            pa.field("week_start", pa.string(), nullable=False),
            pa.field("metric_code", pa.string(), nullable=False),
            pa.field("value", pa.float64(), nullable=False),
            pa.field("coverage_id", pa.string(), nullable=False),
        ]
    ),
    "developer-lens.pr-episode.v1": pa.schema(
        [
            pa.field("episode_id", pa.string(), nullable=False),
            pa.field("repository_alias", pa.string(), nullable=False),
            pa.field("opened_at", pa.string(), nullable=False),
            pa.field("ready_at", pa.string()),
            pa.field("merged_at", pa.string()),
            pa.field("status", pa.string(), nullable=False),
            pa.field("coverage_id", pa.string(), nullable=False),
        ]
    ),
    "developer-lens.ci-attempt.v1": pa.schema(
        [
            pa.field("attempt_id", pa.string(), nullable=False),
            pa.field("repository_alias", pa.string(), nullable=False),
            pa.field("started_at", pa.string(), nullable=False),
            pa.field("completed_at", pa.string()),
            pa.field("outcome_code", pa.string(), nullable=False),
            pa.field("coverage_id", pa.string(), nullable=False),
        ]
    ),
    "developer-lens.release-episode.v1": pa.schema(
        [
            pa.field("release_id", pa.string(), nullable=False),
            pa.field("repository_alias", pa.string(), nullable=False),
            pa.field("week_start", pa.string(), nullable=False),
            pa.field("change_count", pa.int64(), nullable=False),
            pa.field("coverage_id", pa.string(), nullable=False),
        ]
    ),
    "developer-lens.collection-probe.v1": pa.schema(
        [
            pa.field("probe_id", pa.string(), nullable=False),
            pa.field("repository_alias", pa.string(), nullable=False),
            pa.field("observed_at", pa.string(), nullable=False),
            pa.field("status", pa.string(), nullable=False),
            pa.field("coverage_id", pa.string(), nullable=False),
        ]
    ),
    "developer-lens.system-event.v1": pa.schema(
        [
            pa.field("event_id", pa.string(), nullable=False),
            pa.field("repository_alias", pa.string(), nullable=False),
            pa.field("occurred_at", pa.string(), nullable=False),
            pa.field("event_code", pa.string(), nullable=False),
            pa.field("coverage_id", pa.string(), nullable=False),
        ]
    ),
}


class ManifestError(ValueError):
    """A manifest failed its path-free or size boundary."""


def _load_json(path: Path) -> object:
    with path.open("rb") as stream:
        payload = stream.read(MAX_MANIFEST_BYTES + 1)
    if len(payload) > MAX_MANIFEST_BYTES:
        raise ManifestError(f"manifest exceeds {MAX_MANIFEST_BYTES} bytes")
    try:
        text = payload.decode("utf-8")
    except (UnicodeDecodeError, UnicodeError) as exc:
        raise ManifestError(f"manifest {path.name} is not valid UTF-8") from exc
    return json.loads(text)


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
            candidate = node.strip()
            if (
                ABSOLUTE_PATH_RE.match(candidate)
                or ROOTED_PATH_RE.match(candidate)
                or LETTER_COLON_RE.match(candidate)
                or "../" in candidate
                or "..\\" in candidate
                or candidate == ".."
                or "." in re.split(r"[\\/]", candidate)
                or candidate.endswith("/..")
                or candidate.endswith("\\..")
            ):
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


def validate_pack_artifacts(
    pack: ResearchPack, store: ArtifactStore, scope: str | None = None
) -> None:
    # Validate the relation artifacts from the given store scope. The scope
    # defaults to the pack's own identity (used by the standalone `dllab pack
    # validate` command, where the pack owns its scope); a run passes its own
    # run-owned scope so the validation artifacts stay bound to the run and are
    # invalidated with it, rather than accumulating in a shared pack-id scope.
    read_scope = scope if scope is not None else pack.pack_id
    for relation_name, descriptor in _relation_items(pack):
        if descriptor.state != "present" or descriptor.artifact is None:
            continue
        payload = store.get_bytes(read_scope, descriptor.artifact)
        if descriptor.artifact.media_type != "application/x-parquet":
            raise ManifestError(f"present relation {relation_name} must use Parquet")
        try:
            parquet = pq.ParquetFile(pa.BufferReader(payload))
            if parquet.metadata.num_rows != descriptor.row_count:
                raise ManifestError(f"relation {relation_name} row_count does not match Parquet")
            actual_columns = tuple(parquet.schema_arrow.names)
            schema = RELATION_SCHEMAS[RELATION_SCHEMA_IDS[relation_name]]
            if actual_columns != tuple(schema.names):
                raise ManifestError(
                    f"relation {relation_name} columns differ: expected "
                    f"{tuple(schema.names)}, got {actual_columns}"
                )
            for actual, expected in zip(parquet.schema_arrow, schema, strict=True):
                if actual.type != expected.type:
                    raise ManifestError(
                        f"relation {relation_name} field {expected.name} has incompatible type"
                    )
            timestamp = TypeAdapter(CanonicalUtc)
            for batch in parquet.iter_batches():
                for field, column in zip(schema, batch.columns, strict=True):
                    label = f"relation {relation_name} field {field.name}"
                    # Inferred producer schemas allow nulls; enforce required values directly.
                    if not field.nullable and column.null_count:
                        raise ManifestError(f"{label} must not contain nulls")
                    values = [value for value in column.to_pylist() if value is not None]
                    if pa.types.is_floating(field.type):
                        if any(not math.isfinite(value) for value in values):
                            raise ManifestError(f"{label} must contain finite numbers")
                    elif pa.types.is_integer(field.type):
                        if any(value < 0 for value in values):
                            raise ManifestError(f"{label} must contain non-negative counts")
                    elif field.name.endswith(("_at", "_start", "_end")):
                        try:
                            for value in values:
                                timestamp.validate_python(value)
                        except ValidationError:
                            raise ManifestError(
                                f"{label} must contain canonical UTC timestamps"
                            ) from None
        except pa.ArrowException as exc:
            raise ManifestError(f"relation {relation_name} is not valid Parquet") from exc


def explain_validation_error(error: Exception) -> str:
    if isinstance(error, ValidationError):
        return json.dumps(error.errors(include_input=False, include_url=False), sort_keys=True)
    return str(error)
