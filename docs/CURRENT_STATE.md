# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-06
phase: M2_WBC1_SMOKE_IN_REVIEW
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
blockers: GitHub Actions is in a declared critical outage, so Developer Lens producer PR #178 and
  the lab WB-C1 PR cannot claim hosted exact-head proof; no implementation or owner blocker exists
  for the invented vertical
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
exact_resume_point: finish the clean-head WB-C1 smoke/replay proof and fresh-context review, then
  publish the lab PR dependency-gated on Developer Lens producer PR #178; merge neither around a
  missing required hosted check
```
