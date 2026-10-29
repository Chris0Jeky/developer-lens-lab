# Run identity before benchmark work — issue #6

Smoke runs now validate the requested run ID against ArtifactStore's existing scope rules and the
pinned MethodTrialView minimum length before checking the tree, loading a producer snapshot,
building/evaluating a dataset, reserving artifacts, or opening the final holdout. A previously valid
three-character store ID could fail the stricter presentation contract only after those operations.

Only `None` selects the default ID; an explicitly empty value is invalid. Smoke IDs require 8–64
characters; full-mode IDs preserve the store's 3–64 range. Both retain lowercase-letter start and
lowercase letter/digit/underscore content. Diagnostics do not echo rejected IDs or local paths,
and invalid input creates no artifact root.

All 43 new preflight cases failed before the fix. The focused runner/tree/vendor/projection selection
then passed 56 tests. Invalid cases guard every later stage; valid boundaries and both defaults
reach a controlled stop at vendor loading. No benchmark was run for this slice. Ruff, strict
changed-file Pyright, and whitespace checks passed. Integrated and hosted proof belongs in the PR.

This addresses one later comment item in #6. Confound observability and the separately documented
export/provenance issues remain open; it does not make the full umbrella complete.
