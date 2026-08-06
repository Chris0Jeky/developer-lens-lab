from pathlib import Path

from developer_lens_lab.context import verify_repository
from developer_lens_lab.context.verify import verify_markdown_links

ROOT = Path(__file__).resolve().parents[1]


def test_repository_context_is_valid() -> None:
    report = verify_repository(ROOT)
    assert report.ok, report.failures


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
