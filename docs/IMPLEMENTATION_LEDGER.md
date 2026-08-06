# Implementation ledger

Append milestone evidence. Live GitHub facts are snapshots and must be refreshed.

## 2026-08-06 — Repository commission and M0 start

- Owner commissioned repository `Chris0Jeky/developer-lens-lab` and invented-data bootstrap, then
  explicitly changed the route to public and directed a faster value-first posture with hardening
  debt documented for later.
- Remote is public with default branch `main`; bootstrap branch is
  `codex/bootstrap-lab-os`.
- Live Developer Lens correction: the attached blueprint was based on PR #167. At bootstrap,
  product `origin/main` had advanced and PR #176 was the open conflicting LIFE-03 PR. The dirty,
  stale product primary checkout and occupied worktrees were preserved.
- Decision: T1/C0 public synthetic route; no collector, raw response landing, token, model call, real dataset,
  cross-repository identity key, or product promotion.
- Tooling: task-local bootstrap used uv 0.12.2; the locked environment resolved 84 packages and
  used Python 3.12.7.
- Verification: `uv lock --check`, locked sync, Ruff format/lint, strict Pyright, context verifier,
  3 pytest tests (73% package coverage), strict MkDocs build, repository-hygiene scan, skill
  validator, and `git diff --check` passed locally on the completed M0 worktree.
- NOT verified: hosted Linux CI and exact-head independent review remain publication gates.

## 2026-08-06 — M1 contracts and artifact foundation

- PR #1 merged with merge commit `b276656d`; the workflow now exists on default branch. M1 was
  rebased onto that live base before its proving pass.
- Added strict `DeveloperLensResearchPack.v1` and `DeveloperLensEvaluationBundle.v1` models,
  deterministic JSON Schemas, explicit relation/missingness and temporal availability, disjoint
  repository/time/seed splits, closed non-promotion decisions, and path-free artifact references.
- Added `dllab contracts check|render|sync`, `pack validate|profile`, and `bundle validate`. Pinned
  product sync reads only fixed files from the named Git commit and records checksums as provenance,
  not cross-repository identity.
- Added a scope-local content-addressed `.dllab` store with digest/size verification, atomic replace,
  Parquet row/column checks, and confined scope invalidation. Valuable-data durability and hostile
  filesystem defenses remain in `HARDENING_BACKLOG.md`.
- First full-gate attempt exposed a hygiene-scanner substring bug: legitimate `artifacts.py` files
  were mistaken for the ignored `artifacts/` directory. The rule now matches actual top-level
  generated directories and has a regression test.
- Verification after the repair: locked uv resolution/sync, Ruff format/lint, strict Pyright,
  schema/card/context drift checks, 15 pytest tests with 84% package coverage, strict MkDocs,
  repository hygiene, and PR-range `git diff --check` passed on Windows/Python 3.12.7.
- NOT verified: hosted Linux CI, exact-head independent review, the producer-side Developer Lens
  snapshot, and the WB-C1 benchmark remain subsequent gates.
