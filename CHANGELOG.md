# Changelog

This file records public, invented-data-only Lab milestones. A listed version is not evidence that a
tag, package publication, published release asset, product promotion, or owner sign-off exists.

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

### Staged C0 release assets

- Staged the frozen Method Trial v1 exhibit as tracked, review-only release assets under
  `release-assets/v0.1.0/method-trial-v1/`: a byte-preserving copy of the public tracked C0 product
  fixture (`method-trial-view.v1.json`,
  `sha256:afcc1ed9535d9b22fb399375027792489ce6b97949f8f684682943c11152b5f9`) and its deterministic
  derived report (`method-trial-report.v1.html`,
  `sha256:22ca8c03e78c6185e527fa4c0f7312caf7d9077619d46f795f8d8dd25c530a29`), alongside a compact
  provenance/checksum/licence manifest declaring `staged_for_release_review_only`.
- The staged bytes trace to the frozen Lab producer commit
  `0ef193070a9b80b81cef5a1710a1d65e0b271c15` (run `wbc1_demo`) and the product contract commit
  `b48fea579936671397a0486ae7a0342197ee6e4b`; `tests/test_release_assets.py` gates the staged
  bytes, hashes, and manifest coherence.
- In-repository staging is not publication: no GitHub release, package upload, or tag exists, and
  attaching these assets to a release remains behind the separate owner release gates.

### Release boundary

This entry is a draft release note only. It does not authorize a tag, package upload, published
release asset, joint product release, screenshot/video publication, or any owner-gated action.
Those gates remain separate from the recorded experimental result.
