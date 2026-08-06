# Operating model

## Roles

- Coordinator owns live-state reconstruction, architecture, dependency order, integration, exact
  final-head proof, and merge judgment.
- Implementation lanes own bounded non-overlapping paths plus code, tests, and documentation.
- Methodology reviewers attempt to falsify baseline fairness, split policy, holdout custody,
  calibration, leakage, interpretation, and deterministic fallback claims.
- Data stewards challenge minimization, prohibited-field survival, manifests, deletion, and paths.
- Owner decides real datasets, new classes/sinks, credentials, publication, and product promotion.

## Working rules

Use the generated active horizon, not a standing card universe. One writer owns each checkout;
parallel writers use coordinator-created detached worktrees and disjoint paths. Every lane declares
objective, non-goals, acceptance, rollback, proof, and stop condition. Record operational outages
in `docs/CURRENT_STATE.md` or the implementation ledger, never as an inferred owner waiver.

Three bootstrap verticals are intended: repository OS/tooling; contracts/artifact store/validation;
WB-C1 smoke/evaluation report. After two review rounds, ship or park. No background process survives
handoff. Non-essential security and supply-chain improvements go to `HARDENING_BACKLOG.md`; only
irreversible secret/private-data, destructive-root, or person-shape defects interrupt value work.
