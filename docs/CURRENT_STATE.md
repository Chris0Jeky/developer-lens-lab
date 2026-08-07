# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-07
phase: M2_WBC1_DEMO_PREFLIGHT_IN_REVIEW
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: codex/method-trial-demo
head: refresh with git rev-parse HEAD
active_horizon:
  - LAB-WBC1-01
  - LAB-WBC1-05
  - LAB-BRIDGE-01
  - LAB-DEMO-01
product_state_correction: the principal demo has only preflight evidence; no product fixture commit,
  product merge, hosted CI, lab PR/merge, or canonical final run is claimed here
capabilities:
  network_collection: disabled
  external_model: disabled
  real_data: disabled
  product_promotion: owner_gated
preflight:
  run_id: wbc1_demo_preflight
  lab_head: b865d6951e915ffedb4af512a0a673501d12e171
  decision: reject
  metrics: baseline_false_alerts_per_year=2.966666666666667; baseline_detection=0.75;
    candidate_false_alerts_per_year=4.2; candidate_detection=0.75;
    candidate_brier=0.017341137335170863
  cases: no_change/level/parser_shift; 104_points_each
  fixture_sha256_prefix: sha256:847e3c
  report_sha256_prefixes: markdown=3d47b2; html=4409373
blockers: the preflight is not a canonical final run; hosted CI, bounded review, and publication
  gates remain open
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
late_review_debt: lab #6 and product #182 are explicit non-blocking follow-ups; neither changes the
  conservative WB-C1 reject decision
exact_resume_point: refresh the principal demo preflight against the live branch, then run the
  bounded hosted/review gates before treating LAB-DEMO-01 as complete
```
