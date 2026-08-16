# Work classes and model routing

Risk classes scale verification, never permission. Machine-readable mirror:
`.agent-harness/governor.json` (`risk_classes`, `model_routing`).

## Risk and autonomy classes

### L0 — Observation

Read state, inspect CI, inventory runs/cards/issues, compare schemas, produce reports. Any
capable model, no writes, no gate.

### L1 — Mechanical research administration

Card/index regeneration, state/ledger sync after a verified merge, issue labels and metadata,
link repair, dependency inventory, post-merge sweeps, release metadata, C0 artefact catalogue
updates. Opus 5 low, the mechanic, or Governor Lite. Proof: the narrowest check that exercises
the change.

### L2 — Bounded implementation

Harness parity, verifiers, workflow/script/config changes, deterministic bug fixes, dependency
upgrades, packaging, reproducibility checks. The implementer executes a coordinator-scoped card;
a separate fresh-context reviewer reads the exact diff. Full declared gate for code/config
milestones.

### L3 — Methodology, data, model, or cross-repo design

Survival-model design, candidate tournaments, split/holdout changes, real-data pipelines,
text/source features, people/team research design, presentation contracts, promotion
architecture, public corpus shape, experimental-channel publication. The flagship designs;
scouts research; the implementer builds under the approved design; independent methodology
review is mandatory. Governor Lite may execute only a pre-approved L3 plan.

### L4 — Owner-only

Licence/legal terms, public release of private outputs, credential/billing decisions, data-owner
consent, irreversible policy changes, aesthetic sign-off, repository deletion/transfer/
visibility. Agents prepare exact options and stop.

## Model routing

| Role | Model | Use |
|---|---|---|
| Flagship coordinator | Fable 5 | Authority reconciliation, methodology architecture, programme selection, cross-repo contracts, governor evolution, final merge judgment |
| Scout | Opus 5 low | Large reads, issue/PR archaeology, dataset/dependency inventory, experiment summaries, idea mining — returns evidence and bounded plans |
| Implementer | Opus 5 high (`dll-implementer`) | Bounded implementation under an approved card |
| Reviewer | Opus 5 high (`dll-reviewer`) | Fresh-context adversarial and methodology review; separate context from implementation |
| Mechanic | Sonnet 4.6 high (`dll-mechanic`) | Generated files, formatting, repeated checks, metadata — no methodology or policy interpretation |
| Governor Lite | capable non-flagship orchestrator | L0–L2 autonomously; pre-approved L3 plans; prompt in [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md) |

### Codex delegation clarification (2026-08-16)

The Claude routes above remain unchanged. Once Sol/Terra delegates, native `gpt-5.6-luna` is
preferred for paved, directly verifiable L1/L2 child work, including focused implementation,
tests, and checks. Terra/Sol children are reserved for genuinely judgment-heavy investigation or
review, or for implementing an already-approved L3 design. Authority, methodology, cross-repo
contracts, and final decisions remain coordinator-owned.

Haiku is never routed lab work. Pins live in `.claude/agents/` and change only after the runtime
demonstrably accepts the identifier — never commit an invented model ID; if a target identifier
is unsupported, keep the working pin and record the target mapping as an issue.

## Escalation (binding at every level)

Escalate to the flagship — or from the flagship to the owner — when: owner/repository policy
conflicts; dataset authority is undefined; a secret or private publication may be involved;
holdout or leakage is ambiguous; a new data class/sink/capability is needed; contract ownership
is unclear; a model might be promoted; a result would make a strong empirical claim; scope
expands materially; two fix rounds have failed; or construct validity cannot be explained.
