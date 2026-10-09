from __future__ import annotations

import json
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
        pytest.skip("directory symlinks are unavailable on this host")


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
        with pytest.raises(ContractSyncError, match="escapes"):
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
        with pytest.raises(ContractSyncError, match="escapes"):
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
        destination.mkdir()
        (destination / "vendor").mkdir()
        (destination / "vendor" / "method-trial-views").mkdir()
        product_provenance = sync_product_contract(destination, product, commit)
        trial_provenance = sync_method_trial_view_contract(destination, product, commit)
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
        with pytest.raises(ContractSyncError):
            _ensure_confined_parent(target, root, create=False)
        assert not (root / "vendor").exists()
