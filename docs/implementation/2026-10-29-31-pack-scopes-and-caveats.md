# Explicit pack scope and truthful export caveats — issue #31

`dllab pack validate` accepts `--scope <opaque-id>` with `--artifact-root`. The selected scope is
validated before relation iteration, including omitted-relation packs, and then passed to the
existing artifact validator. Omitting scope preserves pack-ID lookup; omitting artifact root
preserves manifest-only validation. There is no scope discovery, directory scan, or source write.

The new CLI tests first produced 19 failures and three passes; all 22 then passed. The broader
validation/CLI selection passed 74. Actual invented Parquet objects prove run scope differing from
pack ID, digest/size integrity, missing-object refusal, invalid scope refusal, and unchanged source
files/directories. Changed-file Ruff and strict Pyright passed. Full proof belongs in the PR.

Four exported caveat statements now use truthful strings already permitted by the pinned Product
schema: artifact lifecycle handling, bounded threshold workload, fail-closed corrupt manifests,
and enforced primary-domain metrics. The six-item shape and codes remain unchanged. Confound
observability remains open in #6, so its explicit deferred caveat is retained. The zero-delay
caveat has no accurate replacement in the pinned vocabulary and needs Product coordination;
the implementation already preserves numeric zero.

The benchmark decision already requires measured primary-domain detection from both methods,
and no-true-change partitions retain unavailable detection. The record layer has no `or 0.0`
fallback; ranking uses an explicit `None` check. Exporting an additional primary-domain gate/reason
would change the pinned seven-gate Product contract, so that remainder stays tracked in #31.
