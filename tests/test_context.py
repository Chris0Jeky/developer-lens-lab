import json
from pathlib import Path
from typing import Any

import pytest

import developer_lens_lab.context.verify as context_verify
from developer_lens_lab.context import verify_repository
from developer_lens_lab.context.verify import (
    COMMON_PROMPT_IDS,
    CONTINUOUS_PROMPT_ID,
    LAB_EXTENSION_PROMPT_IDS,
    REQUIRED_CLAUDE_CLAUSE,
    REQUIRED_CODEX_CLAUSE,
    REQUIRED_SETTINGS_READ_DENY,
    SHARED_BLOCK_IDS,
    normalize_newlines,
    prompt_entries,
    shared_block_digest,
    shared_blocks_in,
    verify_agent_friction_parity,
    verify_context_budget,
    verify_continuous_protocol,
    verify_current_state_yaml,
    verify_governor,
    verify_markdown_links,
    verify_one_shared_block,
    verify_parity_manifest,
    verify_prompt_classifications,
    verify_prompt_library,
    verify_prompt_parity,
    verify_settings_deny,
    verify_skill_parity,
)

ROOT = Path(__file__).resolve().parents[1]
GOVERNOR = ROOT / ".agent-harness" / "governor.json"
LIBRARY = ROOT / "docs" / "agent-system" / "PROMPT_LIBRARY.md"
MANIFEST = ROOT / ".agent-harness" / "prompt-parity.json"


def test_repository_context_is_valid() -> None:
    report = verify_repository(ROOT)
    assert report.ok, report.failures


def _write_current_state(tmp_path: Path, body: str) -> None:
    current = tmp_path / "docs" / "CURRENT_STATE.md"
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text(f"# Current state\n\n```yaml\n{body}```\n", encoding="utf-8")


_VALID_CURRENT_STATE = """updated: 2026-08-09
phase: TEST
posture: synthetic
repository: example/repo
branch: main
head: abc
active_wave: []
delivered:
  - item: done
next_safe_slice: test
release_and_owner_gates: test
capabilities: {}
canonical_evidence: {}
blockers: none
late_review_debt: none
exact_resume_point: test
"""


def test_current_state_yaml_requires_one_fence_and_valid_shape(tmp_path: Path) -> None:
    _write_current_state(tmp_path, _VALID_CURRENT_STATE)
    assert verify_current_state_yaml(tmp_path) == []


def test_current_state_yaml_rejects_missing_or_multiple_fences(tmp_path: Path) -> None:
    current = tmp_path / "docs" / "CURRENT_STATE.md"
    current.parent.mkdir(parents=True, exist_ok=True)
    current.write_text("# Current state\n", encoding="utf-8")
    assert "exactly one YAML fence" in verify_current_state_yaml(tmp_path)[0]
    _write_current_state(tmp_path, _VALID_CURRENT_STATE)
    current.write_text(current.read_text(encoding="utf-8") + "\n```yaml\n```\n", encoding="utf-8")
    assert "exactly one YAML fence" in verify_current_state_yaml(tmp_path)[0]


def test_current_state_yaml_allows_a_later_unrelated_fence(tmp_path: Path) -> None:
    _write_current_state(tmp_path, _VALID_CURRENT_STATE)
    current = tmp_path / "docs" / "CURRENT_STATE.md"
    current.write_text(
        current.read_text(encoding="utf-8") + "\n```text\nexample\n```\n",
        encoding="utf-8",
    )
    assert verify_current_state_yaml(tmp_path) == []


def test_current_state_yaml_reports_bounded_parse_error(tmp_path: Path) -> None:
    _write_current_state(tmp_path, "updated: [unterminated\n")
    failures = verify_current_state_yaml(tmp_path)
    assert failures and failures[0].startswith("docs/CURRENT_STATE.md:")
    assert "invalid YAML" in failures[0]


def test_current_state_yaml_rejects_wrong_mapping_and_key_shapes(tmp_path: Path) -> None:
    _write_current_state(tmp_path, "- not: a mapping\n")
    failures = verify_current_state_yaml(tmp_path)
    assert any("top level must be a mapping" in failure for failure in failures)
    _write_current_state(
        tmp_path, _VALID_CURRENT_STATE.replace("  - item: done", "  - item: [bad]")
    )
    failures = verify_current_state_yaml(tmp_path)
    assert any("delivered entry 1" in failure for failure in failures)


def test_settings_deny_requires_the_confined_and_generated_sinks() -> None:
    assert REQUIRED_SETTINGS_READ_DENY == (
        "Read(./.dllab/**)",
        "Read(./artifacts/**)",
        "Read(./reports/generated/**)",
    )


def test_settings_deny_accepts_all_required_protected_sinks() -> None:
    payload = {"permissions": {"deny": list(REQUIRED_SETTINGS_READ_DENY)}}
    assert verify_settings_deny(payload) == []


def test_settings_deny_accepts_a_superset_of_required_rules() -> None:
    # Extra deny rules must not fail the gate: the check is a subset test, not set-equality. This
    # guards against a regression that tightens it and would then reject a settings.json carrying
    # legitimate additional deny rules.
    deny = [*REQUIRED_SETTINGS_READ_DENY, "Read(./.env)", "Bash(rm -rf /)"]
    assert verify_settings_deny({"permissions": {"deny": deny}}) == []


def test_settings_deny_ignores_non_string_deny_entries() -> None:
    deny = [*REQUIRED_SETTINGS_READ_DENY, {"nested": "object"}, 42, None]
    assert verify_settings_deny({"permissions": {"deny": deny}}) == []


