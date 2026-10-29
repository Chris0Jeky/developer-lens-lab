# Controlled stored-run manifest errors — issue #193

`build_report` and `reproduce_run` now share the manifest-reading boundary in
`src/developer_lens_lab/wbc1/runner.py`. Missing/unreadable files, invalid UTF-8/JSON, and
non-object JSON raise controlled `RunnerError` diagnostics. Underlying read/decode exception
chains are suppressed so the CLI does not echo rejected bytes or local paths. Existing report
identity, provenance, digest, and artifact-store checks remain in place.

The new `tests/test_runner_manifest_errors.py` regressions produced 13 failures before the fix.
Together with the existing report-binding tests, the final focused run passed all 37 cases;
the wider report/replay/export selection passed 84. Tests cover source immutability, preservation
of existing reports on failed forced rebuilds, and unchanged invalid-scope refusal. Changed-file
Ruff and strict Pyright checks passed; the task environment needed explicit dependency search
paths for Pyright, recorded in FR-113. Exact integrated/hosted proof belongs in the delivering PR.

The other #193 code findings were already delivered by PRs #196 and #197. `CONTRACTS.md` now
also states that result references must match their manifest entries in digest, size, and media
type. No stored evidence or product schema changed. Reverting this bounded change restores the
previous manifest-reading behavior.
