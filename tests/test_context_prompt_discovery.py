"""Synthetic discovery and local-routing checks for the single prompt library."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import pytest

from developer_lens_lab.context.verify import (
    COMMON_PROMPT_IDS,
    LAB_EXTENSION_PROMPT_IDS,
    PROMPT_LIBRARY,
    SHARED_BLOCK_IDS,
    prompt_entries,
    shared_block_digest,
    shared_blocks_in,
    verify_prompt_classifications,
    verify_prompt_library,
)

ROOT = Path(__file__).resolve().parents[1]
_ROLE = "You are a synthetic read-only reviewer. Read AGENTS.md first."


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.mark.parametrize(
    ("relative", "body"),
    [
        ("docs/notes.md", "<!-- prompt-id: INVENTED status: active -->\n\n```text\nwork\n```"),
        ("docs/notes.md", "<!-- prompt-id: INVENTED -->"),
        ("docs/notes.md", "<!-- shared-block: invented -->\n\n```text\nwork\n```"),
        ("docs/reviewer_prompt.md", _ROLE),
        ("docs/reviewer-prompt.md", f"```text\n{_ROLE}\n```"),
        ("docs/prompts/reviewer.md", f"~~~plaintext\n{_ROLE}\n~~~"),
        ("docs/notes.md", f"# Reviewer prompt\n\n```text\n{_ROLE}\n```"),
        ("docs/notes.md", "# Prompt: resume\n\nRead CLAUDE.md first."),
    ],
)
@pytest.mark.parametrize("classification", [None, "redirect", "historical"])
def test_prompt_documents_require_one_classification(
    tmp_path: Path, relative: str, body: str, classification: str | None
) -> None:
    marker = f"<!-- prompt-classification: {classification} -->\n\n" if classification else ""
    _write(tmp_path, relative, marker + body)

    failures = verify_prompt_classifications(tmp_path)

    if classification:
        assert failures == []
    else:
        assert any("requires one prompt-classification" in failure for failure in failures), (
            failures
        )


@pytest.mark.parametrize(
    "metadata",
    [
        "<!-- prompt-classification: -->",
        "<!-- prompt-classification historical -->",
        "<!-- prompt-classification: historical",
        "<!-- prompt-classification: historical extra -->",
        "<!-- prompt-classification: historical -->\n<!-- prompt-classification: historical -->",
        "<!-- prompt-classification: historical -->\n<!-- prompt-classification: redirect -->",
    ],
)
def test_malformed_or_duplicate_document_metadata_fails(tmp_path: Path, metadata: str) -> None:
    _write(tmp_path, "docs/notes.md", metadata)

    assert verify_prompt_classifications(tmp_path)


@pytest.mark.parametrize(
    ("relative", "body"),
    [
        ("docs/guide.md", "# Engineering guide\n\nRead the logs and run the tests."),
        ("docs/prompt-format.md", f"# Prompt format guide\n\n```text\n{_ROLE}\n```"),
        ("docs/guide.md", f"# Guide\n\n## Example prompt\n\n```text\n{_ROLE}\n```"),
        ("docs/guide.md", "```html\n<!-- prompt-id: INVENTED status: active -->\n```"),
        ("docs/guide.md", "```text\n<!-- prompt-classification: unsupported -->\n```"),
        (
            "docs/guide.md",
            "````markdown\n```text\n<!-- prompt-id: INVENTED status: active -->\n```\n````",
        ),
        ("docs/guide.md", "~~~markdown\n<!-- prompt-classification: unsupported -->\n~~~"),
        (
            "docs/guide.md",
            "~~~~markdown\n~~~text\n<!-- prompt-classification: unsupported -->\n~~~\n~~~~",
        ),
        (
            "docs/guide.md",
            "````markdown\n~~~\n<!-- prompt-classification: unsupported -->\n````",
        ),
        ("docs/guide.md", "> <!-- prompt-id: INVENTED status: active -->"),
        ("docs/guide.md", "> <!-- prompt-classification: unsupported -->"),
        ("docs/guide.md", "    <!-- prompt-classification: unsupported -->"),
        ("docs/guide.md", "The marker is `<!-- prompt-classification: unsupported -->`."),
        ("docs/notes.md", _ROLE),
    ],
)
def test_routine_documentation_and_examples_are_not_prompt_documents(
    tmp_path: Path, relative: str, body: str
) -> None:
    _write(tmp_path, relative, body)

    assert verify_prompt_classifications(tmp_path) == []


@pytest.mark.parametrize("indent", ["\t", "    ", " \t", "  \t", "   \t", "\t "])
def test_mixed_tab_indentation_is_an_inert_code_example(tmp_path: Path, indent: str) -> None:
    _write(tmp_path, "reviewer-prompt.md", f"# Reviewer prompt\n\n{indent}{_ROLE}\n")

    assert verify_prompt_classifications(tmp_path) == []


@pytest.mark.parametrize("quote", ["> Quoted example:", "   > Quoted example:", "> > Example:"])
def test_lazy_blockquote_paragraph_continuation_is_inert(tmp_path: Path, quote: str) -> None:
    _write(tmp_path, "reviewer-prompt.md", f"# Reviewer prompt\n\n{quote}\n{_ROLE}\n")

    assert verify_prompt_classifications(tmp_path) == []


@pytest.mark.parametrize("underline", ["=", "==", "===", "-", "--", "---", "   ==\t"])
def test_quoted_setext_heading_does_not_swallow_top_level_prompt(
    tmp_path: Path, underline: str
) -> None:
    _write(
        tmp_path,
        "reviewer-prompt.md",
        f"# Reviewer prompt\n\n> Example heading\n> {underline}\n{_ROLE}\n",
    )

    assert any(
        "requires one prompt-classification" in failure
        for failure in verify_prompt_classifications(tmp_path)
    )


@pytest.mark.parametrize("prefix", ["", "> Earlier paragraph\n>\n"])
@pytest.mark.parametrize("equals", ["=", "==", "===", "======="])
def test_quoted_equals_without_preceding_paragraph_remains_inert(
    tmp_path: Path, prefix: str, equals: str
) -> None:
    _write(tmp_path, "reviewer-prompt.md", f"# Reviewer prompt\n\n{prefix}> {equals}\n{_ROLE}\n")

    assert verify_prompt_classifications(tmp_path) == []


@pytest.mark.parametrize("opening, closing", [("```", "```"), ("````", "`````"), ("~~~", "~~~~")])
@pytest.mark.parametrize("paragraph_prefix", ["> > ", "> "])
def test_nested_quoted_fence_preserves_following_quoted_paragraph(
    tmp_path: Path, opening: str, closing: str, paragraph_prefix: str
) -> None:
    _write(
        tmp_path,
        "reviewer-prompt.md",
        f"# Reviewer prompt\n\n> > {opening}text\n> > code\n> > {closing}\n"
        f"{paragraph_prefix}Quoted example:\n{_ROLE}\n",
    )

    assert verify_prompt_classifications(tmp_path) == []


@pytest.mark.parametrize("opening, closing", [("```", "```"), ("````", "`````"), ("~~~", "~~~~")])
def test_nested_quoted_fence_preserves_following_top_level_prompt(
    tmp_path: Path, opening: str, closing: str
) -> None:
    _write(
        tmp_path,
        "reviewer-prompt.md",
        f"# Reviewer prompt\n\n> > {opening}text\n> > code\n> > {closing}\n{_ROLE}\n",
    )

    assert any(
        "requires one prompt-classification" in failure
        for failure in verify_prompt_classifications(tmp_path)
    )


@pytest.mark.parametrize(
    "body",
    [
        f"> Quoted example:\n\n{_ROLE}",
        f"> Quoted example:\n>\n{_ROLE}",
        f"> # Quoted heading\n{_ROLE}",
        f"> Quoted example:\n# Prompt: later\n{_ROLE}",
        f"> Quoted example:\n```text\n{_ROLE}\n```",
        f"> ```text\n> Quoted code\n> ```\n{_ROLE}",
        f"> ```text\n> Quoted code\n{_ROLE}",
        "> Quoted example:\n<!-- prompt-id: INVENTED status: active -->",
    ],
)
def test_quote_termination_preserves_real_prompt_discovery(tmp_path: Path, body: str) -> None:
    _write(tmp_path, "reviewer-prompt.md", f"# Reviewer prompt\n\n{body}\n")

    assert any(
        "requires one prompt-classification" in failure
        for failure in verify_prompt_classifications(tmp_path)
    )


@pytest.mark.parametrize("suffix", ["resume", " resume", "\tresume", ""])
def test_explicit_prompt_title_prefix_needs_no_space_after_colon(
    tmp_path: Path, suffix: str
) -> None:
    _write(tmp_path, "notes.md", f"# Prompt:{suffix}\n\n{_ROLE}\n")

    assert any(
        "requires one prompt-classification" in failure
        for failure in verify_prompt_classifications(tmp_path)
    )


@pytest.mark.parametrize("title", ["Prompter:resume", "Promptness:resume", "Prompt format:resume"])
def test_similar_titles_do_not_broaden_prompt_signature(tmp_path: Path, title: str) -> None:
    _write(tmp_path, "notes.md", f"# {title}\n\n{_ROLE}\n")

    assert verify_prompt_classifications(tmp_path) == []


def test_example_classification_does_not_classify_an_actual_prompt(tmp_path: Path) -> None:
    _write(
        tmp_path,
        "docs/reviewer_prompt.md",
        f"```html\n<!-- prompt-classification: historical -->\n```\n\n{_ROLE}",
    )

    assert any(
        "requires one prompt-classification" in failure
        for failure in verify_prompt_classifications(tmp_path)
    )


def test_only_the_registered_library_is_exempt(tmp_path: Path) -> None:
    text = (ROOT / PROMPT_LIBRARY).read_text(encoding="utf-8")
    _write(tmp_path, PROMPT_LIBRARY, text)
    assert verify_prompt_classifications(tmp_path) == []

    _write(tmp_path, "docs/copied/PROMPT_LIBRARY.md", text)
    assert any(
        "requires one prompt-classification" in f for f in verify_prompt_classifications(tmp_path)
    )


def test_generated_reports_are_skipped_but_tracked_generated_docs_are_checked(
    tmp_path: Path,
) -> None:
    _write(tmp_path, "reports/generated/reviewer_prompt.md", _ROLE)
    assert verify_prompt_classifications(tmp_path) == []

    _write(tmp_path, "generated/reviewer_prompt.md", _ROLE)
    assert verify_prompt_classifications(tmp_path)


def _library_and_digests() -> tuple[str, dict[str, str]]:
    text = (ROOT / PROMPT_LIBRARY).read_text(encoding="utf-8")
    payload = cast(
        dict[str, object],
        json.loads((ROOT / ".agent-harness/prompt-parity.json").read_text(encoding="utf-8")),
    )
    entries = cast(list[dict[str, str]], payload["shared_blocks"])
    return text, {entry["id"]: entry["sha256"] for entry in entries}


def test_all_active_local_bodies_name_the_scout_and_preserve_shared_blocks() -> None:
    text, digests = _library_and_digests()
    blocks = shared_blocks_in(text)
    entries = prompt_entries(text)
    assert tuple(entry[0] for entry in entries) == COMMON_PROMPT_IDS + LAB_EXTENSION_PROMPT_IDS
    for block_id in SHARED_BLOCK_IDS:
        assert shared_block_digest(blocks[block_id]) == digests[block_id]
    for prompt_id, status, body in entries:
        assert status == "active"
        for block in blocks.values():
            body = body.replace(block, "")
        assert "dll-scout" in body, prompt_id


@pytest.mark.parametrize("prompt_id", COMMON_PROMPT_IDS + LAB_EXTENSION_PROMPT_IDS)
def test_every_active_body_requires_the_scout_token(prompt_id: str) -> None:
    text, digests = _library_and_digests()
    body = next(body for found_id, _, body in prompt_entries(text) if found_id == prompt_id)
    text = text.replace(body, body.replace("dll-scout", "invented-scout"), 1)

    failures = verify_prompt_library(text, digests)

    assert any(prompt_id in failure and "'dll-scout'" in failure for failure in failures), failures
