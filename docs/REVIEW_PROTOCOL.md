# Review protocol

Every PR receives one real exact-head review. Documentation-only or very-low-risk work may use a
clean automated review; code or methodology gets one fresh-context adversarial review. A second
distinct lens is reserved for genuinely high-risk privacy/evaluation work.

Reviewers attempt to falsify:

- correctness, failure paths, atomic confinement, and deletion scope;
- baseline fairness and equivalent selection budgets;
- future, provider-lag, coverage, label/seed, repository, duplicate, normalization, threshold,
  censoring, holdout, retention, and person-shaped leakage;
- data minimization and prohibited-field survival;
- deterministic replay, manifest redaction, and no-model fallback;
- calibration, abstention, negative controls, and interpretation limits.

Fix only confirmed CRITICAL/HIGH correctness, security, data-loss, privacy, or evaluation-integrity
defects in the bounded review cycle. Track or decline other findings explicitly. After review-driven
logic changes, rerun affected proof and refresh the final-head lens. Never merge red CI, from draft,
or before the three-minute post-push floor. Operational outages belong in the implementation ledger;
only an actual owner decision belongs in `HUMAN_TODO.md`.
