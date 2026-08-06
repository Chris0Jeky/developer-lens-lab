# Generated task-card index

Generated from `tools/cards.py`; do not edit by hand.

| Card | Title | Status | Depends on | Outcome |
|---|---|---|---|---|
| `LAB-OS-01` | Repository OS and context verifier | DONE | — | Fresh-agent resume |
| `LAB-TOOL-01` | Python, uv, tooling, and CI | DONE | LAB-OS-01 | Locked checks |
| `LAB-CONTRACT-01` | ResearchPack.v1 contracts | IN_REVIEW | LAB-OS-01 | Pack validation |
| `LAB-CONTRACT-02` | EvaluationBundle.v1 contracts | IN_REVIEW | LAB-OS-01 | Decision bundle validation |
| `LAB-ART-01` | Confined content-addressed artifact store | IN_REVIEW | LAB-TOOL-01 | Replayable objects |
| `LAB-WBC1-01` | Invented weekly-series smoke benchmark | ACTIVE | LAB-CONTRACT-01, LAB-ART-01 | Inspectible rejection decision |
| `LAB-SYNC-01` | Generated product-contract snapshot | QUEUED | LAB-CONTRACT-01 | Pinned provenance |
| `LAB-RUN-01` | Reproducible run manifest and replay | QUEUED | LAB-ART-01 | One-command replay |
| `LAB-SPLIT-01` | Repository, time, and seed-family split engine | QUEUED | LAB-CONTRACT-01 | Leakage-safe splits |
| `LAB-HOLDOUT-01` | Explicit final-holdout custody | QUEUED | LAB-SPLIT-01 | Single-use holdout |
| `LAB-WBC1-02` | Rolling median and MAD baseline | QUEUED | LAB-WBC1-01 | Deterministic fallback |
| `LAB-WBC1-03` | Online change-point candidate | QUEUED | LAB-WBC1-02 | Baseline comparison |
| `LAB-WBC1-04` | PELT offline descriptive arm | QUEUED | LAB-WBC1-02 | Localisation evidence |
| `LAB-WBC1-05` | Evaluation bundle and decision report | QUEUED | LAB-WBC1-03 | Reviewable result |
| `LAB-BRIDGE-01` | Product and lab compatibility fixture | QUEUED | LAB-SYNC-01 | Both-end proof |
| `LAB-DEMO-01` | End-to-end smoke demo and runbook | QUEUED | LAB-WBC1-05 | Fresh-clone proof |
| `LAB-CORPUS-01` | Public-repository sampler manifest | OWNER_GATED | — | Quality pilot only |
| `LAB-CORPUS-02` | Bounded public metadata collector | OWNER_GATED | LAB-CORPUS-01 | No raw landing |
| `LAB-CORPUS-03` | Normalizer and coverage profiler | OWNER_GATED | LAB-CORPUS-02 | Explicit coverage |
| `LAB-DQ-01` | Data-quality and candidate-support report | PARKED | LAB-CORPUS-03 | Expansion decision |
