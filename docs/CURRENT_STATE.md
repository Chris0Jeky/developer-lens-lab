# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-09
phase: M3_GOVERNOR_CONTROL_PLANE
posture: public repository; constitution v2 recorded (docs/OWNER_CONSTITUTION.md) — real
  own/curated data, layered people/team research, and raw content are authorized in principle,
  but runtime and tracked inputs remain C0 invented until the activation preconditions in
  .agent-harness/governor.json are mechanically true; tier stays truthfully T1/sensitive_data=false
repository: Chris0Jeky/developer-lens-lab (public)
branch: main
head: refresh with git rev-parse origin/main
active_wave:
  - lane: LAB-REL-01 v0.1.0 release wave (issue #29)
    writer: branch `ci/lab-sdist-lineage-20260809` with code head
      `a23fbcd47b78d4c22400bcc7a217b70a0a9966f3` and main-integration commit
      `2c838bb5d1306434767a90279c6be8fab8a094e5` in its coordinator-owned isolated worktree
    state: ACTIVE after LAB-GOV-01, LAB-WBC1-06, LAB-GOV-02, dependency remediation #5, the
      distinct-signoff release prompt and changelog, and the non-credential package-smoke,
      timeout, ignored-tree exclusion, bounded diagnostics, traversal pruning, PATH/uv validation,
      and diagnostic-redaction/state-reconciliation seams all merged. Sdist-to-wheel lineage is
      implemented, locally proved, and integrated with live main; finish its scoped current-base
      proof and publish it under the ordinary gate. Keep later hardening, asset, and tag work
      separate, with no data activation.
delivered:
  - LAB-GOV-02: DONE — lab PR #35 merged at bba0c18261c0a2b77332a0408f63b10c774c91f4 and
      closed issue #33. This records the merged result only; it does not attribute the GitHub
      operation to an actor.
  - product_concurrent_writer_gate: Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8 is closed by
      direct owner decision and clean-session evidence, recorded through product PR #223 at
      877f1ca07ccee014c0adf50925f989815e6bc7f1. This does not close or alter this repository's
      Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8 real-study public-transformation gate.
  - dependency_remediation: DONE — PR #38 final head `4ebb1049ddb831dc7ff76f5a0050e52bdf37f40c`
      passed hosted proof and independent review, then merged as
      `f893f576f71202375fe93e8c7d9c02e54fbaf08a`; GitHub indexed `main` with zero open Dependabot
      alerts and issue #5 closed at 05:46Z.
  - release_prompt_guard: DONE — exhausted PR #37 was archived without a third fix commit;
      replacement PR #42 changed only DL-P09 at final head `e290d1b94aff9f39de677fd80670f4f9e8f15227`
      and merged as `38ac2eb14c8c9ba742b5f269b7022c7e549b7a5d` after exact hosted proof and fresh review.
  - friction_reconciliation: DONE — PR #41 final head
      `3604e301a5e9930e56edce193ea293698a4870bd` merged as
      `178bd6d695119b74294a8fd6fbe46f54577e49b2`; FR-008 through FR-014 are durably recorded, while
      FR-009/FR-010 enforcement remains task debt on issue #34 and escaped-environment cleanup is
      owner-gated at `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13`.
  - state_reconciliation: DONE — PR #39 final head
      `b36bbadd0365a8958ba741e27c2e36e9458237be` merged as
      `4f355f1e58e1eca1191f899f1fc4354af8a23a00`; exact hosted proof passed, late review was triaged,
      and the resulting wording debt is repaired in the next delivered slice.
  - licence_package_identity: DONE — PR #40 final head
      `7d5610d2280e900d9e2c10c6304455830147ffcd` merged as
      `d203461c023e1661140a1fef38a0f4b68e3454b2` after locked/full local proof, exact hosted proof,
      fresh review, and the bounded PR #39 late-wording repair.
  - community_scaffolding: DONE — PR #43 final head
      `871e014c73972fd65b8e9cd39e0665b6b2cdb65d` merged as
      `56c889141cd4575d12f80c3e0a16a574277e0ddd` after locked/full local proof, exact hosted proof,
      fresh review, complete thread triage, and the neutral public-contact privacy repair.
  - release_notes: DONE — PR #44 final head `ca8c075d286e7812873b86e12c54868b71519217`
      merged as `2e6a7c2b7ff906cb771bb4e904dd18d2717fa536` after exact hosted proof, fresh review, and a clean
      delayed sweep.
  - package_smoke: DONE — PR #45 final head `7f07ce221b7a405c06af70d3a5215910dca72991` passed
      hosted run `31304528858` / job `93222641130` and exact-final-head review, then merged as
      `6e13b6d84391ea7a2579e169151e3d765ad71583` with four pre-merge threads resolved. Its delayed
      sweep found two additional P2s; both were tracked and resolved, leaving all six threads
      resolved. Full local proof was 154 passed / 3 declared skips, including the isolated wheel
      smoke.
  - package_smoke_timeout: DONE — PR #47 final head
      `ea9b39d663bc2edf020d9853ddf854d9cd0cefdc` passed hosted run `31306259562`, exact-final-head
      review, and merge gating, then merged as `c827d6a18490838ab132fc7dc058c29fc727d68b`.
  - package_smoke_scan: DONE — PR #48 final head
      `89cad7d1dff4b00db9459f2739f1db567d266351` passed hosted run `31307153939` / job
      `93229202173`, exact-final-head review, and merge gating, then merged as
      `0b7a452ee0a6ce4c69e91646400fbb98ad8f3ca1`.
  - package_smoke_diagnostics: DONE — PR #49 final head
      `02d3e504b4fde54bd1e33b01d24b33a4de3305c5` passed hosted run `31307993706` / job
      `93231285624`, exact-final-head review, and merge gating, then merged as
      `ece61e0e1ca86e1e38732916fc077c4718bf7de6`; two delayed P2 threads were tracked and resolved.
  - context_traversal_pruning: DONE — PR #50 final head
      `086c9809ae2fd27b0a1bc485d4653764aea8ec08` passed hosted run `31308683005` / job
      `93232990186`, exact-final-head review, and merge gating, then merged as
      `e63086b4ae3b97390969357ebdd9d3e30394814e`.
  - package_smoke_uv_validation: DONE — PR #51 final head
      `adc43aea21834683eaf2749fe3515f10da204bde` passed hosted run `31313571499` / job
      `93245084619` and exact-final-head review, then merged as
      `02a41cac4a461a93d53b481d34c96a48e29291e5` before the binding 15-minute exact-head age;
      FR-028 records the gate miss. Its delayed sweep was otherwise clean.
  - package_smoke_redaction: DONE — PR #52 final head
      `46961957e09bb976b34beb41fee5e69d89d21076` passed hosted run `31332413187` / job
      `93292650747`, exact-final-head review, and the locked local gate, then merged as
      `b966341d293a50d2b51f448fa23d3248d7e575fd`; both review threads are resolved and its delayed
      19:51Z sweep found no new feedback. FR-025 records the separate pre-merge snapshot miss;
      FR-028 records the second exact-head aging-floor miss and selected enforcement layer.
  - diagnostic_state_reconciliation: DONE — PR #54 final head
      `a4eefd9cc4963f684c0376543600969c45d6d057` passed hosted run `31333721317` / job
      `93295965974`, exact-final-head review, the 15-minute age, and complete thread triage, then
      merged as `7fea25023d0704aea685e243708328264b9bcaad` at 20:33:27Z; its delayed 20:37Z sweep was clean.
      FR-032 and FR-033 record the final-snapshot TLS retry and the observed external state
      transition.
next_safe_slice: Finish scoped current-base proof on preserved branch
  `ci/lab-sdist-lineage-20260809`, then publish it under the exact-head hosted, review, and
  15-minute aging gate. Pre-cap diagnostic-memory hardening remains task debt until a design
  avoids both unbounded capture and a raw unredacted disk sink; process-tree cleanup stays separate.
  Lane-P candidate-content review, screenshots, publication, and owner-gated release lanes remain
  parked. Do not inspect ignored candidate bytes, publish assets, tag, add credentials, activate
  data or models, or enable telemetry.
release_and_owner_gates: joint release remains reaffirmed, but no tag is authorized.
  Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c) release sign-off and
  Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11 aesthetic sign-off still block tags. A
  separate Code of Conduct inbox is selected, but its address is pending under
  Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10; CLA and all other owner choices remain deferred.
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13` is separate machine hygiene and does not
  block release preparation or authorize inspection of the two private-handoff targets.
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
  metrics: baseline_false_alerts_per_year=2.966666666666667; baseline_detection=0.75;
    candidate_false_alerts_per_year=4.2; candidate_detection=0.75;
    candidate_brier=0.017341137335170863
  gates: fail/fail/pass/pass/fail/pass/pass
  cases: no_change/level/parser_shift; 104_points_each; deterministic final-holdout selection
  fixture_sha256: sha256:afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9
  report_sha256: markdown=f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8;
    html=22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29
  current_head_replay: deterministic at lab_commit=2e6a7c2b7ff906cb771bb4e904dd18d2717fa536;
    candidate hashes differ because lab_commit is embedded; release candidate NOT approved
  frozen_producer_replay: verified at producer_commit=0ef193070a9b80b81cef5a1710a1d65e0b271c15;
    context/contracts/invented wbc1_demo/reproduce/export/report/hygiene all passed; printed
    export/markdown/html hashes exactly match the frozen claims without byte inspection; current-head
    candidate rejected
  product_tracked_fixture_schema_check: product commit
    7bbb8ee6f9124424b3d8362170f0f4d738f5cb43; 26 focused tests and
    `npm run check:method-trial-view` passed. Product origin/main is now
    7ae4b31861ad5403587adf8fefb90a085598bd57 after routing-only PR #229; the fixture/schema proof
    was not rerun because that merge did not touch the proved seam
blockers: No dependency-alert blocker remains: issue #5 is closed and the post-merge alert count is
  zero. The joint tag remains blocked on issue #29's tracked P2 hardening and unfinished pre-tag
  deliverables plus
  Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c) and
  Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11; no tag is authorized.
  Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13 cleanup is open but does not block these C0
  preparation slices.
late_review_debt: issue #31 tracks the four non-blocking PR #24 review follow-ups; product
  #189 remains a product-side follow-up; issue #23 tracked as LAB-CONTRACT-03
  (product-owned schema change); issue #6 remains open even though LAB-WBC1-06 is DONE
exact_resume_point: Resume preserved branch `ci/lab-sdist-lineage-20260809`; code head
  `a23fbcd47b78d4c22400bcc7a217b70a0a9966f3` is integrated with Lab main merge
  `7fea25023d0704aea685e243708328264b9bcaad` through integration commit
  `2c838bb5d1306434767a90279c6be8fab8a094e5`. Finish scoped current-base context, static, test,
  hygiene, and diff proof, then publish the current branch head for issue #29. Commits
  `b640d8a7fecbb96a3fed88aa8e27afaeaeb22d4d` and
  `a23fbcd47b78d4c22400bcc7a217b70a0a9966f3` build exactly one sdist, build exactly one wheel from
  that selected archive, and add typed synthetic lineage/fail-closed tests; the combined locked
  gate passed 179 tests with 3 declared skips plus automated actual smoke in 87.5 seconds.
  PR #52 final head `46961957e09bb976b34beb41fee5e69d89d21076` and hosted run `31332413187`
  are green and merged as `b966341d293a50d2b51f448fa23d3248d7e575fd`; FR-025 records its
  missed top-level-comment snapshot and FR-028 records the unsatisfied 15-minute exact-head age.
  The frozen producer replay at
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15` and product tracked fixture/schema proof at product
  commit `7bbb8ee6f9124424b3d8362170f0f4d738f5cb43` are complete; current product `origin/main` is
  `7ae4b31861ad5403587adf8fefb90a085598bd57`. Do not substitute the
  rejected current-head candidate, inspect ignored candidate bytes, or cross the Lane-P
  publication/sign-off boundary. Keep
  Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-7
  (CLA/external-contribution strategy), Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11
  (aesthetic sign-off), Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c) release sign-off, and
  every non-C0 lane explicit and closed as applicable; tag, credentials, data, models, and
  telemetry remain closed.
```
