# Data policy

## Classes

- **C0:** invented fixtures and synthetic public examples; may be tracked after hygiene checks.
- **C1:** low-identifiability system aggregates; not authorized during bootstrap.
- **C2:** provider identifiers and exact provenance; not authorized during bootstrap.
- **C3:** isolated sensitive metadata; not authorized during bootstrap.
- **C4:** ephemeral source-derived bytes; never persisted, logged, reported, or committed.
- **X:** credentials, source, diffs, prose, comments, logs, artifacts/caches, working-tree data, and
  person-shaped fields; rejected from every sink.

The T1 declaration is valid only while runtime and tracked inputs remain C0. Public provenance does
not make provider IDs or aliases non-sensitive.

## Sinks

Public tracked Git accepts code, documentation, JSON Schema, and small invented fixtures only. `.dllab`
accepts generated C0 objects through strict schemas and confined atomic writes; it is ignored and
has no network upload. Reports accept controlled codes, bounded numbers, coarse UTC windows, and
request-local opaque IDs. Manifests reject local paths, usernames, environment names/values,
provider IDs, host fingerprints, and command strings containing paths.

No collector is active. A future network task must parse the response in memory, immediately
project an allowlisted schema, discard raw bytes, use no token unless newly approved, record
coverage outcomes, and delete/invalidate by task-local opaque scope without a global scan.

Revocation removes owned inputs and descendants inside the declared lab root, leaving a
content-free tombstone. It cannot recall user copies or provider-held state. Nothing deletes or
scans outside the reviewed root.
