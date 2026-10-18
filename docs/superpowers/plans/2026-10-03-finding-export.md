# Research finding export implementation plan

**Goal:** expose the existing C0 evidence as the producer-owned ResearchFindingProjection.v1,
without rerunning analysis or changing the frozen WB-C1 artifacts.

**Architecture:** pin the Product schema and fixture bytes at
`d8961cdbe794edb40d2ca221a267fe2728ade5d6`. A pure contract validator owns JCS transport
integrity, semantic gate derivation and public privacy. The following adapter slice reads the
EvaluationBundle and optional hash-linked MethodTrialView; the CLI reuses the existing export
publisher only after all checks pass. No network or credentials are used.

**Spec:** GitHub issue #97 and the pinned Product research-finding/v1 contract. Product remains
schema/promotion authority. This is evidence transport, not a new experiment or release.

## Constraints and review focus

- Preserve the source bundle timestamp and lab/input-contract commits. Pin the finding schema
  separately; never replace the input-contract commit with the new schema pin.
- Validate source identity, artifact hashes/sizes, manifest linkage, and source-view provenance.
- Supplement only missing bundle metrics from the linked stored view. Conflicting evidence fails.
- Missing metrics remain unavailable, required missing gate inputs become null, not zero/false.
- Derive projection gates from its transported evidence, including its weaker strict-improvement
  rule, not the source view's preregistered 20 percent rule.
- Unknown studies, methods, outcomes, private tokens, malformed JSON, and corrupt artifacts fail
  before publication. Protect source artifact roots from an output-path collision.
- No timestamp sampling, analysis imports during pure composition, holdout replay, or new data.

## Implementation slices

- [x] Write JCS and producer-fixture conformance/refusal tests; observe failure.
- [x] Add finite-number, UTF-16 key ordering and stable JSON transport helpers with golden vectors.
- [x] Add pinned schema/provenance loading plus semantic/privacy validation; prove mutations fail.
- [ ] Write stored-bundle/view adapter tests using invented scope artifacts and the frozen C0 view.
- [ ] Implement source linkage checks and pure projection, then the CLI and shared publisher call.
- [ ] Prove deterministic fixture bytes, unavailable metrics, source immutability, corruption and
      privacy no-write behavior, all closed outcomes, no analysis calls and path collision refusal.
- [ ] Run local available tests and exact-head hosted full gate, obtain independent review, then
      apply the 15-minute aging floor and re-read live main/reviews/checks before merging.

## Tooling evidence

The ZIP matched initial main tree `1d416e0087ff8be2e8240cc7ba326ae227a5b868` exactly.
Local dependency installation is blocked; pure tests use installed dependencies, not a claimed
locked environment. Hosted CI remains required. Cross-repository blob references are not accepted
by GitHub's tree API, so original verified bytes will be published as new blobs in this repository.

## Delivery split

The pure transport, pinned schema and semantic/privacy validation are an independently reviewable
foundation PR. The stored-evidence adapter and CLI follow in a stacked PR. The CLI is not available
from the foundation alone. Local foundation tests: 62 passed; 20,000 seeded finite IEEE-754 samples
matched Node.js JSON.stringify number output. The real CLI and full locked gate require hosted CI.
