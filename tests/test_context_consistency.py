"""Synthetic regressions for cross-repository and verified-posture consistency."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import cast

import pytest

from developer_lens_lab.context.verify import verify_parity_manifest, verify_repository

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES = (
    "network_collection",
    "external_model",
    "real_data",
    "product_integration",
    "product_promotion",
)


def _manifest() -> dict[str, object]:
    return cast(
        dict[str, object],
        json.loads((ROOT / ".agent-harness/prompt-parity.json").read_text(encoding="utf-8")),
    )


@pytest.mark.parametrize("mutation", ["missing-product", "duplicate-lab", "extra", "malformed"])
def test_parity_requires_exactly_one_entry_for_each_repository(mutation: str) -> None:
    payload = _manifest()
    entries = cast(list[dict[str, object]], payload["repositories"])
    if mutation == "missing-product":
        payload["repositories"] = entries[1:]
    elif mutation == "duplicate-lab":
        entries.append(dict(entries[1]))
    elif mutation == "extra":
        entries.append({**entries[0], "slug": "invented/unregistered"})
    else:
        payload["repositories"] = [*entries, "invented-malformed-entry"]

    assert any("repositories" in failure for failure in verify_parity_manifest(payload))


@pytest.mark.parametrize("index", [0, 1], ids=["product", "lab"])
@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("role", "invented"),
        ("prompt_library", "invented.md"),
        ("continuous_work_protocol", "invented.md"),
        ("friction_log", "invented.md"),
        ("extension_prompt_ids", []),
    ],
)
def test_parity_checks_both_repositories_metadata(index: int, key: str, value: object) -> None:
    payload = _manifest()
    entries = cast(list[dict[str, object]], payload["repositories"])
    entries[index][key] = value

    assert any(key in failure for failure in verify_parity_manifest(payload))


def test_parity_repository_set_is_order_independent() -> None:
    payload = _manifest()
    payload["repositories"] = list(reversed(cast(list[object], payload["repositories"])))

    assert verify_parity_manifest(payload) == []


def _replace_state_read(monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    _replace_read(monkeypatch, ROOT / "docs/CURRENT_STATE.md", state)


def _replace_read(monkeypatch: pytest.MonkeyPatch, target: Path, replacement: str) -> None:
    original_read = Path.read_text

    def read_text(path: Path, encoding: str | None = None, errors: str | None = None) -> str:
        if path == target:
            return replacement
        return original_read(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", read_text)


@pytest.mark.parametrize("capability", CAPABILITIES)
@pytest.mark.parametrize("value", ["enabled", "true", "[]", "disabled_but_enabled"])
def test_repository_rejects_capability_claims_inconsistent_with_verified_policy(
    monkeypatch: pytest.MonkeyPatch, capability: str, value: str
) -> None:
    state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    state, count = re.subn(rf"(?m)^  {capability}:.*$", f"  {capability}: {value}", state)
    assert count == 1
    _replace_state_read(monkeypatch, state)

    failures = verify_repository(ROOT).failures

    assert any(f"capabilities.{capability}" in failure for failure in failures), failures


@pytest.mark.parametrize("capability", CAPABILITIES)
def test_repository_requires_every_capability_name(
    monkeypatch: pytest.MonkeyPatch, capability: str
) -> None:
    state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    state, count = re.subn(rf"(?m)^  {capability}:.*\n", "", state)
    assert count == 1
    _replace_state_read(monkeypatch, state)

    failures = verify_repository(ROOT).failures

    assert any(f"capabilities.{capability}" in failure for failure in failures), failures


def test_repository_rejects_unregistered_capability(monkeypatch: pytest.MonkeyPatch) -> None:
    state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    _replace_state_read(
        monkeypatch, state.replace("capabilities:\n", "capabilities:\n  invented_lane: enabled\n")
    )

    assert any("capabilities" in failure for failure in verify_repository(ROOT).failures)


def test_repository_rejects_empty_capability_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    _replace_state_read(
        monkeypatch, re.sub(r"capabilities:\n(?:  [^\n]*\n)+", "capabilities: {}\n", state)
    )

    failures = verify_repository(ROOT).failures

    for capability in CAPABILITIES:
        assert any(f"capabilities.{capability}" in failure for failure in failures), failures


@pytest.mark.parametrize("policy", ["tier", "governor"])
def test_capability_summary_cannot_activate_unverified_policy(
    monkeypatch: pytest.MonkeyPatch, policy: str
) -> None:
    state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    _replace_state_read(monkeypatch, re.sub(r"(?m)^  real_data:.*$", "  real_data: enabled", state))
    path = ROOT / f".agent-harness/{policy}.json"
    source = path.read_text(encoding="utf-8")
    if policy == "tier":
        source = source.replace('"sensitive_data": false', '"sensitive_data": true')
        diagnostic = "sensitive_data must stay false"
    else:
        source = source.replace('"authorised_awaiting_preconditions"', '"active"')
        diagnostic = "status must remain"
    _replace_read(monkeypatch, path, source)

    report = verify_repository(ROOT)

    assert not report.ok
    assert any(diagnostic in failure for failure in report.failures), report.failures


def test_repository_accepts_statuses_without_explanatory_annotations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    for capability in CAPABILITIES:
        state = re.sub(rf"(?m)^(  {capability}: [^\n(]+?) \([^\n]*\)$", r"\1", state)
    _replace_state_read(monkeypatch, state)

    report = verify_repository(ROOT)

    assert report.ok, report.failures
