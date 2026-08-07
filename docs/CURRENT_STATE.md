# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-07
phase: M2_WBC1_PRINCIPAL_DEMO_FINALIZATION_IN_REVIEW
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: codex/method-trial-demo
head: refresh with git rev-parse HEAD
active_horizon:
  - LAB-WBC1-01
  - LAB-WBC1-05
  - LAB-BRIDGE-01
  - LAB-DEMO-01
product_state_correction: product ResearchPack PR #178 and the lab WB-C1 foundation PR #3 are
  merged; product PR #187 owns the MethodTrialView contract, fixed invented fixture, and lazy
  presentation route; lab PR #8 is the exporter/report follow-up. Product #187 must merge before #8
capabilities:
  network_collection: disabled
  external_model: disabled
  real_data: disabled
  product_promotion: owner_gated
canonical_evidence:
  run_id: wbc1_demo
  producer_commit: b30b22909c9ea44d64bebe9dccf82b8735302d76
  product_contract_commit: b48fea579936671397a0486ae7a0342197ee6e4b
  decision: reject
  metrics: baseline_false_alerts_per_year=2.966666666666667; baseline_detection=0.75;
    candidate_false_alerts_per_year=4.2; candidate_detection=0.75;
    candidate_brier=0.017341137335170863
  cases: no_change/level/parser_shift; 104_points_each
  fixture_sha256: sha256:f87ca9447d320ad7328995cfb5ddef84219dadd5b03092c520b809bd8fb6cfeb
  report_sha256: markdown=482b7c458ff0a33f0d945134241a9a8b500f5f74bb5bde31bb5b67f8f04b9c99;
    html=5bf496b7c6161f381db6b51cae89df06739a6f0aa4daec7eb146c6e7c19e962e
blockers: exact final hosted CI, connector-thread triage, and merge gates remain open; product PR
  #187 must merge first, then the lab must recheck the merged product contract bytes before #8 merges
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
late_review_debt: lab #6 and product #189 are explicit non-blocking follow-ups; neither changes the
  conservative WB-C1 reject decision
exact_resume_point: refresh PRs #187 and #8; prove the product fixture is byte-identical to the
  b30b229 export, finish exact-head CI/review, merge product first, recheck its merge-commit contract
  bytes from the lab, then merge the lab and perform one late-comment sweep
```