def test_settings_deny_reports_each_missing_protected_sink() -> None:
    partial = {"permissions": {"deny": ["Read(./.dllab/**)"]}}
    failures = verify_settings_deny(partial)
    assert any("artifacts" in failure for failure in failures)
    assert any("reports/generated" in failure for failure in failures)
    assert not any(".dllab" in failure for failure in failures)


def test_settings_deny_requires_a_deny_block() -> None:
    for payload in ({"permissions": {"defaultMode": "acceptEdits"}}, {}, "not-an-object"):
        assert len(verify_settings_deny(payload)) == len(REQUIRED_SETTINGS_READ_DENY)


_START = "<!-- shared:evaluation-integrity start -->"
_END = "<!-- shared:evaluation-integrity end -->"


def _write_skill_pair(tmp_path: Path, claude_block: str, agents_block: str) -> Path:
    for rel, block in (
        (".claude/skills/developer-lens-lab-continuation/SKILL.md", claude_block),
        (".agents/skills/developer-lens-lab-continuation/SKILL.md", agents_block),
    ):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(block, encoding="utf-8")
    return tmp_path


def test_skill_parity_passes_on_the_real_repo() -> None:
    assert verify_skill_parity(ROOT) == []


def test_skill_parity_accepts_matching_enclosed_blocks(tmp_path: Path) -> None:
    body = f"# doc\n\n{_START}\n## Protect evaluation integrity\n\n- Shared bullet.\n{_END}\n\n## End\n"  # noqa: E501
    _write_skill_pair(tmp_path, body, body)
    assert verify_one_shared_block(tmp_path, "shared:evaluation-integrity") == []


def test_skill_parity_reports_drift_between_copies(tmp_path: Path) -> None:
    claude = f"{_START}\n## Protect evaluation integrity\n\n- Claude bullet.\n{_END}\n"
    agents = f"{_START}\n## Protect evaluation integrity\n\n- Agents bullet.\n{_END}\n"
    _write_skill_pair(tmp_path, claude, agents)
    failures = verify_one_shared_block(tmp_path, "shared:evaluation-integrity")
    assert failures == [
        "shared evaluation-integrity section drifted between the two SKILL.md copies"
    ]


def test_skill_parity_reports_missing_marker(tmp_path: Path) -> None:
    good = f"{_START}\n## Protect evaluation integrity\n\n- Shared bullet.\n{_END}\n"
    without_end = f"{_START}\n## Protect evaluation integrity\n\n- Shared bullet.\n"
    _write_skill_pair(tmp_path, good, without_end)
    failures = verify_one_shared_block(tmp_path, "shared:evaluation-integrity")
    assert any(
        "marker" in failure and ".agents/skills/developer-lens-lab-continuation/SKILL.md" in failure
        for failure in failures
    )


def test_skill_parity_rejects_duplicate_markers(tmp_path: Path) -> None:
    # A second marker pair (e.g. copy/paste while extending the section) must fail rather than let
    # find() compare only the first block and silently ignore a divergent second one.
    good = f"{_START}\n- Shared bullet.\n{_END}\n"
    duplicated = f"{_START}\n- Shared bullet.\n{_END}\n\n{_START}\n- Divergent bullet.\n{_END}\n"
    _write_skill_pair(tmp_path, good, duplicated)
    failures = verify_one_shared_block(tmp_path, "shared:evaluation-integrity")
    assert any(
        "exactly one" in failure
        and ".agents/skills/developer-lens-lab-continuation/SKILL.md" in failure
        for failure in failures
    )


_AGENT_RELS = (
    ".claude/agents/dll-implementer.md",
    ".claude/agents/dll-mechanic.md",
    ".claude/agents/dll-reviewer.md",
    ".claude/agents/dll-scout.md",
)
_AGENT_START = "<!-- shared:agent-friction-tasking-v1 start -->"
_AGENT_END = "<!-- shared:agent-friction-tasking-v1 end -->"
_AGENT_BODY = (
    "FRICTION TASKING (agent-friction-tasking-v1)\n"
    "Every material workaround reaches docs/agent-system/FRICTION_LOG.md in the same hop and links "
    "to an existing issue, card, or durable task.\n"
    "A write-capable role appends it; a read-only role reports it as a required coordinator "
    "same-hop "
    "append.\n"
    "Capture never widens scope. Never record a PID, absolute local path, token, or private "
    "identifier."
)


def _write_agent_set(tmp_path: Path, bodies: tuple[str, ...] | None = None) -> None:
    chosen = bodies or (_AGENT_BODY,) * len(_AGENT_RELS)
    for rel, body in zip(_AGENT_RELS, chosen, strict=True):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"agent\n{_AGENT_START}\n{body}\n{_AGENT_END}\n", encoding="utf-8")


def test_agent_friction_parity_passes_on_the_real_repo() -> None:
    assert verify_agent_friction_parity(ROOT) == []


def test_agent_friction_parity_reports_missing_marker(tmp_path: Path) -> None:
    _write_agent_set(tmp_path)
    (tmp_path / _AGENT_RELS[0]).write_text("agent\n", encoding="utf-8")
    failures = verify_agent_friction_parity(tmp_path)
    assert any(_AGENT_RELS[0] in failure and "marker" in failure for failure in failures)


def test_agent_friction_parity_reports_duplicate_marker(tmp_path: Path) -> None:
    _write_agent_set(tmp_path)
    path = tmp_path / _AGENT_RELS[1]
    path.write_text(
        f"agent\n{_AGENT_START}\n{_AGENT_BODY}\n{_AGENT_END}\n{_AGENT_START}\n{_AGENT_END}\n",
        encoding="utf-8",
    )
    failures = verify_agent_friction_parity(tmp_path)
    assert any(_AGENT_RELS[1] in failure and "exactly one" in failure for failure in failures)


