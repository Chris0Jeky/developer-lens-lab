from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import cast

from developer_lens_lab.contracts import ResearchPack

PRODUCT_FILES = {
    "schema.json": "research-contracts/research-pack/v1/schema.json",
    "invented.fixture.json": "research-contracts/research-pack/v1/invented.fixture.json",
}
VENDOR_ROOT = Path("vendor/developer-lens/research-pack/v1")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_SCHEMA_PROPERTIES = {
    "schema_version",
    "pack_id",
    "generated_at",
    "classification",
    "provenance",
    "temporal_availability",
    "relations",
    "feature_registry",
}


class ContractSyncError(RuntimeError):
    """A pinned producer snapshot could not be verified or synchronized."""


def _git(checkout: Path, *arguments: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(checkout), *arguments],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ContractSyncError(message or "git command failed")
    return result.stdout


def _is_link_like(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def _ensure_confined_parent(path: Path, root: Path) -> None:
    current = path.parent
    while current != root:
        if current.exists() and _is_link_like(current):
            raise ContractSyncError("contract destination traverses a symlink or junction")
        current = current.parent
    if root.exists() and _is_link_like(root):
        raise ContractSyncError("contract destination root must not be a symlink or junction")
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.parent.resolve().is_relative_to(root.resolve()):
        raise ContractSyncError("contract destination escaped the repository root")


def _atomic_write(path: Path, payload: bytes, root: Path) -> None:
    _ensure_confined_parent(path, root)
    handle, temporary_name = tempfile.mkstemp(prefix=".sync-tmp-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _validate_producer_schema(value: object) -> None:
    if not isinstance(value, dict):
        raise ContractSyncError("producer schema must be a JSON Schema object")
    raw_schema = cast(dict[object, object], value)
    if not all(isinstance(key, str) for key in raw_schema):
        raise ContractSyncError("producer schema keys must be strings")
    schema = cast(dict[str, object], raw_schema)
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        raise ContractSyncError("producer schema must be a strict top-level object")
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, dict) or not isinstance(required, list):
        raise ContractSyncError("producer schema must declare properties and required fields")
    raw_properties = cast(dict[object, object], properties)
    property_names = {key for key in raw_properties if isinstance(key, str)}
    required_items = cast(list[object], required)
    required_names = {item for item in required_items if isinstance(item, str)}
    if (
        not property_names >= REQUIRED_SCHEMA_PROPERTIES
        or not required_names >= REQUIRED_SCHEMA_PROPERTIES
    ):
        raise ContractSyncError("producer schema is missing required ResearchPack fields")
    version = raw_properties.get("schema_version")
    if not isinstance(version, dict):
        raise ContractSyncError("producer schema has the wrong ResearchPack version")
    raw_version = cast(dict[object, object], version)
    if raw_version.get("const") != "DeveloperLensResearchPack.v1":
        raise ContractSyncError("producer schema has the wrong ResearchPack version")


def sync_product_contract(destination_root: Path, checkout: Path, commit: str) -> Path:
    if not COMMIT_RE.fullmatch(commit):
        raise ContractSyncError("--ref must be a full lowercase 40-hex commit")
    checkout = checkout.resolve()
    if not checkout.is_dir():
        raise ContractSyncError("--from must name an existing checkout")
    resolved = _git(checkout, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if resolved.decode("ascii").strip() != commit:
        raise ContractSyncError("--ref did not resolve to the exact requested commit")

    snapshots: dict[str, bytes] = {}
    for target_name, source_path in PRODUCT_FILES.items():
        snapshots[target_name] = _git(checkout, "show", f"{commit}:{source_path}")

    schema_raw = json.loads(snapshots["schema.json"])
    _validate_producer_schema(schema_raw)
    fixture = ResearchPack.model_validate_json(snapshots["invented.fixture.json"])
    if fixture.classification != "C0":
        raise ContractSyncError("producer fixture must remain C0 invented data")

    if destination_root.exists() and _is_link_like(destination_root):
        raise ContractSyncError("contract destination root must not be a symlink or junction")
    destination_root = destination_root.resolve()
    destination = destination_root / VENDOR_ROOT
    file_records: list[dict[str, object]] = []
    for name, payload in sorted(snapshots.items()):
        _atomic_write(destination / name, payload, destination_root)
        file_records.append(
            {
                "name": name,
                "sha256": "sha256:" + hashlib.sha256(payload).hexdigest(),
                "size_bytes": len(payload),
            }
        )
    provenance = {
        "schema_version": "DeveloperLensContractSnapshot.v1",
        "product_commit": commit,
        "files": file_records,
        "identity_semantics": "provenance_only_not_a_join_key",
    }
    provenance_path = destination / "provenance.json"
    _atomic_write(
        provenance_path,
        (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        destination_root,
    )
    return provenance_path
