# Generated task-card index

Generated from `tools/cards.py`; do not edit by hand.

| Card | Title | Status | Depends on | Outcome |
|---|---|---|---|---|
| `LAB-OS-01` | Repository OS and context verifier | DONE | — | Fresh-agent resume |
| `LAB-TOOL-01` | Python, uv, tooling, and CI | DONE | LAB-OS-01 | Locked checks |
| `LAB-CONTRACT-01` | ResearchPack.v1 contracts | DONE | LAB-OS-01 | Pack validation |
| `LAB-CONTRACT-02` | EvaluationBundle.v1 contracts | DONE | LAB-OS-01 | Decision bundle validation |
| `LAB-ART-01` | Confined content-addressed artifact store | DONE | LAB-TOOL-01 | Replayable objects |
| `LAB-WBC1-01` | Invented weekly-series smoke benchmark | DONE | LAB-CONTRACT-01, LAB-ART-01 | Inspectible rejection decision |
| `LAB-SYNC-01` | Generated product-contract snapshot | DONE | LAB-CONTRACT-01 | Pinned provenance |
| `LAB-RUN-01` | Reproducible run manifest and replay | DONE | LAB-ART-01 | One-command replay |
| `LAB-SPLIT-01` | Repository, time, and seed-family split engine | DONE | LAB-CONTRACT-01 | Leakage-safe splits |
| `LAB-HOLDOUT-01` | Explicit final-holdout custody | DONE | LAB-SPLIT-01 | Single-use holdout |
| `LAB-WBC1-02` | Rolling median and MAD baseline | DONE | LAB-WBC1-01 | Deterministic fallback |
| `LAB-WBC1-03` | Online change-point candidate | DONE | LAB-WBC1-02 | Baseline comparison |
| `LAB-WBC1-04` | PELT offline descriptive arm | DONE | LAB-WBC1-02 | Localisation evidence |
| `LAB-WBC1-05` | Evaluation bundle and decision report | DONE | LAB-WBC1-03 | Reviewable result |
| `LAB-WBC1-06` | WB-C1 late-review correctness debt (issue #6) | IN_REVIEW | LAB-WBC1-05 | Reproducer-backed fixes |
| `LAB-BRIDGE-01` | Product and lab compatibility fixture | DONE | LAB-SYNC-01 | Both-end proof |
| `LAB-DEMO-01` | End-to-end smoke demo and runbook | DONE | LAB-WBC1-05 | Fresh-clone proof |
| `LAB-CORPUS-01` | Public-repository sampler manifest | BACKLOG | LAB-ACT-01 | Quality pilot only |
| `LAB-CORPUS-02` | Bounded public metadata collector | BACKLOG | LAB-CORPUS-01, LAB-ACT-01 | No raw landing |
| `LAB-CORPUS-03` | Normalizer and coverage profiler | BACKLOG | LAB-CORPUS-02, LAB-ACT-01 | Explicit coverage |
| `LAB-DQ-01` | Data-quality and candidate-support report | PARKED | LAB-CORPUS-03 | Expansion decision |
| `LAB-GOV-01` | Research governor control plane | DONE | LAB-OS-01 | Governor seeded |
| `LAB-ACT-01` | Real-data activation preconditions (tier flip, executable sinks and deny rules, secret scanning) | BACKLOG | LAB-GOV-01 | Non-C0 lanes unlocked |
| `LAB-REL-01` | v0.1.0 release wave: AGPL and notices, community files, package metadata, dependency triage (issue #5), C0 release assets | BACKLOG | LAB-GOV-01 | Tagged v0.1.0 |
| `LAB-SURV-01` | Integration-tail survival study (product issue #174): KM + AFT over the product input contract | BACKLOG | LAB-BRIDGE-01, LAB-WBC1-06 | Product-owned view + rich report |
| `LAB-CONTRACT-03` | MethodTrialView representative-preference reconcile (issue #23; product-owned schema change) | BACKLOG | LAB-BRIDGE-01 | Contract-faithful preference declaration |
