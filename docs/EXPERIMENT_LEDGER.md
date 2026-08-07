# Experiment ledger

Experiment entries are append-only. Record preregistration ID, dataset card, input hashes, split
policy, holdout custody event, exact command, lock hash, result, decision, and residual limitations.

## 2026-08-06 — WB-C1 reviewed smoke (`wbc1_reviewed`)

- **Preregistration:** `WB.C1.CHANGE_POINT`; rolling median/MAD baseline; fixed-prior
  Adams–MacKay Gaussian BOCPD candidate; false alerts/year primary metric; candidate must pass
  selection viability, detection/delay/confound gates, and improve false alerts by at least 20%.
- **Command:** `uv run dllab benchmark wb-c1 --smoke --run-id wbc1_reviewed`, followed by
  `dllab run reproduce wbc1_reviewed` and `dllab report build wbc1_reviewed`.
- **Code and inputs:** lab `a01a3fd58c78b3c1a7092c1b00e804b3d7ce5eb8`; product contract
  `337d815f5af22691889f00b0ffa5e3cf61b65e74`; environment
  `sha256:e2c92328d1024d2aba0f04895fe5162dbfe54247472d2b8df13770522132e866`;
  dataset recipe `sha256:1b3f8e7d4531a20f788811f433c6196079759d5fd4ae5ec1dc1e96135dfcc00b`.
- **Dataset card and split:** invented C0; 54 system series / 5,616 weekly opportunities; 5,346
  present and 270 absent; disjoint train, test, and final-holdout aliases, seed families, and time
  windows. The panels are ordered but are not claimed as rolling-origin evaluation.
- **Custody:** append-only receipt
  `sha256:9154b5c6a0292061b3f7201c488fe6e9d9be2321dd998d4cf97e558de8534e60`
  bound the run ID, generator revision, dataset recipe, evaluation-plan hash, frozen thresholds, and
  method-parameter hashes before holdout materialization. The scope is single-use; replay verified
  the stored receipt and regenerated every recorded artifact.
- **Result:** baseline false alerts/year `2.966666666666667`, detection `0.75`; candidate false
  alerts/year `4.2`, detection `0.75`; candidate Brier `0.017341137335170863`. Decision: `reject`.
  Failed gates were `BASELINE_SELECTION_VIABLE`, `CANDIDATE_SELECTION_VIABLE`, and
  `CANDIDATE_FALSE_ALERT_IMPROVEMENT`. The deterministic baseline remains the complete fallback.
- **Artifacts:** EvaluationBundle
  `sha256:7bd2da8e88cdb960e52131ea680acc2c98346b1ed578380ea8276791a30717e5`;
  Markdown `sha256:ea40f0daa5c6314f6f533d646f2174d581a9c1f06b28f15934a877f6953dc165`;
  HTML `sha256:9d997d1f70ad147151ad6804f78c1c86a13f63b2ae8d8e5d8d21d9db7232b43b`.
- **Residual limitations:** synthetic mechanics evidence only; neither threshold selection was
  viable. Comparative exposure still includes method-specific warmup weeks. PELT reports
  boundary/localisation evidence, not a no-change false-boundary rate. Explicit generator parameters
  and a normalized command identifier are not yet first-class manifest fields. Hosted Linux proof
  was unavailable during GitHub's critical Actions outage.
