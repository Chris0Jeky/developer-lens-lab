"""Invented current-state and governor structural validation regressions."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import cast

import pytest

from developer_lens_lab.context.verify import verify_current_state_yaml, verify_governor

ROOT = Path(__file__).resolve().parents[1]
_VALID_STATE = """updated: 2026-08-09
phase: TEST
posture: synthetic
repository: example/repo
branch: main
head: abc
active_wave: []
delivered: []
next_safe_slice: test
release_and_owner_gates: test
capabilities: {}
canonical_evidence: {}
blockers: none
late_review_debt: none
exact_resume_point: resume the invented task
"""


def _write_state(root: Path, body: str) -> None:
    path = root / "docs" / "CURRENT_STATE.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Current state\n\n```yaml\n{body}```\n", encoding="utf-8")


@pytest.mark.parametrize(
    ("original", "replacement"),
    [
        ("head: abc", "head: abc\nhead: invented"),
        ("canonical_evidence: {}", "canonical_evidence: {nested: {item: first, item: second}}"),
        ("canonical_evidence: {}", "canonical_evidence: {items: [{item: first, item: second}]}"),
        ("delivered: []", "delivered: [{item: first, item: second}]"),
        (
            "active_wave: []",
            "active_wave: [{lane: test, writer: test, state: first, state: second}]",
        ),
        (
            "canonical_evidence: {}",
            "canonical_evidence:\n  source: &source {item: first, item: second}\n"
            "  merged: {<<: *source}",
        ),
        ("canonical_evidence: {}", "canonical_evidence: {1: first, 01: second}"),
        (
            "canonical_evidence: {}",
            "canonical_evidence: {&key invented: first, *key: second}",
        ),
    ],
    ids=["top-level", "nested", "sequence", "delivered", "wave", "merge-source", "scalar", "alias"],
)
def test_current_state_rejects_duplicate_yaml_mapping_keys(
    tmp_path: Path, original: str, replacement: str
) -> None:
    _write_state(tmp_path, _VALID_STATE.replace(original, replacement))

    failures = verify_current_state_yaml(tmp_path)

    assert len(failures) == 1
    assert "duplicate mapping key" in failures[0]
    assert failures[0].startswith("docs/CURRENT_STATE.md:")


def test_current_state_duplicate_diagnostic_does_not_echo_key_or_values(tmp_path: Path) -> None:
    key = "invented-private-key-" + "x" * 2_000
    body = _VALID_STATE.replace(
        "canonical_evidence: {}",
        f'canonical_evidence:\n  ? "{key}"\n  : invented-first\n  ? "{key}"\n  : invented-second',
    )
    _write_state(tmp_path, body)

    failures = verify_current_state_yaml(tmp_path)

    assert len(failures) == 1
    assert "duplicate mapping key" in failures[0]
    assert "invented" not in failures[0]
    assert len(failures[0]) < 160


@pytest.mark.parametrize(
    "body",
    [
        "canonical_evidence: *invented-private-anchor\n",
        "canonical_evidence: !invented-private-tag value\n",
        "canonical_evidence: !!python/name:invented.private_name ''\n",
    ],
    ids=["unknown-alias", "unknown-tag", "unsafe-tag"],
)
def test_current_state_parse_errors_have_bounded_content_free_diagnostics(
    tmp_path: Path, body: str
) -> None:
    _write_state(tmp_path, body)

    failures = verify_current_state_yaml(tmp_path)

    assert len(failures) == 1
    assert "invalid YAML" in failures[0]
    assert "invented" not in failures[0]
    assert len(failures[0]) < 160


@pytest.mark.parametrize("position", ["key", "value"])
@pytest.mark.parametrize(
    "scalar",
    [
        "!!int invented-private-content",
        "!!bool invented-private-content",
        "!!float invented-private-content",
        "!!timestamp invented-private-content",
        "!!timestamp 2026-13-40",
        "!!int ''",
        "!!float ''",
    ],
    ids=["int", "bool", "float", "timestamp", "invalid-date", "empty-int", "empty-float"],
)
def test_current_state_scalar_constructor_errors_have_fixed_diagnostics(
    tmp_path: Path, position: str, scalar: str
) -> None:
    entry = f"{scalar}: invented-private-value" if position == "key" else f"item: {scalar}"
    _write_state(
        tmp_path,
        _VALID_STATE.replace("canonical_evidence: {}", f"canonical_evidence: {{{entry}}}"),
    )

    assert verify_current_state_yaml(tmp_path) == [
        "docs/CURRENT_STATE.md:4: invalid YAML: invalid syntax or structure"
    ]


def test_current_state_oversized_integer_has_fixed_diagnostic(tmp_path: Path) -> None:
    _write_state(tmp_path, "canonical_evidence: {item: !!int " + "7" * 641 + "}\n")
    previous_limit = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(640)
        failures = verify_current_state_yaml(tmp_path)
    finally:
        sys.set_int_max_str_digits(previous_limit)

    assert failures == ["docs/CURRENT_STATE.md:4: invalid YAML: invalid syntax or structure"]


def test_current_state_excessive_nesting_has_fixed_diagnostic(tmp_path: Path) -> None:
    depth = sys.getrecursionlimit()
    nested = "[" * depth + "invented-private-content" + "]" * depth
    _write_state(tmp_path, f"canonical_evidence: {{item: {nested}}}\n")

    assert verify_current_state_yaml(tmp_path) == [
        "docs/CURRENT_STATE.md:4: invalid YAML: invalid syntax or structure"
    ]


@pytest.mark.parametrize(
    ("tag", "value"),
    [("int", "12"), ("bool", "true"), ("float", "1.25"), ("timestamp", "2026-10-29")],
)
def test_current_state_preserves_tagged_scalar_conversions(
    tmp_path: Path, tag: str, value: str
) -> None:
    _write_state(
        tmp_path,
        _VALID_STATE.replace(
            "canonical_evidence: {}", f"canonical_evidence: {{item: !!{tag} {value}}}"
        ),
    )
    assert verify_current_state_yaml(tmp_path) == []

    _write_state(tmp_path, f"canonical_evidence:\n  !!{tag} {value}: first\n  {value}: second\n")
    assert verify_current_state_yaml(tmp_path) == [
        "docs/CURRENT_STATE.md:6: invalid YAML: duplicate mapping key"
    ]


def test_current_state_preserves_aliases_merge_overrides_and_recursive_values(
    tmp_path: Path,
) -> None:
    body = _VALID_STATE.replace(
        "canonical_evidence: {}",
        "canonical_evidence:\n"
        "  base: &base {item: first, preserved: original}\n"
        "  override: &override {<<: *base, item: second}\n"
        "  repeated: *override\n"
        "  merged: {<<: [*base, *override]}\n"
        "  recursive: &recursive {self: *recursive}",
    ).replace(
        "active_wave: []",
        "active_wave:\n  - &wave {lane: invented, writer: coordinator, state: active}\n  - *wave",
    )
    _write_state(tmp_path, body)

    assert verify_current_state_yaml(tmp_path) == []


@pytest.mark.parametrize("value", ["null", "''", "'   '", "false", "12", "[]", "{}"])
def test_current_state_requires_a_nonempty_resume_string(tmp_path: Path, value: str) -> None:
    _write_state(
        tmp_path,
        _VALID_STATE.replace(
            "exact_resume_point: resume the invented task", f"exact_resume_point: {value}"
        ),
    )

    failures = verify_current_state_yaml(tmp_path)

    assert any("'exact_resume_point' must be a non-empty string" in failure for failure in failures)


@pytest.mark.parametrize("field", ["active_wave", "delivered"])
def test_current_state_rejects_null_lists(tmp_path: Path, field: str) -> None:
    _write_state(tmp_path, _VALID_STATE.replace(f"{field}: []", f"{field}: null"))

    assert any(
        f"'{field}' must be a list" in failure for failure in verify_current_state_yaml(tmp_path)
    )


@pytest.mark.parametrize("item", ["null", "invented", "[]", "17"])
def test_current_state_requires_mapping_wave_entries(tmp_path: Path, item: str) -> None:
    _write_state(tmp_path, _VALID_STATE.replace("active_wave: []", f"active_wave: [{item}]"))

    assert any(
        "active_wave entry 1 must be a mapping" in failure
        for failure in verify_current_state_yaml(tmp_path)
    )


@pytest.mark.parametrize("field", ["lane", "writer", "state"])
@pytest.mark.parametrize("value", [None, "null", "''", "'   '", "false", "[]", "{}"])
def test_current_state_requires_nonempty_operational_wave_fields(
    tmp_path: Path, field: str, value: str | None
) -> None:
    fields = {"lane": "invented task", "writer": "coordinator", "state": "active"}
    if value is None:
        del fields[field]
    else:
        fields[field] = value
    entry = ", ".join(f"{name}: {content}" for name, content in fields.items())
    _write_state(tmp_path, _VALID_STATE.replace("active_wave: []", f"active_wave: [{{{entry}}}]"))

    failures = verify_current_state_yaml(tmp_path)

    assert any(
        f"active_wave entry 1 '{field}' must be a non-empty string" in failure
        for failure in failures
    )


def test_current_state_wave_accepts_additional_operational_fields(tmp_path: Path) -> None:
    _write_state(
        tmp_path,
        _VALID_STATE.replace(
            "active_wave: []",
            "active_wave: [{lane: invented, writer: coordinator, state: active, dependencies: []}]",
        ),
    )

    assert verify_current_state_yaml(tmp_path) == []


def _write_governor(root: Path, field: str, value: object, *, omit: bool = False) -> None:
    payload = cast(
        dict[str, object], json.loads((ROOT / ".agent-harness/governor.json").read_text())
    )
    if omit:
        del payload[field]
    else:
        payload[field] = value
    path = root / ".agent-harness" / "governor.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.mark.parametrize("field", ["prompt_system", "friction_debt", "continuous_execution"])
def test_governor_requires_operational_protocol_blocks(tmp_path: Path, field: str) -> None:
    _write_governor(tmp_path, field, None, omit=True)

    assert f"governor.json is missing required key: {field}" in verify_governor(tmp_path)


@pytest.mark.parametrize("field", ["prompt_system", "friction_debt", "continuous_execution"])
@pytest.mark.parametrize("value", [None, [], False, "invented-invalid-block"])
def test_governor_requires_mapping_protocol_blocks(
    tmp_path: Path, field: str, value: object
) -> None:
    _write_governor(tmp_path, field, value)

    failures = verify_governor(tmp_path)

    assert f"governor.json {field} must be an object" in failures
    assert not any("invented-invalid-block" in failure for failure in failures)
