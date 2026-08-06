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

## 2026-08-06 — M2 WB-C1 invented smoke benchmark

- Pinned the product-owned ResearchPack contract snapshot from Developer Lens producer commit
  `337d815f5af22691889f00b0ffa5e3cf61b65e74` (PR #178). Sync verified the declared schema/fixture
  bytes; the lab validates both the product fixture and its materialized WB-C1 pack against that
  producer schema plus the strict Pydantic runtime contract.
- Added deterministic Gaussian/heavy-tail weekly generators with no-change controls, four planted
  change shapes, missingness, and coverage/permission/parser confounds across disjoint train, test,
  and final-holdout repository/seed/time partitions.
- Added symmetric train-only inner-fit/inner-validation threshold selection, rolling median/MAD and
  online BOCPD arms, non-event false-alert exposure at an eight-week delay budget, measured Brier
  calibration, and PELT as complete-series offline description only.
- The custody callback writes dataset, frozen thresholds, and parameter hashes before holdout
  materialization. The resulting C0 ResearchPack contains real `coverage` and `repository_week`
  Parquet objects; the EvaluationBundle contains Parquet results, PELT/custody JSON, deterministic
  workload evidence, and standalone Markdown/HTML reports.
- Clean code head `f42a9b8de42b9847453d105364fc496e081a7024` ran `dllab benchmark wb-c1
  --smoke`, `dllab run reproduce wbc1_smoke`, and `dllab report build wbc1_smoke`. Replay regenerated
  and byte-compared every recorded artifact. The bundle decision was honestly `reject`: baseline
  false alerts/year `2.966666666666667` and detection `0.75`; candidate `4.133333333333334` and
  `0.625`; candidate Brier `0.02697459311457855`. The deterministic fallback remains complete.
- Pre-commit/full local proof on Windows/Python 3.12.7: locked uv resolution/sync, Ruff
  format/lint, strict Pyright, context/card/schema checks, 29 tests passed plus one Windows symlink
  skip with 88% package coverage, strict MkDocs build, repository hygiene, and `git diff --check`.
- NOT verified: hosted Linux CI. GitHub Status reported a critical Actions outage and neither the
  product producer PR nor the lab branch received a hosted run; no green result or waiver is
  inferred. Product PR #178 and the lab consumer change remain dependency-gated until both land.

## 2026-08-06 - M2 methodology repair and first valid experiment entry

- Exact-head implementation review first found that the eagerly imported `jsonschema` package was
  dev-only and that generated `JsonInteger` bounds used ignored `ge`/`le` keys. The fix promotes the
  dependency to runtime, adds an isolated `--no-dev` CLI proof, emits standard
  `minimum`/`maximum`, and adds standalone negative-bound canaries for both schemas.
- Fresh methodology review invalidated the original `f42a9b8` candidate metrics as evidence for
  the named BOCPD method. The changepoint branch used a different predictive density from the growth
  branch, the first observations informed the prior and were then processed again, final selection
  viability did not gate promotion, and a low-alert baseline could be called improved by a worse
  candidate. The earlier result remains historical implementation evidence only and must not be
  cited as a valid WB-C1 method comparison.
- The repair implements Adams–MacKay Algorithm 1 with a fixed, parameter-hashed
  Normal-Inverse-Gamma prior; uses the same run-specific predictive density for changepoint and
  growth mass; resets the new run to the fixed prior; and adds independent reference-vector,
  normalization, missingness-causality, and parameter-hash tests. Both train selection viability
  flags now gate the final decision, and false-alert improvement requires the candidate to be no
  more than 80% of the baseline rate without an absolute escape floor.
- Final-holdout custody now reserves a single-use scope and writes an append-only named receipt plus
  content-addressed object before materialization. A second process/run with the same ID refuses,
  crash-after-receipt consumes the run identity, and replay reads every stored artifact including
  custody before regenerating bytes. Tests prove repeat-run refusal, crash/restart refusal, missing
  custody-object refusal, and named-receipt tamper refusal.
- Exact clean code head `a01a3fd58c78b3c1a7092c1b00e804b3d7ce5eb8` passed locked
  runtime-only installation, Ruff format/lint, strict Pyright, context/task/schema drift checks,
  37 tests plus one Windows directory-symlink skip with 87% coverage, strict MkDocs, hygiene, and
  range whitespace. `wbc1_reviewed` then completed, reproduced, and rebuilt both reports.
- The reviewed experiment is recorded in `docs/EXPERIMENT_LEDGER.md`. Its decision is `reject`:
  baseline false alerts/year `2.966666666666667`, detection `0.75`; candidate false alerts/year
  `4.2`, detection `0.75`; Brier `0.017341137335170863`. Both selections were nonviable and the
  candidate did not improve false alerts. The baseline remains complete.
- Review also found lower-severity overclaims around rolling-origin language, warmup exposure, PELT
  segmentation evidence, and manifest contents. Prose is corrected and the remaining measurement
  work is tracked in `docs/HARDENING_BACKLOG.md`; it does not change the conservative rejection.
- NOT verified: hosted Linux CI. The official GitHub incident remained critical, with Actions and
  Pages in major outage and most webhook triggers throttled. No missing hosted result is called
  green and neither dependency is merged around it.

## 2026-08-06 - Late producer-contract reconciliation

- Delayed review of product PR #178 found blocking producer-contract gaps. The lab is now synced to
  product head `61f9bdbd2fddcf8cbec7cd6a6f49c00249522374`; the vendored schema SHA-256 is
  `dbeb7c88434dc0849567d3f756304ee25b9f4f0d4b7f985ca16232675bb788b0` and the invented fixture
  SHA-256 is `a05803604ea33cabc72183b5e7db96efe316a4365197256d9b836ed134631da3`.
- The Pydantic consumer mirrors token-aware, case-insensitive person/performance exclusions across
  dot, underscore, and hyphen separators; the closed interpretation-code vocabulary with required
  `NOT_PERSON_MEASURE`; and the C1 Monday 00:00:00Z week floor. Its generated schema publishes the
  required-code `contains` and C1-midnight conditional; typed validation enforces the weekday.
- Focused pre-state-sync proof passed Ruff, strict Pyright, schema drift, seven contract tests, and
  the full 38-test suite with one declared Windows directory-symlink skip. Final exact-head proof
  is recorded in PR #3 after the state commit.
- The remaining mixed-case/numeric-suffix feature-ID grammar edge and five lower-severity semantic
  refinements are explicitly deferred to product #182 and this repository's hardening backlog.
  Hosted Linux proof remains absent during the declared Actions incident and is not called green.
