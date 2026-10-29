# Issue #34: explicit prompt discovery and scout routing

This bounded follow-up to LAB-GOV-02 starts from PR #206 head
`5c12d24c4e01223501fe7dada02971652c736b48`. It addresses the remaining prompt-discovery and
per-body scout-name gaps in [issue #34](https://github.com/Chris0Jeky/developer-lens-lab/issues/34).
The earlier [routing reconciliation](2026-10-29-34-prompt-routing-evidence.md) accurately records
the prior state; this change supplies the explicit scout names that were still pending there.

## Discovery contract

The verifier requires one document-level `prompt-classification` marker, with value `redirect` or
`historical`, for a prompt-shaped Markdown document outside the exact registered prompt-library
path. Discovery uses explicit signatures:

- An unfenced, unquoted, standalone `prompt-id` or `shared-block` HTML-comment directive.
- A filename whose final token is `prompt` or `prompts`, a file beneath a `prompts` directory,
  or an ATX document title ending in `prompt`/`prompts` or starting with `Prompt:`, combined with
  a role/bootstrap opening in prose or a top-level plain-text fence.

Recognized openings are `You are`, `Act as`, `Read AGENTS.md`, `Read CLAUDE.md`, and the registered
runtime-bootstrap heading. Plain-text fences have an empty info string, `text`, or `plaintext`.
Only the document's first level-one heading supplies its title; an ordinary guide's example
subheading does not turn the guide into a standalone prompt.

Classification declarations must occupy their own lines. Malformed, unsupported, duplicate, and
conflicting declarations fail. Samples inside fenced, indented, or quoted examples neither declare
classification nor trigger metadata discovery. Fences use matching backtick/tilde characters and
closing runs at least as long as their opening runs; nested fenced Markdown examples stay inert.
The existing walker still excludes generated run reports, while tracked top-level `generated`
documentation remains checked. Only the exact canonical library path receives the executable
library exemption; a copied library elsewhere requires classification.

This is deterministic artifact discovery, not a semantic classifier for arbitrary instructions.
Unlabelled prose with no metadata signature is deliberately outside detection. The verifier does
not infer that ordinary engineering instructions or code examples are executable prompts, and
the check does not replace review of newly introduced document conventions.

## Scout routing and parity

Every one of the 14 active local routing clauses now names `dll-scout` with its existing Opus 5 low
route, alongside `dll-implementer`, `dll-reviewer`, and `dll-mechanic`. The verifier requires the
scout token after removing the shared blocks, so a shared clause cannot satisfy a missing local
route. The Codex adapter and the existing synthetic routing fixture receive the matching wording.

An exact-base comparison proved that all 14 prompt-body changes are the local scout clause only.
Both shared source blocks and all 14 repeated copies of each block are byte-identical to the base.
The parity manifest is also unchanged:

- Manifest SHA-256: `94e756f3dca1de93b906983395b763f80f156be8cb899c1e665f0f418b09a1b4`.
- Runtime block SHA-256: `3313bc1a9884e5f3e62f621f124da212842e49e018361c99840927836bfedc0e`.
- Friction block SHA-256: `56bc9679fc51fd4ff5f05b715c42a96c3201284a6fee1a033524c2ccc55f5a7e`.

## Verification and handoff

- RED: the initial focused regressions produced **37 failed, 23 passed** against the base verifier.
- GREEN: `pytest tests/test_context*.py` produced **307 passed**, including the 62 new focused
  cases. The new file follows the existing context-test glob, so the compatibility workflow runs
  these cases on both configured Python versions without a workflow change.
- Actual `dllab context verify` passed with this checkout's source.
- Ruff formatting and lint passed for all three touched Python files.
- Strict Pyright passed with **0 errors, 0 warnings, 0 informations**, preserving the repository's
  strict settings and using only this checkout's source as the extra import path.
- `git diff --check` passed. No shared-environment synchronization or network access was needed.

The coordinator owns full gates, independent exact-head review, publication, aging, merges,
current-state/ledger updates, and the matching local scout wording in the cross-repository contract.
No Product-owned schema, shared prompt contract, capability, owner gate, scientific method,
holdout, or frozen evidence changes. Roll back this isolated verifier/routing/test/documentation
patch if its declared signature boundary proves unsuitable; any broader discovery convention
needs an explicit reviewed rule and examples.

## First independent-review correction

Review of `08526698208d60bd72ecedb67cc25fa9f9b80ff7` reproduced inert-example false positives:
one to three leading spaces followed by a tab were not recognized as indented code, and an
unmarked continuation of a quoted paragraph was treated as top-level prose. The installed
CommonMark renderer and the documentation's Python-Markdown renderer both confirmed the reported
code-block and blockquote renderings, including termination by a blank line.

The scanner now measures indentation using four-column tab stops and retains quoted-paragraph
continuation state. Blank lines and relevant heading, fence, thematic-rule, and HTML-metadata
starts terminate that continuation; quoted code fences never create paragraph-continuation state.
Tests preserve discovery of actual prose or fences after quote termination. The explicit title
prefix also now accepts `Prompt:resume`, matching the already declared `Prompt:` convention;
similar words such as `Prompter:` remain outside the signature.

- RED: **8 failed, 78 passed** in the focused discovery module before the correction.
- GREEN: **86 passed** in that module, and **331 passed** across `tests/test_context*.py`.
- Actual context verification, Ruff formatting/lint, and `git diff --check` passed.
- Strict Pyright reported **0 errors, 0 warnings, 0 informations**.

This correction adds no parser dependency or new discovery signature. Renderer use was read-only
proof; production verification remains bounded structural scanning. Prompt-library bytes, the
parity manifest, capability posture, and owner gates are untouched. The earlier checkout remained
unchanged during its concurrent full gate. Final full-gate and exact-head review evidence remain
coordinator-owned.
