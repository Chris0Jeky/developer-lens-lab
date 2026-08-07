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
- Exact clean code/state head `fd094995353dbacee7be40d4cf982f17c3dda3af` completed
  `wbc1_contract_final`, reproduced every recorded artifact byte-for-byte, and rebuilt both reports.
  It retained the conservative `reject`: baseline false alerts/year `2.966666666666667` and
  detection `0.75`; candidate false alerts/year `4.2`, detection `0.75`, and Brier
  `0.017341137335170863`. The bundle digest is
  `sha256:bb40574ec6284d28f14eb4e76e141d981fec484c01eaba89cd51bc34c1befbe7`; custody is
  `sha256:4177b3cdb85533d990de5e9ea836ad493e0caf479afe797556216d545aef4b5a`; Markdown is
  `sha256:f129fd5746f1841e173bad17c80ab966a926d781ebb7c95c7bf3be5fe1697824`; HTML is
  `sha256:d7b8bd1344fa13f76eb65161ee3863bfca24610c0f6ccec47d0a269ec7e13ebf`.
- The first full local pass found only one formatting drift in the changed Python contract. Ruff
  formatted that file; format/lint, strict Pyright, contract drift, and whitespace were rerun green.
  The full proof also passed runtime-only locked installation, context/tasks, 38 tests plus one
  declared Windows directory-symlink skip with 88% coverage, strict MkDocs, and hygiene.
- A delayed PR #3 connector review arrived after the bounded methodology rounds. Its person-shaped
  feature P1 is closed by the canonical contributor/reviewer terms in `fd09499` plus exact hostile
  regressions. Six P2 findings are consolidated in #6: confound observability, run-owned artifact
  lifecycle, workload counts, corrupt-manifest handling, present primary-domain metrics, and
  zero-delay fallback ordering. They do not overturn the already conservative `reject` and are not
  silently dropped or expanded into another fix loop.

## 2026-08-07 - Exact merged producer reconciliation

- Developer Lens ResearchPack PR #178 merged as
  `be9c2451e983e776850c4cd4700cc8c234ea5e14` after exact-head hosted run `31140838615` passed.
  The product schema SHA-256 is
  `7734aad6635f840d16d8dda893f885911401fb32c36a51825d2d142eb6d3c2a2`; the invented fixture is
  `f2bb3da8407633c44dafb7177dccd8fb085f3838f1fc0813d076264afd59e3b4`. The lab sync records that
  merge commit and both byte checksums as provenance only.
- Before the final sync, the isolated lab steward checkout passed the locked runtime-only CLI
  install, Ruff format/lint, strict Pyright, context/task/schema checks, 38 tests plus one declared
  Windows directory-symlink skip with 88% coverage, strict MkDocs, hygiene, and range whitespace.
  Focused post-sync producer/runtime checks passed 9 tests plus the same declared skip.
- Clean synchronized head `b4cdb364b753046588d3bd6c80e027c665b482fa` ran `wbc1_demo`, reproduced
  every stored artifact byte-for-byte, and rebuilt both reports. The exact reviewed result did not
  move: baseline false alerts/year `2.966666666666667` and detection `0.75`; candidate false
  alerts/year `4.2`, detection `0.75`, and Brier `0.017341137335170863`; both selections remain
  nonviable and the decision remains `reject`.
- The new EvaluationBundle digest is
  `sha256:71fd7c90daa794e58424a697984d89aba9f1166cc3af28e7ef2a1ebebb715a29`; custody is
  `sha256:036f62f5f9ade272eba907513e7ab0bbef4a888bb1d86f8ae6e401aebd5c8238`; Markdown is
  `sha256:2c0a638711409122b984abd9d24dd1382f74d05f82508979621ec35e0c21848c`; HTML is
  `sha256:53cf6c19906b3b478be2755b3fc3277364cf27fc7f5bef40c524c50970b78df1`.
- Product #182 and lab #6 retain the bounded non-demo hardening backlog. No real data, corpus,
  additional candidate, product claim, or promotion was added. Lab PR #3 still requires its final
  push, exact-head hosted CI/review sweep, and merge.

## 2026-08-07 - Principal demo preflight (preflight only)

- Exact preflight code head: `b865d6951e915ffedb4af512a0a673501d12e171`. This entry records
  local preflight evidence only; it is not a hosted result, product fixture commit, product merge,
  lab PR/merge, or canonical final run.
- The preflight used the `wbc1_demo_preflight` shape and retained the C0 invented-data boundary:
  54 system series, 5,616 weekly opportunities, 5,346 observed and 270 absent; representative
  scenarios `no_change`, `level`, and `parser_shift`, with 104 points per case.
