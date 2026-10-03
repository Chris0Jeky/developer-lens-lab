"""Refuse corrupt producer snapshots before creating or replacing vendor files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from developer_lens_lab.contract_sync import (
    ContractSyncError,
    sync_method_trial_view_contract,
    sync_product_contract,
)

from .test_contract_sync import (
    _invented_product_repo,  # pyright: ignore[reportPrivateUsage] - shared C0 test fixture
    _run_git,  # pyright: ignore[reportPrivateUsage] - shared pinned-commit test helper
)


def _commit(root: Path) -> str:
    _run_git(root, "add", ".")
    _run_git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-m",
        "Change invented contract",
    )
    return _run_git(root, "rev-parse", "HEAD")


@pytest.mark.parametrize("payload", [b"{", b"\xff"])
@pytest.mark.parametrize("name", ["schema.json", "invented.fixture.json"])
def test_research_pack_sync_controls_decode_errors(
    tmp_path: Path, name: str, payload: bytes
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    (product / "research-contracts/research-pack/v1" / name).write_bytes(payload)
    destination = tmp_path / "lab"
    with pytest.raises(ContractSyncError):
        sync_product_contract(destination, product, _commit(product))
    assert not destination.exists()


@pytest.mark.parametrize(
    "defect",
    ["invalid_type", "extra_required", "fixture_disagreement", "external_ref", "missing_ref"],
)
def test_research_pack_sync_validates_schema_and_producer_fixture(
    tmp_path: Path, defect: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    schema_path = product / "research-contracts/research-pack/v1/schema.json"
    schema = json.loads(schema_path.read_bytes())
    if defect == "invalid_type":
        schema["properties"]["pack_id"]["type"] = "not_a_json_schema_type"
    elif defect == "extra_required":
        schema["properties"]["new_required_field"] = {"type": "string"}
        schema["required"].append("new_required_field")
    elif defect == "external_ref":
        schema["properties"]["pack_id"] = {"$ref": "https://example.invalid/schema.json"}
    elif defect == "missing_ref":
        schema["properties"]["pack_id"] = {"$ref": "#/$defs/missing"}
    else:
        schema["properties"]["pack_id"]["const"] = "different_invented_pack"
    schema_path.write_text(json.dumps(schema), encoding="utf-8")
    destination = tmp_path / "lab"
    with pytest.raises(ContractSyncError):
        sync_product_contract(destination, product, _commit(product))
    assert not destination.exists()


def test_research_pack_sync_controls_runtime_fixture_errors(tmp_path: Path) -> None:
    product, commit = _invented_product_repo(tmp_path)
    destination = tmp_path / "lab"
    sync_product_contract(destination, product, commit)
    before = {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*.json")}
    fixture_path = product / "research-contracts/research-pack/v1/invented.fixture.json"
    fixture = json.loads(fixture_path.read_bytes())
    fixture["classification"] = "C4"
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    with pytest.raises(ContractSyncError):
        sync_product_contract(destination, product, _commit(product))
    after = {p.relative_to(destination): p.read_bytes() for p in destination.rglob("*.json")}
    assert after == before


@pytest.mark.parametrize("defect", ["properties", "version", "nested_type", "utf8"])
def test_method_trial_sync_checks_complete_schema_before_writing(
    tmp_path: Path, defect: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = product / "research-contracts/method-trial-view/v1/schema.json"
    source.parent.mkdir(parents=True)
    vendor = Path(__file__).resolve().parents[1] / "vendor/developer-lens/method-trial-view/v1"
    schema = json.loads((vendor / "schema.json").read_bytes())
    if defect == "properties":
        schema["properties"] = []
    elif defect == "version":
        schema["properties"]["schema_version"] = []
    elif defect == "nested_type":
        schema["properties"]["run_id"] = {"type": "not_a_json_schema_type"}
    source.write_bytes(b"\xff" if defect == "utf8" else json.dumps(schema).encode())
    destination = tmp_path / "lab"
    with pytest.raises(ContractSyncError):
        sync_method_trial_view_contract(destination, product, _commit(product))
    assert not destination.exists()


@pytest.mark.parametrize("contract", ["research-pack", "method-trial-view"])
@pytest.mark.parametrize("keyword", ["$ref", "$dynamicRef"])
@pytest.mark.parametrize("reference", ["#/$defs/missing", "https://example.invalid/missing"])
def test_sync_refuses_unresolved_references_in_unused_subschemas(
    tmp_path: Path, contract: str, keyword: str, reference: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = product / "research-contracts" / contract / "v1/schema.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    vendor = Path(__file__).resolve().parents[1] / "vendor/developer-lens" / contract / "v1"
    schema = json.loads((vendor / "schema.json").read_bytes())
    schema["properties"]["unused"] = {keyword: reference}
    source.write_text(json.dumps(schema), encoding="utf-8")
    destination = tmp_path / "lab"
    sync = sync_product_contract if contract == "research-pack" else sync_method_trial_view_contract
    with pytest.raises(ContractSyncError):
        sync(destination, product, _commit(product))
    assert not destination.exists()


def test_sync_accepts_local_reference_closure_without_scanning_instance_data(
    tmp_path: Path,
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = product / "research-contracts/research-pack/v1/schema.json"
    schema = json.loads(source.read_bytes())
    schema.setdefault("$defs", {})["packId"] = schema["properties"]["pack_id"]
    schema["properties"]["pack_id"] = {"$ref": "#/$defs/packId"}
    schema["examples"] = [{"$ref": "https://example.invalid/instance-not-schema"}]
    source.write_text(json.dumps(schema), encoding="utf-8")
    destination = tmp_path / "lab"
    sync_product_contract(destination, product, _commit(product))
    assert (destination / "vendor/developer-lens/research-pack/v1/schema.json").read_bytes() == (
        source.read_bytes()
    )


@pytest.mark.parametrize("contract", ["research-pack", "method-trial-view"])
@pytest.mark.parametrize("reference", ["child", "", "https://example.invalid/root/child"])
def test_sync_accepts_bundled_uri_references_without_retrieval(
    tmp_path: Path, contract: str, reference: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = product / "research-contracts" / contract / "v1/schema.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    vendor = Path(__file__).resolve().parents[1] / "vendor/developer-lens" / contract / "v1"
    schema = json.loads((vendor / "schema.json").read_bytes())
    schema["$id"] = "https://example.invalid/root/"
    schema.setdefault("$defs", {})["bundledChild"] = {"$id": "child", "type": "string"}
    schema["properties"]["unused"] = {"$ref": reference}
    source.write_text(json.dumps(schema), encoding="utf-8")
    destination = tmp_path / "lab"
    sync = sync_product_contract if contract == "research-pack" else sync_method_trial_view_contract
    sync(destination, product, _commit(product))
    assert (destination / "vendor/developer-lens" / contract / "v1/schema.json").read_bytes() == (
        source.read_bytes()
    )
