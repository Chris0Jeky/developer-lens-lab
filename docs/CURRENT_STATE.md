# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-12
phase: M3_GOVERNOR_CONTROL_PLANE
posture: >-
  public repository; constitution v2 recorded (docs/OWNER_CONSTITUTION.md) — real own/curated data,
  layered people/team research, and raw content are authorized in principle, but runtime and tracked
  inputs remain C0 invented until the activation preconditions in .agent-harness/governor.json are
  mechanically true; tier stays truthfully T1/sensitive_data=false
repository: Chris0Jeky/developer-lens-lab (public)
branch: main
head: refresh with git rev-parse origin/main
active_wave:
  - lane: >-
      LAB-REL-01 v0.1.0 release wave (issue #29)
    writer: >-
      Main's last landed change is PR #68, merged at
      `07929a41fa8c80f05794db9a58fa0bf014b4f961` on 2026-08-12T16:14:34Z after a 17m51s exact-head
      age, so the binding 15-minute floor held. PR #65 is open and ready (not draft), based on
      `bf5b01db178c4dbbbea4ca9dafc5c3fc181b3e2c`, at parked exact head
      `91cf991b96b242680ab6839decb110422ab9755d`; it has two commits and no closing-issue link.
      PR #56 is CLOSED/unmerged at head `e2e2795d7b3ef14c24d30c0a343a8e0fac7983f0` over base
      `e5a85b20a130518a8307ebdb4cb48c3dbbb85052`; GitHub reports DIRTY / CONFLICTING. Preserve its
      coordinator-owned PR #56 refresh worktree, branch `docs/lab55-postmerge-refresh-20260810`, at
      that same head: it has no nonignored changes, but ignored generated/cache outputs whose contents
      were not inspected. Do not remove it until their ignored-output disposition is resolved.
    state: >-
      The merge-eligibility enforcement lane is DELIVERED and landed on main; see
      `delivered.merge_eligibility_enforcement` for its full record. PR #65 remains PARKED, not
      merge-sound, after two review rounds, and no implementation from it is landed on main. The
      final local locked gate on the parked head was green: 198 passed, 3 declared Windows symlink
      skips, focused package-metadata proof 35 passed, and Pyright was clean. Hosted run
      `31413655609` failed Pyright on the original head
      `8cf95d50440047c9e9cb56d9718038600c04dee9`; hosted run `31414895754` on the parked head passed
      package smoke, lint, type, context, and generated-contract checks, then failed pytest at the
      taskkill-path assertion. The first exact-head review found three HIGH proof defects; the fix
      commit closed those, and the second/final review found the remaining HIGH host-portability
      assertion. The loop is parked under the two-review-round ceiling; its exact resume reference
      remains issue #29 comment `5243827843` and PR #65 comment `5243827873`.
delivered:
  - LAB-GOV-02: >-
      DONE — lab PR #35 merged at bba0c18261c0a2b77332a0408f63b10c774c91f4 and closed issue #33.
      This records the merged result only; it does not attribute the GitHub operation to an actor.
  - product_concurrent_writer_gate: >-
      Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8 is closed by direct owner decision and clean-session
      evidence, recorded through product PR #223 at 877f1ca07ccee014c0adf50925f989815e6bc7f1. This does
      not close or alter this repository's Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8 real-study
      public-transformation gate.
  - dependency_remediation: >-
      DONE — PR #38 final head `4ebb1049ddb831dc7ff76f5a0050e52bdf37f40c` passed hosted proof and
      independent review, then merged as `f893f576f71202375fe93e8c7d9c02e54fbaf08a`; GitHub indexed
      `main` with zero open Dependabot alerts and issue #5 closed at 05:46Z.
  - release_prompt_guard: >-
      DONE — exhausted PR #37 was archived without a third fix commit; replacement PR #42 changed only
      DL-P09 at final head `e290d1b94aff9f39de677fd80670f4f9e8f15227` and merged as
      `38ac2eb14c8c9ba742b5f269b7022c7e549b7a5d` after exact hosted proof and fresh review.
  - friction_reconciliation: >-
      DONE — PR #41 final head `3604e301a5e9930e56edce193ea293698a4870bd` merged as
      `178bd6d695119b74294a8fd6fbe46f54577e49b2`; FR-008 through FR-014 are durably recorded, while
      FR-009/FR-010 enforcement remains task debt on issue #34 and escaped-environment cleanup is
      owner-gated at `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13`.
  - state_reconciliation: >-
      DONE — PR #39 final head `b36bbadd0365a8958ba741e27c2e36e9458237be` merged as
      `4f355f1e58e1eca1191f899f1fc4354af8a23a00`; exact hosted proof passed, late review was triaged,
      and the resulting wording debt is repaired in the next delivered slice.
  - licence_package_identity: >-
      DONE — PR #40 final head `7d5610d2280e900d9e2c10c6304455830147ffcd` merged as
      `d203461c023e1661140a1fef38a0f4b68e3454b2` after locked/full local proof, exact hosted proof,
      fresh review, and the bounded PR #39 late-wording repair.
  - community_scaffolding: >-
      DONE — PR #43 final head `871e014c73972fd65b8e9cd39e0665b6b2cdb65d` merged as
      `56c889141cd4575d12f80c3e0a16a574277e0ddd` after locked/full local proof, exact hosted proof,
      fresh review, complete thread triage, and the neutral public-contact privacy repair.
  - release_notes: >-
      DONE — PR #44 final head `ca8c075d286e7812873b86e12c54868b71519217` merged as
      `2e6a7c2b7ff906cb771bb4e904dd18d2717fa536` after exact hosted proof, fresh review, and a clean
      delayed sweep.
  - package_smoke: >-
      DONE — PR #45 final head `7f07ce221b7a405c06af70d3a5215910dca72991` passed hosted run
      `31304528858` / job `93222641130` and exact-final-head review, then merged as
      `6e13b6d84391ea7a2579e169151e3d765ad71583` with four pre-merge threads resolved. Its delayed
      sweep found two additional P2s; both were tracked and resolved, leaving all six threads
      resolved. Full local proof was 154 passed / 3 declared skips, including the isolated wheel smoke.
  - package_smoke_timeout: >-
      DONE — PR #47 final head `ea9b39d663bc2edf020d9853ddf854d9cd0cefdc` passed hosted run
      `31306259562`, exact-final-head review, and merge gating, then merged as `c827d6a18490838ab132fc7dc058c29fc727d68b`.
  - package_smoke_scan: >-
      DONE — PR #48 final head `89cad7d1dff4b00db9459f2739f1db567d266351` passed hosted run
      `31307153939` / job `93229202173`, exact-final-head review, and merge gating, then merged as
      `0b7a452ee0a6ce4c69e91646400fbb98ad8f3ca1`.
  - package_smoke_diagnostics: >-
      DONE — PR #49 final head `02d3e504b4fde54bd1e33b01d24b33a4de3305c5` passed hosted run
      `31307993706` / job `93231285624`, exact-final-head review, and merge gating, then merged as
      `ece61e0e1ca86e1e38732916fc077c4718bf7de6`; two delayed P2 threads were tracked and resolved.
  - context_traversal_pruning: >-
      DONE — PR #50 final head `086c9809ae2fd27b0a1bc485d4653764aea8ec08` passed hosted run
      `31308683005` / job `93232990186`, exact-final-head review, and merge gating, then merged as
      `e63086b4ae3b97390969357ebdd9d3e30394814e`.
  - package_smoke_uv_validation: >-
      DONE — PR #51 final head `adc43aea21834683eaf2749fe3515f10da204bde` passed hosted run
      `31313571499` / job `93245084619` and exact-final-head review, then merged as
      `02a41cac4a461a93d53b481d34c96a48e29291e5` before the binding 15-minute exact-head age;
      FR-028 records the gate miss. Its delayed sweep was otherwise clean.
  - package_smoke_redaction: >-
      DONE — PR #52 final head `46961957e09bb976b34beb41fee5e69d89d21076` passed hosted run
      `31332413187` / job `93292650747`, exact-final-head review, and the locked local gate, then
      merged as `b966341d293a50d2b51f448fa23d3248d7e575fd`; both review threads are resolved and its
      delayed 19:51Z sweep found no new feedback. FR-025 records the separate pre-merge snapshot miss;
      FR-028 records the second exact-head aging-floor miss and selected enforcement layer.
  - diagnostic_state_reconciliation: >-
      DONE — PR #54 final head `a4eefd9cc4963f684c0376543600969c45d6d057` passed hosted run
      `31333721317` / job `93295965974`, exact-final-head review, the 15-minute age, and complete
      thread triage, then merged as `7fea25023d0704aea685e243708328264b9bcaad` at 20:33:27Z; its
      delayed 20:37Z sweep was clean. FR-032 records the final-snapshot TLS retry; FR-033 records
      and corrects a concurrent observer's incomplete merge-operation context.
  - package_smoke_sdist_lineage: >-
      DONE — PR #55 final head `c122868e976ee7f5acce8c6aac20608873c0fa43` passed hosted run
      `31335915850` / job `93301598278`, exact-head review, and the 15-minute age, then merged as
      `02dcfb261f7216f01aa5696888715ac42f0e3830`; its delayed 22:22:38 BST sweep then found no late
      review, comment, or thread debt.
  - package_smoke_contract_tests: >-
      DONE — PR #57 final head `bd4d244f079b46c0425e0618043c37b48abb29c7` passed hosted run
      `31337621819` / job `93305956992`, exact-head review, and the 15-minute age, then merged as
      `64c725c61ab3ccf106c0a0b0fb6ea2489821e9ad`; its delayed 23:10:19 BST sweep then found no late
      review, comment, or thread debt. Its zero/multiple-wheel and full-call-sequence test seam is
      complete.
  - current_state_yaml: >-
      DONE — PR #59 final head `df87407bb74d78277d96aa383148da7211735a6a` passed hosted run
      `31340060061` / job `93312246758` and merged as
      `e5a85b20a130518a8307ebdb4cb48c3dbbb85052`, closing issue #58.
  - pr60_gate_evidence_correction: >-
      CORRECTED — PR #60 final head `925b8ba12c8257a111adb7ec1c7747d3d7da72e4` over base
      `e5a85b20a130518a8307ebdb4cb48c3dbbb85052` passed hosted run `31342280107` / job
      `93317911368`, finished with 6 resolved review threads / 20 inline comments, and merged as
      `ebc8626d6ebd808ecec0a665bf8be5d69fdb67d7`. Its demonstrated exact-head age was 11m33s, so it
      did not satisfy the binding 15-minute floor. The T+3m19 sweep was preliminary and invalid as
      delayed proof; the paginated T+19m32 sweep at 2026-08-10T00:06:40.440807Z was clean but does
      not retroactively repair the age miss. FR-028 and issue #29 comment `5234553210` plus issue
      #34 comment `5234553289` preserve the correction.
  - pr61_history_reconciliation: >-
      DONE — PR #61 final head `9ad495e587f74f9ed0b74bf28917935dd4bbe1d1` over base
      `ebc8626d6ebd808ecec0a665bf8be5d69fdb67d7` passed hosted run `31344915046`, exact-head Codex
      review, complete thread triage, zero closing refs, and 17m04s age, then merged at
      2026-08-10T00:53:07Z as `25567559c649b676f18a7809151d6095a80b271e`. The merge was first
      observed after a concurrent read-only snapshot and was not issued by this coordinator;
      FR-033 records the third missing-operation-context occurrence without inferring an actor. The
      all-surface 2026-08-10T01:03:39Z sweep was clean: no post-merge review/comment/thread activity,
      zero unresolved threads, and zero closing refs.
  - pr62_history_reconciliation: >-
      DONE — PR #62 final head `e833c68314f874d89523e4c97f5a3293548465cd` passed Check run
      `31346126369` and merged as `73a5b9653cccbb470c6bf9f0f5a4a7cd8d3cac45`; its post-merge
      audit was clean.
  - pr63_overnight_delivery: >-
      DONE — PR #63 final head `d48e09cf149d75aee92665e62f3893741cd98104` passed Check run
      `31351467716`, merged as `4519e193ff6601c3d1971bae2ef8444b16bf5d0d`, and had 3 resolved / 0
      unresolved review threads; its post-merge audit was clean.
  - pr64_state_reconciliation: >-
      DONE — PR #64 (governor current-state reconciliation) merged 2026-08-10T16:02:41Z; recorded
      belatedly: this list previously omitted it (ledger correction note 2026-08-12).
  - merge_eligibility_enforcement: >-
      DONE — FR-028's selected enforcement layer is delivered. It was prepared overnight on
      2026-08-10 on branch `ci/lab-merge-eligibility-20260810`, a branch this file had never
      recorded — that omission is recorded here explicitly — then audited and delivered on
      2026-08-12 as PR #68, merged at `07929a41fa8c80f05794db9a58fa0bf014b4f961`. It ships the
      report-only `tools/merge_eligibility.py`, 36 invented-fixture tests, and the "Lab merge
      decision seam" section of `docs/agent-system/CONTINUOUS_WORK_PROTOCOL.md`. Round 1 replaced
      the unsatisfiable formal-APPROVED predicate with an `accepted_review` attestation, because
      GitHub forbids self-approval and every pull request here is single-account, so that state can
      never appear; it also added the closing-reference refusal, bound aging to `collected_at` with
      a `stale_snapshot` bound at the same governor constant, refused an empty-string `--now`,
      ignored `/.dllab/` wholesale (verified against `scripts/verify_hygiene.py`'s
      `--exclude-standard` semantics), and added a governor parity test plus CLI tests including the
      no-path-echo assertion. Round 2, at the two-round ceiling, added `unanchored_accepted_review`:
      an attested top-level comment must cite the exact 40-hex head in its body. Proof: hosted run
      `31615108943` green at final head `8facd3fe79777bd524ea201714b519d24f8a159d`; an independent
      fresh-context review whose initial verdict was NOT MERGE-SOUND with its HIGH finding verified
      closed, plus a CLEAN micro-verification of round 2; and three Codex review rounds triaged with
      dispositions recorded on the thread. Lane coordination during the pipeline: a second
      coordinator posted a stale-read adoption comment at 15:41:29Z citing the superseded head and
      formally stood down at 16:11:29Z after the ownership clarification; one writer held throughout
      and no ref was raced. Post-ceiling P1/P2 findings are tracked on issue #29 comments
      `5269020473` and `5269401432`: PR-identity binding, a dismissed-review state allowlist, and
      identifier validation. The delayed post-merge sweep was clean twice — at 16:24:23Z (T+9m49s)
      and again at 16:28:43Z (T+14m09s), beyond the measured connector delay — with zero post-merge
      reviews, top-level comments, inline comments, and no new issue #29 activity.
next_safe_slice: >-
  SENSE/RECONCILE first from live `origin/main`, the cards source, issue #29, and open pull requests.
  The FR-028 merge-eligibility helper is DELIVERED and is no longer part of the pre-tag remainder.
  The next dependency-safe LAB-REL-01 seam is Lane-P provenance selection: explicitly select the
  frozen producer `0ef193070a9b80b81cef5a1710a1d65e0b271c15` as the release exhibit, per owner
  decision U3=FREEZE and FR-019's recorded unlocking condition. After it comes the Lane-P release
  review — staging only, with the publication decision handed back — then the final changelog sync,
  and the screenshot/video package for `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11` together
  with `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)`. The three tracked helper-hardening
  follow-ups on issue #29 are a later natural slice, not this one. PR #65's portable patch is a
  PARKED REFERENCE only, not a next push: its exact resume reference remains issue #29 comment
  `5243827843` and PR #65 comment `5243827873`, with `synthetic_root =
  r"C:\Windows"` and `expected_taskkill = str(Path(synthetic_root) / "System32" / "taskkill.exe")`.
  Reopen that reference only after a genuinely new unlocking event or explicit fresh authority. Keep
  remaining hardening, asset, release, publication, and tag work separate; no data, model, telemetry,
  contract, credential, or release activation occurred.
release_and_owner_gates: >-
  Live `HUMAN_TODO.md` remains the owner-gate source: joint release remains reaffirmed, but no tag is
  authorized. The closed product
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` gate does not close the distinct open Lab
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8` real-study public-transformation gate.
  Product `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)` release sign-off and Lab
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11` aesthetic sign-off still block tags. Lab
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-7` legal review and
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13` machine hygiene remain open; the separate
  Code of Conduct inbox is pending under `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10`. None authorizes release,
  publication, data, model, credential, or telemetry work.
