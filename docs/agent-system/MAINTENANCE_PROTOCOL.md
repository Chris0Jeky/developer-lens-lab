# Maintenance, administration, and release protocol

The governor owns repository administration end to end: issues/cards/labels, ledgers,
release/tag/version state, packaging and lock state, dependency alerts, CI and docs, generated
schemas and vendored snapshots, artefact/reproduction commands, public C0 release assets,
repository description/topics/community files, worktrees and stale branches, cross-repo
compatibility, and the failure archive.

## Recurring checks

| Check | Command / evidence | Cadence |
|---|---|---|
| Context and authority drift | `uv run dllab context verify` | every proving pass |
| Card/index drift | `python tools/cards.py --check` (also inside context verify) | every proving pass |
| Full code gate | the declared block in `CLAUDE.md` | every code/config milestone |
| Contract parity | `uv run dllab contracts check`; sync commands are check-only outside an intentional change | every proving pass; after any product contract head change |
| Canonical run reproducibility | replay the canonical WB-C1 run and byte-compare manifests | when the runner, contracts, or environment change |
| Prompt parity | `uv run dllab context verify` (manifest schema, prompt IDs, shared-block digests, runtime clauses, qualified human refs) | every proving pass; after any shared-block or manifest change on either side |
| Hygiene | `uv run python scripts/verify_hygiene.py` | every proving pass |
| Dependency alerts | Dependabot view; triage per issue #5 | before release/activation; on new alerts |
| Worktree/process hygiene | `git worktree list`; no background servers after handoff | every handoff |
| Late-review sweep | merged PRs re-checked for late comments at the next workflow event | after every merge |

On this estate's current host there is no repository-wide `uv` on PATH, but a **worktree-confined
bootstrap is proved to work**: create a standard-library virtual environment, install
`uv>=0.12.2,<0.13` into it, configure a confined worktree-local project environment, and invoke
that environment's literal `uv` executable. `uv sync --locked --all-groups` and the full declared gate
both run through it, so dependency re-locking is **not** tooling-blocked — it is unperformed work.
The bootstrap directory is gitignored and `uv.lock` is never modified as a side effect. Recorded as
FR-001 in [FRICTION_LOG.md](FRICTION_LOG.md); the superseded "tooling-blocked" claim is FR-002.

## Merge gate

While `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` — the **product** register's concurrent-writer
gate — stays open, lab pull requests are prepared and parked, never agent-merged. Explicit owner
commissioning permits isolated preparation. The gate is never inferred closed from a merged pull
request, a quiet session, or another agent's message. This is not the lab's own `q-8`, which is an
unrelated real-data publication gate; see [CROSS_REPO_CONTRACT.md](CROSS_REPO_CONTRACT.md) and
FR-004 in [FRICTION_LOG.md](FRICTION_LOG.md).

## Release protocol (v0.1.0 wave and later)

1. State/authority reconciliation is merged and green.
2. AGPL-3.0-only licence text, SPDX/README/package notices, copyright Cristian Tcaci.
3. Community files: CONTRIBUTING, Code of Conduct, issue/PR templates, Discussions, compact
   roadmap. `COMMERCIAL_OPTION.md` explains intent without legal claims; substantial external
   contributions wait for owner/legal CLA review.
4. Dependency triage current (issue #5) — bounded, recorded residuals allowed.
5. Package metadata and uvx/PyPI readiness for the lab.
6. Selected C0 JSON/HTML release assets with provenance and licence notices; release review per
   lane P.
7. Synchronized changelog/release notes; tag; verify the release renders and installs.
8. The frozen Method Trial v1 ships as the canonical exhibit — do not wait for the next
   experiment to tag.

## Health report

A fresh session should be able to state: lab head/version; active wave; active/consumed
holdouts; open PRs/CI/reviews; card drift; reproducibility status; product-contract parity;
dependency alerts; public-artefact eligibility; open owner/data gates; top methodology debt; and
the top three next actions — without reading every historical document.