def test_agent_friction_parity_reports_reversed_markers(tmp_path: Path) -> None:
    _write_agent_set(tmp_path)
    (tmp_path / _AGENT_RELS[2]).write_text(
        f"agent\n{_AGENT_END}\n{_AGENT_BODY}\n{_AGENT_START}\n", encoding="utf-8"
    )
    failures = verify_agent_friction_parity(tmp_path)
    assert any(_AGENT_RELS[2] in failure and "out of order" in failure for failure in failures)


def test_agent_friction_parity_reports_drift(tmp_path: Path) -> None:
    _write_agent_set(tmp_path, (_AGENT_BODY, _AGENT_BODY, _AGENT_BODY, _AGENT_BODY + "\nDrift"))
    failures = verify_agent_friction_parity(tmp_path)
    assert any("bytes drift" in failure for failure in failures)


def test_continuation_friction_marker_failures_are_enforced(tmp_path: Path) -> None:
    marker = "shared:continuation-friction-tasking-v1"
    start = f"<!-- {marker} start -->"
    end = f"<!-- {marker} end -->"
    body = (
        "Every material workaround is logged in docs/agent-system/FRICTION_LOG.md in the same hop."
    )
    good = f"{start}\n{body}\n{end}\n"
    _write_skill_pair(tmp_path, good, good)
    assert verify_one_shared_block(tmp_path, marker) == []
    _write_skill_pair(tmp_path, good, f"{start}\n{body}\n")
    assert any("marker" in failure for failure in verify_one_shared_block(tmp_path, marker))
    _write_skill_pair(tmp_path, good, f"{start}\n{body}\n{end}\n{start}\n{end}\n")
    assert any("exactly one" in failure for failure in verify_one_shared_block(tmp_path, marker))
    _write_skill_pair(tmp_path, good, f"{end}\n{body}\n{start}\n")
    assert any("out of order" in failure for failure in verify_one_shared_block(tmp_path, marker))
    _write_skill_pair(tmp_path, good, f"{start}\n{body} drift\n{end}\n")
    assert any("drifted" in failure for failure in verify_one_shared_block(tmp_path, marker))


def test_protected_data_defaults_block_matches_on_the_real_repo() -> None:
    assert verify_one_shared_block(ROOT, "shared:protected-data-defaults") == []


def test_protected_data_defaults_reports_drift_between_copies(tmp_path: Path) -> None:
    dp_start = "<!-- shared:protected-data-defaults start -->"
    dp_end = "<!-- shared:protected-data-defaults end -->"
    claude = f"{dp_start}\nDefault to invented fixtures. Claude wording.\n{dp_end}\n"
    agents = f"{dp_start}\nDefault to invented fixtures. Agents wording.\n{dp_end}\n"
    _write_skill_pair(tmp_path, claude, agents)
    failures = verify_one_shared_block(tmp_path, "shared:protected-data-defaults")
    assert failures == [
        "shared protected-data-defaults section drifted between the two SKILL.md copies"
    ]


def test_context_budget_passes_on_the_real_repo() -> None:
    assert verify_context_budget(ROOT) == []


