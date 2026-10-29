# Compatible Arrow physical types — issue #169

ResearchPack relation validation now accepts Arrow `large_string` wherever the pinned field type
is `string`, and an all-null physical `null` column only for declared nullable fields. Exact column
order, numeric types, required values, finite metrics, nonnegative counts, and canonical UTC checks
remain enforced. This admits normal external producer encodings without broad type coercion.

The focused reproducer yielded 16 failures and 14 passes before the change, then passed all 30.
The wider validation/artifact selection passed 112 tests with seven native-Windows skips. Ruff and
strict changed-file Pyright passed. Integrated and hosted evidence belongs in the PR.

The second issue item is deliberately retained behavior: ArtifactStore refuses symlink/junction
ancestors in the lexical root path. CONTRACTS.md now tells callers to select a real directory with
non-link ancestors. Race-hardening and additional Windows reparse-point support remain documented
in HARDENING_BACKLOG.md. No claim of native Windows verification is made by this Linux run.
