# Experiment protocol

Every experiment walks an explicit state machine; the experiment ledger records each transition
with evidence. Scientific proof and repository proof are distinct and both required.

## Lifecycle

`IDEA → QUESTION_DEFINED → PREREGISTERED → DATA_AUTHORISED → READY → RUNNING → RUN_RECORDED →
REPRODUCED → INDEPENDENT_REVIEW → DECIDED → (PRODUCT_PROPOSAL) → ARCHIVED`

`DECIDED` is exactly one of `REJECTED`, `REVISE_ONCE`, `BENCHMARKED`, `ABSTAINED`, or
`INVALIDATED`. A reproduced negative result is a valid result. A failed run is not a scientific
decision — it is a failed run.

## Rules

- **Preregistration before running.** Question, cohort/window, splits, primary metric,
  guardrails, uncertainty method, abstention/minimum-support rules, and threshold-selection
  budget are fixed before the run. Post-hoc characterisations are labelled as such, never
  back-dated (see the #4 correction precedent in the experiment ledger).
- **Dataset and holdout authority before RUNNING.** The dataset lane and its authority are named
  per [DATASET_PROTOCOL.md](DATASET_PROTOCOL.md); the final holdout is consumed once, only under
  the preregistered plan, with a custody event recorded immediately. A consumed holdout is never
  reused for a revised candidate — that would be outcome-aware even under a new preregistration.
- **Baseline fairness.** The deterministic baseline receives the same selection budget as every
  candidate; transforms and thresholds fit inside training only; generator/seed-family
  identifiers never enter features or reports.
- **Historical runs are immutable evidence.** Reruns get new IDs; ledgers are append-only and
  corrections are appended, never rewritten.
- **Reports distinguish** mechanics evidence (synthetic), own-data observation, and external
  validation — an invented result never claims empirical validity.
- **Product promotion is separate.** Even `BENCHMARKED` is research evidence; stable product
  integration runs through product-owned compatibility (`PRODUCT_PROPOSAL` state), and an
  EvaluationBundle can never say `ship`.

## Independent review lenses

Non-trivial experiments get a fresh-context methodology review covering: construct validity;
cohort/window; missingness and censoring; leakage; split/holdout integrity; baseline fairness;
threshold selection; uncertainty and calibration; confounds; alternatives and
counter-hypotheses; public claim strength; reproducibility; and whether the result is useful at
all. The reviewer may reject the methodology outright.

## Archival

Killed approaches go to the failure archive with why; decisions and custody events go to the
experiment ledger; code milestones go to the implementation ledger; `docs/CURRENT_STATE.md`
moves only at phase boundaries.
