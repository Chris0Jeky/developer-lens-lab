from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from developer_lens_lab.contract_sync import (
    ContractSyncError,
    _ensure_confined_parent,
    sync_method_trial_view_contract,
    sync_product_contract,
)

from .factories import research_pack


def _run_git(root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *arguments],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def _invented_product_repo(base: Path) -> tuple[Path, str]:
    from developer_lens_lab.contracts import ResearchPack

    product = base / "developer-lens"
    pack_root = product / "research-contracts" / "research-pack" / "v1"
    pack_root.mkdir(parents=True)
    schema = ResearchPack.model_json_schema(mode="validation")
    (pack_root / "schema.json").write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    fixture = ResearchPack.model_validate_json(json.dumps(research_pack()))
    (pack_root / "invented.fixture.json").write_text(
        fixture.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    trial_source = product / "research-contracts" / "method-trial-view" / "v1"
    trial_source.mkdir(parents=True)
    trial_schema = (
        Path(__file__).resolve().parents[1]
        / "vendor/developer-lens/method-trial-view/v1/schema.json"
    ).read_bytes()
    (trial_source / "schema.json").write_bytes(trial_schema)
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
        "Add invented contracts",
    )
    return product, _run_git(product, "rev-parse", "HEAD")


def _symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        if os.name != "nt":
            pytest.skip("directory symlinks are unavailable on this host")
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True,
            check=True,
        )
        assert link.is_junction()


def test_product_sync_rejects_symlinked_vendor_without_outside_write() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        product, commit = _invented_product_repo(base / "product-src")
        destination = base / "destination_root"
        destination.mkdir()
        outside = base / "outside"
        outside.mkdir()
        target = outside / "missing"
        _symlink_or_skip(destination / "vendor", target)
        with pytest.raises(ContractSyncError, match="escape"):
            sync_product_contract(destination, product, commit)
        assert list(outside.iterdir()) == []
        assert list(outside.rglob("*")) == []
        assert not (target / "schema.json").exists()
        assert not (target / "product.contract.json").exists()
        assert list(outside.glob(".contract-sync-*")) == []
        assert list(outside.glob(".sync-tmp-*")) == []


def test_method_trial_sync_rejects_symlinked_vendor_without_outside_write() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        product, commit = _invented_product_repo(base / "product-src")
        destination = base / "destination_root"
        destination.mkdir()
        outside = base / "outside"
        outside.mkdir()
        target = outside / "missing"
        _symlink_or_skip(destination / "vendor", target)
        with pytest.raises(ContractSyncError, match="escape"):
            sync_method_trial_view_contract(destination, product, commit)
        assert list(outside.iterdir()) == []
        assert list(outside.rglob("*")) == []
        assert not (target / "method-trial-views").exists()
        assert not (target / "developer-lens").exists()
        assert list(outside.glob(".contract-sync-*")) == []
        assert list(outside.glob(".sync-tmp-*")) == []


def test_in_root_sync_writes_both_contracts_without_symlinks() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        product, commit = _invented_product_repo(base / "product-src")
        destination = base / "destination_root"
        product_provenance = sync_product_contract(destination, product, commit)
        trial_destination = base / "trial_destination_root"
        trial_provenance = sync_method_trial_view_contract(trial_destination, product, commit)
        assert (product_provenance.parent / "schema.json").is_file()
        assert (product_provenance.parent / "invented.fixture.json").is_file()
        assert (trial_provenance.parent / "schema.json").is_file()
        assert product_provenance.is_file()
        assert trial_provenance.is_file()
        assert product_provenance.read_bytes()
        assert trial_provenance.read_bytes()
        assert [p for p in destination.rglob("*") if p.is_symlink()] == []


def test_ensure_confined_parent_create_false_rejects_missing_parent() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "destination_root"
        root.mkdir()
        target = root / "vendor" / "missing" / "product.contract.json"
        with pytest.raises(FileNotFoundError):
            _ensure_confined_parent(target, root, create=False)
        assert not (root / "vendor").exists()


@pytest.mark.parametrize("existing_root", [False, True])
def test_check_only_missing_snapshot_is_unavailable_without_writes(existing_root: bool) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        product, commit = _invented_product_repo(base / "product-src")
        destination = base / "destination_root"
        if existing_root:
            destination.mkdir()
        with pytest.raises(ContractSyncError, match="unavailable"):
            sync_method_trial_view_contract(destination, product, commit, check_only=True)
        assert destination.exists() == existing_root
        assert not (destination / "vendor").exists()


@pytest.mark.parametrize("method_trial", [False, True])
def test_sync_rejects_dangling_destination_root_without_outside_writes(method_trial: bool) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        product, commit = _invented_product_repo(base / "product-src")
        outside = base / "outside"
        outside.mkdir()
        destination = base / "destination_root"
        _symlink_or_skip(destination, outside / "missing")
        sync = sync_method_trial_view_contract if method_trial else sync_product_contract
        with pytest.raises(ContractSyncError, match="symlink or junction"):
            sync(destination, product, commit)
        assert list(outside.iterdir()) == []
