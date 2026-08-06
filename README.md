# Developer Lens Lab

Public, synthetic-first research and evaluation engine for
[Developer Lens](https://github.com/Chris0Jeky/developer-lens). Developer Lens remains the product,
canonical-contract, runtime, and model-promotion authority. This repository owns invented research
packs, reproducible experiments, candidate evaluation, and explicit rejection evidence.

Bootstrap is C0 invented-data-only. The repository is public by explicit owner direction. No
GitHub corpus collection, credential read, model request, real/private input, or product promotion
is active yet; non-essential hardening is tracked for later rather than blocking the runnable loop.

## Golden path

Install [uv](https://docs.astral.sh/uv/), then run:

```powershell
uv sync --locked --all-groups
uv run dllab doctor
uv run dllab context verify
uv run dllab tasks check
uv run pytest
```

The smoke benchmark command will become `uv run dllab benchmark wb-c1 --smoke` in milestone M2.
Until then, `docs/CURRENT_STATE.md` is the exact resume point.

## Boundaries

- Analytical subjects are repositories, software systems, collection instruments, and aggregate
  time windows; never people.
- Invented fixtures may be tracked. Datasets, Parquet outputs, local artifact objects, credentials,
  real repository allowlists, and generated run outputs may not be committed.
- Missing, unavailable, censored, restricted, or intentionally omitted evidence is explicit and is
  never converted to zero.
- A candidate can be rejected. Nothing installs itself into Developer Lens.

See `docs/PRODUCT_BOUNDARY.md`, `docs/DATA_POLICY.md`, and `docs/CONTRACTS.md` before changing a
contract, artifact, corpus, persistence, or evaluation seam.
