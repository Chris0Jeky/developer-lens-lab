"""Exercise fixture validation after references enter bundled legacy dialects."""

from __future__ import annotations

import json
import socket
import urllib.request
from pathlib import Path
from typing import NoReturn

import pytest

from developer_lens_lab.contract_sync import (
    ContractSyncError,
    _validate_fixture_against_producer_schema,  # pyright: ignore[reportPrivateUsage]
    sync_method_trial_view_contract,
    sync_product_contract,
)

from .test_contract_sync import (
    _invented_product_repo,  # pyright: ignore[reportPrivateUsage] - shared C0 fixture
)
from .test_contract_sync_validation import (
    _commit,  # pyright: ignore[reportPrivateUsage] - shared pinned-commit helper
    _embedded_contract_source,  # pyright: ignore[reportPrivateUsage] - shared C0 fixture
)

DRAFT_2020 = "https://json-schema.org/draft/2020-12/schema"
DRAFT_2019 = "https://json-schema.org/draft/2019-09/schema"
DRAFT_7 = "http://json-schema.org/draft-07/schema#"


@pytest.fixture(autouse=True)
def forbid_external_retrieval(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*_args: object, **_kwargs: object) -> NoReturn:
        raise AssertionError("contract validation must not retrieve external resources")

    monkeypatch.setattr(urllib.request, "urlopen", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(socket, "getaddrinfo", refuse)


def _destination_bytes(destination: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(destination): path.read_bytes()
        for path in destination.rglob("*")
        if path.is_file()
    }


def _write_tuple_schema(product: Path, dialect: str, reference: str = "legacy") -> Path:
    source = product / "research-contracts/research-pack/v1/schema.json"
    schema = json.loads(source.read_bytes())
    schema["$schema"] = DRAFT_2020
    schema["$id"] = "https://example.invalid/root/"
    schema["$defs"]["legacy"] = {
        "$schema": dialect,
        "$id": "legacy",
        "definitions": {
            "tuple": {
                "$id": "tuple",
                "type": "array",
                "items": [
                    {
                        "type": "object",
                        "properties": {"feature_id": {"const": "DL.WEEK.CHANGE_COUNT.v1"}},
                        "required": ["feature_id"],
                    }
                ],
                "additionalItems": False,
                "minItems": 1,
            }
        },
        "allOf": [{"$ref": "tuple"}],
    }
    schema["properties"]["feature_registry"] = {"$ref": reference}
    source.write_text(json.dumps(schema), encoding="utf-8")
    return source


@pytest.mark.parametrize("dialect", [DRAFT_7, DRAFT_2019])
@pytest.mark.parametrize("reference", ["legacy", "tuple", "legacy#/definitions/tuple"])
def test_sync_validates_legacy_tuple_items_reached_through_references(
    tmp_path: Path, dialect: str, reference: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = _write_tuple_schema(product, dialect, reference)
    destination = tmp_path / "lab"

    sync_product_contract(destination, product, _commit(product))

    assert (destination / "vendor/developer-lens/research-pack/v1/schema.json").read_bytes() == (
        source.read_bytes()
    )


@pytest.mark.parametrize("dialect", [DRAFT_7, DRAFT_2019])
@pytest.mark.parametrize("reference", ["legacy", "tuple"])
@pytest.mark.parametrize("existing_destination", [False, True])
@pytest.mark.parametrize("defect", ["item_type", "item_value", "additional_item"])
def test_sync_rejects_invalid_legacy_tuples_before_writing(
    tmp_path: Path, dialect: str, reference: str, existing_destination: bool, defect: str
) -> None:
    product, commit = _invented_product_repo(tmp_path)
    destination = tmp_path / "lab"
    if existing_destination:
        sync_product_contract(destination, product, commit)
    before = _destination_bytes(destination)
    _write_tuple_schema(product, dialect, reference)
    fixture_path = product / "research-contracts/research-pack/v1/invented.fixture.json"
    fixture = json.loads(fixture_path.read_bytes())
    if defect == "item_type":
        fixture["feature_registry"] = [0]
    elif defect == "item_value":
        fixture["feature_registry"][0]["feature_id"] = "DL.WEEK.OTHER_COUNT.v1"
    else:
        fixture["feature_registry"] *= 2
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")

    with pytest.raises(ContractSyncError, match="fixture does not conform"):
        sync_product_contract(destination, product, _commit(product))

    assert _destination_bytes(destination) == before
    assert destination.exists() is existing_destination


@pytest.mark.parametrize("reference", ["legacy", "feature", "legacy#/definitions/feature"])
@pytest.mark.parametrize("allowed_unit", ["count", "different_unit"])
def test_sync_enforces_inherited_draft7_dependencies(
    tmp_path: Path, reference: str, allowed_unit: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = _write_tuple_schema(product, DRAFT_7)
    schema = json.loads(source.read_bytes())
    schema["$defs"]["legacy"] = {
        "$schema": DRAFT_7,
        "$id": "legacy",
        "definitions": {
            "feature": {
                "$id": "feature",
                "type": "object",
                "dependencies": {
                    "feature_id": {"properties": {"unit_code": {"const": allowed_unit}}}
                },
            }
        },
        "allOf": [{"$ref": "feature"}],
    }
    schema["properties"]["feature_registry"] = {"type": "array", "items": {"$ref": reference}}
    source.write_text(json.dumps(schema), encoding="utf-8")
    destination = tmp_path / "lab"
    commit = _commit(product)

    if allowed_unit == "count":
        sync_product_contract(destination, product, commit)
        assert (
            destination / "vendor/developer-lens/research-pack/v1/schema.json"
        ).read_bytes() == (source.read_bytes())
    else:
        with pytest.raises(ContractSyncError, match="fixture does not conform"):
            sync_product_contract(destination, product, commit)
        assert not destination.exists()


def test_sync_preserves_instance_valued_keywords_and_original_schema(tmp_path: Path) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = _write_tuple_schema(product, DRAFT_7, "tuple")
    schema = json.loads(source.read_bytes())
    fixture = json.loads(source.with_name("invented.fixture.json").read_bytes())
    tuple_schema = schema["$defs"]["legacy"]["definitions"]["tuple"]
    tuple_schema["items"][0]["const"] = fixture["feature_registry"][0]
    tuple_schema["examples"] = [{"$schema": "https://example.invalid/instance-only-dialect"}]
    source.write_text(json.dumps(schema), encoding="utf-8")
    before = source.read_bytes()
    destination = tmp_path / "lab"

    _validate_fixture_against_producer_schema(schema, json.dumps(fixture).encode())
    assert schema == json.loads(before)
    sync_product_contract(destination, product, _commit(product))

    assert source.read_bytes() == before
    assert (
        destination / "vendor/developer-lens/research-pack/v1/schema.json"
    ).read_bytes() == before


@pytest.mark.parametrize("allowed", [False, True])
def test_sync_preserves_boolean_legacy_subschemas(tmp_path: Path, allowed: bool) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = _write_tuple_schema(product, DRAFT_7, "tuple")
    schema = json.loads(source.read_bytes())
    schema["$defs"]["legacy"]["definitions"]["tuple"]["items"] = [allowed]
    source.write_text(json.dumps(schema), encoding="utf-8")
    commit = _commit(product)
    destination = tmp_path / "lab"

    if allowed:
        sync_product_contract(destination, product, commit)
    else:
        with pytest.raises(ContractSyncError, match="fixture does not conform"):
            sync_product_contract(destination, product, commit)
        assert not destination.exists()


@pytest.mark.parametrize(
    ("minimum", "maximum", "matching_features", "allowed"),
    [(0, 0, 0, True), (2, 2, 1, False), (2, 2, 2, True), (1, 1, 2, False)],
)
def test_sync_enforces_draft2019_contains_bounds(
    tmp_path: Path, minimum: int, maximum: int, matching_features: int, allowed: bool
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = _write_tuple_schema(product, DRAFT_2019)
    schema = json.loads(source.read_bytes())
    schema["$defs"]["legacy"] = {
        "$schema": DRAFT_2019,
        "$id": "legacy",
        "type": "array",
        "contains": {
            "type": "object",
            "properties": {"evidence_layer": {"const": "deterministic"}},
            "required": ["evidence_layer"],
        },
        "minContains": minimum,
        "maxContains": maximum,
    }
    source.write_text(json.dumps(schema), encoding="utf-8")
    fixture_path = source.with_name("invented.fixture.json")
    fixture = json.loads(fixture_path.read_bytes())
    feature = fixture["feature_registry"][0]
    fixture["feature_registry"] = [
        {**feature, "feature_id": f"DL.WEEK.INVENTED_{index}.v1"}
        for index in range(matching_features)
    ]
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    commit = _commit(product)
    destination = tmp_path / "lab"

    if allowed:
        sync_product_contract(destination, product, commit)
        assert (destination / "vendor/developer-lens/research-pack/v1/schema.json").exists()
    else:
        with pytest.raises(ContractSyncError, match="fixture does not conform"):
            sync_product_contract(destination, product, commit)
        assert not destination.exists()


@pytest.mark.parametrize("contract", ["research-pack", "method-trial-view"])
@pytest.mark.parametrize("location", ["root", "embedded"])
def test_sync_identifies_unknown_dialects_without_replacing_files(
    tmp_path: Path, contract: str, location: str
) -> None:
    product, commit = _invented_product_repo(tmp_path)
    source = _embedded_contract_source(product, contract)
    sync = sync_product_contract if contract == "research-pack" else sync_method_trial_view_contract
    if contract == "method-trial-view":
        commit = _commit(product)
    destination = tmp_path / "lab"
    sync(destination, product, commit)
    before = _destination_bytes(destination)
    schema = json.loads(source.read_bytes())
    unsupported = "https://example.invalid/unsupported-dialect"
    if location == "root":
        schema["$schema"] = unsupported
    else:
        schema.setdefault("$defs", {})["unsupported"] = {
            "$schema": unsupported,
            "$id": "https://example.invalid/unsupported-resource",
            "type": "string",
        }
    source.write_text(json.dumps(schema), encoding="utf-8")

    with pytest.raises(ContractSyncError, match="schema declares an unsupported dialect") as error:
        sync(destination, product, _commit(product))

    assert unsupported not in str(error.value)
    assert str(tmp_path) not in str(error.value)
    assert _destination_bytes(destination) == before


@pytest.mark.parametrize("dialect", [DRAFT_7, DRAFT_2019])
def test_sync_refuses_external_references_from_legacy_resources_offline(
    tmp_path: Path, dialect: str
) -> None:
    product, _ = _invented_product_repo(tmp_path)
    source = _write_tuple_schema(product, dialect)
    schema = json.loads(source.read_bytes())
    schema["$defs"]["legacy"]["allOf"] = [{"$ref": "https://example.invalid/unavailable"}]
    source.write_text(json.dumps(schema), encoding="utf-8")
    destination = tmp_path / "lab"

    with pytest.raises(ContractSyncError, match="unresolvable reference"):
        sync_product_contract(destination, product, _commit(product))

    assert not destination.exists()
