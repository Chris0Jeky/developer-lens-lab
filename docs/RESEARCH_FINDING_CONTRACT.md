# Research finding transport

The Lab can validate the Product-owned `ResearchFindingProjection.v1` contract as a pure,
offline boundary. The stored-run adapter and CLI are the next delivery slice; this foundation
alone does not execute an export command or publish a finding.

## Authority and source pin

The schema and canonical WB-C1 fixture are byte-for-byte copies from Product commit
`d8961cdbe794edb40d2ca221a267fe2728ade5d6`, under
`research-contracts/research-finding/v1/`. Their provenance and SHA-256 digests are checked on
load. The Product remains the owner of schema vocabulary, presentation and promotion decisions.

This Lab producer accepts invented **C0** evidence only, even though the transport schema can
represent C1. It does not authorize new data, another benchmark, a holdout replay, or a release.

The source input-contract commit in a finding is distinct from this transport-schema pin.
Exporters must preserve the recorded Lab and input-contract commits and timestamp, not replace
them with the export checkout, current clock, or new schema pin.

## Canonical bytes and integrity

`finding_canonical.canonical_bytes` produces the JCS representation used for the body hash:
UTF-16 property ordering, finite ECMAScript numbers, JSON escaping, and no extra whitespace.
Lone surrogates, non-JSON objects and integers outside the interoperable exact-integer range are
refused. `stable_bytes` emits the Product fixture's sorted two-space file representation and LF.

`finding_bundle_hash` removes only `provenance.bundle_hash` before hashing the canonical body.
The fixture's body hash is
`sha256:070bf161dbd7fa5bcb858d484024de69f315550ce8692776b241899d54c4cf35`.
Its complete file digest is different. Neither format changes existing EvaluationBundle artifact
hashes, which keep their historical serialization for reproducibility.

## Semantic and privacy validation

`validate_research_finding(value, root=checkout)` validates the pinned structural schema, C0
classification, real UTC timestamp, nonblank text, method identity, unique registry codes, gate
order and derivation, threshold-viability limitation, decision fallback, public text and body hash.
Errors report a controlled boundary reason rather than echoing untrusted source values.

Unavailable measurements remain unavailable. A gate with insufficient carried evidence is
`null`, never a fabricated zero or false. Rejection requires negative measured evidence or an
explicit failed gate, and retains the deterministic baseline. Other outcomes have no retained
fallback. `benchmarked` does not promote a model.

The projection's false-alert-improvement gate means candidate alerts are **strictly lower** than
baseline alerts. It must not be copied from WB-C1's stronger preregistered improvement rule.
Threshold selection gates are derived only from explicit selection evidence. The nonviable
limitation is present exactly when both carried selections are false.

Identity, email, handle, path and repository tokens are refused. Dates are allowed only in the
canonical timestamp. The single Product demo URL is an explicit allowlist exception. Unknown
fields do not become a route around these constraints.

## Verification

The foundation has golden ECMAScript number vectors, UTF-16 key ordering and escape tests,
exact pinned-fixture bytes and hash conformance, and structural, semantic, privacy and provenance
mutation tests. These tests need no research dataset or analysis runner. Stored artifact linkage,
atomic publication and CLI tests belong to the following adapter slice.
