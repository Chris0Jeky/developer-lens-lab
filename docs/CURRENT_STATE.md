# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-08
phase: M3_GOVERNOR_CONTROL_PLANE
posture: public repository; constitution v2 recorded (docs/OWNER_CONSTITUTION.md) — real
  own/curated data, layered people/team research, and raw content are authorized in principle,
  but runtime and tracked inputs remain C0 invented until the activation preconditions in
  .agent-harness/governor.json are mechanically true; tier stays truthfully T1/sensitive_data=false
repository: Chris0Jeky/developer-lens-lab (public)
branch: main
head: refresh with git rev-parse origin/main
active_wave:
  - lane: LAB-REL-01 v0.1.0 release wave (issue #29 / dependency triage #5)
    state: ACTIVE after LAB-GOV-01 and LAB-WBC1-06 completion; writer unassigned; no data
      activation; licence/community/packaging and dependency triage are separate slices
backlog_next: LAB-ACT-01 real-data activation preconditions; LAB-SURV-01 product #174
  survival study; LAB-CONTRACT-03 MethodTrialView preference reconcile (#23, product-owned)
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
blockers: dependency re-lock (issue #5) remains unperformed; a worktree-local uv 0.12.3
  bootstrap and locked environment can run on this host (proved this session), so tool
  availability is no longer the blocker — the selected work is not yet implemented
late_review_debt: issue #31 tracks the four non-blocking PR #24 review follow-ups; product
  #189 remains a product-side follow-up; issue #23 tracked as LAB-CONTRACT-03
  (product-owned schema change); issue #6 remains open even though LAB-WBC1-06 is DONE
exact_resume_point: begin LAB-REL-01 with an isolated dependency-triage #5 slice using a
  worktree-local uv bootstrap; keep licence/community/packaging/release-asset work separate;
  keep q-7 (CLA/external-contribution strategy) and q-11 (aesthetic sign-off) gates explicit;
  keep every non-C0 lane closed
```
