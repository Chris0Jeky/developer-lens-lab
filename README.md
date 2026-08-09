# Developer Lens Lab

Public, synthetic-first research and evaluation engine for
[Developer Lens](https://github.com/Chris0Jeky/developer-lens). Developer Lens remains the product,
canonical-contract, runtime, and model-promotion authority. This repository owns invented research
packs, reproducible experiments, candidate evaluation, and explicit rejection evidence.

Bootstrap is C0 invented-data-only. The repository is public by explicit owner direction. No
GitHub corpus collection, credential read, model request, real/private input, or product promotion
is active yet; non-essential hardening is tracked for later rather than blocking the runnable loop.

## License and package

Developer Lens Lab is copyright (C) 2026 Cristian Tcaci and is released under the GNU Affero
General Public License v3.0 only (`AGPL-3.0-only`). See [LICENSE](LICENSE). The Python package is
distributed as `developer-lens-lab` and provides the `dllab` command.

## Golden path

Install [uv](https://docs.astral.sh/uv/), then run:

```powershell
uv sync --locked --all-groups
uv run dllab doctor
uv run dllab context verify
uv run dllab tasks check
uv run dllab contracts check
uv run pytest
uv run dllab benchmark wb-c1 --smoke
uv run dllab run reproduce wbc1_smoke
uv run dllab report build wbc1_smoke
uv run dllab export method-trial wbc1_smoke
```

The M1 contract vertical is runnable without a collector or dataset:

```powershell
uv run dllab pack validate path\to\invented-pack.json
uv run dllab pack profile path\to\invented-pack.json
uv run dllab bundle validate path\to\evaluation-bundle.json
uv run dllab contracts sync --from path\to\developer-lens --ref <40-hex-commit>
uv run dllab contracts sync-method-trial --from path\to\developer-lens --ref <40-hex-commit>
```

`contracts sync` reads only the fixed ResearchPack schema and invented-fixture paths from the pinned
Git object. `contracts sync-method-trial` reads only the product-owned
`DeveloperLensMethodTrialView.v1` structural schema and requires its structural-only annotation.
The exporter then applies the lab's equivalent implementation of the product-owned cross-field
semantics before it writes a view; a JSON Schema pass alone is not artifact acceptance. Both sync
paths record commit and byte checksums as provenance, never as cross-repository join keys.

The WB-C1 command writes an ignored, content-addressed run beneath
`.dllab/scopes/wbc1_smoke/`. Each run ID is single-use: the runner reserves its scope and writes an
append-only custody record before materializing the final holdout, so a second process cannot reopen
or replace the same experiment. Use `--run-id <new_opaque_id>` for another run. The runner evaluates
the online arms, records PELT only as offline descriptive evidence, and emits an EvaluationBundle
plus standalone Markdown and HTML reports. `run reproduce` verifies every stored object, then
regenerates and byte-compares every recorded artifact. Use `uv run dllab benchmark wb-c1 --full`
only for the larger opt-in lane.

`export method-trial` projects one already validated local WB-C1 smoke run into the small product-owned
presentation schema. It deterministically selects the no-change, planted-change, and instrumentation-
confound windows, validates the result against the pinned product schema, and writes the ignored
`method-trial-view.json` by default. It does not send a request, expose system aliases, install a
model, or add an EvaluationBundle parser to the product. The opt-in `--full` lane retains the generic
EvaluationBundle reports and replay path; it does not record a smoke-only MethodTrial projection.

## Boundaries

- Analytical subjects are repositories, software systems, collection instruments, and aggregate
  time windows; never people.
- Invented fixtures may be tracked. Datasets, Parquet outputs, local artifact objects, credentials,
  real repository allowlists, and generated run outputs may not be committed.
- Missing, unavailable, censored, restricted, or intentionally omitted evidence is explicit and is
  never converted to zero.
- A candidate can be rejected. Nothing installs itself into Developer Lens.
- `.dllab` stores scope-local content-addressed objects. Manifests contain digests and controlled
  metadata, not filesystem paths.

See `docs/PRODUCT_BOUNDARY.md`, `docs/DATA_POLICY.md`, and `docs/CONTRACTS.md` before changing a
contract, artifact, corpus, persistence, or evaluation seam.
