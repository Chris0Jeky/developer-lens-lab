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

## 2026-08-07 - Full-run presentation boundary repair

- Late exact-head review then found one direct regression: `run_benchmark` attempted the smoke-only
  MethodTrial composition for opt-in full benchmarks, whose deliberately different counts fail the
  C0 presentation contract after reserving a single-use scope. The bounded repair keeps the rich
  MethodTrial view and reports on smoke runs only, restores the existing generic EvaluationBundle
  report/reproduction path for full runs, and records no MethodTrial artifact for a full run.
- A focused regression executes and reproduces the complete non-smoke dataset while forbidding
  MethodTrial composition. The exact merged local gate also passed with 54 tests and three declared
  Windows link skips, strict Pyright, Ruff, generated checks, strict MkDocs, hygiene, and
  whitespace. The integrated `wbc1_demo` producer and fixture remain unchanged at `0ef1930` and
  SHA-256 `afcc1ed9`.

## 2026-08-07 - Final product correction merge proof

- Product correction PR #190 passed hosted run `31151644253` at exact head
  `1e1214d9df6fa6b79c1e5743cb8f179f02331fd6` and merged with preserved history as
  `8de65a22fe8a65ced893278a4e5a6835d778d65c`. Focused/full product checks, hosted CI, and fresh
  independent review found no CRITICAL/HIGH blocker.
- The aging-floor claim in the original record was false. PR #190 became ready at
  `2026-08-07T05:45:32Z`, no connector review/comment/thread arrived, and it merged at
  `05:57:09Z`, 3 minutes 23 seconds before the standing 15-minute post-ready fallback ended at
  `06:00:32Z`. This is process noncompliance, not a passed gate, known code defect, or precedent for
  weakening future review timing. The correction is also recorded on product PR #190.
- From the lab, `contracts sync-method-trial --check-only` accepted that exact product merge without
  rewriting the recorded producer provenance. A fresh detached `wbc1_demo` run at producer
  `0ef1930` passed benchmark, byte reproduction, export, and report; its 167,936-byte LF export was
  directly identical to the merged product fixture at SHA-256 `afcc1ed9`.
- The product byte/contract dependency is technically closed. Lab PR #8 then passed exact-head
  hosted run `31152499729`, its full local gate and fresh review, all thread sweeps, and the lab
  aging floor; it merged with preserved history as `1ac32f42e0f6cec57f6ce5ff37fd01e175a4b009`.
  Initial post-merge sweeps found no late feedback; the only later product comment is the explicit
  timing correction above. No model promotion, real/private input, public corpus, additional
  method, or product #174 work is authorized by this evidence.

## 2026-08-07 - Post-merge task-card closure

- A late exact-head connector review posted after evidence-correction PR #9 merged and found a
  direct cold-start contradiction: `CURRENT_STATE.md` said the vertical was complete while the
  authoritative task source still marked `LAB-WBC1-01`, `LAB-WBC1-05`, `LAB-BRIDGE-01`, and
  `LAB-DEMO-01` `IN_REVIEW`.
- Those four delivered C0 cards are now `DONE`, their generated Markdown/JSON indexes are refreshed,
  and the active horizon is empty. Owner-gated corpus cards and the parked data-quality card remain
  unchanged; this closure authorizes no follow-on work.

## 2026-08-07 — Dual-runtime Claude harness

- PR #11 merged with merge commit `c159d96f` after two bounded review rounds (one independent
  fresh-context adversarial pass, two Codex rounds triaged). `CLAUDE.md` became the shared canon;
  `AGENTS.md` slimmed to a thin Codex adapter with an inline protected-data summary; the Claude
  runtime gained committed settings, the `developer-lens-lab-continuation` skill, and pinned
  agents `dll-implementer`/`dll-reviewer` (Opus 4.8 high) and `dll-mechanic` (Sonnet 4.6 high).
- `dllab context verify` now requires the Claude files and the three agent-pin files to exist
  (existence only — it does not parse pin frontmatter), parses committed settings as JSON,
  rejects committed or tracked `bypassPermissions`/`settings.local.json`, and asserts the canon
  anchors (adapter names the canon; canon carries the protected-data rule).
- Same PR untracked the `.coverage` run artifact that had been committed directly to `main`
  (`71db5f1`); CI's `pytest --cov` rewrote it and broke the WB-C1 clean-worktree gate — `main`'s
  red lane healed at the merge (hosted gate green at `91b3505` pre-merge and at `c159d96f`).
- Verified: hosted `Prove the lab` green at `91b3505` and at the merge commit; local ruff,
  pyright, pytest (54 passed, 3 pre-existing symlink skips), strict MkDocs, hygiene.
- Deferred (tracked): #12 skill-copy parity markers, combined context budget, settings-guard
  scope. (#13 deny-rule parity landed 2026-08-07 — see the next entry; #12 landed 2026-08-07 via
  PR #17 — see the final entry.) No research vertical, corpus, model, or gate activation is
  authorized by this evidence.

## 2026-08-07 — Protected-data deny-rule parity

- PR #15 (`claude/settings-deny-dllab-parity`) closes #13. Committed `.claude/settings.json` gained
  `permissions.deny` `Read` rules for `.dllab/**`, `artifacts/**`, and `reports/generated/**`,
  mirroring developer-lens PR #191 (confined store + gitignored generated output). `dllab context
  verify` now asserts those rules via `verify_settings_deny()` (`REQUIRED_SETTINGS_READ_DENY`), so
  removing a required rule fails the gate — the protected-data rule's read-scoping is harness-
  enforced for those sinks, not prose-only.
- Scope is deliberately the product's: only the `Read` tool on those three sinks. Broader coverage
  (`Grep`/`Glob`, `.env`/keys, scattered `*.parquet`/`method-trial-view.json`) is tracked in
  `docs/HARDENING_BACKLOG.md`, not claimed here. Runtime precedence of a committed `deny` over a
  machine-local `settings.local.json` `bypassPermissions` default is NOT verified (outside a
  repo-level static check).
- Verified locally at the reviewed head: ruff format/check, pytest 60 passed / 3 pre-existing
  symlink skips, `dllab context verify`, hygiene, `tasks`/`contracts check`, and `pyright` scoped to
  the changed files (0 errors). NOT verified locally: repo-wide `uv run pyright` (the local venv
  reports pre-existing `typer.testing` import-resolution errors — an environment gap, not this
  change) and `uv run mkdocs build --strict` (this seam does not touch it). The full canonical gate,
  including repo-wide pyright and strict MkDocs, was proven green by hosted `Prove the lab` at the
  reviewed and merged heads — so this milestone is fully gated, but the full gate was hosted, not
  local.
- Review: two-lens fresh-context adversarial pass (security-efficacy + code-correctness, both SHIP,
  no CRITICAL/HIGH) plus two Codex comments — the stale deferred-entry note fixed pre-merge in
  `33af8d2`, and this verification-wording correction landed post-merge as a doc-only follow-up.
  Findings triaged once; the coverage residual is tracked, not fixed here. Dependabot alerts triaged
  separately on #5 (not reachable / tooling-blocked). No research, corpus, model, or gate activation
  is authorized by this evidence.

## 2026-08-07 — Harness follow-ups: SKILL.md parity, context budget, settings-guard scope

- PR #17 (`claude/harness-followups-12`) closes #12 — the three non-blocking findings from PR #11's
  review. `dllab context verify` gained two pure checks in `src/developer_lens_lab/context/verify.py`,
  both wired into `verify_repository`: `verify_skill_parity()` and `verify_context_budget()`.
- `verify_skill_parity()` guards the byte-identical `## Protect evaluation integrity` section shared by
  the `.claude` and `.agents` `SKILL.md` copies. Both copies now wrap that section in
  `<!-- shared:evaluation-integrity start/end -->` markers (only marker lines added; enclosed wording
  unchanged). The check requires exactly one ordered pair per file and fails if the two enclosed blocks
  diverge, so editing one copy without the other now fails the gate.
- `verify_context_budget()` enforces `tier.json` `budgets.standing_context_tokens` (2500) against a
  deterministic ~4-chars/token estimate of `AGENTS.md`+`CLAUDE.md` combined (6329 chars ≈ 1583 tokens
  ≤ 2500). An absent budget is skipped; a declared-but-invalid one (non-positive / wrong type) fails
  loudly rather than silently disabling the check. The per-file 100-line cold-start cap is unchanged.
- Settings-guard scope: documentation-only. One `docs/HARDENING_BACKLOG.md` bullet reconfirms, as
  tracked non-expansion (law 8), that the committed-settings guard rejects only the `bypassPermissions`
  substring and the three `Read` deny rules and does not inspect `hooks` blocks, `permissions.allow`
  wildcards, or `.mcp.json`; `.claude/settings.local.json` content is unscanned while a `git ls-files`
  tracked-status guard blocks committing it. No guard code was expanded.
- Review: two-lens fresh-context adversarial pass (parity + budget/boundary, both no-blocking) plus
  Codex. Fixed pre-merge — the malformed-budget fail-loud gap and the duplicate-marker false-pass,
  plus doc-precision wording. Declined/tracked — the sibling "Default to invented fixtures…" shared
  paragraph is also identical but unwrapped, filed as #18. Findings triaged once; no CRITICAL/HIGH.
- Verified locally at the reviewed head via `.venv` (no uv on host): ruff format/check, pyright scoped
  to the changed files (0 errors), pytest (69 passed / 3 pre-existing symlink skips; 17 context tests),
  `dllab context verify`, hygiene, strict MkDocs, doctor. Repo-wide pyright NOT run locally
  (pre-existing `typer.testing` import-resolution errors — an environment gap); hosted `Prove the lab`
  covers the full gate at the reviewed/merged heads. No research, corpus, model, or gate activation is
  authorized by this evidence.

## 2026-08-07 — Context-verify hardening follow-ups (#18, #19)

- Batch PR (`claude/ctx-hardening-18-19`) closes the two non-blocking follow-ups spun off from the #12
  review: #19 (Codex round-2) and #18 (fresh-context reviewer). Harness/tooling only; T1/C0 posture
  unchanged; no owner gate crossed.
- #19 — `verify_context_budget` now distinguishes an absent `budgets` key (legitimately unenforced →
  `[]`) from a present-but-malformed `budgets` container (string/list/null/number/bool → the failure
  `"tier.json budgets must be an object to declare a standing-context budget"`). This closes the
  container-level twin of the value-level gap fixed in `de061c7`; `_verify_tier` validates only
  top-level keys, so this is the sole reporter and cannot double-report.
- #18 — the SKILL.md parity check now guards *every* named shared block, not just the
  evaluation-integrity one. The byte-identical "Default to invented fixtures… closed first." paragraph
  is wrapped in `<!-- shared:protected-data-defaults start/end -->` markers in both copies;
  `SHARED_SKILL_MARKER` becomes `SHARED_SKILL_MARKERS`, the per-marker logic is factored into the
  public `verify_one_shared_block(root, marker)` (message strings label-parameterized so the
  evaluation-integrity wording is byte-preserved), and `verify_skill_parity` loops over both. Adding a
  future shared block needs only its marker name here plus the two wrapping lines.
- Review: one fresh-context adversarial pass (no blocking defects). Its lone LOW recommendation — make
  the test-imported helper public rather than carry a `# pyright: ignore[reportPrivateUsage]` — was
  applied inline (pure rename, no logic change, so no new review pass owed). Residual #18/#19 follow-up
  #19-container consistency is fully resolved by this slice; no new tracked debt.
- Verified locally against the worktree source via `.venv` (no uv on host; PYTHONPATH pinned to the
  worktree `src` because the editable install otherwise resolves to the main checkout): ruff
  format/check, pyright scoped to the changed files (0 errors), full pytest (73 passed / 3 pre-existing
  symlink skips; 21 context tests), `verify_repository(.)` OK, strict MkDocs, hygiene, doctor. Repo-wide
  pyright NOT run locally (pre-existing `typer.testing` import errors); hosted `Prove the lab` covers the
  full gate at the reviewed/merged heads. No research, corpus, model, or gate activation is authorized.

