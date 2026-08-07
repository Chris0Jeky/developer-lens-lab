from pathlib import Path

from developer_lens_lab.context import verify_repository
from developer_lens_lab.context.verify import (
    REQUIRED_SETTINGS_READ_DENY,
    verify_context_budget,
    verify_markdown_links,
    verify_settings_deny,
    verify_skill_parity,
)

ROOT = Path(__file__).resolve().parents[1]


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
    assert verify_skill_parity(tmp_path) == []


def test_skill_parity_reports_drift_between_copies(tmp_path: Path) -> None:
    claude = f"{_START}\n## Protect evaluation integrity\n\n- Claude bullet.\n{_END}\n"
    agents = f"{_START}\n## Protect evaluation integrity\n\n- Agents bullet.\n{_END}\n"
    _write_skill_pair(tmp_path, claude, agents)
    failures = verify_skill_parity(tmp_path)
    assert failures == [
        "shared evaluation-integrity section drifted between the two SKILL.md copies"
    ]


def test_skill_parity_reports_missing_marker(tmp_path: Path) -> None:
    good = f"{_START}\n## Protect evaluation integrity\n\n- Shared bullet.\n{_END}\n"
    without_end = f"{_START}\n## Protect evaluation integrity\n\n- Shared bullet.\n"
    _write_skill_pair(tmp_path, good, without_end)
    failures = verify_skill_parity(tmp_path)
    assert any(
        "marker" in failure and ".agents/skills/developer-lens-lab-continuation/SKILL.md" in failure
        for failure in failures
    )


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
