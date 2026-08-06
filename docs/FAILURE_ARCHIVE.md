# Failure archive

Record disproved approaches and the evidence required to reopen them.

## Bootstrap decisions

- **Raw provider response landing — rejected.** Even outside Git, raw provider JSON can contain
  prohibited prose, people, identifiers, or paths. A future collector must project allowed fields
  in memory and discard the response.
- **Optional bootstrap token — rejected.** The initial corpus design has no credential path.
- **Cross-repository C4 content identity — deferred.** Product commit provenance and schema
  checksums do not authorize a durable join key. Reopen only after `HUMAN_TODO.md` q-5.
- **System `uv` assumption — disproved.** The host had no `uv` on `PATH`; commissioning used a
  task-local bootstrap and the repository pins the supported uv range.
