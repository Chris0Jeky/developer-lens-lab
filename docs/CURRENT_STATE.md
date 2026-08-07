# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-07
phase: M2_WBC1_PRINCIPAL_DEMO_COMPLETE
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: main
head: refresh with git rev-parse origin/main
active_horizon: []
product_state: product ResearchPack PR #178, lab WB-C1 foundation PR #3, product MethodTrial PR
  #187, product correction PR #190, and lab MethodTrial PR #8 are merged; product main owns the
  contract, lazy route, and exact integrated fixture, while the lab owns generation/evaluation
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
blockers: none for the bounded C0 MethodTrial vertical; the product PR #190 aging-floor miss is
  recorded as process noncompliance and does not change the verified reject result
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
late_review_debt: lab #6, lab #7, and product #189 are explicit non-blocking follow-ups; none changes
  the conservative WB-C1 reject decision
exact_resume_point: stop; no work remains in this vertical. A later authorized slice should start
  from fresh detached product/lab origin/main worktrees and select an explicit tracked residual or
  human action instead of extending the demo implicitly
```