def test_context_budget_reports_oversized_canon(tmp_path: Path) -> None:
    (tmp_path / ".agent-harness").mkdir()
    (tmp_path / ".agent-harness" / "tier.json").write_text(
        '{"budgets": {"standing_context_tokens": 5}}', encoding="utf-8"
    )
    (tmp_path / "AGENTS.md").write_text("A" * 400, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("C" * 400, encoding="utf-8")
    failures = verify_context_budget(tmp_path)
    assert len(failures) == 1
    assert "exceeds" in failures[0]


def test_context_budget_skips_when_budget_key_absent(tmp_path: Path) -> None:
    (tmp_path / ".agent-harness").mkdir()
    (tmp_path / ".agent-harness" / "tier.json").write_text(
        '{"budgets": {"session_baseline_tokens": null}}', encoding="utf-8"
    )
    (tmp_path / "AGENTS.md").write_text("A" * 400, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("C" * 400, encoding="utf-8")
    assert verify_context_budget(tmp_path) == []


def test_context_budget_skips_when_budgets_container_absent(tmp_path: Path) -> None:
    # No budgets key at all -> the budget is legitimately unenforced -> [].
    (tmp_path / ".agent-harness").mkdir()
    (tmp_path / ".agent-harness" / "tier.json").write_text('{"tier": 1}', encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("A" * 400, encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("C" * 400, encoding="utf-8")
    assert verify_context_budget(tmp_path) == []


def test_context_budget_reports_a_malformed_budgets_container(tmp_path: Path) -> None:
    # A present-but-non-object budgets silently disabled the check before; it must fail loudly, like
    # a present-but-invalid value, not revert to the "nothing enforces it" gap.
    (tmp_path / ".agent-harness").mkdir()
    tier = tmp_path / ".agent-harness" / "tier.json"
    expected = ["tier.json budgets must be an object to declare a standing-context budget"]
    for bad_container in ('"oops"', "null", "[]"):
        tier.write_text(f'{{"budgets": {bad_container}}}', encoding="utf-8")
        assert verify_context_budget(tmp_path) == expected, bad_container


def test_context_budget_reports_a_present_but_invalid_budget(tmp_path: Path) -> None:
    # A declared-but-unusable budget must fail loudly, not silently disable enforcement (the exact
    # gap the check exists to close). Absent -> [] (tested above); present-but-invalid -> failure.
    (tmp_path / ".agent-harness").mkdir()
    tier = tmp_path / ".agent-harness" / "tier.json"
    expected = [
        "tier.json budgets.standing_context_tokens must be a positive integer to enforce "
        "the standing-context budget"
    ]
    for bad_value in ('"2500"', "0", "-5", "12.5", "true", "null"):
        tier.write_text(
            f'{{"budgets": {{"standing_context_tokens": {bad_value}}}}}', encoding="utf-8"
        )
        assert verify_context_budget(tmp_path) == expected, bad_value


def test_link_verifier_does_not_read_generated_output(tmp_path: Path) -> None:
    tracked_doc = tmp_path / "docs" / "guide.md"
    tracked_doc.parent.mkdir()
    tracked_doc.write_text("[authority](../AGENTS.md)\n", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# authority\n", encoding="utf-8")
    generated_doc = tmp_path / ".dllab" / "private.md"
    generated_doc.parent.mkdir()
    generated_doc.write_text("[local output](missing.md)\n", encoding="utf-8")
    report_doc = tmp_path / "reports" / "generated" / "run.md"
    report_doc.parent.mkdir(parents=True)
    report_doc.write_text("[local report](missing.md)\n", encoding="utf-8")

    assert verify_markdown_links(tmp_path) == []


def test_package_smoke_markdown_is_skipped_but_tracked_docs_are_checked(tmp_path: Path) -> None:
    ignored_doc = tmp_path / ".package-smoke" / "candidate.md"
    ignored_doc.parent.mkdir()
    ignored_doc.write_text(
        "[missing](missing.md)\n<!-- prompt-classification: unsupported -->\n",
        encoding="utf-8",
    )
    tracked_doc = tmp_path / "docs" / "guide.md"
    tracked_doc.parent.mkdir()
    tracked_doc.write_text(
        "[missing](missing.md)\n<!-- prompt-classification: unsupported -->\n",
        encoding="utf-8",
    )

    assert verify_markdown_links(tmp_path) == [
        f"broken local link in {Path('docs') / 'guide.md'}: missing.md"
    ]
    classification_failures = verify_prompt_classifications(tmp_path)
    assert len(classification_failures) == 1
    assert classification_failures[0].startswith(
        f"{Path('docs') / 'guide.md'}: prompt-classification 'unsupported' must be one of "
    )


def test_markdown_scans_prune_skipped_directories_before_descent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    skipped_child = tmp_path / ".package-smoke" / "nested"
    skipped_child.mkdir(parents=True)
    (skipped_child / "candidate.md").write_text(
        "[missing](missing.md)\n<!-- prompt-classification: unsupported -->\n",
        encoding="utf-8",
    )
    tracked_dir = tmp_path / "docs"
    tracked_dir.mkdir()
    (tracked_dir / "guide.md").write_text("# Tracked\n", encoding="utf-8")

    visited: list[Path] = []
    original_walk = context_verify.os.walk

    def tracking_walk(root: Path, *args: Any, **kwargs: Any) -> Any:
        for directory, dirnames, filenames in original_walk(root, *args, **kwargs):
            visited.append(Path(directory).relative_to(tmp_path))
            yield directory, dirnames, filenames

    monkeypatch.setattr(context_verify.os, "walk", tracking_walk)

    assert verify_markdown_links(tmp_path) == []
    assert verify_prompt_classifications(tmp_path) == []
    assert Path("docs") in visited
    assert all(".package-smoke" not in path.parts for path in visited)


def _load_governor() -> dict[str, Any]:
    return json.loads(GOVERNOR.read_text(encoding="utf-8"))


def _write_governor(tmp_path: Path, payload: object) -> Path:
    dest = tmp_path / ".agent-harness" / "governor.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_governor_passes_on_the_real_repo() -> None:
    assert verify_governor(ROOT) == []


def test_governor_dropped_locked_invariant_fails(tmp_path: Path) -> None:
    # A governor edit that silently drops a locked invariant is exactly what this check exists to
    # catch: it must fail loudly here, not relax the constitution unnoticed.
    payload = _load_governor()
    payload["self_evolution"]["may_never_self_relax"].remove("holdout integrity")
    _write_governor(tmp_path, payload)
    failures = verify_governor(tmp_path)
    assert any(
        "may_never_self_relax must retain" in failure and "holdout integrity" in failure
        for failure in failures
    )


def test_governor_schema_mismatch_fails(tmp_path: Path) -> None:
    payload = _load_governor()
    payload["schema"] = "dllab-governor.v2"
    _write_governor(tmp_path, payload)
    assert any("schema must be" in failure for failure in verify_governor(tmp_path))


def test_governor_authority_pointing_at_missing_file_fails(tmp_path: Path) -> None:
    payload = _load_governor()
    payload["authorities"]["ghost"] = "docs/does-not-exist.md"
    _write_governor(tmp_path, payload)
    assert any("authority 'ghost'" in failure for failure in verify_governor(tmp_path))


def test_governor_missing_required_key_fails(tmp_path: Path) -> None:
    payload = _load_governor()
    del payload["activation_preconditions"]
    _write_governor(tmp_path, payload)
    assert any(
        "missing required key: activation_preconditions" in failure
        for failure in verify_governor(tmp_path)
    )


def _pin_governor(agent_rel: str, declared_model: str) -> dict[str, Any]:
    payload = _load_governor()
    payload["model_routing"]["implementer"] = {"agent": agent_rel, "model": declared_model}
    return payload


def _write_agent(tmp_path: Path, agent_rel: str, model: str) -> None:
    agent_path = tmp_path / agent_rel
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    agent_path.write_text(f"---\nname: x\nmodel: {model}\n---\nbody\n", encoding="utf-8")


def test_governor_pin_mismatch_fails(tmp_path: Path) -> None:
    agent_rel = ".claude/agents/dll-implementer.md"
    _write_agent(tmp_path, agent_rel, "claude-sonnet-4-6")
    _write_governor(tmp_path, _pin_governor(agent_rel, "claude-opus-5"))
    failures = verify_governor(tmp_path)
    assert any("frontmatter declares 'claude-sonnet-4-6'" in failure for failure in failures)


def test_governor_pin_match_reports_no_pin_failure(tmp_path: Path) -> None:
    agent_rel = ".claude/agents/dll-implementer.md"
    _write_agent(tmp_path, agent_rel, "claude-opus-5")
    _write_governor(tmp_path, _pin_governor(agent_rel, "claude-opus-5"))
    failures = verify_governor(tmp_path)
    assert not any("model_routing.implementer" in failure for failure in failures)


def test_governor_routing_to_a_prohibited_model_fails(tmp_path: Path) -> None:
    # Listing "haiku" under prohibited_models is not enforcement. A routed model id that embeds a
    # prohibited token must fail even when the pin itself is coherent with the agent file.
    agent_rel = ".claude/agents/dll-mechanic.md"
    _write_agent(tmp_path, agent_rel, "claude-haiku-4-5")
    payload = _load_governor()
    payload["model_routing"]["mechanic"] = {"agent": agent_rel, "model": "claude-haiku-4-5"}
    _write_governor(tmp_path, payload)
    failures = verify_governor(tmp_path)
    assert any(
        "prohibited model token 'haiku'" in failure and "model_routing.mechanic" in failure
        for failure in failures
    )


def test_governor_prohibited_token_match_is_case_insensitive(tmp_path: Path) -> None:
    agent_rel = ".claude/agents/dll-mechanic.md"
    _write_agent(tmp_path, agent_rel, "Claude-HAIKU-4-5")
    payload = _load_governor()
    payload["model_routing"]["mechanic"] = {"agent": agent_rel, "model": "Claude-HAIKU-4-5"}
    _write_governor(tmp_path, payload)
    assert any("prohibited model token" in failure for failure in verify_governor(tmp_path))


def test_governor_pin_role_missing_agent_key_fails(tmp_path: Path) -> None:
    # Dropping the agent key previously skipped the pin check silently, leaving a pinned role
    # unverified while the gate stayed green.
    payload = _load_governor()
    del payload["model_routing"]["implementer"]["agent"]
    _write_governor(tmp_path, payload)
    assert any(
        "model_routing.implementer must declare agent and model" in failure
        for failure in verify_governor(tmp_path)
    )


def test_governor_pin_role_entirely_absent_fails(tmp_path: Path) -> None:
    payload = _load_governor()
    del payload["model_routing"]["reviewer"]
    _write_governor(tmp_path, payload)
    assert any(
        "model_routing.reviewer must declare agent and model" in failure
        for failure in verify_governor(tmp_path)
    )


def test_governor_emptied_activation_preconditions_fails(tmp_path: Path) -> None:
    # A presence-only key check passes an emptied gate; the floor makes weakening it a failure.
    payload = _load_governor()
    payload["activation_preconditions"]["items"] = []
    _write_governor(tmp_path, payload)
    assert any(
        "activation_preconditions.items must be a list of at least" in failure
        for failure in verify_governor(tmp_path)
    )


def test_governor_weakened_review_gate_values_fail(tmp_path: Path) -> None:
    payload = _load_governor()
    payload["review_gates"]["aging_minutes_after_push"] = 0
    payload["review_gates"]["fix_round_ceiling"] = 99
    _write_governor(tmp_path, payload)
    failures = verify_governor(tmp_path)
    assert any("aging_minutes_after_push must be an integer of at least" in f for f in failures)
    assert any("fix_round_ceiling must be an integer between" in f for f in failures)


def test_governor_authority_outside_the_repo_fails(tmp_path: Path) -> None:
    # An absolute path or a `..` escape points the authority list at a machine-local file no
    # reviewer sees; both must fail on containment, before any existence check. Escapes are
    # constructed from tmp_path so each is genuinely absolute (or genuinely traversing) on
    # whichever platform runs the suite — a hardcoded drive-letter path is relative on POSIX.
    for escape in (
        str(tmp_path.parent / "outside-escape.md"),
        "../outside-escape.md",
        "../../secrets.md",
    ):
        payload = _load_governor()
        payload["authorities"]["canon"] = escape
        _write_governor(tmp_path, payload)
        failures = verify_governor(tmp_path)
        assert any(
            "must stay inside the repository" in failure and "'canon'" in failure
            for failure in failures
        ), escape


def test_governor_opened_private_lane_fails(tmp_path: Path) -> None:
    # Flipping a non-synthetic lane open by an unreviewed edit is exactly what the lane pin blocks.
    payload = _load_governor()
    payload["data_lanes"]["O_own_private"]["status"] = "active"
    _write_governor(tmp_path, payload)
    assert any(
        "data_lanes.O_own_private.status must remain" in failure
        for failure in verify_governor(tmp_path)
    )


def test_governor_placeholder_preconditions_fail(tmp_path: Path) -> None:
    # Seven filler strings satisfy the length floor while deleting every real precondition, so the
    # identity check must reject them.
    payload = _load_governor()
    payload["activation_preconditions"]["items"] = ["ok"] * 7
    _write_governor(tmp_path, payload)
    failures = verify_governor(tmp_path)
    assert any("must still cover every precondition subject" in failure for failure in failures)


def test_governor_reallocated_focus_fails(tmp_path: Path) -> None:
    payload = _load_governor()
    payload["focus"]["research"] = 0
    payload["focus"]["realdata_standalone"] = 100
    _write_governor(tmp_path, payload)
    failures = verify_governor(tmp_path)
    assert any(
        "focus.research must be the constitution's allocated weight 7" in f for f in failures
    )
    assert any("focus.realdata_standalone must be" in f for f in failures)


def test_governor_emptied_review_triggers_fail(tmp_path: Path) -> None:
    payload = _load_governor()
    payload["review_gates"]["fresh_context_review_required_for"] = []
    _write_governor(tmp_path, payload)
    assert any(
        "fresh_context_review_required_for must retain every required trigger" in failure
        for failure in verify_governor(tmp_path)
    )


def test_governor_disabled_late_comment_sweep_fails(tmp_path: Path) -> None:
    payload = _load_governor()
    payload["review_gates"]["post_merge_late_comment_sweep"] = False
    _write_governor(tmp_path, payload)
    assert any(
        "post_merge_late_comment_sweep must be true" in failure
        for failure in verify_governor(tmp_path)
    )


def test_governor_boolean_gate_values_fail(tmp_path: Path) -> None:
    # bool is an int subclass: True must not pass as a 1-minute window or a 1-round ceiling.
    payload = _load_governor()
    payload["review_gates"]["aging_minutes_after_push"] = True
    payload["review_gates"]["fix_round_ceiling"] = True
    _write_governor(tmp_path, payload)
    failures = verify_governor(tmp_path)
    assert any("aging_minutes_after_push" in f for f in failures)
    assert any("fix_round_ceiling" in f for f in failures)


# --- Prompt operating system parity ------------------------------------------------------------

_ALL_PROMPT_IDS = COMMON_PROMPT_IDS + LAB_EXTENSION_PROMPT_IDS
_CLAUDE_LINE = (
    "LAB RUNTIME ROUTING\n"
    "Claude: read CLAUDE.md first; delegate large reads to Opus 5 low scouts, bounded work to "
    "dll-implementer, review to dll-reviewer, sweeps to dll-mechanic."
)
_CODEX_LINE = (
    "Codex: read AGENTS.md first, then the shared canon; invoke the "
    "developer-lens-lab-continuation skill; follow Sol/Terra/Luna routing."
)
_GATE_LINE = "GATE: Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8 stays open."


def _real_blocks() -> dict[str, str]:
    return shared_blocks_in(LIBRARY.read_text(encoding="utf-8"))


def _real_digests() -> dict[str, str]:
    payload: dict[str, Any] = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {entry["id"]: entry["sha256"] for entry in payload["shared_blocks"]}


def _load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _body(
    blocks: dict[str, str],
    *,
    claude: str = _CLAUDE_LINE,
    codex: str = _CODEX_LINE,
    gate: str = _GATE_LINE,
) -> str:
    parts = ["You do one bounded thing.", *(blocks[bid] for bid in SHARED_BLOCK_IDS)]
    parts.extend(part for part in (claude, codex, gate) if part)
    return "\n\n".join(parts)


def _library(
    blocks: dict[str, str],
    ids: tuple[str, ...] = _ALL_PROMPT_IDS,
    bodies: dict[str, str] | None = None,
) -> str:
    chunks = ["# Prompt library", ""]
    for block_id in SHARED_BLOCK_IDS:
        chunks.append(f"<!-- shared-block: {block_id} -->\n\n```text\n{blocks[block_id]}\n```\n")
    for prompt_id in ids:
        body = (bodies or {}).get(prompt_id, _body(blocks))
        chunks.append(f"<!-- prompt-id: {prompt_id} status: active -->\n\n```text\n{body}\n```\n")
    return "\n".join(chunks)


def test_prompt_parity_passes_on_the_real_repo() -> None:
    assert verify_prompt_parity(ROOT) == []


def test_real_shared_blocks_match_the_manifest_digests() -> None:
    # The manifest is copied byte-for-byte from the product reference, so this is the actual
    # cross-repository parity assertion: the lab's block bodies hash to the product's digests.
    blocks = _real_blocks()
    digests = _real_digests()
    assert set(blocks) == set(SHARED_BLOCK_IDS)
    for block_id, body in blocks.items():
        assert shared_block_digest(body) == digests[block_id], block_id


def test_real_library_declares_every_pinned_id_in_order() -> None:
    found = tuple(prompt_id for prompt_id, _, _ in prompt_entries(LIBRARY.read_text("utf-8")))
    assert found == _ALL_PROMPT_IDS


def test_synthetic_library_is_accepted() -> None:
    assert verify_prompt_library(_library(_real_blocks()), _real_digests()) == []


def test_prompt_library_is_crlf_stable() -> None:
    # A Windows checkout must not change a digest or a body match. Same content, CRLF line endings,
    # identical result - otherwise the parity gate would fail purely on checkout style.
    blocks = _real_blocks()
    text = _library(blocks)
    assert verify_prompt_library(text.replace("\n", "\r\n"), _real_digests()) == []
    assert normalize_newlines(text.replace("\n", "\r\n")) == text
    for body in blocks.values():
        assert shared_block_digest(body.replace("\n", "\r\n")) == shared_block_digest(body)


def test_prompt_library_digest_drift_fails() -> None:
    # Editing a shared block in the lab without the product edit landing first is the exact failure
    # the SHA-256 pin exists to catch.
    blocks = _real_blocks()
    drifted = dict(blocks)
    drifted[SHARED_BLOCK_IDS[0]] = blocks[SHARED_BLOCK_IDS[0]] + "\nAn unauthorised extra line."
    failures = verify_prompt_library(_library(drifted), _real_digests())
    assert any("digest" in failure and SHARED_BLOCK_IDS[0] in failure for failure in failures), (
        failures
    )


def test_prompt_library_missing_id_fails() -> None:
    blocks = _real_blocks()
    failures = verify_prompt_library(_library(blocks, _ALL_PROMPT_IDS[:-1]), _real_digests())
    assert any(_ALL_PROMPT_IDS[-1] in failure for failure in failures), failures


def test_prompt_library_extra_id_fails() -> None:
    blocks = _real_blocks()
    text = _library(blocks, (*_ALL_PROMPT_IDS, "DL-P99-NOT-IN-THE-MANIFEST"))
    failures = verify_prompt_library(text, _real_digests())
    assert any("DL-P99-NOT-IN-THE-MANIFEST" in failure for failure in failures), failures


def test_prompt_library_duplicate_marker_fails() -> None:
    # A duplicated marker makes "the" body for an ID ambiguous; whichever copy a reader pastes, the
    # other is unchecked drift.
    blocks = _real_blocks()
    text = _library(blocks, (*_ALL_PROMPT_IDS, _ALL_PROMPT_IDS[0]))
    failures = verify_prompt_library(text, _real_digests())
    assert any("duplicate prompt markers" in failure for failure in failures), failures


def test_prompt_library_missing_shared_block_copy_fails() -> None:
    blocks = _real_blocks()
    target = _ALL_PROMPT_IDS[3]
    stripped = "\n\n".join(
        [
            "You do one bounded thing.",
            blocks[SHARED_BLOCK_IDS[0]],
            _CLAUDE_LINE,
            _CODEX_LINE,
            _GATE_LINE,
        ]
    )
    failures = verify_prompt_library(_library(blocks, bodies={target: stripped}), _real_digests())
    assert any(
        target in failure and SHARED_BLOCK_IDS[1] in failure and "found 0" in failure
        for failure in failures
    ), failures


def test_prompt_library_duplicated_shared_block_copy_fails() -> None:
    blocks = _real_blocks()
    target = _ALL_PROMPT_IDS[1]
    doubled = _body(blocks) + "\n\n" + blocks[SHARED_BLOCK_IDS[0]]
    failures = verify_prompt_library(_library(blocks, bodies={target: doubled}), _real_digests())
    assert any(
        target in failure and SHARED_BLOCK_IDS[0] in failure and "found 2" in failure
        for failure in failures
    ), failures


def test_prompt_library_missing_each_claude_clause_token_fails() -> None:
    # Every token individually, because the tokens are checked outside the shared blocks: several
    # of them also occur inside runtime-bootstrap-v1, and the check must not be satisfiable by the
    # shared spine alone.
    blocks = _real_blocks()
    target = _ALL_PROMPT_IDS[0]
    for token in REQUIRED_CLAUDE_CLAUSE:
        clause = _CLAUDE_LINE.replace(token, "[removed]")
        codex = _CODEX_LINE.replace(token, "[removed]")
        body = _body(blocks, claude=clause, codex=codex, gate=_GATE_LINE.replace(token, "[x]"))
        failures = verify_prompt_library(_library(blocks, bodies={target: body}), _real_digests())
        assert any(
            "Claude runtime clause token" in failure and repr(token) in failure
            for failure in failures
        ), (token, failures)


def test_prompt_library_missing_each_codex_clause_token_fails() -> None:
    blocks = _real_blocks()
    target = _ALL_PROMPT_IDS[0]
    for token in REQUIRED_CODEX_CLAUSE:
        clause = _CODEX_LINE.replace(token, "[removed]")
        claude = _CLAUDE_LINE.replace(token, "[removed]")
        body = _body(blocks, claude=claude, codex=clause, gate=_GATE_LINE.replace(token, "[x]"))
        failures = verify_prompt_library(_library(blocks, bodies={target: body}), _real_digests())
        assert any(
            "Codex runtime clause token" in failure and repr(token) in failure
            for failure in failures
        ), (token, failures)


def test_prompt_library_rejects_a_bare_human_ref() -> None:
    # product q-8 and lab q-8 are different gates, so an unqualified ref is genuinely ambiguous.
    blocks = _real_blocks()
    target = _ALL_PROMPT_IDS[2]
    body = _body(blocks, gate="GATE: q-8 stays open.")
    failures = verify_prompt_library(_library(blocks, bodies={target: body}), _real_digests())
    assert any(target in failure and "unqualified human ref" in failure for failure in failures), (
        failures
    )


def test_prompt_library_accepts_qualified_human_refs_for_either_repository() -> None:
    blocks = _real_blocks()
    for ref in (
        "Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8",
        "Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-9",
    ):
        body = _body(blocks, gate=f"GATE: {ref} stays open.")
        bodies: dict[str, str] = {prompt_id: body for prompt_id in _ALL_PROMPT_IDS}
        assert verify_prompt_library(_library(blocks, bodies=bodies), _real_digests()) == [], ref


def test_prompt_library_rejects_a_stray_text_fence() -> None:
    blocks = _real_blocks()
    text = _library(blocks) + "\n```text\nA stray unattached prompt body.\n```\n"
    failures = verify_prompt_library(text, _real_digests())
    assert any("text fences" in failure for failure in failures), failures


def test_parity_manifest_accepts_the_real_manifest() -> None:
    assert verify_parity_manifest(_load_manifest()) == []


def test_parity_manifest_malformed_shapes_fail() -> None:
    payloads: tuple[object, ...] = ("not-an-object", [], 42, None, {1: "int-keyed"})
    for payload in payloads:
        assert verify_parity_manifest(payload), payload


def test_parity_manifest_wrong_schema_version_fails() -> None:
    payload = _load_manifest()
    payload["manifest_schema_version"] = 2
    assert any("manifest_schema_version" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_reordered_common_ids_fail() -> None:
    # Order is part of the contract: the library is required to present prompts in manifest order.
    payload = _load_manifest()
    payload["common_prompt_ids"] = list(reversed(payload["common_prompt_ids"]))
    assert any("common_prompt_ids" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_dropped_common_id_fails() -> None:
    payload = _load_manifest()
    payload["common_prompt_ids"] = payload["common_prompt_ids"][:-1]
    assert any("common_prompt_ids" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_dropped_continuous_id_fails() -> None:
    payload = _load_manifest()
    payload["continuous_prompt_ids"] = []
    assert any(CONTINUOUS_PROMPT_ID in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_malformed_shared_blocks_fail() -> None:
    payload = _load_manifest()
    payload["shared_blocks"] = [{"id": "runtime-bootstrap-v1"}]
    assert any("shared_blocks" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_reordered_shared_blocks_fail() -> None:
    payload = _load_manifest()
    payload["shared_blocks"] = list(reversed(payload["shared_blocks"]))
    assert any("shared_blocks" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_missing_lab_repository_entry_fails() -> None:
    payload = _load_manifest()
    payload["repositories"] = [
        entry
        for entry in payload["repositories"]
        if entry["slug"] != "Chris0Jeky/developer-lens-lab"
    ]
    assert any("developer-lens-lab" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_wrong_lab_extension_ids_fail() -> None:
    payload = _load_manifest()
    for entry in payload["repositories"]:
        if entry["slug"] == "Chris0Jeky/developer-lens-lab":
            entry["extension_prompt_ids"] = ["DL-PX01-PRODUCT-DEEP-DISCOVERY"]
    assert any("extension_prompt_ids" in failure for failure in verify_parity_manifest(payload))


def test_parity_manifest_wrong_lab_role_or_paths_fail() -> None:
    payload = _load_manifest()
    for entry in payload["repositories"]:
        if entry["slug"] == "Chris0Jeky/developer-lens-lab":
            entry["role"] = "product"
            entry["friction_log"] = "docs/elsewhere.md"
    failures = verify_parity_manifest(payload)
    assert any("role must be 'lab'" in failure for failure in failures), failures
    assert any("friction_log" in failure for failure in failures), failures


_EXEC = ("<!-- continuous-execution-begin -->", "<!-- continuous-execution-end -->")
_STOP = ("<!-- continuous-stop-begin -->", "<!-- continuous-stop-end -->")


def _continuous(exec_pair: str, stop_pair: str) -> str:
    return f"# Continuous work protocol\n\n{exec_pair}\n\nThe wave.\n\n{stop_pair}\n"


def test_continuous_protocol_passes_on_the_real_file() -> None:
    text = (ROOT / "docs" / "agent-system" / "CONTINUOUS_WORK_PROTOCOL.md").read_text("utf-8")
    assert verify_continuous_protocol(text) == []


def test_continuous_protocol_accepts_ordered_pairs() -> None:
    good = _continuous(f"{_EXEC[0]}\n\nExecution.\n\n{_EXEC[1]}", f"{_STOP[0]}\nStops.\n{_STOP[1]}")
    assert verify_continuous_protocol(good) == []


def test_continuous_protocol_missing_stop_marker_fails() -> None:
    text = _continuous(f"{_EXEC[0]}\nExecution.\n{_EXEC[1]}", f"{_STOP[0]}\nStops without an end.")
    failures = verify_continuous_protocol(text)
    assert any("continuous-stop" in failure and "exactly one" in failure for failure in failures)


def test_continuous_protocol_reversed_stop_markers_fail() -> None:
    text = _continuous(f"{_EXEC[0]}\nExecution.\n{_EXEC[1]}", f"{_STOP[1]}\nStops.\n{_STOP[0]}")
    failures = verify_continuous_protocol(text)
    assert any("out of order" in failure for failure in failures), failures


def test_continuous_protocol_duplicate_stop_markers_fail() -> None:
    # A duplicated pair would let an extractor see only the first region and miss a divergent one.
    duplicated = f"{_STOP[0]}\nStops.\n{_STOP[1]}\n\n{_STOP[0]}\nDivergent stops.\n{_STOP[1]}"
    text = _continuous(f"{_EXEC[0]}\nExecution.\n{_EXEC[1]}", duplicated)
    failures = verify_continuous_protocol(text)
    assert any("continuous-stop" in failure and "exactly one" in failure for failure in failures)


def test_continuous_protocol_missing_execution_pair_fails() -> None:
    text = _continuous("No execution markers here.", f"{_STOP[0]}\nStops.\n{_STOP[1]}")
    failures = verify_continuous_protocol(text)
    assert any("continuous-execution" in failure for failure in failures), failures


def test_prompt_classifications_pass_on_the_real_repo() -> None:
    assert verify_prompt_classifications(ROOT) == []


def test_prompt_classification_accepts_supported_values(tmp_path: Path) -> None:
    for value in ("redirect", "historical"):
        (tmp_path / "doc.md").write_text(
            f"# Old prompt\n\n<!-- prompt-classification: {value} -->\n", encoding="utf-8"
        )
        assert verify_prompt_classifications(tmp_path) == [], value


def test_prompt_classification_rejects_an_unsupported_value(tmp_path: Path) -> None:
    # "active" outside the library would claim a second executable-prompt surface.
    (tmp_path / "doc.md").write_text(
        "# Old prompt\n\n<!-- prompt-classification: active -->\n", encoding="utf-8"
    )
    failures = verify_prompt_classifications(tmp_path)
    assert any("prompt-classification 'active'" in failure for failure in failures), failures


def test_prompt_parity_reports_a_malformed_manifest(tmp_path: Path) -> None:
    harness = tmp_path / ".agent-harness"
    harness.mkdir()
    (harness / "prompt-parity.json").write_text("{not json", encoding="utf-8")
    failures = verify_prompt_parity(tmp_path)
    assert any("invalid .agent-harness/prompt-parity.json" in failure for failure in failures)
