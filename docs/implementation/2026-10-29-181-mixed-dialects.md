# Embedded schema dialect validation — issues #181 and #128

Explicit Draft 7 and Draft 2019-09 resources already selected the correct validator. Runtime
regressions exposed a deeper gap: references into descendants without their own `$schema` lost
the enclosing dialect. Draft 7 tuple validation could crash, and `dependencies` could be silently
ignored. The reference-closure traversal now supplies a schema-object dialect map to an in-memory
validation copy. Source objects, instance-valued `const`/`examples`, synchronized bytes, and offline
reference confinement remain unchanged. Unknown dialects receive a controlled diagnostic.

The initial regressions produced 23 failures and 22 passes. The completed dedicated suite passed
49 cases; the wider contract-sync, schema, confinement, and contract selection passed 143. Coverage
includes inherited and explicit dialects, tuple constraints, Draft 7 dependencies, Draft 2019-09
contains bounds, booleans, source immutability, unsupported dialects, and refusal before writes.
Changed-file Ruff and strict Pyright passed. Integrated and hosted evidence belongs in the PR.

Earlier structural work landed in PRs #126 and #179; this closes their runtime validation follow-up.
No Product schema or vendor bytes changed. Revert the source/test change to roll back this slice.

The integrated strict gate exposed that the bundled typing protocol omits the concrete validators'
`ID_OF` attribute. A typed metaschema-identity helper now reads `$id` or legacy `id` directly and is
also used by reference-closure fallback. Runtime dialect selection is unchanged; strict checking
retains the normal bundled stubs and no repository type setting is relaxed.
