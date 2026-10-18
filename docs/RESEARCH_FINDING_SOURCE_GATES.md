# Stored finding source gates

The WB-C1 exporter is a closed protocol adapter, not a generic labeler. It checks the
question, primary metric, baseline/candidate methods, generator and method revisions,
acceptance and abstention rules, deterministic flags, parameter hashes and fallback codes.
Its parameter hashes are compared with the real method defaults in a regression test.
The bundle identity must equal the recorded and requested run identity.

Both bundle-only and stored-view exports require the run manifest's recorded
`research_pack` and `method_trial_view` provenance snapshots. Each snapshot is compared
with the trusted checkout snapshot after the latter's schema/fixture bytes, sizes,
version and identity semantics are checked. The manifest's two producer commits and
ResearchPack schema digest must agree. A syntactically valid but unrelated commit is
not sufficient provenance. Pure composition also checks the supplied contract pin.

Only fixed known vendor filenames are read. Names supplied by provenance are compared
as declarations, never followed as paths. A mismatch is refused before output creation
or replacement; no evidence is repaired, regenerated or silently substituted.

The source pin checks preserve the existing distinction between the ResearchPack input
contract, MethodTrialView contract, and new ResearchFinding transport contract. They
establish consistency with the trusted checkout, not remote signature verification or
scientific validity. No network collection, benchmark, holdout replay, release or model
promotion is performed by the adapter.

## Recovery and evidence

PR #127 landed the transport foundation at
`c9ca22ef54e0037f407ca142404a208c28827868`. PR #129 integrates that foundation and addresses
review comments 4171233990, 4171233994 and 4171233999 without replacing the PR's history.
The resumed sandbox has 29 passing pure source-guard tests; one parameter-default test
and all exporter/CLI integration tests require the complete hosted environment. Full
exact-head CI and independent review remain the merge authority.

The former unpublished five-fix workspace and its reported 433-test run were not
recovered. Those claims are not used as proof for this delivery.
