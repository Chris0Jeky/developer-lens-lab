# Contracts

Developer Lens is the producer and authority for product-owned research input schemas. The lab is
the consumer of generated, pinned snapshots and the producer of reviewed evaluation bundles.

## Compatibility window

Bootstrap targets `DeveloperLensResearchPack.v1` and `DeveloperLensEvaluationBundle.v1`. Changes
within v1 are additive and strict readers reject unknown schema versions. Missing relations are
declared `present`, `absent`, `unsupported`, or `intentionally_omitted`; missing is never zero.
Timestamps are canonical UTC, feature availability is distinct from event/collection time, and
identifiers are opaque and bundle-local.

ResearchPack has exactly seven relation slots: `coverage`, `repository_week`, `pr_episode`,
`ci_attempt`, `release_episode`, `collection_probe`, and `system_event`. A present relation names a
closed schema ID, observed row count, and content-addressed Parquet object. Every other state has a
controlled reason and no count or artifact. The bootstrap validator accepts C0 only. Parquet
validation checks the exact allowlisted column order for each relation.

`schemas/research-pack/v1/consumer.schema.json` is the lab's generated strict-reader mirror, not the
canonical producer schema. Developer Lens publishes its canonical schema and invented fixture at
`research-contracts/research-pack/v1/`. The lab vendors only a pinned generated snapshot beneath
`vendor/developer-lens/research-pack/v1/`.

`dllab contracts sync --from <checkout> --ref <40-hex-commit>` will copy only the generated schema
and invented-fixture boundary. It records the product commit and snapshot byte checksums as
provenance. Those values are not cross-repository identity or join keys. Snapshots are generated and
must not be hand-edited.

The lab returns an EvaluationBundle with preregistration, dataset/model cards, split/run manifests,
baseline/candidate results, calibration, abstention, leakage, resource, decision, and artifact
manifests. Bundle manifests are path- and identity-free. Nothing automatically imports the bundle
into Developer Lens. Repository, time, and seed-family partitions are disjoint. A decision is only
`reject`, `revise_once`, or `benchmarked`; even `benchmarked` is research evidence, never promotion.

`schemas/evaluation-bundle/v1/schema.json` is generated from the lab-owned Pydantic contract. Run
`dllab contracts render` only when intentionally changing a contract and `dllab contracts check`
in every proving pass. Unknown fields, non-`Z` timestamps, paths, provider/person identifiers,
unbounded counts, non-finite metrics, missing artifact references, and `ship` decisions fail closed.
The resource record contains deterministic workload counts, a workload checksum, and declared
budgets so byte-equivalent replay remains possible. Volatile observed wall-clock and RSS
measurements belong in the run report and never participate in bundle identity.

The generated schemas encode closed object shapes, scalar bounds, canonical UTC patterns, and the
present-versus-unavailable null rules. Runtime Pydantic/Zod validation remains required for
cross-record invariants such as split disjointness, schema-ID matching, artifact linkage, and a
failed leakage check blocking a benchmarked decision. Third-party schema-only interoperability is
not claimed during bootstrap.

## Artifact resolution

Manifests carry `{sha256, size_bytes, media_type}` only. `.dllab/scopes/<opaque scope>/objects/`
derives the storage location from the digest, so no path enters a portable manifest. Writes publish
through a same-directory temporary file and atomic replace; reads verify digest and size. Scope
invalidation is confined to the validated scope root. Crash durability, hostile same-user races,
Windows reparse points, quotas, and artifact signing remain explicitly deferred in
`HARDENING_BACKLOG.md` while all inputs are regenerable C0.

The current Developer Lens AnalysisPack 1.0 and proposed Pack 2.0 disagreement is outside this seam.
The lab must not pretend that either is the ResearchPack contract.
