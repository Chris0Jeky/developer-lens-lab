# Research governor

The governor is the lab's durable operating system for independent agent sessions: how any
capable model resumes, decides what the next unit of work is, executes it at the right risk
level, proves it, and hands off. Authority comes from
[OWNER_CONSTITUTION.md](../OWNER_CONSTITUTION.md) and the machine-readable policy in
`.agent-harness/governor.json`; this directory holds the operating semantics.

The governor evaluates methods and repository health. It never scores people outside the
explicitly layered research modes, never promotes a model, and never becomes stable-product
authority.

## Surfaces

| Surface | Role |
|---|---|
| `.agent-harness/governor.json` | Machine-readable policy: routing, risk classes, lanes, gates |
| [WORK_CLASSES.md](WORK_CLASSES.md) | Risk/autonomy classes L0–L4 and model routing |
| [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) | Experiment lifecycle, custody, review, decisions |
| [DATASET_PROTOCOL.md](DATASET_PROTOCOL.md) | Data lanes S/O/C/P and activation preconditions |
| [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md) | Recurring checks, admin, release, health report |
| [IDEA_PROTOCOL.md](IDEA_PROTOCOL.md) | Idea lifecycle and independent criticism |
| [PROMPT_LIBRARY.md](PROMPT_LIBRARY.md) | Reusable role prompts, including Research Governor Lite |

`docs/CURRENT_STATE.md` stays the single tracked live resume point; `tools/cards.py` stays the
authoritative task source; the ledgers and failure archive stay history; `HUMAN_TODO.md` holds
only genuinely open owner actions. Transient runtime state may live under
`.agent-harness/runtime/` (gitignored, regenerable, never private data). `uv run dllab context
verify` enforces that these surfaces exist and cannot silently drift.

## The governor loop

Every substantial session walks this loop; short sessions walk the phases that apply.

1. **SENSE** — refresh Git/branches/worktrees, PRs/reviews/CI, issues and card drift, tier and
   owner decisions, ledgers, dependency alerts, release state, product-contract heads, stale
   worktrees and background processes. Never inspect real/private artefacts merely because they
   exist; a data task must name its scope and authority.
2. **RECONCILE** — find lies: completed work still marked active, claims without run evidence,
   manifest/ledger mismatch, contract drift, owner decisions not unpacked, stale tier or
   boundary, unresolved review comments, repeated failures missing from the failure archive.
3. **CLASSIFY** — control plane, experiment maintenance, new experiment, methodology,
   dataset/corpus, data quality, reproducibility, product-contract integration,
   report/visualisation, administration/release, dependency, idea, owner-gated, human action.
4. **PRIORITISE** — bias by the owner focus allocation (research 7, story/product 5,
   distribution 3, community 2, standalone real-data activation 0). Rigor alone is not
   priority: prefer work that answers a useful question, improves validity or reproducibility
   materially, creates a visible result, unlocks cross-repo value, corrects a false claim, or
   prepares release. Ceremony and extreme edge cases must not dominate.
5. **SELECT THE WAVE** — keep the unlimited opportunity backlog in `tools/cards.py`; choose a
   focused active wave. Every lane declares question, owner/model, worktree, paths,
   prerequisites, dataset authority, holdout status, outputs, checks, merge order, and stop
   condition. Parallel experiments never share a live holdout.
6. **DELEGATE AND EXECUTE** — one writer per checkout; separate worktrees for parallel lanes;
   pin heads and contract versions in every delegation prompt; separate archaeology from
   implementation and implementation from review; treat negative results as valid.
7. **PROVE** — focused checks first, the full declared gate for code/config milestones;
   scientific proof (reproduction, byte comparison, custody) and repository proof (CI, drift
   checks) are distinct — record both.
8. **REVIEW AND DECIDE** — fresh-context adversarial review for non-trivial work; methodology
   review per [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md); decision states stay explicit;
   a method rejection is a success of the process, not a failure.
9. **MERGE, ARCHIVE, LEARN** — merge under the repository authority after exact-head proof,
   review disposition, and aging; sweep late comments; truth-sync cards/state/ledgers; archive
   killed approaches; remove clean coordinator worktrees; stop processes; update governor
   heuristics only for recurring lessons; set the exact resume point.

## Self-evolution

The governor may improve its prompts, routing, templates, checklists, taxonomies, budgets, and
checks when repeated evidence (not one anecdote) shows a better shape — through an ordinary
reviewed PR. It may never self-relax the locked list in `.agent-harness/governor.json`
(`self_evolution.may_never_self_relax`): secret prohibition, data authority, private-output
locality, missingness honesty, deterministic fallback, holdout integrity, model-output
labelling, owner-only decisions, the stable-product promotion boundary, or review/merge gates.
