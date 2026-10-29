# Finding verification after writing, before publication — issue #97

Finding export now owns a small same-directory temporary-file publisher. After writing and flushing,
it rereads the actual bytes with the existing size and link checks, validates schema/semantics/privacy,
and requires exact intended-payload and stable-serialization equality before atomic replacement.
Rejection preserves any previous destination and removes the temporary output. This is a written-file
check before publication, not a second scan of the already-replaced final pathname.

All eight new regressions failed on the prior publisher. The final focused finding exporter/CLI
selection passed 104 tests, including the unchanged Product golden fixture, source-store integrity,
repeatability, output confinement, and final-symlink replacement. Injected denied, altered, oversized,
malformed, and noncanonical bytes fail before publication. Ruff, strict Pyright, and whitespace
checks passed. Full integrated/hosted proof and independent review belong in the delivering PR.

No Product schema, vendor fixture, frozen evidence, or source artifact changed. #97 remains open for
broader non-reject/revision evidence and paired Product runtime verification. Reverting the focused
publisher/test change restores the former validated-in-memory atomic publication path.
