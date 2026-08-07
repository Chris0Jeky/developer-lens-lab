from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import developer_lens_lab.contract_sync as contract_sync
from developer_lens_lab.contract_sync import (
    ContractSyncError,
    sync_method_trial_view_contract,
    sync_product_contract,
)
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


def test_sync_rejects_schema_name_drop_and_symlink_destination(tmp_path: Path) -> None:
    product, _ = _invented_product_repo(tmp_path)
    schema_path = product / "research-contracts" / "research-pack" / "v1" / "schema.json"
    schema_path.write_text('["DeveloperLensResearchPack.v1"]\n', encoding="utf-8")
    _run_git(product, "add", str(schema_path))
    _run_git(
        product,
        "-c",
        "user.name=Invented Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Break schema shape",
    )
    bad_commit = _run_git(product, "rev-parse", "HEAD")
    with pytest.raises(ContractSyncError, match="JSON Schema object"):
        sync_product_contract(tmp_path / "bad-lab", product, bad_commit)

    valid_commit = _run_git(product, "rev-parse", "HEAD^")
    destination = tmp_path / "linked-lab"
    outside = tmp_path / "outside"
    destination.mkdir()
    outside.mkdir()
    try:
        (destination / "vendor").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("directory symlinks are unavailable on this host")
    with pytest.raises(ContractSyncError, match="symlink or junction"):
        sync_product_contract(destination, product, valid_commit)
    assert list(outside.iterdir()) == []


def test_method_trial_sync_check_only_verifies_bytes_without_rewriting(tmp_path: Path) -> None:
    product = tmp_path / "product"
    source = product / "research-contracts" / "method-trial-view" / "v1"
    source.mkdir(parents=True)
    schema = (
        Path(__file__).resolve().parents[1]
        / "vendor/developer-lens/method-trial-view/v1/schema.json"
    ).read_bytes()
    (source / "schema.json").write_bytes(schema)
    _run_git(product, "init", "-b", "main")
    _run_git(product, "add", ".")
    _run_git(
        product,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "schema",
    )
    commit = _run_git(product, "rev-parse", "HEAD")
    destination = tmp_path / "lab"
    sync_method_trial_view_contract(destination, product, commit)
    before = (
        destination / "vendor/developer-lens/method-trial-view/v1/provenance.json"
    ).read_bytes()
    sync_method_trial_view_contract(destination, product, commit, check_only=True)
    assert (
        destination / "vendor/developer-lens/method-trial-view/v1/provenance.json"
    ).read_bytes() == before
    (destination / "vendor/developer-lens/method-trial-view/v1/schema.json").write_bytes(b"{}")
    with pytest.raises(ContractSyncError, match="schema differs"):
        sync_method_trial_view_contract(destination, product, commit, check_only=True)


def test_method_trial_check_only_accepts_same_bytes_at_newer_commit(tmp_path: Path) -> None:
    product = tmp_path / "product"
    source = product / "research-contracts" / "method-trial-view" / "v1"
    source.mkdir(parents=True)
    schema = (
        Path(__file__).resolve().parents[1]
        / "vendor/developer-lens/method-trial-view/v1/schema.json"
    ).read_bytes()
    (source / "schema.json").write_bytes(schema)
    _run_git(product, "init", "-b", "main")
    _run_git(product, "add", ".")
    _run_git(
        product,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "schema",
    )
    schema_commit = _run_git(product, "rev-parse", "HEAD")
    (product / "README.md").write_text("same schema bytes\n", encoding="utf-8")
    _run_git(product, "add", "README.md")
    _run_git(
        product,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "unrelated follow-up",
    )
    newer_commit = _run_git(product, "rev-parse", "HEAD")

    destination = tmp_path / "lab"
    provenance_path = sync_method_trial_view_contract(destination, product, schema_commit)
    sync_method_trial_view_contract(destination, product, newer_commit, check_only=True)
    assert (
        json.loads(provenance_path.read_text(encoding="utf-8"))["product_commit"] == schema_commit
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", "DeveloperLensContractSnapshot.v0"),
        ("identity_semantics", "join_key"),
        ("product_commit", "not-a-commit"),
        ("files", []),
    ],
)
def test_method_trial_check_only_rejects_tampered_provenance(
    tmp_path: Path, field: str, value: object
) -> None:
    product = tmp_path / "product"
    source = product / "research-contracts" / "method-trial-view" / "v1"
    source.mkdir(parents=True)
    schema = (
        Path(__file__).resolve().parents[1]
        / "vendor/developer-lens/method-trial-view/v1/schema.json"
    ).read_bytes()
    (source / "schema.json").write_bytes(schema)
    _run_git(product, "init", "-b", "main")
    _run_git(product, "add", ".")
    _run_git(
        product,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "schema",
    )
    commit = _run_git(product, "rev-parse", "HEAD")
    destination = tmp_path / "lab"
    provenance_path = sync_method_trial_view_contract(destination, product, commit)
    provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    provenance[field] = value
    provenance_path.write_text(json.dumps(provenance) + "\n", encoding="utf-8")
    with pytest.raises(ContractSyncError, match="provenance is not valid"):
        sync_method_trial_view_contract(destination, product, commit, check_only=True)


def test_method_trial_check_only_rejects_link_like_vendor_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    product = tmp_path / "product"
    source = product / "research-contracts" / "method-trial-view" / "v1"
    source.mkdir(parents=True)
    schema = (
        Path(__file__).resolve().parents[1]
        / "vendor/developer-lens/method-trial-view/v1/schema.json"
    ).read_bytes()
    (source / "schema.json").write_bytes(schema)
    _run_git(product, "init", "-b", "main")
    _run_git(product, "add", ".")
    _run_git(
        product,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "schema",
    )
    commit = _run_git(product, "rev-parse", "HEAD")
    destination = tmp_path / "lab"
    sync_method_trial_view_contract(destination, product, commit)
    vendor_parent = destination / "vendor"

    def forced_link_like(path: Path) -> bool:
        return path == vendor_parent

    monkeypatch.setattr(
        contract_sync,
        "_is_link_like",
        forced_link_like,
    )
    with pytest.raises(ContractSyncError, match="symlink or junction"):
        sync_method_trial_view_contract(destination, product, commit, check_only=True)
