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

## 2026-08-07 — WB-C1 exact producer resync (`wbc1_demo`)

- **Preregistration and commands:** `WB.C1.CHANGE_POINT`; `uv run dllab benchmark wb-c1 --smoke
  --run-id wbc1_demo`, followed by `uv run dllab run reproduce wbc1_demo` and
  `uv run dllab report build wbc1_demo`.
- **Code and inputs:** lab `b4cdb364b753046588d3bd6c80e027c665b482fa`; merged product producer
  `be9c2451e983e776850c4cd4700cc8c234ea5e14`; producer schema
  `sha256:7734aad6635f840d16d8dda893f885911401fb32c36a51825d2d142eb6d3c2a2`;
  invented compatibility fixture
  `sha256:f2bb3da8407633c44dafb7177dccd8fb085f3838f1fc0813d076264afd59e3b4`;
  environment `sha256:e2c92328d1024d2aba0f04895fe5162dbfe54247472d2b8df13770522132e866`;
  dataset recipe `sha256:1b3f8e7d4531a20f788811f433c6196079759d5fd4ae5ec1dc1e96135dfcc00b`.
- **Dataset and custody:** invented C0; 54 system series / 5,616 weekly opportunities; 5,346
  present and 270 absent. The single-use custody object is
  `sha256:036f62f5f9ade272eba907513e7ab0bbef4a888bb1d86f8ae6e401aebd5c8238`.
  Reproduction verified the receipt and regenerated every recorded artifact byte-for-byte.
- **Result:** baseline false alerts/year `2.966666666666667`, detection `0.75`; candidate false
  alerts/year `4.2`, detection `0.75`; candidate Brier `0.017341137335170863`. Both threshold
  selections remain nonviable. The decision remains `reject`, with failed gates
  `BASELINE_SELECTION_VIABLE`, `CANDIDATE_SELECTION_VIABLE`, and
  `CANDIDATE_FALSE_ALERT_IMPROVEMENT`; the deterministic baseline remains the complete fallback.
- **Artifacts:** EvaluationBundle
  `sha256:71fd7c90daa794e58424a697984d89aba9f1166cc3af28e7ef2a1ebebb715a29`;
  Markdown `sha256:2c0a638711409122b984abd9d24dd1382f74d05f82508979621ec35e0c21848c`;
  HTML `sha256:53cf6c19906b3b478be2755b3fc3277364cf27fc7f5bef40c524c50970b78df1`.
- **Movement and limits:** the exact merged producer sync changed schema/fixture and artifact
  digests, but not the dataset recipe or canonical metrics/decision. This remains synthetic
  mechanics evidence only; issue #6 stays deferred and no product promotion is implied.

## 2026-08-07 - Principal demo preflight (`wbc1_demo_preflight`)

- **Status:** preflight only; keep `LAB-DEMO-01` `IN_REVIEW`. This is local evidence at lab head
  `b865d6951e915ffedb4af512a0a673501d12e171`, not a canonical final run or hosted/publication gate.
- **Flow:** benchmark, reproduce, canonical export, then report:
  `uv run dllab benchmark wb-c1 --smoke --run-id wbc1_demo_preflight`,
  `uv run dllab run reproduce wbc1_demo_preflight`,
  `uv run dllab demo export wbc1_demo_preflight --output <path>`, and
  `uv run dllab report build wbc1_demo_preflight`.
- **Dataset and cases:** C0 invented data only; 54 system series / 5,616 weekly opportunities /
  5,346 observed / 270 absent. Representative scenarios are `no_change`, `level`, and
  `parser_shift`, with 104 points in each case. No real data, public corpus, person-shaped unit,
  product UI code, additional candidate, or model promotion is part of this preflight.
- **Result:** decision `reject`. Baseline false alerts/year `2.966666666666667`, detection `0.75`,
  median delay `2`, confound rate `0.5`, measured threshold `2.5` marked nonviable. Candidate false
  alerts/year `4.2`, detection `0.75`, median delay `1`, confound rate `0.5`, Brier
  `0.017341137335170863`, measured threshold `0.05` marked nonviable. Failed gates are
  `BASELINE_SELECTION_VIABLE`, `CANDIDATE_SELECTION_VIABLE`, and
  `CANDIDATE_FALSE_ALERT_IMPROVEMENT`; the deterministic baseline remains the complete fallback.
- **Preflight provenance:** compatibility fixture digest prefix `sha256:847e3c`, product contract
  prefix `2fd1637`, schema digest prefix `86cf53a`, and ResearchPack merge reference `be9c245`.
  Report references are Markdown digest prefix `3d47b2` and HTML digest prefix `4409373`.
- **Limits:** issue #6 remains deferred. Hosted CI, product fixture commit/product merge claims,
  lab PR/merge, and canonical final-run status are not verified here.

## 2026-08-07 - Superseded parallel final-run evidence

- **Status:** producer commits `5c79236beb0a0b25819f14510b79bb15813d7337` and
  `b30b22909c9ea44d64bebe9dccf82b8735302d76` each produced a deterministic `wbc1_demo`, but each
  predates one independently reviewed final repair. Neither fixture is the integrated publication
  artifact; their exact hashes are preserved in their commits and intentionally not repeated here.