## 2026-08-07 — BOCPD missing-week semantics clarified post-hoc (#4)

- Branch `claude/bocpd-semantics-4` closes #4 by making the BOCPD missing-week run-length semantics
  explicit. Coordinator methodology decision: **observed-sample semantics** (see the
  `docs/EXPERIMENT_LEDGER.md` post-hoc clarification entry of the same date). This documents the
  as-implemented behavior of the already-completed runs; it is NOT a preregistration. No detector
  behavior change.
- `src/developer_lens_lab/wbc1/methods.py`: comments only — on `BocpdParameters.expected_run_length`
  (denominated in observed samples; canonical Adams–MacKay run-length-in-observations) and at the
  `bocpd_scores` skip site (a censored week is a deliberate no-op on the posterior). No logic, default,
  signature, or field-name change; `parameters_sha256` custody surface untouched.
- `docs/RESEARCH_PROGRAMME.md`: documents the observed-sample unit as a post-hoc characterization of
  existing behavior, scoped precisely to the run-length/hazard posterior (score emission still begins
  after a fixed calendar-week `warmup`).
- `tests/test_wbc1_methods.py`: adds `test_bocpd_missing_block_is_observed_sample_equivalent`, a
  characterization lock — a contiguous missing block yields bit-identical post-gap scores to the
  gap-deleted series; it would fail if the detector were changed to advance across censored weeks.
- Review: one fresh-context adversarial pass (no blocking; confirmed the test is a genuine bit-identical
  lock and methods.py is comments-only). Its LOW nit — scope the "equivalent to deleting samples" claim
  to the posterior given the calendar-indexed warmup gate — was applied to the clarification wording.
