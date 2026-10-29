# Redacted installation timeout progress — issue #177

The supervised runner in `scripts/verify_package_smoke.py` now retains bounded, redacted progress
when the isolated wheel-install command times out. Diagnostics are opt-in at that call only.
Captured bytes decode with UTF-8 replacement; missing or empty streams are explicit. Existing
normalization, secret/path redaction, terminal-control escaping, and per-stream truncation apply.

Independent review reproduced a privacy failure in the initial implementation: a timeout could
capture only part of an environment value, bypassing complete-value redaction. The review-fix implementation
publishes newline-completed progress and explicitly omits the unfinished final line. For timeout
output, normalized per-line fragments of known environment values and task paths are redacted too,
so a completed prefix of a multiline value cannot escape. Complete-command diagnostics keep their
existing behavior. This is not a claim to detect arbitrary transformations of secrets.

Progress is reported only after process-tree cleanup confirms. Unconfirmed cleanup still raises
the existing generic `ProcessTreeCleanupUnconfirmedError`, and probes/other commands still suppress
captured output. No stale subprocess implementation was restored.

Twelve new timeout regressions failed before the production fix. The initial package-metadata,
environment, and redaction selection passed 74 tests with one Windows-only taskkill skip on Linux.
Ruff, changed-file strict Pyright, and whitespace checks passed. Tests exercise the current
`Popen`/`communicate` supervision seam with invented processes and values. Exact integrated and
hosted proof belongs in the delivering PR. Native Windows execution is not claimed. Reverting this
bounded change removes progress reporting while retaining the original supervision path. The
review-fix round adds regression proof for truncated tokens/credential URLs, multiline values,
native/slash-normalized paths, CRLF/bare-CR output, and a cut UTF-8 character.

The review-fix regression run reproduced 20 failures across timeout-tail privacy and manifest
parser limits. The final combined package/manifest selection passed 113 tests with one native
Windows skip. Exact-head integrated and independent-review evidence remains PR-local.
