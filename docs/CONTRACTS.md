# Contracts

Developer Lens is the producer and authority for product-owned research input schemas. The lab is
the consumer of generated, pinned snapshots and the producer of reviewed evaluation bundles.

## Compatibility window

Bootstrap targets `DeveloperLensResearchPack.v1` and `DeveloperLensEvaluationBundle.v1`. Changes
within v1 are additive and strict readers reject unknown schema versions. Missing relations are
declared `present`, `absent`, `unsupported`, or `intentionally_omitted`; missing is never zero.
Timestamps are canonical UTC, feature availability is distinct from event/collection time, and
identifiers are opaque and bundle-local.

`dllab contracts sync --from <checkout> --ref <40-hex-commit>` will copy only the generated schema
and invented-fixture boundary. It records the product commit and snapshot byte checksums as
provenance. Those values are not cross-repository identity or join keys. Snapshots are generated and
must not be hand-edited.

The lab returns an EvaluationBundle with preregistration, dataset/model cards, split/run manifests,
baseline/candidate results, calibration, abstention, leakage, resource, decision, and artifact
manifests. Bundle manifests are path- and identity-free. Nothing automatically imports the bundle
into Developer Lens.

The current Developer Lens AnalysisPack 1.0 and proposed Pack 2.0 disagreement is outside this seam.
The lab must not pretend that either is the ResearchPack contract.
