# Developer Lens Lab — Codex adapter

`CLAUDE.md` is the shared repository canon: identity, cold start, source-of-truth map, authority,
protected-data rule, run/prove gate, and handoff shape live there. Read it first and treat it as
binding; this file adds only Codex-runtime deltas. `uv run dllab context verify` enforces both.

## Codex continuation

Invoke `$developer-lens-lab-continuation` before implementation, contract, corpus, experiment,
artifact-store, or handoff work.

## Codex routing

Use `tools/cards.py` as the task source and choose the first dependency-safe active card. Use one
writer per checkout; parallel writers need separate coordinator-owned worktrees and disjoint
paths. Escalate judgment-heavy implementation or review to Terra/Sol. Risk classes, routing, and
protocols live in `.agent-harness/governor.json` and `docs/agent-system/`; non-flagship
orchestrators use the Research Governor Lite prompt in `docs/agent-system/PROMPT_LIBRARY.md`.

## Protected data (full rule in `CLAUDE.md`)

Invented fixtures only. Never inspect real repositories, provider accounts, credentials, browser
profiles, working trees, or generated product outputs; never track `.dllab`, run artifacts,
repository allowlists, provider IDs, local paths, or environment values.

## Prove and close

Run the focused check first, then the full gate in `CLAUDE.md` for a code/config milestone. Close
under changed / verified / NOT verified / failures and workarounds / docs-state sync / residual
risk / human actions / exact branch-HEAD-PR-check-worktree state / exact resume point.
