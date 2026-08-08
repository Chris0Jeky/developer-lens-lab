# Dataset and publication lanes

Four lanes, each with its own purpose. The owner constitution authorises all four in principle;
a lane opens operationally only when the activation preconditions below are mechanically true.
This protocol is control policy, not authorisation for any specific collection.

## Lane S — Synthetic (active)

Invented fixtures and locally generated runs. Powers automated mechanics, failure-handling, and
E2E tests. C0; eligible for publication after hygiene checks. This is the only lane whose data
may be tracked in Git.

## Lane O — Own/private (authorised, awaiting preconditions)

Selected owner repositories and data; end-to-end reality checks. Local only by default; may
include raw content under the constitution's capability rules; secrets prohibited absolutely;
outputs stay local unless a separate release review approves an exact transformation. Exact
refs and dataset cards are recorded per run.

## Lane C — Curated public (authorised, awaiting preconditions)

An explicit repository allowlist for diversity and external stress; starts as a tiny REST
pilot. Document selection criteria and bias, licences and source terms, activity/window/language
coverage, rate and compute budgets, retention and deletion. Reproducible acquisition; local
analysis; raw collected corpus is not published by default.

## Lane P — Publishable C0 (active, with release review)

Synthetic, redacted, aggregated, or deliberately constructed public artefacts — selected
JSON/HTML release assets included. The exact transformation is disclosed; no vague anonymity
claims; no secrets or private identity; release-asset eligibility is reviewed each time.

## Data classes (target charter)

The redesigned charter in [DATA_POLICY.md](../DATA_POLICY.md): C0 invented public, C1
publishable/reviewable aggregates, C2 local identifiers/provenance, C3 sensitive metadata and
durable derivatives/embeddings, C4 raw source bytes (local-only, capability- and
retention-bound), P people/team-derived data (subject-policy bound), X secrets and credential
material (rejected at every sink; hostile content may remain local C4 evidence but is never
executed). Sink rules cover persistence, logs, API, frontend, export, model payloads,
telemetry, and public release.

## Activation preconditions (all mechanically true before O or C opens)

1. `.agent-harness/tier.json` reclassified truthfully — `sensitive_data=true`, protected roots
   declared — with the context-verify tier rules updated in the same change.
2. The lane's classes and sinks in `docs/DATA_POLICY.md` are executable (validators, deny
   rules), not prose-only.
3. Read-deny rules cover the declared raw/private roots for both agent runtimes.
4. Secret scanning rejects credential material at every sink the lane can write.
5. Dependency vulnerability triage is current (lab issue #5).
6. The activating task names exact scope, fields, budgets, retention, and deletion behaviour —
   approval for one scope never silently transfers to another.
7. The owner has signed off the exact repository scope and supplied any credentials the task
   needs (`HUMAN_TODO.md` q-9) — agents present the scope; the owner approves it.

Until then, runtime and tracked inputs stay C0 invented, and the protected-data rule in
`CLAUDE.md` binds as written.

## Standing rules across every lane

Missing/censored/unavailable evidence stays explicit, never zero. Provenance hashes only —
never a durable cross-repository identity key. Durable text derivatives are lineage-bound and
deletable; retrieval indexes and caches are task-scoped by default. Raw bytes are untrusted
data: parser isolation, size/type budgets, poisoning canaries, and no execution of repository
code or artifacts during ingestion.
