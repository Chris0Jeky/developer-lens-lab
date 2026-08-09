# Roadmap

This is a compact dependency order for the Lab, not a schedule or delivery promise. The active
release wave is **LAB-REL-01** (issue [#29](https://github.com/Chris0Jeky/developer-lens-lab/issues/29));
the detailed task-card source remains [`tools/cards.py`](tools/cards.py).

## Milestones

- **M0 — Repository OS and tooling:** authority, context verification, locked Python environment,
  CI, and documentation.
- **M1 — Runnable foundation:** strict ResearchPack/EvaluationBundle contracts, compatibility
  sync, content-addressed artifact store, and CLI.
- **M2 — WB-C1 smoke:** invented generator, deterministic baseline/candidates, disjoint splits,
  holdout, bundle, report, and explicit decision.
- **M3 — Corpus quality pilot:** owner-gated and inactive until its activation preconditions hold.
- **M4 — Empirical candidate:** separately authorised data, untouched holdout, and disclosed
  transformation; never a default activation.
- **M5 — Product proposal:** product-owned compatibility and promotion review; deterministic
  fallback remains complete and a rejection remains a valid outcome.

LAB-REL-01 prepares the v0.1.0 baseline around these milestones: licence and community scaffolding,
packaging and dependency health, and selected invented release evidence. It does not activate data,
models, telemetry, credentials, third-party ResearchPack producers, or product installation.

See [`docs/ROADMAP.md`](docs/ROADMAP.md), [`docs/PRODUCT_BOUNDARY.md`](docs/PRODUCT_BOUNDARY.md), and
[`docs/CONTRACTS.md`](docs/CONTRACTS.md) for the fuller boundaries and contract details.
