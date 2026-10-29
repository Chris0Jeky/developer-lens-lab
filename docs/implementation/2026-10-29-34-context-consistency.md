# Issue #34: manifest membership and capability consistency

## Scope and source evidence

This bounded follow-up starts from PR #201 head
`4b0ab8b7d1f971b41a18959337b60c71d5615eaf` and addresses two reproduced context-verification
gaps for [issue #34](https://github.com/Chris0Jeky/developer-lens-lab/issues/34).
The registered LAB-GOV-02 card remains delivered; this is its tracked post-review hardening.
Owned paths are the context verifier, the new focused consistency tests, and this fragment.

The live Product `.agent-harness/prompt-parity.json` was read through the connected GitHub source.
Blob `2d4e274f55ee2438230eda0b621c761dd554757e` declares the same two repository identities,
roles, paths, and extension IDs as the Lab manifest. No manifest or shared prompt bytes change.
The current capability vocabulary follows the existing T1/C0 checks, governor lane and gate pins,
stable-product promotion boundary, and the bounded presentation approval in
`Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-4`. No new configurable policy source is added.

## Changed behavior

The parity verifier requires exactly one Product entry and exactly one Lab entry. Missing,
duplicate, unexpected, or non-object repository entries fail. Both entries must retain their
declared roles, all three registered paths, and ordered extension IDs. Repository entry order is
not significant. Existing common-ID and shared-block digest verification is preserved.

Repository verification first runs the existing tier and governor checks. Only their successfully
verified bootstrap posture is used to check the resume document's capability summary. It requires
all five governed names and rejects unknown names, missing statuses, non-string values, enabled
claims, and misleading status prefixes. A status may retain its optional parenthesized explanation;
that prose carries no authority. The standalone YAML shape verifier remains usable without a
complete policy fixture.

This is a consistency check for the currently supported bootstrap posture, not an activation
engine. LAB-ACT-01 must update it together with the existing tier/lane pins before a future
activation can be represented. Owner-decision prose still requires review; this check does not
infer new approval from a summary, replace live owner gates, or independently authenticate
`Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-4`.

## Verification

- RED: the initial focused regression suite reported **35 failed, 7 passed** against the unmodified
  verifier. Missing Product membership, duplicate/extra entries, invalid Product metadata, and
  conflicting/missing/unknown capability claims were all accepted before the fix.
- GREEN: the final focused suite plus all existing context tests reported **245 passed**.
- `dllab context verify` passed using this checkout's source.
- Ruff formatting and lint passed on the changed Python files.
- Strict Pyright passed with **0 errors, 0 warnings, 0 informations**, using the repository's strict
  settings, the coordinator-provided environment, and this checkout's source as the only extra
  import path.
- `git diff --check` passed.

The final tests also prove that invalid tier or governor activation edits still fail when the
resume summary claims the same activation. Current annotated statuses and their unannotated
equivalents pass. All test mutations are invented and transient.

A local Pyright configuration initially supplied absolute include paths, which Pyright ignores;
that invocation was stopped and the include paths were corrected to be configuration-relative.
The corrected strict run above is the verification evidence. No environment resynchronization
or dependency mutation was needed.

The coordinator's full gate passed 1,326 tests with nine native-Windows skips, then stopped at
the clean-tree benchmark preflight because generated coverage shards remained untracked.
The exact published commit passed the remaining smoke/replay/export checks in a clean checkout.
After the same friction occurred independently for PR #200, FR-114 records the bounded promotion:
ignore only `.coverage.*` generated shards alongside the already ignored combined database.
Ordinary untracked paths still fail the clean-tree guard; source and experiment checks are unchanged.

## Boundaries and handoff

Full code/config gates, fresh-context exact-head review, GitHub publication, aging, merge judgment,
and shared ledger/current-state synchronization remain coordinator-owned. No Product schema,
paired runtime contract, frozen exhibit, prompt digest, owner gate, or capability activation changes.
No benchmark, holdout opening, or data collection occurred during the initial implementation slice.

Rollback is this isolated three-file change. Stop if review requires changing Product-owned
contracts or capability authority; reconcile that scope before proceeding. Resume with exact-head
review and the complete declared gate, then link this fragment from the implementation ledger.
