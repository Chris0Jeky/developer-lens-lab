from pathlib import Path

import pytest

from developer_lens_lab.context.verify import (
    verify_markdown_links,
    verify_prompt_classifications,
    verify_repository,
)


def test_invalid_utf8_markdown_reports_failure_not_crash(tmp_path: Path) -> None:
    broken = tmp_path / "broken.md"
    broken.write_bytes(b"\xff")

    link_failures = verify_markdown_links(tmp_path)
    classification_failures = verify_prompt_classifications(tmp_path)

    assert any("broken/unreadable file in broken.md" in failure for failure in link_failures)
    assert any(
        "broken/unreadable file in broken.md" in failure for failure in classification_failures
    )


def test_vanishing_markdown_reports_failure_not_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    vanished = tmp_path / "vanished.md"
    vanished.write_text("# present during discovery\n", encoding="utf-8")
    original_read_text = Path.read_text

    def read_text(path: Path, encoding: str | None = None, errors: str | None = None) -> str:
        if path == vanished:
            raise FileNotFoundError(path)
        return original_read_text(path, encoding=encoding, errors=errors)

    monkeypatch.setattr(Path, "read_text", read_text)

    link_failures = verify_markdown_links(tmp_path)
    classification_failures = verify_prompt_classifications(tmp_path)

    assert any("broken/unreadable file in vanished.md" in failure for failure in link_failures)
    assert any(
        "broken/unreadable file in vanished.md" in failure for failure in classification_failures
    )


def test_git_less_host_reports_probe_failure_not_crash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import developer_lens_lab.context.verify as context_verify

    def missing_git(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("git")

    monkeypatch.setattr(context_verify.subprocess, "run", missing_git)

    report = verify_repository(tmp_path)

    assert not report.ok
    assert any(
        "git trust probe unavailable" in failure for failure in report.failures
    )
