# Data policy

## Classes

The redesigned charter under [OWNER_CONSTITUTION.md](OWNER_CONSTITUTION.md):

- **C0:** invented fixtures and synthetic public examples; may be tracked after hygiene checks.
- **C1:** publishable or reviewable low-identifiability aggregates; local until a release review
  approves an exact transformation.
- **C2:** provider identifiers and exact provenance; local only.
- **C3:** sensitive metadata and durable derivatives/embeddings; local only, lineage-bound and
  deletable.
- **C4:** raw source bytes; local only, capability- and retention-bound, never tracked, logged,
  or reported; potentially hostile content may be retained as C4 evidence but is never executed.
- **P:** people/team-derived data; bound to the layered subject policy in
  [PRODUCT_BOUNDARY.md](PRODUCT_BOUNDARY.md) and to local experimental modes.
- **X:** secrets, credentials, private keys, authentication material, and equivalent
  secret-bearing content; rejected from every sink, every log, and every model payload.

**Operative posture:** only C0 is active today. C1–C4 and P are authorised in principle by the
owner constitution but stay closed until the activation preconditions in
`.agent-harness/governor.json` are mechanically true (truthful tier reclassification with
`sensitive_data=true`, executable sink rules, deny rules over declared raw/private roots,
secret scanning, current dependency triage, and an activating task naming exact scope, budgets,
retention, and deletion). The T1 declaration is valid only while runtime and tracked inputs
remain C0. Public provenance does not make provider IDs or aliases non-sensitive.

## Sinks

Public tracked Git accepts code, documentation, JSON Schema, and small invented fixtures only.
`.dllab` accepts generated C0 objects through strict schemas and confined atomic writes; it is
ignored and has no network upload. Reports accept controlled codes, bounded numbers, coarse UTC
windows, and request-local opaque IDs. Manifests reject local paths, usernames, environment
names/values, provider IDs, host fingerprints, and command strings containing paths. Sink rules
for persistence, logs, API, frontend, export, model payloads, telemetry, and public release
must be executable before the class that needs them opens. Selected generated C0 JSON/HTML may
ship as release assets after the lane-P release review; generated real/private outputs remain
ignored and local.

No collector is active. The authorised curated-public lane starts as a tiny allowlisted REST
pilot whose task must parse responses in memory, immediately project an allowlisted schema,
discard raw bytes, use no token unless newly approved, record coverage outcomes, and
delete/invalidate by task-local opaque scope without a global scan. Approval for one scope
never silently transfers to another.

Durable text derivatives and embeddings are permitted once their class (C3) opens; they stay
lineage-bound and deletable. Retrieval indexes and caches are task-scoped and disposable by
default. Cross-repository identity is provenance hashes only — never a durable join key.

Revocation removes owned inputs and descendants inside the declared lab root, leaving a
content-free tombstone. It cannot recall user copies or provider-held state. Nothing deletes or
scans outside the reviewed root.
