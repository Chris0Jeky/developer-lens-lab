from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from developer_lens_lab.contract_sync import ContractSyncError, sync_product_contract
from developer_lens_lab.contracts import ResearchPack

from .factories import research_pack


def _run_git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _invented_product_repo(tmp_path: Path) -> tuple[Path, str]:
    product = tmp_path / "developer-lens"
    contract_root = product / "research-contracts" / "research-pack" / "v1"
    contract_root.mkdir(parents=True)
    schema = ResearchPack.model_json_schema(mode="validation")
    (contract_root / "schema.json").write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    fixture = ResearchPack.model_validate_json(json.dumps(research_pack()))
    (contract_root / "invented.fixture.json").write_text(
        fixture.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    _run_git(product, "init", "-b", "main")
    _run_git(product, "add", ".")
    _run_git(
        product,
        "-c",
        "user.name=Invented Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Add invented contract",
    )
    return product, _run_git(product, "rev-parse", "HEAD")


def test_sync_reads_pinned_git_objects_and_persists_no_checkout_path(tmp_path: Path) -> None:
    product, commit = _invented_product_repo(tmp_path)
    destination = tmp_path / "lab"

    provenance_path = sync_product_contract(destination, product, commit)
    provenance_text = provenance_path.read_text(encoding="utf-8")
    provenance = json.loads(provenance_text)

    assert provenance["product_commit"] == commit
    assert provenance["identity_semantics"] == "provenance_only_not_a_join_key"
    assert str(product) not in provenance_text
    assert (provenance_path.parent / "schema.json").is_file()
    assert (provenance_path.parent / "invented.fixture.json").is_file()


def test_sync_requires_full_commit(tmp_path: Path) -> None:
    product, commit = _invented_product_repo(tmp_path)
    with pytest.raises(ContractSyncError, match="40-hex"):
        sync_product_contract(tmp_path / "lab", product, commit[:12])
