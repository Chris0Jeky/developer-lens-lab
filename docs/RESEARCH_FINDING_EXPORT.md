# Export a stored research finding

The finding export is an offline projection of **already stored invented C0 evidence**. It does
not run a benchmark, reproduce a run, compose a new MethodTrialView, reopen a holdout, acquire data,
or publish a release. Product remains the schema, presentation and promotion authority.

From inside the Lab checkout, for an existing stored run:

```console
uv run dllab export finding wbc1_demo --out /tmp/research-finding.json
```

Use `--artifact-root` to select an existing artifact store instead of `.dllab`. The default output
is `research-finding.json` in the checkout root. `--output` is an alias for `--out`. The command
prints both the full-file SHA-256 and the canonical finding-body hash, not source filesystem paths.

## Evidence flow

The reader loads `run.json` and its hash-addressed EvaluationBundle. It verifies bounded JSON,
regular files, no symlink/junction traversal, unique JSON object keys, media type, byte size,
digest, run identity and recorded Lab/input-contract provenance. An optional stored MethodTrialView
must satisfy its existing pinned contract and agree with bundle identity, hashes, decision,
coverage counts and all overlapping measurements. A present but corrupt view is not silently ignored.

The bounded adapter supports the existing WB-C1 change-point study and deterministic rolling
median/MAD versus Gaussian BOCPD methods. Unknown study or method semantics are refused, not
mapped approximately. Extending this registry requires a separately tested adapter and Product
contract review where its vocabulary changes.

The EvaluationBundle carries primary false-alert and detection measurements. Delay, confound and
threshold viability may be supplied only by a validated linked stored view. Missing metrics stay
unavailable and insufficient gate inputs stay null. An explicit missing bundle measurement may not
be overwritten by a conflicting measured view value. The projection derives its own gate claims;
it never reinterprets `benchmarked` as model promotion or changes the stored rejection decision.

## Publication and provenance

The original bundle timestamp, Lab commit and input-contract commit are preserved. The finding
transport schema is pinned separately. See [Research finding transport](RESEARCH_FINDING_CONTRACT.md)
for canonical bytes, privacy, closed vocabulary and body-hash rules.

All checks finish before the output is replaced atomically through a same-directory temporary
file. Failed validation preserves an existing destination and creates no output parent directory.
The destination may not be inside the source artifact store. A final output symlink is replaced
as a directory entry rather than followed; no source artifact bytes are changed. Parent paths are
resolved before the source-store collision check.

## Verification boundary

Tests use newly invented linked bundle evidence and a copy of the frozen public C0 view. They do
not reconstruct or claim to reproduce the historical EvaluationBundle bytes. Their projection
matches the exact Product finding fixture. Tests cover source immutability, repeatable output,
missing evidence, all closed outcomes, provenance/metric conflicts, corrupt references, oversized
JSON, symlinks and output collisions. CLI tests forbid the analysis entry points during export.

The historical WB-C1 source hashes and frozen release artifacts are unchanged. Full locked CI,
independent exact-head review and ordinary merge gates are still required; passing local pure
adapter tests is not proof of the runtime CLI or release readiness.
