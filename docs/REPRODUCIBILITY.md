# Reproducibility

`uv.lock` pins the Python environment. Dataset cards freeze generator ID/version, parameters, seed
families, holdout range, and emitted checksums. Run manifests record lab commit, uv lock hash, input
snapshot checksums, method versions, seeds, bounded resources, and a normalized command ID.

Manifests must not contain absolute/local paths, usernames, environment names/values, credentials,
provider IDs, machine names, exact host timings, or stable real-scope hashes. Hashes address
lab-local generated objects and prove bytes; they do not imply anonymity or authorize cross-repo
linkage.

Normal smoke flow:

```powershell
uv sync --locked --all-groups
uv run dllab context verify
uv run dllab benchmark wb-c1 --smoke
uv run pytest
```

The benchmark must reproduce a byte-equivalent decision bundle from the same frozen inputs. Larger
benchmarks are opt-in until measured and never download data or weights at runtime.
