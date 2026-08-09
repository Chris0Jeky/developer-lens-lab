# Contributing to Developer Lens Lab

Thanks for helping with the Lab. It is the public, invented-data-first research and evaluation
companion to Developer Lens: the Lab owns research questions, reproducible experiments, candidate
evaluation, and explicit rejection evidence; the product remains the stable contract and promotion
authority.

Read this guide with the [Code of Conduct](CODE_OF_CONDUCT.md). The Lab's boundaries are described
in [`docs/PRODUCT_BOUNDARY.md`](docs/PRODUCT_BOUNDARY.md), [`docs/DATA_POLICY.md`](docs/DATA_POLICY.md),
and [`docs/CONTRACTS.md`](docs/CONTRACTS.md).

## Data and evaluation boundary

This public repository is a C0, invented-fixture surface. Use made-up repositories, systems,
events, identifiers, and evaluation cases. Do not add real or private datasets, Parquet files,
`.dllab` content, generated run outputs, credentials, provider IDs, repository allowlists, local
paths, or copied source material. These rules apply to tests, examples, screenshots, issue bodies,
and pull requests.

Research and evaluation changes must preserve:

- reproducibility from declared seeds and pinned inputs;
- compatibility with the reviewed `DeveloperLensResearchPack.v1` and
  `DeveloperLensEvaluationBundle.v1` contracts;
- explicit states for missing, unavailable, censored, restricted, refused, or intentionally omitted
  evidence — missingness is never zero;
- a deterministic no-model or no-service fallback; and
- the boundary that nothing installs itself into or silently promotes through Developer Lens.

Third-party ResearchPack producers remain closed pending the product-side ResearchPack hardening
work in issues [#181](https://github.com/Chris0Jeky/developer-lens/issues/181) and
[#182](https://github.com/Chris0Jeky/developer-lens/issues/182). Do not add a producer, collector,
credential flow, telemetry destination, or product installer in this repository.

## Small contributions

Small fixes, documentation corrections, tests with invented fixtures, and issue discussion may
proceed. A substantial external code contribution waits for the owner/legal review recorded in
[`Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-7`](HUMAN_TODO.md); no CLA or contributor-agreement
terms currently exist in this repository. Do not invent legal terms in an issue or pull request.

The Lab is licensed **AGPL-3.0-only**, copyright Cristian Tcaci. By opening a pull request you are
proposing the contribution under that licence. This statement does not create a separate agreement
or promise dual licensing.

## Local setup and focused proof

Use the locked environment and run the narrowest command that exercises your change:

```powershell
uv sync --locked --all-groups
uv run dllab context verify
uv run pytest tests/path/to/focused_test.py
```

For docs, templates, or authority-adjacent changes, run `uv run dllab context verify` and
`git diff --check origin/main...HEAD`. For code or configuration, use the full gate in `CLAUDE.md`
when the changed seam warrants it. Do not inspect or commit generated `.dllab` runs while proving a
change.

## Issues, Discussions, and pull requests

Use the issue templates for bug reports and feature requests, and use
[Lab Discussions](https://github.com/Chris0Jeky/developer-lens-lab/discussions) for questions or
open-ended research ideas. Use invented/public examples only; do not paste private data, logs,
screenshots, links to private material, credentials, or real repository identities.

Keep pull requests small and explain the proving command and anything not verified. A candidate may
be rejected: research evidence is not a product promotion request, and a green test is not evidence
that a method should ship.
