# Changelog

This file records public, invented-data-only Lab milestones. A listed version is not evidence that a
tag, package publication, release asset, product promotion, or owner sign-off exists.

## 0.1.0 — release preparation, not tagged

### Scope

- Established the synthetic-first Developer Lens research and evaluation engine, with strict
  `DeveloperLensResearchPack.v1` and `DeveloperLensEvaluationBundle.v1` validation.
- Added content-addressed local artifacts, deterministic replay, explicit missingness, and a CLI for
  contract checks, invented benchmarks, reports, and product-owned Method Trial view export.
- Kept collection, external models, telemetry, credentials, real/private inputs, third-party pack
  producers, product installation, and automatic promotion disabled.

### Package and community foundation

- Added the canonical [AGPL-3.0-only licence](LICENSE), package identity for
  `developer-lens-lab`, and the `dllab` command without publishing a package or tag.
- Added [contribution guidance](CONTRIBUTING.md), a [Code of Conduct](CODE_OF_CONDUCT.md), public
  issue and pull-request templates, and a compact roadmap. Substantial external code remains gated
  on the separate owner/legal decision recorded in
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-7`.
- The interim public contact request is deliberately content-free and warns that both the issue and
  requesting GitHub account are public. No dedicated inbox or monitoring promise exists.

### Reviewed WB-C1 result

The reviewed C0 benchmark used invented fixtures and ended in `reject`, not promotion. Baseline and
candidate detection were both `0.75`; false alerts per year were `2.966666666666667` for the
baseline and `4.2` for the candidate, and the candidate Brier score was
`0.017341137335170863`. Both selections were nonviable, the candidate did not improve false alerts,
and the deterministic baseline remains the complete fallback.

Replay regenerated the recorded benchmark evidence byte-for-byte, and the reviewed smoke lane can
export the product-owned Method Trial presentation view without installing a model or adding a Lab
parser to Developer Lens.

### Release boundary

This entry is a draft release note only. It does not authorize a tag, package upload, release asset,
joint product release, screenshot/video publication, or any owner-gated action. Those gates remain
separate from the recorded experimental result.
