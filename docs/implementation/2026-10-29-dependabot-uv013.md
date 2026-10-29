# Restore the supported uv toolchain for Dependabot

The [Dependabot security-update job](https://github.com/Chris0Jeky/developer-lens-lab/actions/runs/40807635186/job/123230269968)
failed on merge `c2648f3ed9b4aa2eb7ecfcd0670aaeedfeefce64` because its installed uv 0.13.5 could not
satisfy the project's `>=0.12.2,<0.13` requirement. Both filelock and virtualenv updates reported
`tool_version_not_supported`; retrying the same toolchain constraint would not resolve that cause.

The old range originated in the
[bootstrap commit](https://github.com/Chris0Jeky/developer-lens-lab/commit/9fe9e6db31d203c8951e558a29bb68fc4bc6312e).
[PR #51](https://github.com/Chris0Jeky/developer-lens-lab/pull/51) subsequently made package smoke
enforce the range before building and try the current-interpreter module when PATH uv was invalid.
This migration preserves that validation and fallback behavior while selecting a new bounded
toolchain: `>=0.13.5,<0.14`, with both CI workflows installing exactly uv 0.13.5. The README and active
bootstrap instructions describe the same range; historical bootstrap and implementation entries
remain unchanged.

[uv 0.13.5](https://github.com/astral-sh/uv/releases/tag/0.13.5) is the updater's available version.
The [uv 0.13.0 release notes](https://github.com/astral-sh/uv/releases/tag/0.13.0) describe behavioral
changes, including interpreter defaults and stricter archive handling, so real locked synchronization
and package-smoke execution remain necessary evidence. This slice keeps the Python 3.12 pin,
supported Python range, and `uv.lock` bytes unchanged.

## Focused implementation proof

- The unchanged package-metadata baseline passed 85 tests, with one native Windows taskkill test
  skipped on Linux.
- Test-first uv selection, bounds, fallback, and range-diagnostic expectations produced 10 expected
  failures against the old production bounds. The new cases accept 0.13.5 and a later 0.13 patch,
  reject 0.13.4, 0.14.0, and the former 0.12.2 baseline, and retain config-parity coverage.
- After the production update, `python -m pytest tests/test_package_metadata.py -q` passed 86 tests
  with the same one Windows-only skip. Changed-file Ruff formatting and lint checks passed, as did
  `git diff --check`.
- An optional local changed-file Pyright invocation could not resolve pytest from the external test
  environment, including when the interpreter was supplied explicitly. Its 355 cascading diagnostics
  do not supply type-checking proof. The coordinator owns verification in the newly synced toolchain.

This focused proof used the existing locked test interpreter. It does not claim an actual uv 0.13.5
sync, isolated package smoke, full gate, hosted checks, independent final-head review, or a successful
new Dependabot run. Those checks belong to the delivering PR and coordinator closeout.

The failed updater selected filelock 4.2.1 and virtualenv 21.14.13 as its aggregate security-fix
targets. This toolchain slice changes neither dependency and claims no alert closure. A subsequent
targeted dependency PR must retain resolver evidence and its own validation. Reverting this slice
restores the former toolchain requirement and docs without changing locked dependencies or Python.
