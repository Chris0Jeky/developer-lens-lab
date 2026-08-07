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

## 2026-08-07 - Canonical MethodTrial presentation run (`wbc1_demo`)

- **Status and flow:** isolated final synthetic store at lab producer commit
  `5c79236beb0a0b25819f14510b79bb15813d7337`; benchmark, byte reproduction, report build, and
  canonical MethodTrial export all passed. Product contract commit is
  `b48fea579936671397a0486ae7a0342197ee6e4b`, schema SHA-256
  `634b0cc7a0c3dbcefe8b9cf258e157695beae06d08cc9d02bb781a4267f633ef`.
- **Dataset and selection:** invented C0 only; 54 system series, 5,616 weekly opportunities,
  5,346 observed and 270 absent. Fixed final-holdout rules selected `no_change`, `level`, and
  `parser_shift`, each with 104 points; no aliases or seeds are exported.
- **Result:** baseline/candidate false alerts per year `2.966666666666667`/`4.2`, detection
  `0.75`/`0.75`, median delay `2`/`1`, confound rate `0.5`/`0.5`; candidate Brier
  `0.017341137335170863`. Both thresholds remain nonviable. Failed gates are
  `BASELINE_SELECTION_VIABLE`, `CANDIDATE_SELECTION_VIABLE`, and
  `CANDIDATE_FALSE_ALERT_IMPROVEMENT`; decision `reject`, deterministic baseline retained.
- **Artifacts:** fixture `sha256:26c3a9184adfce4ff5756e702b36d6db7af7c5f2dab9eb3eb3081ca598eafd95`;
  EvaluationBundle `sha256:cbd9415bf9e26683656259bcef5a402b1745570c2a31e5c44dbfee74cfaea75f`;
  custody `sha256:036f62f5f9ade272eba907513e7ab0bbef4a888bb1d86f8ae6e401aebd5c8238`;
  Markdown `sha256:8144410775717d8b280a41b95c18dd22a8de45c765186ecaeb1fd5c6745e30f0`;
  HTML `sha256:fca7aac3e567f6de84b6dd60f476e77bf2a18f7a20cefde4563856e6ada99eec`.
- **Verification and limits:** local full gate, exact-head independent review, hosted lab run
  `31150109110`, and hosted product run `31150326515` passed. Product PR #187 must merge before lab
  PR #8. This remains synthetic mechanics evidence; issues #6/#7 retain post-demo debt and no model
  promotion is implied.
