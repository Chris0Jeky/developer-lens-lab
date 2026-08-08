# Developer Lens Lab repository canon

Developer Lens Lab is the public, invented-data-first research companion to Developer Lens.
It evaluates methods; person/team analysis stays inside the layered research modes of
`docs/PRODUCT_BOUNDARY.md`; it never promotes a model or becomes stable-product authority.
This file is the shared canon for every agent runtime; `AGENTS.md` is the thin Codex adapter.
`uv run dllab context verify` enforces required files, links, and budgets.

## Cold start

1. Read `.agent-harness/tier.json`, `HUMAN_TODO.md`, and `docs/CURRENT_STATE.md` completely.
2. Refresh `git status --short --branch`, remotes, recent commits, worktrees, the current PR, CI,
   and unresolved review threads. Live Git and CI outrank every state file.
3. Invoke the `developer-lens-lab-continuation` skill before implementation, contract, corpus,
   experiment, artifact-store, or handoff work (Codex form: `$developer-lens-lab-continuation`).
4. Read `docs/PRODUCT_BOUNDARY.md` and `docs/DATA_POLICY.md` before any data or model change;
   `docs/CONTRACTS.md` before touching a contract seam; `docs/agent-system/README.md` before
   selecting or sequencing multi-lane work.
5. Use invented fixtures unless a task names a newer explicit owner approval and exact data scope.

## Source of truth

| Surface | Authority |
|---|---|
| `docs/OWNER_CONSTITUTION.md` | Binding owner strategy and policy (constitution v2) |
| `.agent-harness/governor.json` + `docs/agent-system/` | Governor policy: risk classes, routing, lanes, protocols |
| `.agent-harness/tier.json` | Repository tier, overlays, and Git authority |
| `HUMAN_TODO.md` | Explicit owner decisions and genuinely open gates |
| `docs/PRODUCT_BOUNDARY.md` | Product/lab split and prohibited analytical shapes |
| `docs/DATA_POLICY.md` | Classes, sinks, retention, deletion, and publication |
| `docs/CONTRACTS.md` | ResearchPack/EvaluationBundle ownership and compatibility |
| `docs/CURRENT_STATE.md` | Single compact resume point |
| `docs/IMPLEMENTATION_LEDGER.md` | Code and repository milestone evidence |
| `docs/EXPERIMENT_LEDGER.md` | Experiment decisions, runs, holdout use, and rejections |
| `tools/cards.py` | Task-card source and active-horizon generator |
| `docs/HARDENING_BACKLOG.md` | Explicitly deferred security and operational debt |

## Current authority

- T1 sandbox, public synthetic route, C0 invented tracked/runtime inputs only.
- Push and merge are free after the declared checks, review, and aging gates.
- Favor runnable product/research value over non-essential security ceremony. Track deferred
  hardening rather than making it a prerequisite.
- Owner constitution v2 authorizes real own/curated data, layered people/team research, raw
  content (secrets prohibited absolutely), and an experimental channel — but every non-C0 lane
  stays closed until the activation preconditions in `.agent-harness/governor.json` are
  mechanically true. External model calls and credentials still need their own explicit gate.
  No durable cross-repo identity key; promotion stays product-governed.
- Product contract work is additive, synthetic-only, and lands through Developer Lens's own gate.

## Protected-data rule

Never inspect or ingest real repositories, provider accounts, credentials, browser profiles,
working trees, private data, or generated product outputs during ordinary work. Never track `.dllab`,
Parquet/run artifacts, repository allowlists, provider IDs, local paths, or environment values.
Missing, unsupported, omitted, censored, or unavailable evidence is explicit, never zero.

## Run and prove

```powershell
uv sync --locked --all-groups
uv run dllab doctor
uv run dllab context verify
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run mkdocs build --strict
uv run python scripts/verify_hygiene.py
```

Narrow first: one focused pytest path proves a slice; the full block above is the code/config
milestone gate. Run `uv run dllab benchmark wb-c1 --smoke` for the WB-C1 seam. Full benchmarks and
any networked command are opt-in and must not become normal PR checks until measured and authorized.

## Claude routing and delegation

- The coordinating session owns orchestration, decisions, and architecture: card selection,
  methodology judgment, contract design, and final merge judgment stay with it.
- Delegate bounded implementation to `dll-implementer`, fresh-context adversarial review to
  `dll-reviewer` (both Opus 5 high, pinned in `.claude/agents/`), and mechanical sweeps to
  `dll-mechanic` (Sonnet 4.6 high). Never route repo work to Haiku.
- One writer per checkout; parallel writers require separate coordinator-owned worktrees and
  non-overlapping paths. Subagents can move HEAD — pin git state in prompts, re-verify after each.
- `bypassPermissions` lives only in gitignored `.claude/settings.local.json`, never committed.

## Collaboration and handoff

Keep no server, notebook kernel, or background agent after handoff. Use one fresh-context
adversarial review for non-trivial code or methodology and review the exact final head. Update the
implementation ledger for code milestones, the experiment ledger for run/holdout decisions, the
failure archive for killed approaches, and `docs/CURRENT_STATE.md` only at a phase boundary. Close
with changed / verified / NOT verified / failures and workarounds / docs-state sync / residual
risk / human actions / exact branch-HEAD-PR-check-worktree state / exact resume point.
