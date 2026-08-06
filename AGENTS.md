# Developer Lens Lab repository guide

Developer Lens Lab is the public, invented-data-first research companion to Developer Lens.
It evaluates methods; it never scores people, promotes a model, or becomes product authority.

## Cold start

1. Read `.agent-harness/tier.json`, `HUMAN_TODO.md`, and `docs/CURRENT_STATE.md` completely.
2. Refresh `git status --short --branch`, remotes, recent commits, worktrees, the current PR, CI,
   and unresolved review threads. Live Git and CI outrank every state file.
3. Invoke `$developer-lens-lab-continuation` before implementation, contract, corpus, experiment,
   artifact-store, or handoff work.
4. Read `docs/PRODUCT_BOUNDARY.md` and `docs/DATA_POLICY.md` before any data or model change; read
   `docs/CONTRACTS.md` before changing a pack, bundle, snapshot, or compatibility seam.
5. Use invented fixtures unless a task names a newer explicit owner approval and exact data scope.

## Source of truth

| Surface | Authority |
|---|---|
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
- Network collection, credentials, real/private data, external model calls, product promotion,
  generated dataset/artifact publication, and a durable cross-repository identity key still need
  an explicit bounded task or owner decision.
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

Run `uv run dllab benchmark wb-c1 --smoke` once the WB-C1 slice exists. Full benchmarks and any
networked command are opt-in and must not be normal PR checks until measured and authorized.

## Collaboration and handoff

Use one writer per checkout. Parallel writers require separate coordinator-owned worktrees and
non-overlapping paths. Keep no server, notebook kernel, or background agent after handoff. Use one
fresh-context adversarial review for non-trivial code or methodology and review the exact final
head. Close with changed / verified / NOT verified / failures and workarounds / docs-state sync /
residual risk / human actions / exact branch-HEAD-PR-check-worktree state / exact resume point.
