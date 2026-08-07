# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-07
phase: M2_WBC1_DEMO_INTEGRATION_READY
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: codex/method-trial-demo
head: refresh with git rev-parse HEAD
active_horizon:
  - LAB-WBC1-01
  - LAB-WBC1-05
  - LAB-BRIDGE-01
  - LAB-DEMO-01
product_state: product PR #187 merged as 7b22491b28acbe467e2facb85723a91fd37af52b after
  exact-head hosted proof and review; lab PR #8 is now the ordered follow-up
capabilities:
  network_collection: disabled
  external_model: disabled
  real_data: disabled
  product_integration: bounded_c0_presentation_approved
  product_promotion: prohibited
canonical_demo:
  run_id: wbc1_demo
  producer_commit: 5c79236beb0a0b25819f14510b79bb15813d7337
  product_contract_commit: b48fea579936671397a0486ae7a0342197ee6e4b
  product_fixture_head: 53f0cfda65392fc2a3763bff9284b6af80aa1e98
  product_merge_commit: 7b22491b28acbe467e2facb85723a91fd37af52b
  decision: reject
  metrics: baseline_false_alerts_per_year=2.966666666666667; baseline_detection=0.75;
    candidate_false_alerts_per_year=4.2; candidate_detection=0.75;
    candidate_brier=0.017341137335170863
  gates: fail/fail/pass/pass/fail/pass/pass
  cases: no_change/level/parser_shift; 104_points_each; deterministic final-holdout selection
  fixture_sha256: sha256:26c3a9184adfce4ff5756e702b36d6db7af7c5f2dab9eb3eb3081ca598eafd95
  report_sha256: markdown=8144410775717d8b280a41b95c18dd22a8de45c765186ecaeb1fd5c6745e30f0;
    html=fca7aac3e567f6de84b6dd60f476e77bf2a18f7a20cefde4563856e6ada99eec
  hosted: lab run 31150109110 passed at producer commit; product run 31150326515 passed at fixture head
blockers: merge lab PR #8 after the final full-benchmark preservation repair passes its hosted
  gate, review/thread sweep, and aging floor; the product dependency, merged-schema check, and
  exact producer byte comparison pass
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
late_review_debt: lab #6 and product #182 are explicit non-blocking follow-ups; neither changes the
  conservative WB-C1 reject decision
exact_resume_point: prove and resolve the final full-benchmark preservation repair on lab PR #8,
  merge it with history preserved, and close the bounded programme before considering product #174
```