capabilities:
  network_collection: disabled (authorized in principle; gated on LAB-ACT-01 preconditions)
  external_model: disabled (auto-hypotheses authorized in principle; gated + product-side)
  real_data: disabled (authorized in principle; gated on LAB-ACT-01 preconditions)
  product_integration: bounded_c0_presentation_approved
  product_promotion: prohibited (stable channel stays product-governed)
canonical_evidence:
  run_id: wbc1_demo
  producer_commit: 0ef193070a9b80b81cef5a1710a1d65e0b271c15
  product_contract_commit: b48fea579936671397a0486ae7a0342197ee6e4b
  product_fixture_merge_commit: 8de65a22fe8a65ced893278a4e5a6835d778d65c
  lab_merge_commit: 1ac32f42e0f6cec57f6ce5ff37fd01e175a4b009
  decision: reject
  metrics: >-
    baseline_false_alerts_per_year=2.966666666666667; baseline_detection=0.75;
    candidate_false_alerts_per_year=4.2; candidate_detection=0.75;
    candidate_brier=0.017341137335170863
  gates: fail/fail/pass/pass/fail/pass/pass
  cases: no_change/level/parser_shift; 104_points_each; deterministic final-holdout selection
  fixture_sha256: sha256:afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9
  report_sha256: >-
    markdown=f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8;
    html=22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29
  current_head_replay: >-
    deterministic at lab_commit=2e6a7c2b7ff906cb771bb4e904dd18d2717fa536, but that lab_commit is a
    historical anchor many merges old and is NOT current main; it was not re-measured at
    07929a41fa8c80f05794db9a58fa0bf014b4f961. The candidate hashes differ because lab_commit is
    embedded, so the current-head release candidate remains NOT approved a fortiori — a newer head
    can only change the embedded value again. frozen_producer_replay stays the verified exhibit path
  frozen_producer_replay: >-
    verified at producer_commit=0ef193070a9b80b81cef5a1710a1d65e0b271c15; context/contracts/invented
    wbc1_demo/reproduce/export/report/hygiene all passed; printed export/markdown/html hashes exactly
    match the frozen claims without byte inspection; current-head candidate rejected
  product_tracked_fixture_schema_check: >-
    Product commit 7bbb8ee6f9124424b3d8362170f0f4d738f5cb43; 26 focused tests and
    `npm run check:method-trial-view` passed. Product origin/main is now
    7ae4b31861ad5403587adf8fefb90a085598bd57 after routing-only PR #229; the fixture/schema proof
    was not rerun because that merge did not touch the proved seam
