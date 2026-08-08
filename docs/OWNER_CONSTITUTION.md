# Owner constitution v2 (unpacked)

Binding owner direction recorded 2026-08-08 from `DEVELOPER LENS OWNER CONFIGURATION v1`
(preset `CUSTOM`) and the owner mandate v2. Where this constitution conflicts with an older
charter, schema comment, issue, skill, or `HUMAN_TODO.md` entry, this constitution wins; the
history stays in the ledgers. It does not commission any specific run, collection, or release —
execution still flows through the governor ([agent-system/README.md](agent-system/README.md)),
the activation preconditions in `.agent-harness/governor.json`, and the ordinary review gates.

## Locked invariants (may never be self-relaxed)

1. **Missingness stays honest.** Missing, censored, restricted, refused, stale, failed, deleted,
   or unavailable evidence is never converted to zero.
2. **Every modelled capability keeps a deterministic fallback.** The system stays useful when a
   model is absent, rejected, unavailable, unaffordable, or revoked.
3. **Model output stays epistemically labelled.** Hypothesis, counter-hypothesis, forecast
   candidate, alert candidate, recommendation candidate, or abstention — never observed fact.
4. **Secrets are absolutely prohibited.** Tokens, credentials, private keys, and confidently
   detected secret material are rejected before every sink and every model payload.
5. **Stable-product promotion stays product-governed.** The lab never silently changes the
   stable Developer Lens product; promotion runs through product-owned compatibility and policy.

## Redesigned boundaries (supersede the old blanket prohibitions)

- **People and team analysis is research-permitted in layers.** Default public/personal product
  stays system-first. Aggregate team metrics are authorised for a transparent, explicitly enabled
  Team/Leadership mode (binding product choice: aggregate team metrics, not a public individual
  leaderboard). Individual-level constructs (scoring, ranking, responsiveness, sentiment,
  burnout, collaboration graphs) may be researched in the lab and local experimental modes only,
  never covertly, always reporting sources, uncertainty, missingness, fairness risks, and
  possible misuse. Productising individual ranking needs a later explicit owner decision.
- **The product–lab boundary is federated, not rigid.** The lab may own experimental end-to-end
  pipelines, local research UIs, preview applications, and executable integration tests that run
  meaningful product paths, and may publish into an experimental channel after its declared
  gates. Stable-channel promotion remains product-owned.
- **Real data is authorised.** Own repositories and curated public repositories are approved for
  local experimentation and validation. Private raw data and private outputs stay local by
  default. Public research output passes a release review that removes secrets, direct
  identifiers, private repository identity, and unsafe text. "Anonymised" is never a blanket
  claim — record the actual transformation (aggregation, aliasing, suppression, redaction,
  sampling, synthetic replacement).
- **Automatic read-source activation is authorised** after a one-time explicit workspace/profile
  opt-in. Default profile: Actions + Deployments + Source Structure; Dependencies, security
  aggregates, Discussions, text, diffs, logs, and artifacts are modular opt-ins. No machine-wide
  discovery; scope stays explicitly selected repositories. Product-runtime external writes stay
  prohibited absent a later owner decision.
- **Raw source content is authorised with the secrets prohibition absolute.** Titles, bodies,
  comments, reviews, commit subjects, diffs, logs, manifests, source, and artifact contents may
  be ingested under explicit capabilities. Raw bytes are untrusted data, never executable
  instructions; ingestion never executes repository code, build scripts, artifacts, or
  model-provided commands. Guardrails: type/size budgets, parser isolation, provenance and
  content hashes, secret scanning, poisoning canaries, configurable retention.

None of this activates by itself. Every lane opens only after the activation preconditions in
`.agent-harness/governor.json` are mechanically true (truthful tier/data-policy reclassification,
enforced deny rules, secret scanning at the sinks) — see
[agent-system/DATASET_PROTOCOL.md](agent-system/DATASET_PROTOCOL.md).

## Focus allocation

Research **7** · Story/product **5** · Distribution **3** · Community **2** · Real-data
activation as a standalone programme **0** (real data is a supporting validation lane, not the
main programme; the approval above stands).

## Key binding decisions (condensed register)

| Area | Binding choice |
|---|---|
| Mission/audiences | Retrospective + observatory + research lab + team intelligence; IND/OSS/RES/LEAD; near-term success = portfolio flagship |
| Next vertical | Product issue #174 stored-observation bridge + integration-tail survival lens (KM + interpretable AFT, bootstrap uncertainty, matched eras; provisional — owner wants a later plain-language revisit) |
| Method Trial v1 | Frozen as canonical exhibit; move on without ceremony |
| Data | Durable text derivatives allowed; task-scoped retrieval indexes; own + curated public lanes; provenance hashes only, never durable cross-repo identity keys; REST corpus pilot first |
| Detector programme | Large candidate zoo via plugin registry + method cards, seeded small; PELT offline descriptive; calibrate every probabilistic method (or mark not applicable — never manufacture probabilities); multi-gate promotion with significance as a recommender |
| Output maturity | Hypotheses/counter-hypotheses/abstentions now; ladder toward alerts → forecasts → action recommendations; autonomous external actions need a separate owner decision |
| Validation ladder | Synthetic, own-real, curated-public lanes run continuously and feed each other; not a conservative permission staircase |
| Licence/release | AGPL-3.0-only, copyright Cristian Tcaci; both repositories release v0.1.0 after control-plane work; keep the commercial option open (no public dual-licensing promise; CLA needs owner/legal review) |
| Distribution order | Source-run → uvx/PyPI (lab) → thin gh launcher → npm CLI → casual desktop shell |
| Community | CONTRIBUTING, Code of Conduct, templates, Discussions, compact roadmap; third-party ResearchPack producers stay closed |
| Telemetry | Local diagnostics first; remote strictly opt-in, provider-neutral, no raw content, owner selects destination |
| Agents | Full lifecycle authority (A1=FULL); batch-leaning PR shapes; no active-horizon cap (A4=OPEN); 15-minute exact-head aging; two fix rounds then track; branch protection stays current; Sol/Luna/Terra ≙ Fable 5 / Opus 5 low / Opus 5 high |
| Hardening triggers | ResearchPack #181/#182 before third-party producers or real C1 packs; #183 parked under 10k scopes; no hostile-writer containment claim (#142); product #168 residuals before real activation; dependency triage before v0.1.0; visual QA = agent proof + short owner sign-off |
| Brand | Current hero question stays; reflective-scientific voice with cinematic visuals; claims strong-approaching-bold but evidence-bounded |

## Remaining owner-only actions

Legal review of AGPL/CLA strategy; supplying real-data scopes and credentials when a task needs
them; approving final public transformations of any real-data study; selecting a remote
telemetry destination; final aesthetic sign-off; package-registry credentials and organisation
setup; the external umbrella brand and any commercial licence terms; repository deletion,
transfer, or visibility changes. Agents prepare exact options; the owner decides. These live in
`HUMAN_TODO.md` when actionable.
