from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "release-assets" / "v0.1.0" / "method-trial-v1"
JSON_NAME = "method-trial-view.v1.json"
HTML_NAME = "method-trial-report.v1.html"
JSON_SHA256 = "afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9"
HTML_SHA256 = "22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29"
IMPLEMENTATION_IDENTITY = {
    "frozen_producer_commit": "0ef193070a9b80b81cef5a1710a1d65e0b271c15",
    "verified_lab_commit": "89358200b428aac53d1c8b47a3d544e7a981efac",
    "pins": {
        "renderer": {
            "path": "src/developer_lens_lab/wbc1/report.py",
            "blob": "4abe3bc5d3a370705ed910c3deabd870710f3b23",
        },
        "validator": {
            "path": "src/developer_lens_lab/contracts/method_trial_view.py",
            "blob": "0caeccf7b15f088ad97d26a14517a71afcee3634",
        },
        "serializer": {
            "path": "src/developer_lens_lab/artifacts.py",
            "blob": "7d82ad2e8a800bc2f1169c6cdce6ee1bc300365c",
        },
        "schema": {
            "path": "vendor/developer-lens/method-trial-view/v1/schema.json",
            "blob": "71ea3e61c912915e1dffb2b51b33ccbad379c4a5",
        },
    },
}


def _run_git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), *arguments],
        capture_output=True,
        check=True,
        text=True,
    )
    return result.stdout.strip()


def test_staged_method_trial_implementation_provenance_is_immutable() -> None:
    manifest = json.loads((ASSET_ROOT / "provenance.json").read_bytes())
    identity = manifest["transformation"]["implementation_identity"]

    assert identity == IMPLEMENTATION_IDENTITY
    for commit in (
        identity["frozen_producer_commit"],
        identity["verified_lab_commit"],
    ):
        assert _run_git("rev-parse", "--verify", f"{commit}^{{commit}}") == commit
        for pin in identity["pins"].values():
            object_name = f"{commit}:{pin['path']}"
            assert _run_git("cat-file", "-t", object_name) == "blob"
            assert _run_git("rev-parse", "--verify", object_name) == pin["blob"]


def test_staged_method_trial_assets_are_exact_and_offline_safe() -> None:
    from developer_lens_lab.artifacts import canonical_json_bytes
    from developer_lens_lab.contracts.method_trial_view import validate_method_trial_view
    from developer_lens_lab.wbc1.report import build_method_trial_html

    json_bytes = (ASSET_ROOT / JSON_NAME).read_bytes()
    html_bytes = (ASSET_ROOT / HTML_NAME).read_bytes()
    manifest = json.loads((ASSET_ROOT / "provenance.json").read_bytes())

    assert len(json_bytes) == 167936
    assert hashlib.sha256(json_bytes).hexdigest() == JSON_SHA256
    assert len(html_bytes) == 24318
    assert hashlib.sha256(html_bytes).hexdigest() == HTML_SHA256

    view = json.loads(json_bytes)
    assert json_bytes == canonical_json_bytes(view) + b"\n"
    validated_view = validate_method_trial_view(view, root=ROOT)
    assert html_bytes == build_method_trial_html(validated_view).encode("utf-8")

    assert manifest["release_status"] == "staged_for_release_review_only"
    assert manifest["data_class"] == "C0"
    assert manifest["invented"] is True
    assert manifest["transformation"] == {
        "json": (
            "Byte-preserving copy of the public tracked C0 fixture Chris0Jeky/developer-lens "
            "at immutable commit 8de65a22fe8a65ced893278a4e5a6835d778d65c, "
            "research-contracts/method-trial-view/v1/wbc1.fixture.json."
        ),
        "html": "build_method_trial_html(json.loads(JSON)) from the staged JSON bytes.",
        "implementation_identity": IMPLEMENTATION_IDENTITY,
        "finding_scope": "invented benchmark mechanics and explicit reject/fallback decision only",
    }
    assert manifest["producer"] == {
        "lab_commit": "0ef193070a9b80b81cef5a1710a1d65e0b271c15",
        "run_id": "wbc1_demo",
        "generator_provenance": (
            "Frozen run provenance only; the staged release inputs are "
            "the immutable Product fixture and its derived deterministic HTML."
        ),
    }
    assert manifest["product_contract"] == {
        "commit": "b48fea579936671397a0486ae7a0342197ee6e4b",
        "method_trial_view_schema_sha256": (
            "634b0cc7a0c3dbcefe8b9cf258e157695beae06d08cc9d02bb781a4267f633ef"
        ),
    }
    assert manifest["license"] == {"spdx": "AGPL-3.0-only", "copyright": "Cristian Tcaci"}
    assert manifest["artifacts"] == [
        {
            "filename": JSON_NAME,
            "sha256": JSON_SHA256,
            "size_bytes": 167936,
            "media_type": "application/json",
        },
        {
            "filename": HTML_NAME,
            "sha256": HTML_SHA256,
            "size_bytes": 24318,
            "media_type": "text/html",
        },
    ]

    html_lower = html_bytes.lower()
    for forbidden in (b"<script", b"<link", b"http://", b"https://"):
        assert forbidden not in html_lower