- Verified locally against the worktree source via `.venv` (PYTHONPATH pinned; no uv on host): ruff
  format/check, full pytest **70 passed / 3 pre-existing symlink skips on the pre-integration branch
  (base d3ddf49)** — at the integrated head this is 74 (the preceding entry's 73 plus the one new lock),
  covered by hosted `Prove the lab`; the "70" figure was the pre-rebase count and did not reflect the
  merged head. Downstream `test_wbc1_evaluation`/`test_wbc1_runner`/`test_method_trial_export` green
  UNCHANGED (proving zero byte/behavior change). Repo-wide pyright NOT run locally (pre-existing
  `typer.testing` import errors). No research, corpus, model, or gate activation is authorized by this
  evidence.
- **[Correction, 2026-08-07]** Reframed from "preregistered/preregistration" to a post-hoc clarification
  and corrected the pre-integration test count, per the PR #21 Codex review (P1 + P2). Landed as a
  follow-up on branch `claude/fix-4-prereg-framing`.

## 2026-08-07 — MethodTrial fallback labels made contract-faithful (#7)

- Branch `claude/fallback-labels-7` closes #7. Discovery + a fresh-context implementer STOP corrected
  the issue's premise: the vendored MethodTrialView v1 schema pins each representative case's
  `scenario_code` to a `const` (case[1]=level, case[2]=parser_shift), validated before any Python
  check — so threading a fallback `scenario_code` (the issue's original ask) is contract-invalid.
- Coordinator methodology decision: **canonical-or-fail-export.** `_build_cases`
  (`wbc1/export.py`) narrows the planted/confound representative preferences from multi-item
  (`("level","slope",...)` / `("parser_shift","coverage_gap",...)`) to the single contract-required
  canonical scenario (`("level",)` / `("parser_shift",)`), so `_select_series` raises its existing
  missing-role `ValueError` when the canonical scenario is ineligible instead of silently
  substituting a non-canonical series the case could only mislabel. `_select_series`/`_case_points`
  bodies untouched; `contracts/method_trial_view.py` and the vendored schema untouched.
- Byte-stable: the dense canonical demo still has eligible `level`/`parser_shift`, so selection and
  every composed byte are identical — the deterministic-export and vendor-snapshot (`sha256:634b0cc7…`,
  `product_commit b48fea57…`) pins pass UNCHANGED. Added two fail-export tests (planted + confound
  ineligible-canonical paths); the test file's existing broad `# pyright:` header gained
  `reportPrivateUsage=false` for the two internal-helper imports (consistent with that file's posture).
- Review: one fresh-context adversarial pass (no blocking). It confirmed the fix resolves the mislabel
  (selection can only return a series whose scenario_code matches the const label) and flagged one
  contract-forced, pre-existing imperfection: the view still DECLARES a multi-item
  `planted_preference`/`confound_preference` (schema-pinned consts) the code no longer honors past
  index 0. That is a product-contract tension (const scenario_code vs declared fallbacks), tracked as
  a cross-repo follow-up, not fixable in the lab.
- Verified locally against the worktree source via `.venv` (PYTHONPATH pinned; no uv on host): ruff
  format/check, full pytest (71 passed / 3 pre-existing symlink skips; the +2 are the fail-export
  tests) with the byte pins green UNCHANGED, `verify_repository(.)` OK. Repo-wide pyright NOT run
  locally (pre-existing `typer.testing` import errors); hosted `Prove the lab` covers the full gate.
  No research, corpus, model, or gate activation is authorized by this evidence.

## 2026-08-08 — Research governor control plane and owner constitution v2 (LAB-GOV-01)

- Branch `claude/governor-bootstrap-v2` seeds the durable research governor commissioned by the
  owner mandate v2 and governor bootstrap v1. Live-truth reconciliation first: the prepared
  baseline (PR #14, #12/#13 open) was stale — #12/#13/#7/#4 were already closed by PRs #15–#26;
  the genuinely missing pieces were the governor surfaces and the constitution unpacking.
- New authority surfaces: `docs/OWNER_CONSTITUTION.md` (unpacked binding owner decisions: locked
  invariants, layered people/team research, federated product–lab boundary, real-data and
  raw-content authorization with the secrets prohibition absolute, focus allocation, condensed
  decision register); `.agent-harness/governor.json` (machine-readable `dllab-governor.v1`
  policy: routing, risk classes, lanes, activation preconditions, review gates, self-evolution
  locks — JSON not YAML because the host cannot re-lock dependencies); seven
  `docs/agent-system/` protocols (governor loop, work classes, experiment/dataset/maintenance/
  idea protocols, prompt library incl. Research Governor Lite).
- Reconciled: `PRODUCT_BOUNDARY.md` and `DATA_POLICY.md` rewritten to the layered charter
  (C0–C4/P/X target classes; only C0 operative until the activation preconditions are
  mechanically true — tier stays truthfully T1/`sensitive_data=false` while the repo holds C0
  only); `HUMAN_TODO.md` q-1/q-2/q-3/q-5/q-6 closed with their binding constitution answers and
  new open owner items q-7–q-12 added; CLAUDE.md/AGENTS.md pointers updated inside the
  100-line/2500-token budgets (~1748 tokens combined after edits).
- Model pins: `dll-implementer`/`dll-reviewer` repinned `claude-opus-4-8` → `claude-opus-5`
  (runtime-validated by actually spawning the repinned implementer for this card's code);
  `dll-mechanic` stays `claude-sonnet-4-6` per the estate routing ladder.
- Code: `tools/cards.py` → `lab-task-programme.v2` (six-card cap removed per A4=OPEN; BACKLOG
  status; wave dependency-closure kept; scheduled cards LAB-GOV-01, LAB-WBC1-06 (=PR #24 lane),
  LAB-ACT-01, LAB-REL-01, LAB-SURV-01 (#174), LAB-CONTRACT-03 (#23); corpus cards OWNER_GATED →
  BACKLOG gated on LAB-ACT-01). `context/verify.py` gains `verify_governor`: required governor
  files, schema/key checks, authority-file existence, haiku prohibition, the ten hardcoded
  never-self-relax invariants, focus axes, and agent-pin coherence against `.claude/agents/`
  frontmatter. New tests in `tests/test_context.py` and `tests/test_tasks.py`.
- Review rounds (ceiling 2, both spent): round 1 (fresh-context adversarial, 0 CRITICAL/HIGH)
  hardened enforcement — routed-model prohibition over `model`/`models` keys, loud pin-role
  failures, gate-value floors (≥7 activation items, aging ≥15, fix rounds ≤2), plus the q-9
  owner-scope precondition, skill-block gate pointer, and CLAUDE.md external-model clause;
  LOWs tracked as #27. Round 2 (Codex, 3 P1 / 5 P2) pinned values by identity — authority
  paths bounded inside the repo, lane statuses hardcoded (O/C stay
  `authorised_awaiting_preconditions` until LAB-ACT-01), precondition token identity, the
  binding 7/5/3/2/0 focus weights, non-numeric review gates (four fresh-review triggers +
  sweep=True) — and fixed the q-9 circularity and lane-P real-data wording.
- Verified locally at the final head via `.venv` (no uv on host): ruff format/check, focused +
  full pytest (101 passed / 3 pre-existing symlink skips), focused pyright on the changed code
  files (0 errors; repo-wide pyright has pre-existing venv import-resolution noise — hosted
  `Prove the lab` remains the arbiter), `tools/cards.py --check`, `dllab context verify`,
  `mkdocs build --strict`, `verify_hygiene.py`, `dllab doctor`. This entry authorizes no
  research, collection, model call, or lane activation — activation preconditions still gate
  every non-C0 lane.

## 2026-08-08 — WB-C1 correctness fixes reconciled on PR #24 (partial #6 closure)

- Branch `claude/lab-wbc1-correctness-6` (PR #24) carries four WB-C1 correctness fixes against the
  P2 findings consolidated in issue #6 from the delayed original PR #3 connector review. The
  integration merge `6d71cdc` is a clean merge of `origin/main` `f14da50` over the four authored
  commits `f044b36`, `a11872d`, `6b9ebf6`, and the `acc3b95` format pass.
- Resolves original finding 2 from #6 (run-owned validation artifacts): `_store_research_pack` (`wbc1/runner.py`)
  no longer writes a second copy of each `coverage`/`repository_week` Parquet into a shared
  pack-id scope. `validate_pack_artifacts` (`validation.py`) gains an optional `scope` argument
  defaulting to `pack.pack_id`, so standalone `dllab pack validate` keeps its behavior, while the
  runner validates against the run-owned scope — `invalidate_scope(run_id)` now reaches every
  artifact a run wrote instead of leaving copies in a never-invalidated scope.
- Resolves original finding 4 from #6 (controlled error for malformed manifests): `reproduce_run` and `build_report`
  read every required run-manifest field through new `_require_field`/`_require_ref` helpers, and
  `_assert_reproduced_reference` wraps its own reference validation. A missing key or a malformed
  artifact reference now raises a controlled `RunnerError` naming the field, instead of an
  uncaught `KeyError` or a raw pydantic `ValidationError`.
- Resolves original finding 5 from #6 (present primary-domain metrics): `decide_benchmark` (`wbc1/evaluation.py`)
  gains a leading `PRIMARY_DOMAIN_METRICS_PRESENT` gate requiring both baseline and candidate
  `detection_rate` to be actually present. A partition that planted no true changes reports an
  absent detection rate, which the downstream `or 0.0` coercions would otherwise let through as a
  `benchmarked` verdict resting on unmeasured evidence. Missing evidence stays explicit, not zero.
- Resolves original finding 6 from #6 (numeric zero-delay ordering): the `select_threshold` tie-break replaced
  `median_detection_delay or float("inf")` with an explicit `is not None` test, so a genuine
  median detection delay of `0` ranks as the best tie-break rather than collapsing to the worst.
- Still mapped, not closed by this lane: finding 1 (confound observability) and finding 3
  (threshold-selection workload counting). Both would move the generator or the recorded
  EvaluationBundle, custody record, or digests, and so depend on the methodology and run handling
  already recorded in the entries above rather than fitting this correctness lane. They remain
  open in #6. The later PR #8 follow-up set in #6 is untouched and also remains open.
- Scope held: C0 invented data only; five changed files (`validation.py`, `wbc1/evaluation.py`,
  `wbc1/runner.py`, `tests/test_wbc1_evaluation.py`, `tests/test_wbc1_runner.py`) carrying five
  new regression tests. No canonical run was executed, and no recorded run, metric, artifact,
  custody record, or digest moved.
- Verified in an isolated worktree using a worktree-local uv 0.12.3 bootstrap with
  the confined worktree-local project environment configured for the bootstrap (project interpreter Python 3.12.7): locked
  `uv sync --locked --all-groups` left `uv.lock` unchanged, and focused
  `pytest tests/test_wbc1_evaluation.py tests/test_wbc1_runner.py` passed 19 with the declared
  Windows symlink skip. The full gate then passed at this head: `dllab doctor`, `dllab context
  verify`, Ruff format (75 files) and lint, repo-wide strict Pyright at 0 errors/0 warnings, 106
  pytest tests with 3 declared host symlink skips, strict MkDocs, `verify_hygiene.py`, and
  `git diff --check`. Unlike the recent ad-hoc .venv fallback entries above, this worktree-local locked uv environment
  resolved their recorded import-noise caveat for this pass.
- NOT verified: hosted CI and independent review of this exact head are later gates and are not
  claimed by this entry, which authorizes no research, collection, model call, or lane activation.

## 2026-08-09 — Prompt operating system and dual-runtime parity (LAB-GOV-02, issue #33)

- Adopted the cross-repository prompt operating system on the lab side, paired with product issue
  `Chris0Jeky/developer-lens#214`. `.agent-harness/prompt-parity.json` was copied **byte-for-byte**
  from the product reference at commit `30529d4370ba857e4815135ee87fb14f214913a7`; both copies hash
  to `sha256:d2f78a1481cfcc4ba6e6f925d09d1090fc5ffbe69b6ffb444bcdef4b5c740171`. The manifest was
  not recalculated or edited on this side.
- Rewrote `docs/agent-system/PROMPT_LIBRARY.md` around stable markers: the twelve common IDs
  (`DL-P01`…`DL-P12`) in manifest order plus the two lab extensions
  `DL-LX01-LAB-EXPERIMENT-HARNESS` and `DL-LX02-LAB-EVALUATION-REPRODUCIBILITY`, which carry the
  experiment, methodology and reproduction behaviour previously held by the ad-hoc role prompts.
- Both shared block bodies were copied verbatim from the product library and are carried exactly
  once by every active prompt. Measured digests match the manifest exactly:
  `runtime-bootstrap-v1 = 018c0db78a90107022e76a14a03fee5fe3afe5cbf16a7dd26b0b91e3e1839ef6`,
  `friction-tasking-v1 = 56bc9679fc51fd4ff5f05b715c42a96c3201284a6fee1a033524c2ccc55f5a7e`.
- Added `docs/agent-system/CONTINUOUS_WORK_PROTOCOL.md` (repeated governor-loop waves,
  deterministic queue hop, work-while-aging, park-not-nurse, resource-bounded disjoint fan-out,
  anti-manufacture legitimacy test, durable state every hop, no non-C0 lane, and explicit
  policy/budget/tooling/queue stops), the append-only `docs/agent-system/FRICTION_LOG.md`
  (FR-001…FR-005), and the lab-side `docs/agent-system/CROSS_REPO_CONTRACT.md` recording merge
  order product #214 then lab #33.
- Corrected a false operational claim: `MAINTENANCE_PROTOCOL.md` had stated that `uv` is
  unavailable on this host and therefore dependency re-locking is tooling-blocked. The confined
  bootstrap route is proved to run both the locked sync and the full gate, so the text now
  describes that route and the superseded claim is preserved as FR-002 rather than erased.
- Mechanical enforcement added to `src/developer_lens_lab/context/verify.py` with 32 new tests:
  manifest schema/types/lab-entry resolution; code-pinned common and lab extension IDs required to
  equal both the manifest and the Markdown in order; unique markers and exactly one text fence per
  prompt; exactly one digest-matched copy of each shared block per active body under LF
  normalization; the Claude and Codex runtime clauses; fully qualified
  `<owner>/<repo>::HUMAN_TODO.md::q-N` refs; ordered continuous execution/stop marker pairs; and
  redirect/historical classification where declared. Clause tokens are matched **outside** the
  shared blocks, because `CLAUDE.md`, `AGENTS.md` and `Sol/Terra/Luna` also occur inside
  `runtime-bootstrap-v1` and would otherwise let the shared spine satisfy the check for a prompt
  carrying no lab routing clause at all.
- Scope held: C0 invented control-plane work only. No data lane, model, telemetry, credential,
  publication, release/tag, methodology, experiment, holdout, product contract, generated product
  output, or owner-policy value changed. `governor.json` gained prompt/continuous/friction surfaces
  and checks with authority, risk-class, data-lane and review-gate values untouched.
  `.claude/agents` and both continuation skills were deliberately NOT edited in this slice.
- Verified at this head with the FR-001 confined `uv 0.12.3` bootstrap
  (confined worktree-local project environment configured for the bootstrap, project interpreter Python 3.12.7): `uv sync --locked
  --all-groups` left `uv.lock` unchanged; `dllab doctor`; `dllab context verify` passed; Ruff
  format (78 files) and Ruff lint clean; repo-wide strict Pyright 0 errors/0 warnings; full pytest
  **143 passed / 3 declared host symlink skips** (78 of them in `tests/test_context.py`); strict
  MkDocs build; `verify_hygiene.py` passed; `git diff --check` clean.
- NOT verified: hosted CI and independent fresh-context review of this exact head are later gates
  and are not claimed here. The three new agent-system documents are intentionally absent from the
  MkDocs `nav` (INFO only; the strict build still exits 0) because `mkdocs.yml` is outside this
  card's owned paths; adding the nav entries is a separate one-line slice.
- Merge gate: this branch is prepared and parked. It must not be agent-merged while
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` — the product register's concurrent-writer gate,
  not this repository's own `q-8` — stays open.

## 2026-08-09 — Claude agent-surface fallback and parity enforcement (LAB-GOV-02, issue #33)

- The required `dll-mechanic` write to `.claude/agents` was denied by the Claude runtime, matching
  the product-side occurrence. The bounded fallback was completed by the isolated Codex writer;
  the runtime boundary was not bypassed. FR-007 records both occurrences and the same-hop task.
- Added the pinned `dll-scout` route and enforced the four-agent friction block plus the two-copy
  continuation-friction block in `dllab context verify`. Missing, duplicate, reversed, or drifted
  blocks are fail-closed; the blocks are byte-identical across their required copies.
- Updated the prompt library runtime bootstrap to the exact product reference body and copied the
  product parity manifest byte-for-byte. Lab-specific routing remains outside the shared block.
- Scope remains C0 control-plane only: no research implementation, data/model/telemetry lane,
  credential, generated output, product contract, or owner-policy value changed. LAB-GOV-02 stays
  `IN_REVIEW` and the lab PR remains parked under the cross-repository q-8 gate.

## 2026-08-09 — Post-merge LAB-GOV-02 state reconciliation

- Reconciled the delivered prompt operating-system milestone: lab PR #35 merged at
  `bba0c18261c0a2b77332a0408f63b10c774c91f4` and closed issue #33, so LAB-GOV-02 is `DONE` in the
  task source and its generated indexes. This records the merged result only and does not infer
  who operated GitHub.
- Reconciled the distinct product concurrent-writer gate from direct owner decision and
  clean-session evidence recorded through product PR #223 at
  `877f1ca07ccee014c0adf50925f989815e6bc7f1`. The product q-8 closure does not alter
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8`, the real-study public-transformation gate,
  which remains open in `HUMAN_TODO.md`.
- Joint release is reaffirmed but no tag, release, data/model/telemetry/credential/publication
  lane, or additional owner gate is authorized.
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)` and
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11` still block tags; the separate Code of
  Conduct inbox has a pending address under `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10`, and
  CLA plus all other owner choices remain deferred.
- Exact next safe slice: LAB-REL-01 isolated dependency triage for issue #5. Licence, community,
  packaging, and release-asset work remain separate slices.

## 2026-08-09 — Patched dependency bounds for LAB-REL-01 (issue #5)

- Raised the direct runtime constraint from `pyarrow>=21,<23` to `pyarrow>=23.0.1,<24` and the
  development constraint from `pytest>=8.4,<9` to `pytest>=9.0.3,<10`, then regenerated the locked
  resolution with the confined uv 0.12.3 bootstrap. The lock moves only `pyarrow` 22.0.0 to 23.0.1
  and `pytest` 8.4.2 to 9.1.1; no transitive package changed.
- Integrated Lab main merge `faa36c6cb193af4a72d750ed557c7ac9719c2430` before final proof. The
  dependency change still touches only `pyproject.toml` and `uv.lock`; this append-only entry is the
  required durable evidence record. The corrected bootstrap instructions already landed in the
  maintenance protocol and were not rewritten here.
- Verified at combined head `2bc4f9fe490ce0a6f9aac04ffe35d0813a2fc048`: locked all-group sync;
  Python 3.12.7 imports reporting pyarrow 23.0.1 and pytest 9.1.1; doctor; context verification;
  Ruff format and lint; strict Pyright with 0 errors, warnings, or information; full pytest with
  149 passed and 3 declared Windows symlink skips; strict MkDocs; repository hygiene; and a fresh
  invented-only WB-C1 smoke run whose deterministic reproduce and report commands passed. Generated
  artifact contents were not inspected.
- NOT verified until the branch is published: hosted exact-head CI/review and live Dependabot alert
  closure. The existing Material-for-MkDocs upstream warning and three unnav'ed agent-system pages
  remain non-blocking; no opportunistic documentation-toolchain upgrade was attempted.
- Scope held: no Python-support, contract, methodology, data/model/telemetry, credential,
  publication, release, tag, or owner-gate change. After this dependency slice lands and alert state
  is refreshed, the next separate pre-tag #29 deliverable is licence/package identity metadata.

## 2026-08-09 — Dependency remediation merge and alert closure (LAB-REL-01, issue #5)

- PR #38 reached final head `4ebb1049ddb831dc7ff76f5a0050e52bdf37f40c`; hosted Check run
  31296773324 succeeded on that exact head, the independent review was merge-sound, and the PR
  merged as `f893f576f71202375fe93e8c7d9c02e54fbaf08a`.
- A post-merge GitHub Dependabot API refresh returned zero open alerts. Issue #5 was then closed at
  05:46Z with the exact-head, check, merge, and alert evidence. The release curator still owes a
  fresh Dependabot read at the eventual release head.
- This entry supplies the evidence that the preceding append-only entry explicitly left NOT
  verified while the branch was unpublished. No earlier ledger wording was rewritten.
- The PR #38 post-merge sweep found no reviews, inline comments, or issue comments. The next
  separate issue #29 deliverable is licence/package identity metadata; no data, model, telemetry,
  credential, publication, tag, or owner-gate state changed here.

## 2026-08-09 — Distinct-signoff prompt and friction closeout (LAB-REL-01)

- Lab PR #37 was archived at `4a044dcec134cda313cffb7087389f64d28fe8c9` after two fix rounds; its
  unresolved HIGH thread remains provenance and received no third fix commit. Replacement PR #42
  changed only DL-P09 at final head `e290d1b94aff9f39de677fd80670f4f9e8f15227` and merged as
  `38ac2eb14c8c9ba742b5f269b7022c7e549b7a5d`.
- PR #42 hosted run `31299725193`, job `93210447311`, passed on the exact head. Fresh review found no
  causal CRITICAL/HIGH defect; the sole connector P2 about future bounded dependency residuals was
  tracked on issue #34 and resolved without a fix commit. The T+3:54 post-merge sweep was clean.
- Friction PR #41 integrated that base, passed hosted run `31300174204`, job `93211576790`, at final
  head `3604e301a5e9930e56edce193ea293698a4870bd`, then merged as
  `178bd6d695119b74294a8fd6fbe46f54577e49b2` after fresh merge-sound review and complete thread
  triage. Its known FR-001 wording P2 stays tracked on issue #34 without another fix.
- `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13` now owns removal of the two escaped bootstrap
  directories. Their names were confirmed present without content inspection; cleanup remains
  NOT verified and does not block C0 release preparation.
- Exact next slice is the already-open licence/package identity PR #40, followed by the prepared
  community-files branch. No owner sign-off, tag, publication, data/model/telemetry activation,
  credential or protected/generated operational content moved in this closeout.

## 2026-08-09 — State and package-identity closeout (LAB-REL-01)

- State PR #39 reached final head `b36bbadd0365a8958ba741e27c2e36e9458237be`; hosted run
  `31300971426`, job `93213564502`, passed, fresh review was merge-sound, and it merged as
  `4f355f1e58e1eca1191f899f1fc4354af8a23a00`. Its delayed connector P2 distinguished durable
  friction records from durably installed remedies; the bounded wording repair landed through the
  next slice and the thread was resolved.
- Licence/package PR #40 integrated that base, added the canonical AGPL-3.0-only text and package
  identity, and reached final head `7d5610d2280e900d9e2c10c6304455830147ffcd`. Its locked/full local
  gate passed with 150 tests and 3 declared Windows symlink skips; hosted run `31301396559`, job
  `93214649991`, passed; fresh review was merge-sound; and it merged as
  `d203461c023e1661140a1fef38a0f4b68e3454b2`.
- PR #40 also repaired the PR #39 wording P2 and recorded the seventh FR-001 tooling occurrence.
  The exact built-artifact installation guard remains a separate non-credential package-smoke task
  under issue #29; no registry, credential, upload, release, or tag action was opened.
- Exact active slice is now community scaffolding and its bounded contribution policy. The public
  contact-request surface is neutral and warns that the issue and requesting GitHub account are
  public; it invents no inbox or monitoring promise. The prepared changelog remains the next
  separate slice, and every non-C0 or owner-gated lane stays closed.

## 2026-08-09 — Community scaffolding closeout (LAB-REL-01)

- Community PR #43 integrated package-identity merge
  `d203461c023e1661140a1fef38a0f4b68e3454b2` and reached final head
  `871e014c73972fd65b8e9cd39e0665b6b2cdb65d`. The locked/full local gate passed with 150 tests and
  3 declared Windows symlink skips; hosted run `31301825986`, job `93215733777`, passed; fresh
  review was merge-sound; and the PR merged as `56c889141cd4575d12f80c3e0a16a574277e0ddd`.
- The public contact request exposes only a neutral contact category, warns that the issue and
  requesting account are public, and contains no conduct-reporting intent. The exact-final-head P2
  about that intentional neutral category was explicitly declined; no inbox or monitoring promise
  was invented.
- FR-016 records the failed unnumbered `gh pr view --repo` verification read after PR creation. The
  numbered retry verified the exact head/base; no ref or PR content was lost.
- Exact active slice is the bounded v0.1.0 changelog. The non-credential built-artifact/package-smoke
  guard remains the next separate issue #29 residual; no tag, asset, registry, credential,
  publication, owner sign-off, or non-C0 lane moved here.

## 2026-08-09 — Changelog closeout and package-smoke review lane (LAB-REL-01)

- Changelog PR #44 reached final head `ca8c075d286e7812873b86e12c54868b71519217`; hosted run
  `31302156997`, job `93216571555`, passed; fresh review found no causal CRITICAL/HIGH defect; and it
  merged as `2e6a7c2b7ff906cb771bb4e904dd18d2717fa536`. The delayed sweep found no new comment or thread
  debt.
- Package-smoke PR #45 starts from that merge. Code head
  `8523a1b19f8f62a132c081e488bd6916b1e3d82e` adds a confined sdist/wheel build, isolated wheel
  install, installed `dllab doctor --json` proof, focused tests, and the matching CI step. The full
  local gate passed with 154 tests and 3 declared Windows symlink skips; the supported Python 3.12
  artifact smoke passed. Exact hosted proof and final review remain pending on the final docs head.
- FR-001 records the repeated confined-environment setup cost, FR-017 records the unavailable
  PowerShell UTC switch, and FR-009 records the failed outer-wrapper Markdown quoting attempt; each
  failed before changing a protected output or unintended ref.
- After PR #45, the only unattended-safe asset step is an automated canonical replay/hash evidence
  packet for the invented C0 exhibit. Candidate-byte inspection, Lane-P publication, screenshots,
  release/tag actions, credentials, and both distinct owner sign-offs remain NOT verified and
  closed as applicable.
- That automated packet subsequently ran from exact Lab main
  `2e6a7c2b7ff906cb771bb4e904dd18d2717fa536` without opening candidate bytes. Locked context,
  contracts, the invented `wbc1_demo` smoke producer, deterministic reproduce, report build, and
  hygiene all passed. The printed Method Trial export hash was
  `d0a3c978392151012532d8be49ff95e23f7da096879712d3e4392ff3f6d76748`; Markdown was
  `0243f5bac6fcaf63042b35e2ffad4eb794ef6b41a25f07015431aac808a9a96c`; HTML was
  `bb056321d948fe1a25e43c3ac7ff7c914168a254f74d8a99f945cd22aefd2dbc`. None matches the frozen
  producer hashes recorded above because the export provenance embeds `lab_commit`. Lane-P content
  review and every publication action remain parked until a bounded provenance/hash reconciliation
  chooses the frozen producer or a reviewed current-head contract.
- The binding constitution and issue #29 already select the frozen Method Trial v1 exhibit, so a
  separate detached proof reran the existing sequence at producer
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15`. Context, contracts, invented `wbc1_demo`, deterministic
  reproduce, export, report build, hygiene and diff checks passed without opening generated bytes.
  Printed hashes exactly matched the frozen claims: export
  `afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9`, Markdown
  `f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8`, and HTML
  `22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29`. The current-head candidate
  is rejected for this release; product-fixture checking remains next, while Lane-P byte/content
  review and publication stay NOT verified.

## 2026-08-09 — Package-smoke merge and frozen-evidence closeout (LAB-REL-01, issue #29)

- Package-smoke PR #45 reached final head `7f07ce221b7a405c06af70d3a5215910dca72991`; hosted run
  `31304528858`, job `93222641130`, passed on that exact head. Exact-final-head review was
  merge-sound, four pre-merge review threads were resolved, and the PR merged as
  `6e13b6d84391ea7a2579e169151e3d765ad71583`. The delayed sweep then found two additional P2
  threads; both were tracked on issue #29 and resolved, leaving all six threads resolved.
- The full local proof passed with 154 tests and 3 declared skips, including the isolated wheel
  smoke. Remaining PATH, uv/diagnostics, and timeout hardening is tracked on issue #29; it does not
  block this merged baseline or authorize credentials, publication, or a tag.
- Detached frozen-producer proof at
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15` passed context, contracts, invented `wbc1_demo`,
  reproduce, export, report, and hygiene. Printed hashes exactly matched the frozen claims without
  byte inspection: export `afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9`,
  Markdown `f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8`, and HTML
  `22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29`. The current-head candidate
  is rejected for this release.
- Product tracked fixture/schema proof at origin/main
  `7bbb8ee6f9124424b3d8362170f0f4d738f5cb43` passed 26 focused tests and
  `npm run check:method-trial-view`.
- Lane-P candidate-content review, screenshots, and publication remain parked and NOT verified.
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11` aesthetic sign-off and
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)` release sign-off remain owner gates; tag,
  credentials, data, model, and telemetry activation remain closed. The next safe slice is the
  bounded tracked package-smoke P2 hardening on issue #29.

## 2026-08-09 — Package-smoke subprocess-timeout review lane (LAB-REL-01, issue #29)

- Code commit `d7470dd1c36c0ad178e7ce8d64a43c5d834942c2` adds one named 300-second timeout to
  every package-smoke subprocess and converts `TimeoutExpired` into a deterministic `RuntimeError`
  that reports the command without the environment. Focused tests cover timeout propagation and
  confirm that an environment value is not rendered. The branch integrated current Lab main
  `a1dc7caa4015f200a10cf7218d904001c90184cc` before publication.
- The confined `uv 0.12.3` route completed locked sync, doctor/context, Ruff, Pyright, 156 passed / 3
  declared Windows symlink skips, strict MkDocs, hygiene, diff check, and the isolated package
  smoke. The complete gate took 312.5 seconds; no individual subprocess reached the new ceiling.
- No protected, generated, candidate, or private bytes were inspected. The ignored smoke-tree
  context-scan exclusion is a separate prepared issue #29 seam; PATH-uv validation, bounded failure
  diagnostics, and sdist-to-wheel lineage also remain separate. Hosted exact-head proof and fresh
  review are pending; release, tag, publication, credentials, data, model, and telemetry lanes stay
  closed.

## 2026-08-09 — Timeout merge and ignored-smoke scan review lane (LAB-REL-01, issue #29)

- Timeout PR #47 reached final head `ea9b39d663bc2edf020d9853ddf854d9cd0cefdc`; hosted run
  `31306259562` and exact-final-head review passed, and it merged as
  `c827d6a18490838ab132fc7dc058c29fc727d68b`. Descendant process-tree cleanup is tracked on issue
  #29 as a separate P2; it did not expand the direct-child timeout slice.
- Code commit `8fa67280edc56c152ed30ffc454ad6dfe45a9ed9` adds `.package-smoke` to the existing
  explicit Markdown/prompt traversal skip set. An invented temporary fixture proves ignored smoke
  Markdown is skipped while an ordinary tracked document still reports broken-link and invalid
  prompt-classification failures. The branch integrated current Lab main
  `c827d6a18490838ab132fc7dc058c29fc727d68b` before publication.
- The pre-timeout-base local gate passed locked sync, doctor/context, Ruff, Pyright, 155 passed / 3
  declared Windows symlink skips, strict MkDocs, hygiene, diff check, and the actual isolated package
  smoke in 329.8 seconds. After integrating PR #47's two tests, exact-head hosted run `31306855781`
  passed the full combined gate at 157 passed / 3 skips; the focused current-base recheck passed 92
  tests. No ignored, protected, generated, candidate, cache, or private bytes were surfaced to or
  inspected by the agent; automation used only newly created task-local environments. PATH-uv
  validation, bounded diagnostics, sdist lineage, process-tree cleanup, release, tag, publication,
  credentials, data, model, and telemetry remain separate and closed as applicable.

## 2026-08-09 — Ignored-smoke scan merge and bounded-diagnostics review lane (LAB-REL-01, issue #29)

- Ignored-smoke scan PR #48 reached final head
  `89cad7d1dff4b00db9459f2739f1db567d266351`; hosted run `31307153939` / job `93229202173` and
  exact-final-head review passed, and it merged as `0b7a452ee0a6ce4c69e91646400fbb98ad8f3ca1`.
  Its delayed 10:13Z sweep found no new review, comment, or unresolved-thread debt. The non-blocking
  traversal-enumeration performance finding is tracked on issue #29; it did not expand the bounded
  skip-set slice.
- Diagnostics commits `2ec21e8003a24a10ebb4d4c10f2bd5ba4b61fc96` and
  `f9da437e1f1ff0ac601361ccbbdd0fd2b932b0ed` add deterministic, labelled stdout/stderr failure
  diagnostics with a 2,000-character per-stream cap, environment/path redaction, and escaped
  terminal control characters. Invented synthetic tests cover caps, secrets, Windows path forms,
  multiline values, control characters, and formatting. The branch integrated Lab main
  `0b7a452ee0a6ce4c69e91646400fbb98ad8f3ca1` before publication.
- An early fresh-context review found two P2 sanitization gaps: slash-swapped path values and
  terminal control characters. Both were repaired in `f9da437e1f1ff0ac601361ccbbdd0fd2b932b0ed`
  before publication. Redaction remains exact-value based after canonicalization; unusual
  transformations remain outside this bounded slice.
- The confined `uv 0.12.3` route completed locked sync, doctor/context, Ruff, Pyright, 161 passed /
  3 declared Windows symlink skips, strict MkDocs, hygiene, diff check, and actual package smoke in
  318.3 seconds. Hosted exact-head proof and final review remain pending. No ignored, protected,
  generated, candidate, cache, or private bytes were surfaced to or inspected by the agent.

## 2026-08-09 — Diagnostics merge and context-traversal-pruning review lane (LAB-REL-01, issue #29)

- Package diagnostics PR #49 reached final head `02d3e504b4fde54bd1e33b01d24b33a4de3305c5`;
  hosted run `31307993706` / job `93231285624` and exact-final-head review passed, and it merged as
  `ece61e0e1ca86e1e38732916fc077c4718bf7de6`. Pre-merge review left two non-blocking diagnostic
  hardening seams on issue #29. Its delayed sweep found two connector P2 threads: environment-value
  redaction order was newly tracked, while pre-cap stream scanning duplicated existing debt. Both
  threads were replied to and resolved without reopening the merged slice.
- Code commit `08e9fce51f3908b353eef489bfd6fb8c5d7dcde7` replaces eager recursive Markdown globbing with one
  deterministic shared walk that prunes every existing `SKIPPED_MARKDOWN_PARTS` directory before
  descent. An invented temporary fixture records visited directories and proves `.package-smoke`
  descendants are never entered while ordinary tracked Markdown remains checked. The branch
  integrated merged PR #49 before publication.
- The confined locked gate passed doctor/context, Ruff, Pyright, 162 tests with 3 declared Windows
  symlink skips, strict MkDocs, hygiene, and diff check. The first package-smoke call selected a
  task-environment Python without the `uv` module and failed before artifact build; the bounded
  retry through the reviewed `uv 0.12.3` bootstrap interpreter passed the actual isolated package
  smoke in 282.8 seconds. No ignored, protected, generated, candidate, cache, or private bytes were
  surfaced to or inspected by the agent.
- PATH/uv validation is prepared separately; sdist lineage, process-tree cleanup, diagnostic
  redaction-order, short-secret, and pre-cap memory hardening remain separate issue #29 seams.
  Hosted exact-head proof and final review for traversal pruning remain pending; release, tag,
  publication, credentials, data, model, and telemetry lanes stay closed as applicable.

## 2026-08-09 — Traversal-pruning merge and PATH/uv validation review lane (LAB-REL-01, issue #29)

- Context-traversal-pruning PR #50 reached final head
  `086c9809ae2fd27b0a1bc485d4653764aea8ec08`; hosted run `31308683005` / job `93232990186` and
  exact-final-head review passed, and it merged as `e63086b4ae3b97390969357ebdd9d3e30394814e`.
  A delayed sweep at 2026-08-09T12:28:24Z found zero hosted reviews and zero review threads; its
  single top-level exact-review comment was unchanged.
- Code commit `a5978bc0302c5ab20cc40d53c7714a200332db52` validates a PATH `uv` command before any
  package build, accepts only `>=0.12.2,<0.13`, and deterministically probes the current-interpreter
  module before failing safely. Synthetic tests cover both bounds, compatible versions, malformed,
  nonzero and timed-out probes, valid fallback, both candidates invalid, and no build before
  validation. Commit `f85346e575dfb161bb16cfd3e63b982fd290b11c` repairs strict test typing and pins the
  rendered runtime range to `pyproject.toml`.
- The first full gate stopped at six strict Pyright errors from three untyped test lambdas, before
  suite or smoke execution. After the typed-helper fix, the confined locked gate passed
  doctor/context, Ruff, Pyright, 171 tests with 3 declared Windows symlink skips, strict MkDocs,
  hygiene, diff check, and actual package smoke in 290.5 seconds. After integrating merged PR #50,
  the focused current-base context/package seam passed 107 tests with context, Ruff, Pyright, and
  diff checks green.
- No ignored, protected, generated, candidate, cache, or private bytes were surfaced to or
  inspected by the agent. Hosted exact-head proof and final review remain pending. Diagnostic
  redaction-order, short-secret, pre-cap memory, sdist-lineage, and process-tree hardening remain
  separate issue #29 seams; release, tag, publication, credentials, data, model, and telemetry stay
  closed as applicable.

## 2026-08-09 — PATH/uv merge and diagnostic-redaction review lane (LAB-REL-01, issue #29)

- PATH/uv-validation PR #51 reached final head `adc43aea21834683eaf2749fe3515f10da204bde`;
  hosted run `31313571499` / job `93245084619` and exact-final-head review passed, and it merged as
  `02a41cac4a461a93d53b481d34c96a48e29291e5`. Its delayed 12:44Z sweep found zero reviews and
  zero review threads; two top-level exact-review comments were merge-sound and informational.
- Code commit `e3e1ab6aa7fe4c0c68521da4e3658a6eec41d6cc` redacts canonical environment values before cwd
  and command-path substitutions, preventing path replacement from exposing a secret suffix. It
  also treats `pass` as a sensitive key marker so short invented `DB_PASS` values are redacted
  without lowering the global short-value threshold. Two synthetic regressions preserve safe short
  non-secret text and prove neither a complete path-valued secret nor its suffix survives.
- The confined `uv 0.12.3` route completed the initial locked sync, doctor/context, Ruff, Pyright,
  174 tests with 3 declared Windows symlink skips, strict MkDocs, hygiene, diff check, and actual
  package smoke in 195.5 seconds.
- Exact-head hosted review on `eb51ccd0d32714ca040b0feb7030eb070015e2f3` found one blocking path
  redaction-order defect and one non-blocking short-marker collision; the fresh independent lens
  also found that short `PWD` values remained exposed. The single blocking fix commit
  `261fb4ed71006f5210c92de29b1bf9fde4bcd73f` applies every replacement longest-source-first with
  environment-priority ties, and recognizes only exact `PASS`/`PWD` key components for the new
  short-secret exception. Synthetic regressions cover cwd/env collisions, path-valued secrets,
  `DB_PASS`, `DB_PWD`, and safe `BYPASS`/`COMPASS` values.
- The exact fix-head locked gate passed doctor/context, Ruff, Pyright, 176 tests with 3 declared
  Windows symlink skips, strict MkDocs, hygiene, diff check, and actual package smoke in 179.7
  seconds. No ignored, protected, generated, candidate, cache, or private bytes were surfaced to or
  inspected by the agent.
- A TemporaryFile pre-cap design was parked: it would move raw potentially X-class diagnostics to
  an unredacted disk sink and leave disk growth unbounded. Sdist-lineage is the next bounded seam;
  pre-cap memory, process-tree, and component-skip-semantics hardening remain separate issue #29
  debt. Exact fix-head hosted run `31332035344` and final review passed; merge remains pending.
  Release, tag, publication, credentials, data, model, and telemetry stay closed as applicable.

## 2026-08-09 — Diagnostic-redaction merge and sdist-lineage selection (LAB-REL-01, issues #29/#34)

- Diagnostic-redaction PR #52 reached final head
  `46961957e09bb976b34beb41fee5e69d89d21076`; hosted run `31332413187` / job `93292650747`, the
  locked local gate, and exact-final-head review passed. Both hosted review threads were resolved,
  and the PR merged as `b966341d293a50d2b51f448fa23d3248d7e575fd` at
  2026-08-09T19:48:10Z. Its delayed 19:51Z sweep found no new review, comment, or unresolved-thread
  debt.
- A top-level exact-head comment posted at 19:47:58Z set a conservative 19:58:52Z eligibility
  checkpoint. The coordinator's final snapshot covered head, base, hosted proof, closing refs, and
  review threads but omitted top-level comments, so the merge began nine seconds after that comment
  arrived and before its stated checkpoint. The session prompt's three-minute floor, exact-head
  green proof, and exact-final-head review were satisfied, but the owner constitution's 15-minute
  exact-head age was not. No code defect is known. FR-025 records the missed comment surface and
  FR-028 records the second aging-floor miss plus selected enforcement layer; neither rewrites refs
  or merge history.
- Concurrent closeout PR #53 was found open against obsolete base `02a41cac4a461a93d53b481d34c96a48e29291e5`
  with two unresolved blocking threads and overlapping state files. Its still-relevant aging and
  preservation evidence already remained on issue #29; the public preservation note was reduced to
  generic state classes, both threads were reconciled and resolved, and #53 was archived without
  merging or rewriting its commits. FR-029 records this stale-branch divergence.
- Sdist-to-wheel commits `b640d8a7fecbb96a3fed88aa8e27afaeaeb22d4d` and
  `a23fbcd47b78d4c22400bcc7a217b70a0a9966f3` are preserved on
  `ci/lab-sdist-lineage-20260809` over `b966341d293a50d2b51f448fa23d3248d7e575fd`. They build exactly
  one source distribution, pass that selected archive as the source of a separate wheel build,
  require exactly one wheel, and install that wheel. Typed invented tests prove call order,
  selected-archive lineage, and fail-closed zero/multiple-sdist behavior.
- The first integrated gate stopped at four strict test-typing errors before the suite or artifact
  smoke. After the typed-helper fix, Pyright, Ruff, 179 tests with 3 declared Windows symlink skips,
  strict MkDocs, context, hygiene, and diff checks passed. The first two smoke invocations stopped
  at uv-command validation before artifact build; the reviewed confined `uv 0.12.2` route then
  completed the automated sdist-derived wheel smoke in 87.5 seconds. No generated artifact,
  ignored, protected, credential, candidate, cache, or private byte was opened or inspected.
- The code branch is not published yet. After this state repair lands, integrate refreshed main,
  re-prove the affected seam, and publish under the ordinary exact-head hosted, review, and
  15-minute aging gate. The TemporaryFile pre-cap design remains parked because it would create a
  raw unredacted disk sink with unbounded growth; process-tree and component-skip-semantics
  hardening remain separate. Release, tag, publication, credentials, data, model, and telemetry
  stay closed as applicable.

## 2026-08-09 — State reconciliation merge and sdist current-base integration (issues #29/#34)

- State-reconciliation PR #54 reached final head
  `a4eefd9cc4963f684c0376543600969c45d6d057`; hosted run `31333721317` / job `93295965974`, the
  exact-final-head fresh review, and the binding 15-minute age passed. Its P1 and two operational
  P2 threads were reconciled and resolved, and the final snapshot reported zero closing refs.
  GitHub records merge commit `7fea25023d0704aea685e243708328264b9bcaad` at
  2026-08-09T20:33:27Z. Its delayed 20:37Z sweep found no new review, comment, or thread debt.
- The first post-resolution all-surface query failed with a TLS handshake timeout. One smaller
  bounded retry succeeded, confirmed all threads resolved and the hosted check green, and also
  showed the PR as merged before this concurrent observer had merge-operation context. Direct
  evidence on issue #34 then confirmed that a separate root governor process had issued the
  exact-head REST merge and received merge commit `7fea25023d0704aea685e243708328264b9bcaad`.
  No human actor is inferred from account metadata; no duplicate merge command or ref rewrite was
  attempted. FR-032 records the TLS retry, while corrected FR-033 records the context reconciliation.
- Preserved sdist-lineage branch `ci/lab-sdist-lineage-20260809` integrated the new main merge with
  merge commit `2c838bb5d1306434767a90279c6be8fab8a094e5`, retaining code commits
  `b640d8a7fecbb96a3fed88aa8e27afaeaeb22d4d` and
  `a23fbcd47b78d4c22400bcc7a217b70a0a9966f3`. Current-base scoped proof and publication remain next;
  the pre-integration locked proof and actual sdist-derived wheel smoke remain applicable to the
  unchanged code seam.
- Integrated head `adffe0b66131f085a4b48899cca863fc46faa779` then passed doctor/context, Ruff,
  Pyright, 179 tests with 3 declared Windows symlink skips, strict MkDocs, hygiene, diff check, and
  the automated actual sdist-derived wheel smoke. Ready PR #55 now carries the branch; its live
  exact-head hosted, review, 15-minute age, merge, and delayed-sweep gates remain pending.

## 2026-08-10 — Post-merge release-wave state replacement (LAB-REL-01, issues #29/#58)

- Live `origin/main` is `e5a85b20a130518a8307ebdb4cb48c3dbbb85052`. PR #55 reached final head
  `c122868e976ee7f5acce8c6aac20608873c0fa43`, passed hosted run `31335915850` / job
  `93301598278`, exact-head review, and the 15-minute age, then merged as
  `02dcfb261f7216f01aa5696888715ac42f0e3830`; its delayed 22:22:38 BST sweep then found no late
  review, comment, or thread debt. Its sdist-to-wheel lineage is delivered.
- PR #57 reached final head `bd4d244f079b46c0425e0618043c37b48abb29c7`, passed hosted run
  `31337621819` / job `93305956992`, exact-head review, and the 15-minute age, then merged as
  `64c725c61ab3ccf106c0a0b0fb6ea2489821e9ad`; its delayed 23:10:19 BST sweep then found no late
  review, comment, or thread debt. Its zero/multiple-wheel and full-call-sequence test seam is
  complete; production package-smoke behavior was unchanged.
- PR #59 reached final head `df87407bb74d78277d96aa383148da7211735a6a`, passed hosted run
  `31340060061` / job `93312246758`, then merged as `e5a85b20a130518a8307ebdb4cb48c3dbbb85052`
  and closed issue #58. The current-state YAML enforcement is now on live main.
- PR #56 is open at live head `ccf6d9e465c5fd8629de27b0762f5c43fc588fc0` on current base
  `e5a85b20a130518a8307ebdb4cb48c3dbbb85052`; it remains the exhausted, superseded duplicate after
  its two-round ceiling. This slice records no PR #56 close or comment, infers no actor, and preserves
  its unique sound friction corrections without copying stale state. The prepared local short-env
  diagnostics redaction branch is PARKED at `e673102348e8ee7d8c7d45b6ed4e1530cd775972` after
  194 passed / 3 skips and two package-smoke timeouts during uv pip install; issue #29 comment
  `5234405496` is the unlocking source. Other actually tracked issue #29 pre-tag work remains
  ordinary next slices. Lane-P candidate-content review remains unauthorized and closed; no asset
  review, publication, tag, or release action is authorized.
- The closed product `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` remains distinct from the open
  Lab `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8`; product
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)`, Lab
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-7`, Lab
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11`, and Lab
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13` remain explicit owner gates or human actions.
  No tag, release/publication, data, model, credential, or telemetry action is authorized by this
  state replacement.

## 2026-08-10 — PR #60 gate-evidence correction (LAB-REL-01, issues #29/#34)

- PR #60 final head `925b8ba12c8257a111adb7ec1c7747d3d7da72e4` over base
  `e5a85b20a130518a8307ebdb4cb48c3dbbb85052` passed hosted run `31342280107` / job
  `93317911368`, finished with 6 resolved review threads / 20 inline comments, and merged as
  `ebc8626d6ebd808ecec0a665bf8be5d69fdb67d7`.
- The demonstrated exact-head age was 11m33s, below the binding 15-minute floor. The T+3m19 sweep
  was preliminary and invalid as delayed proof. The paginated T+19m32 sweep at
  2026-08-10T00:06:40.440807Z was clean, but it does not retroactively satisfy the pre-merge age
  gate. FR-028 records the third occurrence; issue #29 comment `5234553210` and issue #34 comment
  `5234553289` retain the live reconciliation evidence.

## 2026-08-10 — PR #61 history reconciliation merge (issues #29/#34)

- PR #61 final head `9ad495e587f74f9ed0b74bf28917935dd4bbe1d1` over base
  `ebc8626d6ebd808ecec0a665bf8be5d69fdb67d7` corrected PR #60's 11m33s age miss and delayed-sweep
  history, while preserving PR #56 as closed, unmerged, superseded, and worktree-preserved.
- Hosted run `31344915046` / job `93324950033` succeeded on the exact head. The exact-head Codex
  review was triaged, all 3 review threads were resolved, closing refs were zero, and the head was
  17m04s old at merge. GitHub records merge commit
  `25567559c649b676f18a7809151d6095a80b271e` at 2026-08-10T00:53:07Z.
- A read-only observer reported the PR open and gate-eligible at 00:52:07Z; the next coordinator
  snapshot found it merged before this coordinator issued any merge request. GitHub identifies the
  account but not the issuing process, so no human/session attribution is inferred and no duplicate
  merge was attempted. FR-033 records this third concurrent operation-context occurrence; issue
  #34 retains the already-selected ownership-token or merge-lease preflight.
- The all-surface 2026-08-10T01:03:39Z delayed sweep was past the measured 10-minute connector
  window and clean: 1 top-level comment, 6 reviews, 3 resolved threads, zero unresolved threads,
  zero closing refs, and no activity after the 00:53:07Z merge. No release, tag, publication, asset
  review, credential, data, model, telemetry, or protected-data action occurred.

## 2026-08-10 - Flagship overnight delivery governor (DL-P01 / DL-P03)

- Upgraded the existing `DL-P03-OVERNIGHT-CONTINUOUS` launcher and its protocol into the flagship
  delivery governor: per-slice impact contracts, a six-step delivery-first queue, C0-only
  preregistered experiment limits, and explicit Product-owned promotion preserve the existing
  authority and data boundaries. The context verifier now requires P03 delivery semantics and one
  ordered continuous-impact marker pair, with focused positive and negative tests. Shared prompt
  blocks and the parity manifest remain unchanged.

## 2026-08-10 - Locked-gate correction and finish-before-expand backpressure (DL-P03)

- The standalone `uv` command was absent from PowerShell PATH, but the installed route
  `py -3 -m uv` synchronized successfully and completed the full declared gate: doctor, context,
  Ruff format/check, Pyright, 189 pytest passes with 3 declared symlink skips, strict MkDocs, and
  hygiene. FR-050 now records that verified workaround rather than a false tooling gap.
- P03 and its impact protocol now require actionable research questions rather than metric-only
  work, declare capability and owner gates, and apply finish-before-expand review-capacity
  backpressure without a fixed fleet cap. No active-wave schema or capability implementation changed.

## 2026-08-10 - P03 structured delivery-contract review fix (PR #63)

- Replaced loose P03 delivery tokens with eight exact, ordered, single-copy Lab delivery clauses:
  flagship ownership, slice impact, first-card mission delivery, metric-only rejection,
  finish-before-expand, review-events-only, C0/holdout authority, and conditional evidence closeout.
  Focused mutation coverage removes and duplicates every clause, reverses an adjacent clause pair,
  and retains missing, duplicate, and reversed continuous-impact marker cases.
- Corrected execution rules from connector feedback: `tools/cards.py` remains authoritative for the
  first dependency-safe ACTIVE card; a tracked issue is considered only when no such card exists.
  Evidence ledgers are conditional on their real events, and FR-050 now links durable Lab #34 comment
  `5235339754` while retaining the verified `py -3 -m uv` workaround.
- The full locked gate on this final pre-push tree passed through `py -3 -m uv`: sync, doctor,
  context, Ruff format/check, Pyright, 193 pytest passes with 3 declared Windows symlink skips,
  strict MkDocs, hygiene, and diff check. No shared prompt block or parity manifest changed.

## 2026-08-10 - Package-smoke ordinary process-tree timeout cleanup (issue #29)

- Replaced direct `subprocess.run` timeout supervision with `Popen` plus bounded `communicate`.
  POSIX children run in a new session and timeout cleanup targets that process group; Windows uses
  fully qualified `System32\\taskkill.exe /PID <pid> /T /F` with no shell and discarded cleanup
  streams. Both paths require a bounded direct-child reap before reporting the ordinary timeout.
- Cleanup denial, failure, or bounded-drain failure reports only the fixed redacted
  `package smoke process-tree cleanup could not be confirmed` error; this slice makes no claim
  about escaping descendants or hostile-writer containment.
- Added invented child/grandchild lock fixture coverage. On Windows, a two-second timeout proved
  the lock resource became available after `taskkill /T`; focused
  `py -3 -m uv run pytest tests/test_package_metadata.py -q` passed (34 tests).
- The full locked code/config gate passed from this worktree: locked sync, doctor, context, Ruff
  format/check, Pyright, 198 tests with 3 declared unavailable-symlink skips, strict MkDocs, and
  hygiene. The generated documentation directory remains ignored.
- Written on the parked PR #65 branch and re-placed unchanged at its chronological position during
  the 2026-08-14 base refresh; the 2026-08-14 continuation at the end of this ledger carries the
  refreshed base, the friction renumbering, the cross-platform test repair, and the re-proved gate.

## 2026-08-12 - Report-only Lab merge-eligibility helper (FR-028 / issue #29)

- Delivered the enforcement layer FR-028's `promotion` field had selected:
  `tools/merge_eligibility.py` evaluates one coherent, head/base-bound snapshot and refuses
  eligibility below the governor's 15-minute exact-head floor, returning head, base, hosted checks,
  formal reviews, top-level comments, closing refs, and review threads together. It has no GitHub
  or Git side effects and performs no merge; every surface, item, and identifier failure is a
  deterministic reason code.
- Aligned two predicates to the practiced gate. The unsatisfiable `formal_approval_missing`
  requirement was removed — GitHub forbids self-approval and every Lab pull request is
  single-account, so a formal `APPROVED` state can never appear — and replaced by a required
  `accepted_review` attestation naming one exact-head item by `surface` plus `review_id` or
  `comment_id`, with `missing_accepted_review`, `invalid_accepted_review_surface`,
  `invalid_accepted_review_id`, `stale_accepted_review` and `unknown_accepted_review` failing
  closed. `changes_requested` still refuses any `CHANGES_REQUESTED` review. Any `closing_refs` item
  now yields `closing_reference_present:<index>`, because a closing keyword once auto-closed the
  live release-programme issue; an intentional issue-completing merge needs a coordinator override
  recorded on the pull request thread, outside the tool.
- `docs/agent-system/CONTINUOUS_WORK_PROTOCOL.md` documents the attestation shape, the
  closing-reference refusal and its override, and keeps the one-coherent-snapshot and
  recollect-after-movement rules. FR-028 moved to `promoted` with a dated 2026-08-12 note; it stays
  short of `resolved` because the helper binds only through the protocol's use of it.
- Focused proof: `py -3 -m uv run pytest tests/test_merge_eligibility.py -q` — 15 passed. Fixtures
  are invented C0; no test performs file, network or GitHub I/O.
- Full locked gate through `py -3 -m uv` on the final tree: sync, doctor, context verify, Ruff
  format (92 files) and check, Pyright 0 errors, 208 pytest passes with 3 declared Windows symlink
  skips, strict MkDocs, hygiene, and a clean `git diff --check`. No shared prompt block or parity
  manifest changed.

_Addendum 2026-08-12 (PR #68 fix round 1):_ Codex and one independent fresh-context review of head
`3efc1f4` produced four accepted findings, all now implemented.

- HIGH, both reviews: a `formal_reviews` item with a missing, non-string or unknown `state` passed
  the `CHANGES_REQUESTED` test silently — the single place where absent evidence became a pass.
  Every item must now carry a state from the closed vocabulary `APPROVED`, `CHANGES_REQUESTED`,
  `COMMENTED`, `DISMISSED`, `PENDING`; anything else is `invalid_review_state:<index>` and an
  in-flight review is `pending_formal_review:<index>`.
- Codex P1: aging was measured from evaluation time, so a snapshot collected minutes after a push
  matured merely by being read later. A required `collected_at` now binds the floor to
  `collected_at − pushed_at`, with `invalid_collected_at`, `future_collected_at`, and a
  `stale_snapshot` refusal once the observation is more than `AGING_MINUTES_AFTER_PUSH` past
  collection — the same constant, because the validity window and the aging floor are one
  observation quantum. The report gained `snapshot_age_minutes` for observability.
- MEDIUM: an empty `--now` was falsy and fell back to the wall clock; both CLI branches now test
  `is not None`, so an empty string yields `invalid_now`.
- Codex P1: the documented sink `.dllab/merge-eligibility/<snapshot>.json` was untracked but not
  ignored, while `scripts/verify_hygiene.py` denies `.dllab` as a top-level directory. Resolved by
  ignoring the directory: the script lists paths with
  `git ls-files --cached --others --exclude-standard` (line 22), so `--exclude-standard` keeps
  ignored content out of the scan entirely and `is_denied_generated_path` (line 12) only ever sees
  tracked or unignored paths. `.gitignore`'s narrow `/.dllab/scopes` became `/.dllab/`, matching the
  canon that `.dllab` is never tracked at all. No tracked file exists under `.dllab`.
- Protocol seam updated for coherence: the mandatory `repository` field is now in the snapshot
  spec, identifier matching is documented as type-strict with booleans excluded, and the
  collection-bound aging, stale-snapshot bound and review-state vocabulary are described.
- Coverage added: the exact aging-defeat scenario, the stale and window-edge cases, missing /
  non-string / unknown / `PENDING` review states, `"5"`-versus-`5` and boolean identifiers, a
  governor-parity test asserting `review_gates.aging_minutes_after_push` in the tracked
  `.agent-harness/governor.json` equals `AGING_MINUTES_AFTER_PUSH`, and offline `main()` CLI tests
  over `tmp_path` covering exit codes 0 and 1, `snapshot_read_failed` (asserting the report does not
  echo the path), `invalid_snapshot`, and `invalid_now` for empty and malformed values.
- Focused proof: `py -3 -m uv run pytest tests/test_merge_eligibility.py -q` — 33 passed (was 15).
  Full locked gate on the final tree: doctor, context verify, Ruff format (92 files) and check,
  Pyright 0 errors, 226 pytest passes with the same 3 declared Windows symlink skips, strict
  MkDocs, hygiene, clean `git diff --check`. Codex P2 PR-identity binding was declined here and is
  tracked separately by the coordinator. FR-058 and FR-059 record this round's review-lane friction.

_Addendum 2026-08-12 (PR #68 fix round 2, ceiling):_ Codex's re-review of the fix head found one
accepted gap. An attested `top_level_comments` item must now cite the full 40-hex
`expected.head_sha` in a string `body`, or the snapshot is `unanchored_accepted_review`. GitHub
binds a formal review to a commit natively, so a `formal_reviews` attestation still needs no `body`;
a top-level comment has no such anchor, and without the check a stale review comment about an older
head could carry the gate for a new one. The estate's fresh-context reviews already cite the exact
head reviewed, so this makes a practiced convention mechanical; only the attested item is affected.
Codex's second re-review finding — refusing top-level comments newer than the accepted review — was
declined as coordinator-owned semantic triage, because a recency proxy would false-refuse nearly
every real snapshot: dispositions and lane-claim comments legitimately post after a review. Focused
proof: `py -3 -m uv run pytest tests/test_merge_eligibility.py -q` — 36 passed (was 33). Full locked
gate on the final tree: doctor, context verify, Ruff format (92 files) and check, Pyright 0 errors,
229 pytest passes with the same 3 declared Windows symlink skips, strict MkDocs, hygiene, and a
clean `git diff --check`. Two review rounds is the ceiling; no further round is opened.

_Correction note 2026-08-12:_ two records above are superseded or missing, and are corrected here
rather than rewritten in place.

- The present-tense sentence "PR #56 is open at live head `ccf6d9e465c5fd8629de27b0762f5c43fc588fc0`
  on current base `e5a85b20a130518a8307ebdb4cb48c3dbbb85052`" describes a snapshot that no longer
  holds. Per `docs/CURRENT_STATE.md`, PR #56 is CLOSED and unmerged at head
  `e2e2795d7b3ef14c24d30c0a343a8e0fac7983f0` over that same base, with GitHub reporting
  DIRTY / CONFLICTING. The original entry is preserved as the historical observation it was; the
  live state file outranks it.
- PR #64 (governor current-state reconciliation) merged 2026-08-10T16:02:41Z and never received a
  milestone entry here. Recording it belatedly: the reconciliation landed on main, and
  `docs/CURRENT_STATE.md` now carries it as `delivered.pr64_state_reconciliation` with the same
  belated-record note.

## 2026-08-13 - Lane-P frozen Method Trial v1 exhibit staging (LAB-REL-01 / issue #29)

- The already-recorded 2026-08-09 frozen replay at producer
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15` and invented run `wbc1_demo` remains the evidence for
  the selected exhibit, including frozen JSON `afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9`,
  Markdown `f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8`, and HTML
  `22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29` hashes.
- This staging fix performs no benchmark, reproduction, export, or report build. It validates the
  immutable Product C0 fixture in canonical-LF and semantic form, verifies the exact derived renderer
  bytes and static content, and stages the existing JSON/HTML beneath
  `release-assets/v0.1.0/method-trial-v1/` as the chosen release-upload location. The provenance
  records the immutable fixture source, frozen producer/run, contract commit
  `b48fea579936671397a0486ae7a0342197ee6e4b`, schema checksum
  `634b0cc7a0c3dbcefe8b9cf258e157695beae06d08cc9d02bb781a4267f633ef`, AGPL-3.0-only, and
  copyright Cristian Tcaci.
- No new run, custody decision, experiment, holdout decision, or Experiment Ledger update occurred.
  This remains staged C0 review only, not publication, a release, a tag, a real-data transformation
  approval, model activation, telemetry activation, or either owner sign-off.
- Live truth sync: Lane-P began from PR #72 merge base
  `db104ca1f2bae2de214024e69fddff8cf9822373`; live Git/PR supplies the current landing state.
  Before ordinary merge it is a candidate; after ordinary merge it is tracked staging only; neither
  state authorizes publication, release, or a tag. The next separate pre-tag work is final
  changelog/release-note synchronisation followed by screenshot/video preparation for
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)` and
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11`; no tag is authorised.

_Rebase correction 2026-08-13:_ Lane-P began from PR #72 merge base
`db104ca1f2bae2de214024e69fddff8cf9822373`; live Git/PR supplies the current landing state.
Before ordinary merge it is a candidate; after ordinary merge it is tracked staging only; neither
state authorizes publication, release, or a tag. FR-068 and FR-069 record the separate
connector-identifier and repeated Windows PowerShell compatibility friction observed during this
slice. The next pre-tag work remains final changelog/release-note synchronisation, then the
screenshot/video package and its distinct owner gates; publication and tagging remain unperformed
and unauthorised.

## 2026-08-14 - Changelog synchronisation and q-11 media package (LAB-REL-01 / issue #29)

- Changelog/release-note synchronisation is DONE: PR #78 merged as
  `05090e7f3840265759a37a1587aee176f5461fe4` after the full gate, hosted proof at each of its
  three heads, a MERGE-SOUND/CLEAN/CONFIRMED fresh-context review sequence, Codex P2 triage, and
  an `eligible: true` merge-eligibility report on a fresh snapshot. The initial agent merge was
  denied by the runtime permission layer and proceeded on explicit owner authorization (FR-074).
- The q-11 screenshot/video package v1 was then produced locally from that merged head and
  delivered to the owner in-session for the
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11` aesthetic review. It is NOT tracked,
  staged, published, or attached to any release. Contents and SHA-256 digests:
  `report-full.png` `a9834cfd2adff46a2646105add0acffd5a6fc0630fdc6f5d0e876122dfda38c1` (full-page
  headless-Chrome capture of the staged HTML asset served on `127.0.0.1`; the bottom trim removed
  only blank canvas below the last rendered row, detected by background-color scan plus a 60px
  margin, so no report content was cropped),
  `report-viewport.png` `a79d7c412ca643d65b67a5b2b12109e693cd88ab173ac1c174d60e6cc284a63c`
  (1280×900 above-the-fold capture), `report-scroll.gif`
  `e265fc80c612c248289dfaafefb2783bb83164f0210c124facbf2922bcee4057` (programmatic 14-step pan of
  the full-page capture, disclosed as a scripted pan rather than a screen recording),
  `cli-demo.png` `d3e991f358ff0412dbe8870113c1bcade643fe91e0d515abd47cd9608aaf2612` and
  `cli-demo.html` `d64153dde65e241b1c6ece2b95e0d4fb4a97f970c66b591bc18b5861d0d74e7a` (rendered
  transcript of a real deterministic demo run with local paths elided), and `MANIFEST.md`
  `ead2bf8afc7952ad01e8ffc40035c7f8e97cffb98793b8ea7c49c75414f76c11` — the provenance manifest
  disclosing every transformation and the review-only posture, hashed here so the exact reviewed
  disclosures are durably identifiable.
- Media provenance: the page captures render the staged
  `release-assets/v0.1.0/method-trial-v1/method-trial-report.v1.html`
  (`22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29`) without modifying any asset
  byte. The transcript records a real `wbc1_smoke` run in a clean detached worktree at the merged
  head (report `markdown=aae1e2ce42c8e0d9e16a0a05ef2cde76380df550546277056569bca6509495b9`,
  `html=c2a4f6df4ef08a3396a3416470b0d5ae9995964bc687201f5df6c5094ae74feb`; MethodTrialView export
  `104f007189765ce06870b1321d3f555ccfce22396f8e52cb03424de027c8c18b`); the worktree was removed
  after capture. FR-075 records the headless-capture substitution for the unavailable
  browser-automation extension.
- Custody honesty: like every execution of the standing smoke path (hosted CI runs it on each
  pull request), the `wbc1_smoke` run mechanically wrote its single-use `final_holdout_custody`
  receipt before opening the freshly generated invented dataset's final holdout — benchmark
  mechanics on invented C0 data inside an ephemeral worktree that was then removed. This is not a
  research holdout decision on a preregistered experiment, no finding was drawn from it, and the
  Experiment Ledger convention (only named decision runs are ledgered) is unchanged; the frozen
  `wbc1_demo` exhibit's recorded custody is untouched. No new experiment or Experiment Ledger
  update occurred. No publication, release, tag, data,
  model, telemetry, credential, or owner-gate action occurred; q-11 sign-off remains open and
  owner-only, distinct from product `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)`.

_Note 2026-08-14 (owner sign-off):_ Later the same day the owner explicitly approved the
delivered package v1, closing `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11`; the closure
record and its exact scope live in `HUMAN_TODO.md`. The approval is aesthetic acceptance of the
hashed package bytes only; the joint tag remains blocked on product
`Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)` and stays owner-executed.

## 2026-08-14 - PR #65 base refresh and cross-platform taskkill test repair (issue #29)

- Resumed the parked package-smoke process-tree branch by merging the current default branch into
  it as an ordinary merge commit. Every code path merged cleanly; the only conflicts were the two
  append-only documents, which both sides had extended at the same former end of file. Both files
  were restored to the incoming default-branch content and confirmed identical to that branch's
  blob by object hash before this branch's own additions were re-placed, so the resolution removes
  no landed line from either document. FR-078 records the merge shape and the verified procedure.
- The default branch advanced mid-slice, past the base this resume was planned against, and the
  newly landed tail had itself taken `FR-074` and `FR-075`. The refresh was therefore retargeted at
  the live default branch rather than the planned base, since merging the superseded base would
  have landed colliding identifiers. FR-080 records the divergence; FR-070 is its lineage.
- Renumbered this branch's two friction entries to the log's next free identifiers at the tail:
  `FR-053` became `FR-076` and `FR-054` became `FR-077`. The default branch had already recorded,
  in its dated PR #65 note, that these records lived only on the parked branch; `FR-053` and
  `FR-054` therefore stay permanently unassigned, and that note's reference is resolved by the
  dated reconciliation note under the renumbered pair. No entry that exists on the default branch
  was renumbered or edited. `FR-077`'s original `tracked-task-debt` status was outside the schema's
  six named states and is now `workaround-documented`; FR-072 records why that is a defect.
- Repaired the hosted Ubuntu failure in the mocked Windows timeout tests. Three sites set
  `SYSTEMROOT` from a raw literal that encoded a doubled backslash, and one assertion hard-coded
  native separators, so the expectation could only match on a Windows host. Each site now sets
  `SYSTEMROOT` from a `synthetic_root` literal, and the assertion compares against
  `expected_taskkill`, built as `str(Path(synthetic_root) / "System32" / "taskkill.exe")` — the same
  expression production uses — so the expectation renders through host `Path` semantics on either
  platform. Production code in `scripts/verify_package_smoke.py` was not changed.
- The full declared gate passed from this worktree through the FR-050 user-level `uv 0.12.4` module
  route, with the cache and managed-Python directories held outside the repository per FR-060:
  locked sync with `uv.lock` unmodified, doctor, context verification, Ruff format and check, strict
  Pyright, the full pytest suite, strict MkDocs, hygiene, the card programme check, and
  `git diff --check`. The focused
  `pytest tests/test_package_metadata.py -k "taskkill or timeout"` selection passed 8 tests.
- The package smoke needed a separate route and passed only through a repository-external
  standard-library bootstrap holding `uv` in its own site directory. The smoke deliberately sets
  `PYTHONNOUSERSITE`, which makes its current-interpreter module probe unable to see a
  user-installed `uv`; FR-079 records that interaction and why it is environment debt rather than a
  production defect.
- Scope stayed C0 code, tests, and docs. No capability, authority, release, or tag state changed,
  and no real or private input was inspected. This section originally asserted that nothing was
  pushed; that was written before the push and is corrected here. The head `ed281ec` was pushed to
  the PR branch at 2026-08-14T11:59:46Z and the hosted `Prove the lab` check succeeded at that exact
  head. The fix round recorded in the next section supersedes `ed281ec`, and its own hosted proof is
  pending at the time this correction is authored. FR-081 records the pre-push-prose defect.

## 2026-08-14 - PR #65 review fix round 1 (issue #29)

- A fresh-context adversarial review returned MERGE-SOUND with no CRITICAL or HIGH findings against
  `ed281ec`, and a Codex round posted two P2s at the same exact head that independently confirmed
  two of its MEDIUMs. Because two independent reviews converged, this round changes production
  supervision in `scripts/verify_package_smoke.py`, which the preceding slice had deliberately left
  untouched.
- Unconfirmed process-tree cleanup now raises a distinct `ProcessTreeCleanupUnconfirmedError`
  rather than a generic `RuntimeError`, and `_probe_uv_command` re-raises it instead of swallowing
  it. Previously an unreaped tree was indistinguishable from an unusable candidate, so the resolver
  moved on to the next candidate while that tree was still running. The class carries an `Error`
  suffix because Ruff `N818` rejects the bare name.
- `_run` supervised its child only against `TimeoutExpired`, so any other exit from `communicate` —
  notably `KeyboardInterrupt` — left the child detached with its pipes open. A catch-all now reaps
  the tree on the existing bounded budget, releases the pipes, and re-raises the original exception
  unchanged. This deliberately does not adopt `with subprocess.Popen(...)`: `Popen.__exit__` ends in
  an unbounded `wait()`, which would convert the fail-closed cleanup-unconfirmed path into an
  indefinite hang on the very tree that could not be reaped. Timeout-branch semantics are otherwise
  unchanged.
- Both guards carry a discriminating test, and each was verified to fail against a mutated build
  with that guard removed rather than merely passing against the fixed one.
- Closed a vacuous-coverage gap: the fail-closed cleanup test was the only mocked-Windows timeout
  test that never set `SYSTEMROOT`, so on a non-Windows host it exercised the absent-root early
  return and its failed-taskkill assertions asserted nothing. It now sets the synthetic root, and a
  sibling test covers the absent-`SYSTEMROOT` branch deterministically, asserting that no
  unqualified `taskkill` is attempted when the system root is unknown.
- Friction: added a dated forward pointer under the landed stale note that still described
  FR-053/FR-054 as living only on the parked branch; raised FR-070 to three occurrences with a dated
  note citing FR-080 and corrected FR-080's justification, which had wrongly claimed such an update
  was forbidden; and added FR-081 for the pre-push ledger prose.
- Deferred by coordinator decision to
  [Lab #81 issue](https://github.com/Chris0Jeky/developer-lens-lab/issues/81), deliberately
  untouched here: the `SYSTEMROOT` absolute-path check, `taskkill` already-exited diagnostics, the
  Windows-only timing-fragile test, and the impossible-state parametrization.
- Scope stayed C0 code, tests, and docs. No capability, authority, release, or tag state changed,
  no real or private input was inspected, and `uv.lock` was not modified. This section was authored
  before its head was pushed; the exact-head hosted result is recorded by the PR's `Prove the lab`
  check.

## 2026-08-14 - Post-merge state reconciliation after PR #65 (issue #29)

- PR #65 merged 2026-08-14T13:03:19Z as `eab341b9f7cdf98ce64676a7c12f4ed61563573b` from final head
  `01d4368b812a9fa12aae377db31c5567b3bf393a`, closing the package-smoke process-tree lane that had
  been parked since 2026-08-10 and was resumed per the issue #29 recipe.
- Merge evidence, recorded here because the state artifact is a resume point rather than an evidence
  archive: hosted `Prove the lab` was green at each of the three heads `ed281ec`, `1ecc8b7`, and
  `01d4368`, the last of which is the merged final head. The review sequence was a MERGE-SOUND
  fresh-context review, a micro-verification round, and a CONFIRMED CLEAN final round, reaching the
  two-fix-round ceiling. All 5 Codex threads were triaged and resolved. The post-merge sweep at
  2026-08-14T13:35Z, T+32 after the merge, found zero post-merge reviews and zero post-merge
  comments, with all 5 threads resolved.
- Reconciled `docs/CURRENT_STATE.md`, which still described PR #65 as open, PARKED, CONFLICTING at
  the superseded head `91cf991b…`, and as something not to receive another fix push. The stale
  claims in the active-wave writer and state fields, in `next_safe_slice`, and in
  `exact_resume_point` are replaced with the merged record, and a new
  `delivered.package_smoke_process_tree` entry carries the delivery evidence in the same shape as
  its sibling lanes. The superseded resume references (issue #29 comment `5243827843`, PR #65
  comment `5243827873`) are retained but explicitly marked as history rather than as a live
  unlocking path. The pinned `active_wave[0].lane` scalar was deliberately left untouched, because
  `tests/test_context.py` asserts it exactly.
- The resume point states only what the artifact's own structure supports: the pre-tag agent
  remainder is complete, the Lab q-11 gate is closed by the 2026-08-14 owner approval recorded
  through merged PR #80, and the sole remaining joint-tag blocker is the product gate
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)`, after which the joint v0.1.0 tag decision
  returns to the owner and is never agent-executed. No new work was invented.
- Raised FR-078 to three occurrences with a dated note for the PR #65 round-2 ledger-tail conflict
  resolved as merge `738b91e`, where the restore-verbatim-then-re-place procedure again produced a
  zero-deletion result. Its promotion reasoning is restated explicitly for three episodes: the
  recorded procedure still holds and the case for it is stronger than at two, while an automated
  append-only merge driver stays task debt.
- Deferred package-smoke hardening from the merged lane is tracked at
  [Lab #81 issue](https://github.com/Chris0Jeky/developer-lens-lab/issues/81) and is later work.
- Scope stayed C0 docs, limited to `docs/CURRENT_STATE.md`, `docs/agent-system/FRICTION_LOG.md`, and
  this ledger. No capability, authority, release, publication, or tag state changed, no real or
  private input was inspected, and `uv.lock` was not modified. This section was authored before its
  head was pushed; the exact-head hosted result is recorded by the PR's `Prove the lab` check.

## 2026-08-14 - Merge-eligibility snapshot hardening (issue #29 follow-ups)

- Landed the three tracked snapshot-hardening follow-ups from PR #68's Codex triage (issue #29
  comments `5269020473` and `5269401432`), taken as one slice on the first subsequent touch of
  `tools/merge_eligibility.py`, exactly as the tracking comments planned.
- Pull-request identity binding: a snapshot now requires `pull_request.number` as its one
  immutable identity, cross-checked as `pr_number` at surface and item level on the four
  pull-request-scoped surfaces and on the `accepted_review` attestation, so surfaces from two
  pull requests sharing a head/base pair can no longer be substituted. The `checks` surface is
  deliberately outside the binding in both directions: check runs are commit-scoped, and a
  collector-stamped number there would be invented evidence rather than hosted state.
- Attested-review state allowlist: an attested `formal_reviews` item must itself be `APPROVED`
  or `COMMENTED`; a `DISMISSED`, `CHANGES_REQUESTED`, `PENDING`, or stateless item can no longer
  carry the gate. The general review-state rules are unchanged.
- Identifier validation: non-positive integers and empty or whitespace-only strings are refused
  as identifiers on both the attestation and item sides, closing the sentinel-matches-itself
  shape where a blank field could attest an equally blank record.
- Every new rule fails in the refusal direction only; no new path can make an ineligible
  snapshot eligible. `docs/agent-system/CONTINUOUS_WORK_PROTOCOL.md` documents the new snapshot
  fields, the checks-surface exception, the allowlist, and the degenerate-identifier refusal in
  the merge-gate section. Proof: focused merge-eligibility suite then the full gate (ruff
  format/check, pyright, pytest, strict mkdocs, hygiene, context verify) green at the
  implementation head `4f10c0e19eee0c55c93670c634f7876cacf184a9` and re-run green in full at the
  PR #82 fix-round head `dcbb848c3f9709bdd1f7e2928cbb4dccc36e5329`; the later docs-only commits
  were each verified with the focused docs checks (strict mkdocs, hygiene, context verify) at
  their own heads. Existing snapshot collectors must emit the new fields; the in-session
  collector is runtime state and was updated in place.
- A MERGE-SOUND fresh-context review of the implementation head returned five LOW findings. The
  fix round closes the three coverage gaps: identifier validation is only observable when the
  attestation and the item carry the same degenerate identifier, so that matched-pair test now
  covers every degenerate form and the item-side test is renamed to say it pins the outcome
  rather than the guard; the attested-state allowlist is pinned across every record matching the
  attested identifier, not just the first; and a present-but-non-mapping `pull_request` is pinned
  to `invalid_pull_request_number`. Each was confirmed discriminating by temporarily reverting the
  guarded code and observing the failure; no revert was committed.

## 2026-08-14 - Merge-eligibility snapshot hardening merge evidence (PR #82 closeout)

- Merge evidence, recorded here because the state artifact is a resume point rather than an
  evidence archive: PR #82 merged 2026-08-14T21:17:34Z as
  `02afd7c37b3c7d0a30551025a1724fb5aa5d064b` from final head
  `e57576469f2fa87b76372918fc78a17e776e3cf0` over base
  `f0d497d6a371e783fde5f8028a856f4d2544956c` (then-current main after absorbing the concurrent
  PR #83 state reconciliation). Hosted `Prove the lab` was green at the final head (run
  `31840866416`) and at the merge commit (run `31841789754`).
- Review chain: the MERGE-SOUND fresh-context review of the implementation head and its fix-round
  micro-verification were extended through both base absorptions to the exact final head
  (accepted attestations of 20:47:54Z at `d021e37c990cd93beb567076a8298d694e07f9a7` and 21:08:23Z
  at the final head), plus a Codex round whose both findings were accepted, fixed, and resolved.
- The merge executed on an explicit owner instruction at a demonstrated public head age of about
  12m22s, below the binding 15-minute exact-head floor; FR-028 records this as its fourth
  occurrence, and the same-hop capture is PR #82 comment `5298266904` with the delivery
  checkpoint at issue #29 comment `5298304308`.
- The 2026-08-14T21:39-21:41Z (T+22m) post-merge sweep was clean and was independently
  re-confirmed at 21:50Z: zero post-merge reviews, inline comments, or further top-level
  comments, and main unmoved at the merge commit.
- Scope: C0 docs closeout only, landed with the PR #84 state reconciliation; no capability,
  authority, release, publication, or tag state changed, no real or private input was inspected,
  and `uv.lock` was not modified.
