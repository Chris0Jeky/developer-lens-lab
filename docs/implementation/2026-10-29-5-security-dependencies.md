# Targeted security dependency update — issue #5

This slice follows the uv 0.13.5 toolchain migration and addresses the two dependency targets from
the [failed Dependabot security-update job](https://github.com/Chris0Jeky/developer-lens-lab/actions/runs/40807635186/job/123230269968).
That job selected filelock 4.2.1 and virtualenv 21.14.13, then stopped because the former project uv
range excluded its updater. The targeted resolver command is:

```console
uv lock --upgrade-package filelock==4.2.1 --upgrade-package virtualenv==21.14.13
```

It ran with uv 0.13.5, CPython 3.12.14, and a task-confined cache. The initial sandbox request to
PyPI failed with `Operation not permitted`; the same bounded command succeeded through the
authorized network allowance. No broad dependency upgrade was requested.

## Complete resolver delta

| Package | Previous lock | Updated lock |
| --- | --- | --- |
| filelock | 3.32.2 | 4.2.1 |
| virtualenv | 21.7.13 | 21.14.13 |

The lock still contains 89 packages, with no package added or removed. The other 87 package records
are unchanged. Artifact URLs, sizes, upload times, and SHA-256 values changed only for the two new
releases. Virtualenv gained a dependency edge to the already locked packaging 26.3; the installed
21.14.13 distribution metadata requires `packaging>=26.3`. Its Python 3.10+ filelock requirement is
`>=3.24.2,<5`, which admits the selected 4.2.1. No additional package version change was necessary.

uv rewrote the lock format revision from 3 to 5. The lock format version remains 1; Python support,
resolution markers, project metadata, and all other top-level lock fields remain unchanged.
`pyproject.toml`, the Python 3.12 pin, and all policy/configuration files remain unchanged.

- Previous lock SHA-256: `a061af827c0366e6b9b954b5d40d9d7976adb2a79246d480d7bb7304692b8f67`.
- Updated lock SHA-256: `8bec8ecaa09d7f47de0fc4e9fd16d279084ed5c49b730ea6def0bce3c594a69a`.

## Compatibility and integrity proof

- `uv lock --check --offline` passed with 89 resolved packages. Parsed old/new lock comparison and
  the full Git diff confirmed the complete delta above. `git diff --check` passed.
- A separate disposable environment installed the 11-package pre-commit dependency closure with
  `uv pip sync --require-hashes`, using versions and artifact hashes from the updated lock.
  `uv pip check` reported all installed packages compatible.
- Actual `FileLock` and `SoftFileLock` holders blocked a second process, and the second process
  acquired each lock after its holder released it.
- Actual virtualenv 21.14.13 created a CPython 3.12.14 environment with downloads and periodic
  updates disabled, a confined app-data directory, and bundled pip 26.2.2. The new interpreter
  started with an isolated prefix and imported pip successfully.
- Existing pre-commit 4.6.1 validated an invented local configuration and successfully ran its
  system-language hook in a temporary invented Git repository. This does not claim a full
  third-party hook environment installation.

These checks use normal dependency interfaces, not exploit probes. They ran on Linux and do not
claim native Windows behavior, the full lab gate, actual lab-package smoke, hosted CI, independent
final-head review, or live alert closure. Those proofs remain with the delivering PR and coordinator.
No shared environment was modified and no new version-mirroring regression tests were added.

## Advisory evidence and remaining uncertainty

The [filelock maintainer advisory GHSA-69hj-f68j-2879](https://github.com/tox-dev/filelock/security/advisories/GHSA-69hj-f68j-2879)
includes locked 3.32.2 in its affected range through 4.2.0; the fix is
[filelock 4.2.1](https://github.com/tox-dev/filelock/releases/tag/4.2.1). Runtime exposure under that
advisory's local filesystem preconditions was not established for the lab.

For virtualenv, the [GitHub-reviewed GHSA-6w3r-xr62-4xcp](https://github.com/advisories/GHSA-6w3r-xr62-4xcp)
lists `<21.14.9`, while the [maintainer advisory](https://github.com/pypa/virtualenv/security/advisories/GHSA-6w3r-xr62-4xcp)
lists the confirmed version 21.14.8 and leaves the first affected version unestablished. This slice
preserves that discrepancy rather than claiming demonstrated exploitation of locked 21.7.13.
The subsequent [GHSA-cx6f-vjhg-g3cc](https://github.com/advisories/GHSA-cx6f-vjhg-g3cc) affects
21.14.9 through 21.14.12 and is fixed in
[virtualenv 21.14.13](https://github.com/pypa/virtualenv/releases/tag/21.14.13), matching the updater's
aggregate target. The connected GitHub surface cannot read repository Dependabot alert records;
exact current alert identifiers, counts, and closure remain unavailable.

Reverting this slice restores the prior lock and its security-update debt without reverting the
uv toolchain migration or changing policy, Python support, or project dependency constraints.
