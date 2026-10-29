# Prompt routing and historical digest reconciliation — issue #34

This prose-only correction distinguishes the existing routes from the stronger naming claim:
active lab bodies say "Opus 5 low scouts" and explicitly name the implementer, reviewer, and
mechanic. The governor selects `.claude/agents/dll-scout.md`, but that name is not yet required
in each body or by the routing-token verifier. The prompt library and cross-repository contract
now describe that gap accurately. The shared runtime block delegates naming to each repository;
it does not contain the previously claimed `dl-*` prefix.

The shell-less scout requires coordinator-provided, policy-permitted tracked-file scope, a checked
commit, and tracking-check evidence before discovery. It attributes that evidence to the
coordinator rather than claiming to run Git itself. Its Read/Grep/Glob tool set is unchanged.
This addresses the scope contract in
[issue #34 comment 5229533508](https://github.com/Chris0Jeky/developer-lens-lab/issues/34#issuecomment-5229533508)
without adding a tool or authorizing protected input. The scout and continuous-work protocol also
use the established L0–L4 and L3/L4 taxonomy in place of their two stray W labels.

## Explicit supersession of LAB-GOV-02 digests

The earlier LAB-GOV-02 ledger entry remains an immutable historical observation. For current
parity, its manifest and runtime-block digests are explicitly superseded by the following values,
measured at repository commit `4b0ab8b7d1f971b41a18959337b60c71d5615eaf`:

- Manifest file SHA-256, over its exact raw bytes:
  historical `d2f78a1481cfcc4ba6e6f925d09d1090fc5ffbe69b6ffb444bcdef4b5c740171`;
  current `94e756f3dca1de93b906983395b763f80f156be8cb899c1e665f0f418b09a1b4`.
- `runtime-bootstrap-v1` body SHA-256:
  historical `018c0db78a90107022e76a14a03fee5fe3afe5cbf16a7dd26b0b91e3e1839ef6`;
  current `3313bc1a9884e5f3e62f621f124da212842e49e018361c99840927836bfedc0e`.
- `friction-tasking-v1` body SHA-256 is unchanged:
  `56bc9679fc51fd4ff5f05b715c42a96c3201284a6fee1a033524c2ccc55f5a7e`.

Block hashes use the manifest's normalization: exact fenced body, CRLF/CR converted to LF,
no trailing newline, UTF-8 bytes. Both current block hashes match the manifest entries.
Immutable evidence: the [historical ledger entry](https://github.com/Chris0Jeky/developer-lens-lab/blob/4b0ab8b7d1f971b41a18959337b60c71d5615eaf/docs/IMPLEMENTATION_LEDGER.md#L665),
the [manifest bytes](https://github.com/Chris0Jeky/developer-lens-lab/blob/4b0ab8b7d1f971b41a18959337b60c71d5615eaf/.agent-harness/prompt-parity.json),
and the [shared block source](https://github.com/Chris0Jeky/developer-lens-lab/blob/4b0ab8b7d1f971b41a18959337b60c71d5615eaf/docs/agent-system/PROMPT_LIBRARY.md).

No shared block, registered prompt-library body, parity-manifest byte, source verifier, test,
Product schema, or owner gate changes in this slice.
`Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` retains its existing closure.
Local context verification, strict MkDocs, and whitespace checks passed. A base comparison
confirmed all 14 registered prompt bodies, both shared blocks, and the manifest bytes unchanged;
final gate and review evidence belong to the delivering PR.
Explicit scout naming in active bodies, prompt discovery, and other remaining #34 work stay open.
Revert this single documentation patch if its descriptions or recorded hashes prove inaccurate.
