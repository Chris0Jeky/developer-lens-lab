from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from developer_lens_lab.contracts import ResearchPack

PRODUCT_FILES = {
    "schema.json": "research-contracts/research-pack/v1/schema.json",
    "invented.fixture.json": "research-contracts/research-pack/v1/invented.fixture.json",
}
VENDOR_ROOT = Path("vendor/developer-lens/research-pack/v1")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


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


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(prefix=".sync-tmp-", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


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
    if "DeveloperLensResearchPack.v1" not in json.dumps(schema_raw, sort_keys=True):
        raise ContractSyncError("producer schema does not declare DeveloperLensResearchPack.v1")
    fixture = ResearchPack.model_validate_json(snapshots["invented.fixture.json"])
    if fixture.classification != "C0":
        raise ContractSyncError("producer fixture must remain C0 invented data")

    destination = destination_root / VENDOR_ROOT
    file_records: list[dict[str, object]] = []
    for name, payload in sorted(snapshots.items()):
        _atomic_write(destination / name, payload)
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
    )
    return provenance_path
