# Governor path compatibility

## Scope and behavior

Issue #107 recovery slice: governor agent-pin validation now requests strict path resolution.
Missing paths and symlink loops produce the existing controlled resolution diagnostic on both
supported Python minors. Legitimate in-repository symlinks still resolve and their model pin is
checked; paths resolving outside the repository remain refused. The existing exception boundary
is unchanged. No governor policy, role/model routing, authority, data lane, or merge gate changed.

The runtime patch is one line in `context/verify.py`. Three new tests cover a missing agent,
a valid internal link, and an external link. The existing symlink-loop regression remains the
original bug reproducer. A context-only CI matrix explicitly selects Python 3.12 and 3.13 for
both locked sync and test execution; it does not rely on the checkout's default Python hint.

## Observed evidence

On the recovered old-main source, Python 3.13.5 produced 1 failed and 104 passed context tests:
`test_governor_pin_resolution_failure_is_a_controlled_diagnostic` received an unreadable-frontmatter
diagnostic because non-strict resolution returned the loop path instead of raising.

After the repair, the original context suite plus the three new regressions produced **108 passed**.
Syntax and whitespace checks passed. The published verifier blob is
`9fa8b89c66cee2d78c5ca01e65a5244a50a2c18a`, identical to the locally tested file. Publication is based
on main `c9ca22ef54e0037f407ca142404a208c28827868`; the ResearchFinding foundation did not change this
verifier. Full locked hosted proof and independent exact-head review remain required.

## Tooling and residuals

The former unpublished maintenance workspace was not recovered. This change was reproduced and
implemented afresh, not inferred from the earlier reported 433-test count. Local package
installation is unavailable; installed dependencies support the context tests, while hosted CI
provides locked-environment proof. These facts are also recorded on issue #107.

This is not general hostile-filesystem hardening or a fix for every path reader. No Windows
machine cleanup is performed. The separate mixed-dialect contract-sync review remains parked in
#126/#128. The normal post-push aging, independent review, and post-merge sweep still apply.
Rollback is a revert of this isolated compatibility change and its matrix workflow.