- **Result:** both retained the same invented-C0 `reject`: 54 systems / 5,616 opportunities /
  5,346 observed / 270 absent; false alerts `2.966666666666667`/`4.2`; detection `0.75`/`0.75`;
  delay `2`/`1`; confound rate `0.5`/`0.5`; candidate Brier `0.017341137335170863`; thresholds
  nonviable; deterministic baseline retained.
- **Next evidence:** run benchmark, reproduction, export, and report once from the integrated merge
  commit that contains both semantic acceptance and safe, honest export publication. Only those
  bytes may be pinned into product PR #187. Issue #6 and every real-data/promotion gate remain
  deferred.

## 2026-08-07 - Integrated canonical principal demonstration (`wbc1_demo`)

- **Status and flow:** canonical local evidence at integrated producer
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15`; benchmark, reproduction, export, and
  standalone report all passed in a fresh detached checkout. Product contract commit is
  `b48fea579936671397a0486ae7a0342197ee6e4b`, schema SHA-256
  `634b0cc7a0c3dbcefe8b9cf258e157695beae06d08cc9d02bb781a4267f633ef`.
- **Dataset and cases:** invented C0 only; 54 series / 5,616 opportunities / 5,346 observed / 270
  absent; `no_change`, `level`, and `parser_shift`, 104 points each. Aliases and seeds are absent;
  PELT is offline descriptive evidence only.
- **Result:** `reject`. Baseline/candidate false alerts per year `2.966666666666667`/`4.2`,
  detection `0.75`/`0.75`, delay `2`/`1`, confound false-alert rate `0.5`/`0.5`, candidate Brier
  `0.017341137335170863`, and nonviable thresholds `2.5`/`0.05`. Failed reasons are
  `BASELINE_SELECTION_VIABLE`, `CANDIDATE_SELECTION_VIABLE`, and
  `CANDIDATE_FALSE_ALERT_IMPROVEMENT`; deterministic baseline retained.
- **Artifacts:** fixture
  `sha256:afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9`;
  EvaluationBundle `sha256:e925c8ac44d914ce0003ef218d90187535eedfef3eb8d436a3c9a135e3d1a3a9`;
  custody `sha256:036f62f5f9ade272eba907513e7ab0bbef4a888bb1d86f8ae6e401aebd5c8238`;
  ResearchPack `sha256:bd96e45eed454b0ed42f37fa0c518f3b2883816aab876bd6e2e5718c9e24fb90`;
  Markdown `sha256:f9173354e86b20ccabe91334136017ff03ae68b3ba4432666f6af72172fb11b8`;
  HTML `sha256:22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29`.
- **Limits:** artifact verification remains honestly `not_run`; exact local/hosted command results
  are external evidence, not retroactive mutation of the append-only view. Issue #6 remains
  deferred. No real/public corpus, person-level inference, lab-owned product UI, or promotion was
  added.

## 2026-08-07 — Post-hoc clarification (NOT a preregistration): BOCPD missing-week run-length unit (issue #4)

- **Nature of this entry.** This is a POST-HOC clarification of the missing-week run-length semantics as
  ALREADY IMPLEMENTED and run — it is **not** a preregistration. The `wbc1_demo` / `wbc1_reviewed` /
  `wbc1_contract_final` runs above are complete, their results and artifact hashes are recorded, and their
  producer commits predate this note; a run-length unit cannot be preregistered for a run that has already
  executed. A genuine preregistration of a different unit would have to precede a fresh run/holdout (see the
  alternative below).
- **Semantics documented.** As implemented, the online BOCPD run length and its constant hazard
  `1 / expected_run_length` are in **observed samples**, not calendar weeks. Missing/non-finite weeks are
  skipped and do not advance the run-length/hazard posterior, so a contiguous missing block leaves that
  posterior unchanged (equivalent, for the posterior, to deleting those samples).
- **Why this is the documented behavior (not an outcome-chosen option).** This is the canonical
  Adams–MacKay run-length-in-observations semantics and is exactly what `bocpd_scores` already does, so
  writing it down changes no detector logic and therefore no result or digest. That byte-invariance is a
  CONSEQUENCE of documenting existing behavior, not a reason it was chosen; the earlier framing that
  justified an "option" by preservation of the known reject / zero digest churn was outcome-aware and is
  withdrawn.
- **Alternative (would require a real preregistration + a fresh run):** calendar-week semantics (advance the
  posterior across censored weeks with predictive ≡ 1, statistics frozen). It would change candidate scores
  → false-alert/Brier metrics → every recorded digest, so it is out of scope here; adopting it would need a
  preregistration entry written BEFORE a fresh run/holdout, never a post-hoc note.
- **Scope caveat:** score emission still begins after a fixed calendar-week `warmup`, so output-level
  gap-equivalence holds only for gaps past that boundary; the documented claim is about the
  run-length/hazard posterior, which the warmup gate does not affect.
- **Evidence:** locked by the characterization test
  `test_bocpd_missing_block_is_observed_sample_equivalent` (green on current code; it would fail if the
  detector were changed to advance across censored weeks). No real/public corpus, credential, network
  collection, model call, or promotion is involved.
- **[Correction, 2026-08-07]** This entry originally read "Preregistration: BOCPD missing-week run-length
  unit" and justified an "option" by outcome preservation; corrected to a post-hoc clarification per the
  PR #21 Codex review (a completed run cannot be preregistered, and outcome-aware justification weakens the
  holdout-custody claim). The observed-sample semantics and the characterization lock are unchanged.