- The honest decision remains `reject`. Baseline metrics are false alerts/year
  `2.966666666666667`, detection `0.75`, median delay `2`, confound rate `0.5`, and measured
  threshold `2.5` marked nonviable. Candidate metrics are false alerts/year `4.2`, detection
  `0.75`, median delay `1`, confound rate `0.5`, Brier
  `0.017341137335170863`, and measured threshold `0.05` marked nonviable. The deterministic
  baseline remains the complete fallback; no promotion is implied.
- Preflight provenance records the product contract prefix `2fd1637`, schema digest prefix
  `86cf53a`, ResearchPack merge reference `be9c245`, and compatibility fixture digest prefix
  `sha256:847e3c`. These are provenance notes only; no product fixture commit or product merge is
  claimed by this entry.
- Preflight report references are Markdown digest prefix `3d47b2` and HTML digest prefix `4409373`.
  Rich report generation, the explicit demo export path, and report materialization are local
  behavior checks. Issue #6 remains deferred; product UI code is outside this vertical.
- NOT verified: hosted CI, bounded review/publication gates, and a canonical final run.

## 2026-08-07 - Parallel final-repair precursors (superseded by integration)

- Product contract commit `b48fea579936671397a0486ae7a0342197ee6e4b` remains pinned at schema
  SHA-256 `634b0cc7a0c3dbcefe8b9cf258e157695beae06d08cc9d02bb781a4267f633ef`.
- Lab commit `5c79236beb0a0b25819f14510b79bb15813d7337` added equivalent semantic
  acceptance with eleven structural-valid mutation regressions. Parallel commit
  `b30b22909c9ea44d64bebe9dccf82b8735302d76` made named export publication atomic over a final
  symlink and changed premature `verification.local: passed` evidence to honest `not_run`.
- Both precursor heads passed their scoped local proof and independent review, but each canonical
  fixture predates the other repair. Their fixture and report hashes are therefore superseded and
  must not be copied into the product. The integrated merge head requires one fresh canonical run,
  byte pin, exact-head CI, and final review before either PR can merge.
- The scientific result remains the conservative `reject` with no real/private input, full-run
  publication, lab-owned product UI, additional method, or model promotion. Issue #6 remains
  explicitly deferred.

## 2026-08-07 - Integrated canonical MethodTrial producer

- Merge commit `0ef193070a9b80b81cef5a1710a1d65e0b271c15` contains both final repair
  lines: equivalent cross-field semantic acceptance plus atomic final-path export with honest
  `verification.local: not_run`. It also records the owner's bounded q-4 integration approval
  without authorizing model promotion, real data, or a general product claim.
- A fresh detached checkout at that exact producer passed the locked runtime-only installation,
  locked sync, Ruff format/lint, strict Pyright, context/task/contract checks, 53 tests with three
  declared Windows symlink skips and 87% coverage, default smoke reproduction/report, strict
  MkDocs, hygiene, and range whitespace.
- Canonical `wbc1_demo` then passed benchmark, byte reproduction, export, and report. The LF export
  is 167,936 bytes with SHA-256
  `afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9`; the stored view object is
  `sha256:30768b506607c05fe186fbd3db51ddae7ba47f2d0cf58a5ade509f4295736a88`.
  EvaluationBundle, custody, ResearchPack, Markdown, and HTML digests are respectively
  `sha256:e925c8ac44d914ce0003ef218d90187535eedfef3eb8d436a3c9a135e3d1a3a9`,
  `sha256:036f62f5f9ade272eba907513e7ab0bbef4a888bb1d86f8ae6e401aebd5c8238`,
  `sha256:bd96e45eed454b0ed42f37fa0c518f3b2883816aab876bd6e2e5718c9e24fb90`,
  `sha256:f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8`, and
  `sha256:22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29`.
- The result is unchanged: seven gates fail/fail/pass/pass/fail/pass/pass, decision `reject`, and
  rolling-median/MAD fallback retained. Product PR #187 later merged at `7b22491`; correction commit
  `1e1214d` pins these integrated bytes on `codex/method-trial-final-evidence`. Its PR/hosted gate and
  merge, the merged-contract recheck, and lab PR #8 remain live gates at this record.
- Late exact-head review then found one direct regression: `run_benchmark` attempted the smoke-only
  MethodTrial composition for opt-in full benchmarks, whose deliberately different counts fail the
  C0 presentation contract after reserving a single-use scope. The bounded repair keeps the rich
  MethodTrial view and reports on smoke runs only, restores the existing generic EvaluationBundle
  report/reproduction path for full runs, and records no MethodTrial artifact for a full run. A
  focused regression test forbids MethodTrial composition on that path; the full local gate passed
  with 54 tests and two declared Windows link skips, strict Pyright, Ruff, generated checks, strict
  MkDocs, hygiene, and whitespace. The integrated `wbc1_demo` producer and fixture remain unchanged
  at `0ef1930` and SHA-256 `afcc1ed9`.
