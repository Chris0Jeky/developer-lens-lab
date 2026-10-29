# Unambiguous current-state validation — issue #34

The context verifier rejects duplicate YAML mapping keys before safe construction can overwrite
them, including duplicates in nested mappings and merge sources. A node-graph prepass visits each
node once, preserving legitimate aliases, recursive values, and explicit merge overrides. Parse
diagnostics contain fixed reasons and source line numbers, never attacker-controlled key, tag, or
anchor text.

`exact_resume_point` must be a nonempty string. `active_wave` and `delivered` must be lists, and
each active-wave entry must have nonempty `lane`, `writer`, and `state` strings. Extra operational
fields remain allowed. The already-governed `prompt_system`, `friction_debt`, and
`continuous_execution` sections are now required mappings; no new capability is enabled.

The new regressions produced 61 failures and two compatibility passes on the original source.
The final related context selection passed 178 tests. Changed-file Ruff and strict Pyright passed.
Full integrated/hosted proof and independent review belong in the delivering PR. A scratch-only
Pyright config selected the installed virtual environment while preserving bundled-stub priority;
the repository's strict settings were unchanged.

The supported Python 3.12/3.13 context matrix now runs the complete `test_context*.py` selection,
including the new malformed-state regressions, instead of only the two older context files.

The current-state checkpoint is also refreshed from live GitHub evidence and the verified code.
Its former August snapshot remains available in immutable Git history. This is a phase-boundary
reconciliation, not a release, Product sign-off, or experiment decision. Broader prompt discovery,
capability cross-checks, and cross-repository parity work remain open in #34.
