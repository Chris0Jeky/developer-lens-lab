# Current state

Live Git and CI outrank this file. Historical ledgers never override it.

```yaml
updated: 2026-08-06
phase: M0_REPOSITORY_OS_PUBLICATION_GATE
posture: public C0 invented-data-only; value-first with non-essential hardening deferred
repository: Chris0Jeky/developer-lens-lab (public)
branch: codex/bootstrap-lab-os
head: refresh with git rev-parse HEAD
active_horizon:
  - LAB-OS-01
  - LAB-TOOL-01
  - LAB-CONTRACT-01
  - LAB-CONTRACT-02
  - LAB-ART-01
  - LAB-WBC1-01
product_state_correction: developer-lens blueprint snapshot PR #167 is stale; refresh product Git
capabilities:
  network_collection: disabled
  external_model: disabled
  real_data: disabled
  product_promotion: owner_gated
blockers: none for invented bootstrap; q-1 through q-6 gate expansion only
hardening: docs/HARDENING_BACKLOG.md; debt is visible but does not block M0-M2 unless it crosses an
  irreversible secret/private-data/out-of-root/person-shape boundary
exact_resume_point: continue the stacked M1 contracts branch while the green M0 bootstrap PR ages;
  do not mark M0 done or merge dependent work to main until M0 lands, then retarget and re-prove M1
```
