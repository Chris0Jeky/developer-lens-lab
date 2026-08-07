# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-07
phase: M2_WBC1_PRINCIPAL_DEMO_FINAL_GATES
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: codex/method-trial-demo
head: refresh with git rev-parse HEAD
active_horizon:
  - LAB-WBC1-01
  - LAB-WBC1-05
  - LAB-BRIDGE-01
  - LAB-DEMO-01
product_state: product ResearchPack PR #178, lab WB-C1 foundation PR #3, and product MethodTrial PR
  #187 are merged; #187 owns the contract and lazy presentation route. Product correction commit
  1e1214d pins the integrated producer bytes and must merge before lab PR #8
capabilities:
  network_collection: disabled
  external_model: disabled
  real_data: disabled
  product_integration: bounded_c0_presentation_approved
  product_promotion: prohibited
canonical_evidence:
  run_id: wbc1_demo
  producer_commit: 0ef193070a9b80b81cef5a1710a1d65e0b271c15
  product_contract_commit: b48fea579936671397a0486ae7a0342197ee6e4b
  decision: reject
  metrics: baseline_false_alerts_per_year=2.966666666666667; baseline_detection=0.75;
    candidate_false_alerts_per_year=4.2; candidate_detection=0.75;
    candidate_brier=0.017341137335170863
  gates: fail/fail/pass/pass/fail/pass/pass
  cases: no_change/level/parser_shift; 104_points_each; deterministic final-holdout selection
  fixture_sha256: sha256:afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9
  report_sha256: markdown=f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8;
    html=22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29
blockers: merge product correction PR #190 after its exact-head hosted/review/aging gates; verify
  its merged contract and fixture bytes; then prove and resolve the lab full-benchmark preservation
  repair and merge lab PR #8 after its exact-head hosted/review/aging gates
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
late_review_debt: lab #6 and product #189 are explicit non-blocking follow-ups; neither changes the
  conservative WB-C1 reject decision
exact_resume_point: finish product correction PR #190, run the merged-contract and fixture byte
  check, finish the lab full-benchmark repair gate on PR #8, merge it, and perform one late-comment
  sweep per PR before considering product #174
```
