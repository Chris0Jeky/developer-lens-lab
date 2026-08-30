# Roadmap

`tools/cards.py` is the only task-card source. It renders `CARD_INDEX.md` and the JSON representation;
do not hand-edit generated card text.

## Bootstrap milestones

1. **M0 repository OS/tooling:** authority, context verifier, locked Python environment, CI, docs.
2. **M1 runnable foundation:** ResearchPack/EvaluationBundle schemas, sync, artifact store, CLI.
3. **M2 WB-C1 smoke:** invented generator, baseline/candidates, splits, holdout, bundle/report.
4. **M3 corpus quality pilot:** authorised in principle but inactive until every governor
   activation precondition, including exact-scope owner sign-off, is mechanically true.
5. **M4 empirical candidate:** governor-activated representative dataset and untouched holdout
   required.
6. **M5 product proposal:** owner/product promotion gate; deterministic fallback remains complete.
7. **H1 deferred hardening:** address the measured items in `HARDENING_BACKLOG.md` after the
   runnable foundation, unless a listed item becomes an irreversible-boundary defect first.

The opportunity backlog is unbounded. Only the dependency-closed `ACTIVE`/`IN_REVIEW` wave is
execution authority; `BACKLOG`, `OWNER_GATED`, and `PARKED` cards remain explicit non-executable
states. Public-corpus work starts only after M0-M2 are coherent.

See the [generated card index](CARD_INDEX.md).
