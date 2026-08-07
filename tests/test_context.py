from pathlib import Path

from developer_lens_lab.context import verify_repository
from developer_lens_lab.context.verify import (
    REQUIRED_SETTINGS_READ_DENY,
    verify_markdown_links,
    verify_settings_deny,
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


def test_settings_deny_reports_each_missing_protected_sink() -> None:
    partial = {"permissions": {"deny": ["Read(./.dllab/**)"]}}
    failures = verify_settings_deny(partial)
    assert any("artifacts" in failure for failure in failures)
    assert any("reports/generated" in failure for failure in failures)
    assert not any(".dllab" in failure for failure in failures)


def test_settings_deny_requires_a_deny_block() -> None:
    for payload in ({"permissions": {"defaultMode": "acceptEdits"}}, {}, "not-an-object"):
        assert len(verify_settings_deny(payload)) == len(REQUIRED_SETTINGS_READ_DENY)


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
