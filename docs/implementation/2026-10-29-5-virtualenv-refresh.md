# Dependabot virtualenv follow-up — issue #5

This slice follows the targeted security update in PR #204 and retains its historical evidence.
It applies the exact lock from [Dependabot PR #205](https://github.com/Chris0Jeky/developer-lens-lab/pull/205),
head `561fb2c743f81d8810d2c595187840bc7753e2e2`, on the PR #204 head
`c5741aa1310352ee431467f7b7939ce0612afef7`. No broad lock regeneration was performed.

## Why the updater selected 21.15.1

The [recovered updater job](https://github.com/Chris0Jeky/developer-lens-lab/actions/runs/40811433180/job/123242419597)
identifies filelock 4.2.1 as its lowest security fix, runs
`uv lock --upgrade-package filelock==4.2.1`, and then skips virtualenv because resolution has already
updated it to 21.15.1. The previous
[virtualenv 21.7.13 metadata](https://github.com/pypa/virtualenv/blob/21.7.13/pyproject.toml)
requires filelock `<4` on Python 3.10+, so the filelock update forces a compatible virtualenv
replacement. The higher virtualenv choice is a resolver consequence, not evidence of a newly
required security floor.

Virtualenv 21.14.13 remains outside every virtualenv affected range supplied to this job.
[GHSA-cx6f-vjhg-g3cc](https://github.com/advisories/GHSA-cx6f-vjhg-g3cc) specifies 21.14.13 as its fix.
The inspected [21.15.0 release](https://github.com/pypa/virtualenv/releases/tag/21.15.0) changes
standalone-zipapp bundling and release packaging. The
[21.15.1 release](https://github.com/pypa/virtualenv/releases/tag/21.15.1) fixes seeded console-script
names, symlinked-directory copying, repeated option counting, unavailable-symlink fallback, and
debug-interpreter environment handling. Neither release note declares a new security minimum.
This supports preserving PR #204's valid security slice and delivering this incremental refresh
separately. It does not establish the absence of undiscovered advisories or live alert closure.

## Complete incremental lock delta

Only virtualenv changes: **21.14.13 to 21.15.1**, including its source and wheel artifact metadata.
The lock still contains 89 packages; the other 88 complete package records are unchanged.
Virtualenv's dependency edges, every top-level field, Python constraints, resolution markers,
lock revision 5, and filelock 4.2.1 are unchanged. Project dependency declarations and the Python
3.12 pin are unchanged.

- Previous lock SHA-256: `8bec8ecaa09d7f47de0fc4e9fd16d279084ed5c49b730ea6def0bce3c594a69a`.
- Updated lock SHA-256: `9fea2fb33ff2a8545bd2d02c4fc8aa00256005ca950631ec9aacd732aba07dfc`.
- Exact Dependabot lock Git blob: `910c606749d5ee561b853bdd00a92539e550cada`.

The tagged [21.14.13 metadata](https://github.com/pypa/virtualenv/blob/21.14.13/pyproject.toml) and
[21.15.1 metadata](https://github.com/pypa/virtualenv/blob/21.15.1/pyproject.toml) have identical
runtime requirement arrays and both declare Python `>=3.9`. On the lab's supported interpreters,
these require distlib `>=0.4.3,<1`, filelock `>=3.24.2,<5`, packaging `>=26.3`, platformdirs
`>=4.4,<5`, and python-discovery `>=1.6.1`. The unchanged lower-Python markers apply a filelock
3.19.1 requirement below Python 3.10 and typing-extensions `>=4.16` below Python 3.11; neither
applies to the lab's Python 3.12/3.13 range. Upstream adds the source-build requirement
`hatch-fancy-pypi-readme>=25.1`; it adds no lab runtime lock dependency. The compatibility proof
installed the available universal wheel, so it does not claim a source-distribution build.

## Focused proof

- Parsed old/new lock comparison confirmed the complete delta above; the Git blob and SHA-256
  remained exact after verification. `uv lock --check --offline` passed with 89 resolved packages.
  `git diff --check` passed.
- A new disposable CPython 3.12.14 environment installed the 11-package pre-commit closure with
  `uv pip sync --require-hashes`, deriving every version and artifact hash from this lock.
  `uv pip check` reported all installed packages compatible. Distribution metadata confirmed
  virtualenv 21.15.1, filelock 4.2.1, pre-commit 4.6.1, and the declared runtime requirements.
- Actual virtualenv 21.15.1 created another isolated CPython 3.12.14 environment using a confined
  app-data directory, with downloads and periodic updates disabled. Its bundled pip 26.2.2
  imported successfully.
- Actual pre-commit 4.6.1 installed and ran one invented local Python-language hook in a new
  temporary Git repository. The hook asserted Python 3.12, an isolated interpreter prefix below
  its confined pre-commit home, and a prefix different from the invoking dependency environment.
  It passed; the generated `pyvenv.cfg` identified virtualenv 21.15.1 and excluded system site
  packages. This exercises pre-commit's Python environment creation and local placeholder install.

The initial sandbox package request failed with `Operation not permitted`; the initial hook
placeholder install could not resolve its setuptools build dependency. The same bounded commands
succeeded through the authorized PyPI network allowance. All subprocesses exited. No shared
environment was changed, and unchanged filelock contention checks were not repeated.

These focused checks ran on Linux. Native Windows behavior, Python 3.13 execution, an upstream
source build, the full lab gate, actual lab-package smoke, hosted CI, independent final-head review,
and live alert closure are not established by this fragment. The delivering PR and coordinator own
the remaining declared gate and state/ledger/friction synthesis. The prior fragment's advisory-range
uncertainty and unavailable exact repository-alert inventory remain unchanged.

Rollback restores virtualenv 21.14.13 while retaining filelock 4.2.1, the uv 0.13.5 migration, and
the previously evidenced known-security minimum.