blockers: >-
  No dependency-alert blocker remains: issue #5 is closed and the post-merge alert count is zero.
  The FR-028 merge-eligibility helper is DELIVERED and no longer blocks. The pre-tag remainder is
  Lane-P provenance selection, the Lane-P release review (stage only), the final changelog sync, and
  the screenshot/video package; the three tracked helper-hardening follow-ups on issue #29 are later
  work. The joint tag remains blocked on that remainder plus
  Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c) and
  Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11; no tag is authorized.
  Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13 cleanup is open but does not block these C0
  preparation slices.
late_review_debt: >-
  Issue #31 tracks the four non-blocking PR #24 review follow-ups; product #189 remains a product-side
  follow-up; issue #23 tracked as LAB-CONTRACT-03 (product-owned schema change); issue #6 remains open
  even though LAB-WBC1-06 is DONE.
exact_resume_point: >-
  Resume with the live SENSE/RECONCILE described in `next_safe_slice`, not with another PR #65 fix
  push. The selected next seam is Lane-P provenance selection of the frozen producer
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15` as the release exhibit, under owner decision U3=FREEZE
  and FR-019's recorded unlocking condition. PR #65 remains parked at
  exact head `91cf991b96b242680ab6839decb110422ab9755d` over base
  `bf5b01db178c4dbbbea4ca9dafc5c3fc181b3e2c`; its portable patch/comment IDs are a parked reference
  only and require a genuinely new unlocking event or explicit fresh authority before reopening.
  The last landed main anchor is PR #68 at `07929a41fa8c80f05794db9a58fa0bf014b4f961`. Preserve
  the parked short-redaction lane anchor: branch `fix/package-smoke-short-env-redaction-20260809` at
  `e673102348e8ee7d8c7d45b6ed4e1530cd775972`, after 194 passed / 3 skips and two package-smoke
  uv-pip-install timeouts, with issue #29 comment `5234405496` as the unlocking source. It is not the
  selected slice. Keep release/publication, tag, credentials, data, model, telemetry, and all owner
  gates closed.
```
