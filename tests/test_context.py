import json
from pathlib import Path
from typing import Any

from developer_lens_lab.context import verify_repository
from developer_lens_lab.context.verify import (
    REQUIRED_SETTINGS_READ_DENY,
    verify_context_budget,
    verify_governor,
    verify_markdown_links,
    verify_one_shared_block,
    verify_settings_deny,
    verify_skill_parity,
)

ROOT = Path(__file__).resolve().parents[1]
GOVERNOR = ROOT / ".agent-harness" / "governor.json"


def test_repository_context_is_valid() -> None:
    report = verify_repository(ROOT)
    assert report.ok, report.failures


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
