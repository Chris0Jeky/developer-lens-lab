# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-06
phase: M2_WBC1_SMOKE_READY_FOR_PR
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: codex/wbc1-smoke
head: refresh with git rev-parse HEAD
active_horizon:
  - LAB-WBC1-01
  - LAB-WBC1-05
  - LAB-BRIDGE-01
  - LAB-DEMO-01
product_state_correction: developer-lens blueprint snapshot PR #167 is stale; refresh product Git
capabilities:
  network_collection: disabled
  external_model: disabled
  real_data: disabled
  product_promotion: owner_gated
blockers: GitHub Actions is in a declared critical outage and webhook triggers are heavily
  throttled, so Developer Lens producer PR #178 and lab PR #3 cannot claim hosted exact-head proof;
  no remaining local implementation or owner blocker exists for the invented vertical
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
late_review_debt: lab #6 and product #182 are explicit non-blocking follow-ups; neither changes the
  conservative WB-C1 reject decision
exact_resume_point: refresh hosted checks on Developer Lens producer PR #178 at 61f9bdb and lab PR
  #3 at its latest head after the GitHub Actions incident; merge the producer first, then refresh
  and merge the lab only when both required exact-head checks are green
```
