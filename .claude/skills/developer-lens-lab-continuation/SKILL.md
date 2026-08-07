---
name: developer-lens-lab-continuation
description: Resume and advance Developer Lens Lab from live repository evidence while preserving its invented-data-first posture, product/lab authority split, generated contract seam, holdout integrity, deterministic fallback, and explicit owner gates. Use for lab implementation, contracts, artifact storage, experiments, corpus planning, methodology review, PR continuation, or handoff.
---

# Developer Lens Lab Continuation (Claude runtime)

## Resume from truth

1. Read `CLAUDE.md`, `.agent-harness/tier.json`, `HUMAN_TODO.md`, and `docs/CURRENT_STATE.md`.
2. Refresh Git status, upstream, worktrees, PR/check state, and unresolved review threads.
3. Read only the objective-relevant product boundary, data policy, contracts, research programme,
   implementation ledger, experiment ledger, code, and tests.
4. Treat live Git and executable checks as stronger than state or ledger prose.

## Select one bounded vertical

Use `tools/cards.py` as the task source and choose the first dependency-safe active card. State its
owned paths, non-goals, acceptance behavior, rollback, focused checks, and stop condition.

Keep orchestration, methodology judgment, and contract design in the coordinating session.
Delegate bounded implementation to `dll-implementer`, fresh-context adversarial review to
`dll-reviewer`, and mechanical sweeps to `dll-mechanic` (definitions in `.claude/agents/`). Use
one writer per checkout; parallel writers need separate coordinator-owned worktrees and disjoint
paths. Subagents can move HEAD — pin git state in every delegation prompt and re-verify after.

<!-- shared:protected-data-defaults start -->
Default to invented fixtures. Do not inspect or collect real repositories, generated product data,
credentials, browser profiles, caches, working trees, or provider accounts. Network collection,
real datasets, new classes/sinks, durable indexes, model calls, publication, cross-repo identity,
and product promotion require the exact open owner gate to be closed first.
<!-- shared:protected-data-defaults end -->

<!-- shared:evaluation-integrity start -->
## Protect evaluation integrity

- Keep generator/seed-family identifiers out of features and reports.
- Group by repository or seed family and time; fit transforms and thresholds inside training only.
- Give the deterministic baseline the same selection budget as the candidate.
- Open a final holdout once and record the custody event immediately.
- Score offline PELT only on offline localisation unless a causal repeated-prefix wrapper was
  separately preregistered.
- Interpret invented results as mechanics/failure-handling evidence, never empirical validity.
- Preserve a complete deterministic fallback and allow a clean rejection decision.
<!-- shared:evaluation-integrity end -->

## Prove and hand off

Run the focused check, then the full gate in `CLAUDE.md` for a code/config milestone. Review the
exact diff against `docs/PRODUCT_BOUNDARY.md`, `docs/DATA_POLICY.md`, and `docs/CONTRACTS.md`.
Non-trivial logic or methodology needs a fresh-context adversarial review (`dll-reviewer`). Update
the implementation ledger for code milestones, experiment ledger for run/holdout decisions, failure
archive for killed approaches, and current state only at a phase boundary.

Report changed, verified, NOT verified, failures/workarounds, docs-state sync, residual risk, human
actions, exact branch/HEAD/PR/check/worktree state, and one exact resume point.
