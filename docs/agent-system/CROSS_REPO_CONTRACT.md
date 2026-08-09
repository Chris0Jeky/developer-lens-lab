# Cross-repository governor contract

`developer-lens` is the **stable product and release side**: it owns presentation contracts,
compatibility, releases and the default runtime. `developer-lens-lab` is the **research and
experimental side**: experiments, corpora, methodological evaluation, candidate registries,
reproducibility and reports. This file is the lab-side statement of the agreement between the two
governors; the product repository carries its counterpart. Loop context: [README.md](README.md).
Owner authority: [OWNER_CONSTITUTION.md](../OWNER_CONSTITUTION.md). Product/lab analytical split:
[PRODUCT_BOUNDARY.md](../PRODUCT_BOUNDARY.md).

## What both governors must agree on

1. **Owner constitution version** — the same constitution version binds both sides; a version bump
   on one side is reconciled on the other before either merges dependent work.
2. **Responsibility split** — product owns stable contracts, compatibility, release and the default
   runtime; the lab owns experimental pipelines, research questions, generators and datasets, the
   candidate registry, evaluation, reports, reproducibility and public C0 scientific assets.
3. **Model routing** — the same table: flagship coordinator, Opus 5 low scout, Opus 5 high builder
   and reviewer, Sonnet 4.6 high mechanic ([WORK_CLASSES.md](WORK_CLASSES.md)). The lab's agents are
   named `dll-*`; the product's are named `dl-*`.
4. **Risk classes** — the same L0–L4 classes and the same mandatory-escalation list.
5. **Queue vocabulary** — the same labels and the same two-layer model: an unlimited GitHub-issue
   backlog plus a focused wave in each repository's live state file.
6. **Contract checks** — which shared surfaces are checked, by which command, on which side.
7. **Stable vs experimental channel** — the lab may publish to the experimental channel after its
   declared gates; promotion into the stable channel is governed by product-owned compatibility
   checks and the owner-approved promotion policy. An experimental output may be shown without
   becoming a default product claim, and the lab never promotes a model.
8. **Release sequencing** — both repositories tag together; product-owned schema changes release
   before or with the consumer that needs them, never after.
9. **Merge order** — stated explicitly per programme, before either side merges.
10. **Late-review protocol** — the same aging floor, the same two-round ceiling and the same
    mandatory post-merge sweep ([MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md)).
11. **Prompt operating system** — the same twelve common prompt IDs (`DL-P01`…`DL-P12`), the same
    two shared blocks, and a byte-identical `.agent-harness/prompt-parity.json`. See below.

## Prompt parity

The prompt library is per-repository, but its spine is shared. `.agent-harness/prompt-parity.json`
is **repo-neutral and byte-identical in both repositories**: each side resolves its own entry by
matching its declared repository slug, so the same file is copied across without editing. It pins
the twelve common IDs, each side's extension IDs (`DL-PX…` product, `DL-LX…` lab), and the SHA-256
of each shared block.

Two blocks are shared: `runtime-bootstrap-v1` (which canon each runtime reads first, how Claude
routes through its named agents, how Codex routes through `AGENTS.md` → shared `CLAUDE.md` →
continuation skill → Sol/Terra/Luna, and the fully qualified human-ref form) and
`friction-tasking-v1` (log material friction in the same hop, link it to a durable task, and treat
capture as a record rather than a licence to detour). Both must be **byte-for-byte identical** in
both repositories, which is why the digest is pinned rather than the prose merely being "kept in
sync".

The shared block names the repo-neutral `dl-*` spine. The lab's own agent files — `dll-implementer`,
`dll-reviewer`, `dll-mechanic` — are named by each prompt's lab runtime-routing clause, which lives
**outside** the shared block precisely so the block can stay byte-identical.

Editing a shared block is therefore a `cross-repo` change, and it runs like one:

1. Edit the block once in the product library, recompute its digest, and update every prompt that
   carries it plus the manifest **in the same commit** — the product's context verifier fails
   otherwise.
2. Copy the identical block body and the identical manifest to the lab side.
3. Prove on both sides with each repository's own context verifier (`uv run dllab context verify`
   here).
4. Record the merge order before either merge.

A lab-side edit that changes a shared block without the product edit landing first is out of order,
and the digest pin is what makes that failure loud rather than silent.

## Human-action reference discipline

The two repositories have **independent** human-action registers, issue numbers and card IDs. Every
human reference inside an active prompt body is written fully qualified —
`Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` is a **different gate** from
`Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8` — and a bare `q-N` fails the lab context
verifier for exactly that reason.

Concretely, and this is the pair most often conflated:

- `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` is the **product** register's concurrent-writer
  gate. It is what blocks agent merges in this repository (see below).
- `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8` is this repository's own gate on approving the
  final public transformation of a real-data study. It has nothing to do with merges.

## Compatibility rule

Any product-owned schema or presentation-contract change runs this sequence, in order:

1. **Product generation and check** — the product regenerates the artifact and runs its drift gate.
2. **Lab check-only sync** — the lab validates as a consumer without redefining the contract. The
   lab never edits a product-owned schema to make its own check pass.
3. **Fixture and export proof on both sides** — the lab proves its consumer path against the exact
   fixture bytes; the product proves its producer and rendering path.
4. **Explicit merge order** — written down before either merge; product-owned schema lands first
   unless a stated dependency inverts it, in which case the inversion is recorded.
5. **Post-merge byte and schema compatibility check** — re-verified after both merges, not inferred
   from the pre-merge run.

A change that skips a step is not compatible-by-assumption; it is unverified.

## Current status

- **Prompt operating system: delivered on both sides.** The product reference (issue
  `Chris0Jeky/developer-lens#214`) preceded lab PR #35, which merged at
  `bba0c18261c0a2b77332a0408f63b10c774c91f4` and closed lab issue #33. The lab result retains the
  byte-for-byte manifest and shared-block reuse; this records the merge result, not its operator.
- **Product concurrent-writer gate: closed by direct owner decision.** Clean-session evidence and
  the explicit closeout were merged through product PR #223 at
  `877f1ca07ccee014c0adf50925f989815e6bc7f1`. Therefore the conditional lab parking rule is not
  presently triggered. If the fully qualified product register is later open, prepare and park the
  lab PR again; never infer its state from a pull request, a quiet session, or another agent's
  message. The lab's own q-8 remains the unrelated real-data public-transformation gate.
- **Release remains gated.** Joint release is reaffirmed, but no tag is authorized until
  `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-10(c)` release sign-off and
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-11` aesthetic sign-off are complete. No data,
  model, telemetry, credential, or publication lane is opened by this reconciliation.
- **Shared surfaces today:** the `methodTrialView` presentation contract with its C0 fixture parity,
  and the ResearchPack schema. Both are product-owned; the lab consumes them check-only.
- **Data lanes stay C0.** Nothing in this contract opens a real-data lane on either side; that is
  governed by the activation preconditions in `.agent-harness/governor.json` and the owner sign-off
  `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-9`.
