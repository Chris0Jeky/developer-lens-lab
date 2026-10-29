# Redacted installation timeout progress — issue #177

The supervised runner in `scripts/verify_package_smoke.py` now retains bounded, redacted progress
when the isolated wheel-install command times out. Diagnostics are opt-in at that call only.
Captured bytes decode with UTF-8 replacement; missing or empty streams are explicit. Existing
normalization, secret/path redaction, terminal-control escaping, and per-stream truncation apply.

Progress is reported only after process-tree cleanup confirms. Unconfirmed cleanup still raises
the existing generic `ProcessTreeCleanupUnconfirmedError`, and probes/other commands still suppress
captured output. No stale subprocess implementation was restored.

Twelve new timeout regressions failed before the production fix. The final package-metadata,
environment, and redaction selection passed 74 tests with one Windows-only taskkill skip on Linux.
Ruff, changed-file strict Pyright, and whitespace checks passed. Tests exercise the current
`Popen`/`communicate` supervision seam with invented processes and values. Exact integrated and
hosted proof belongs in the delivering PR. Native Windows execution is not claimed. Reverting this
bounded change removes progress reporting while retaining the original supervision path.
