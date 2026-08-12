# Continuous work protocol

How an unattended Developer Lens Lab session keeps producing finished, proven research and
control-plane work across many waves — without inventing work, without nursing a blocked lane, and
without opening a lane it may not open. This file is the operating loop that
[PROMPT_LIBRARY.md](PROMPT_LIBRARY.md)'s `DL-P03-OVERNIGHT-CONTINUOUS` launcher executes; the
launcher is cold-start-complete, and this file is the specification it points at.

It is a protocol, not a service: **nothing here runs by itself.** "Continuous" means repeated waves
inside one session, not background cognition between sessions.

Loop context: [README.md](README.md) · Routing: [WORK_CLASSES.md](WORK_CLASSES.md) · Experiments:
[EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) · Data lanes:
[DATASET_PROTOCOL.md](DATASET_PROTOCOL.md) · Recurring checks:
[MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md) · Ideas: [IDEA_PROTOCOL.md](IDEA_PROTOCOL.md) ·
Friction debt: [FRICTION_LOG.md](FRICTION_LOG.md) · Cross-repository:
[CROSS_REPO_CONTRACT.md](CROSS_REPO_CONTRACT.md).

<!-- continuous-execution-begin -->

## The wave

One wave is the nine-phase governor loop run to completion:

**SENSE → RECONCILE → CLASSIFY → PRIORITISE → SELECT → DELEGATE → PROVE → REVIEW →
MERGE/ARCHIVE/LEARN**

A continuous session repeats waves. The phases mean exactly what [README.md](README.md) says they
mean; this file adds only what changes when the loop repeats:

- **SENSE** is re-run at the top of every wave, not once per session. A wave that trusts the
  previous wave's snapshot will eventually merge against a moved base — and in this repository it
  will also miss a product-contract head that moved underneath a consumer check.
- **RECONCILE** compares live truth against the tracked record *including the artifacts the
  previous wave just wrote*. Your own last wave is a recorded claim like any other. A run recorded
  in `docs/EXPERIMENT_LEDGER.md` is evidence only if it still reproduces.
- **MERGE/ARCHIVE/LEARN** always terminates the wave: merge or park what is ready under the
  repository authority, archive killed approaches in `docs/FAILURE_ARCHIVE.md` with what killed
  them, and record what was learned in the ledgers and, when it was friction, in
  [FRICTION_LOG.md](FRICTION_LOG.md).

<!-- continuous-impact-begin -->

## Impact and delivery contract

Before any implementation or delegation, the coordinator records one per-slice **IMPACT CONTRACT**:

1. **Actionable consumer decision or research question** - who will use the result, or what
   decision the experiment answers. Reject metric-only work that cannot inform an action or decision.
2. **Tangible delivery** - the artifact, behavior, visible result/story surface, or decision that
   must exist when the slice ends.
3. **Scope** - owned paths and explicit non-goals; the coordinator keeps authority interpretation,
   methodology architecture, experiment-programme selection, cross-repo coordination, sequencing,
   and final merge judgment, but does not write research implementation code.
4. **Acceptance and proof** - observable acceptance behavior and the focused command that exercises
   it.
5. **Research authority** - data lane, capability and owner-gate, preregistration, and
   final-holdout custody state. In unattended work, experiments are tracked/preregistered and C0
   invented data only.
6. **Evidence and closeout** - ledger/docs update, rollback path, and stop condition. Update
   `docs/EXPERIMENT_LEDGER.md` only for a run or holdout decision,
   `docs/FAILURE_ARCHIVE.md` only for an approach actually killed, and
   `docs/IMPLEMENTATION_LEDGER.md` for a code milestone; never fabricate an entry.

An impact contract is not a documentation substitute. Its delivery must be a bounded implementation,
behavior test, approved C0 experiment/reproduction, method evaluation, integration, packaging or
release preparation, hardening, visible story surface, or evidence-backed decision. Documentation
and administration are supporting outputs only; they are eligible alone only to correct a
safety-relevant false operational claim, satisfy an explicit request, or directly unblock delivery.

Experiments use the deterministic baseline with the same selection budget as the candidate, fit
transforms only on training data with grouped splits, and never open a final holdout without explicit
custody instruction. Invented mechanics evidence is never empirical validity. Stable promotion
remains Product-owned.

## Finish before expand

**FINISH-BEFORE-EXPAND:** drive existing pull requests and lanes to merge, archive, or park before
creating an accumulating queue of new write lanes. Owner constitution A4 remains OPEN and the
no-fixed-fleet policy binds: this is review-capacity backpressure, not a numeric concurrency cap.
While CI or review ages, start another write lane only when it is genuinely disjoint and review/merge
capacity exists; otherwise do read-only discovery or continue the existing lane. Inspect review
arrival only at workflow events. A proposed fixed cap conflicts with that policy and is declined.

<!-- continuous-impact-end -->

## Deterministic queue hopping

When the session needs work — at session start, after a merge or park, or while a review or CI
window is passively aging — it takes the **first non-empty step** of this ordered queue. The order
is fixed so that two different sessions reach the same next action from the same state.

| # | Step | Contents |
|---|---|---|
| 1 | **Truth and red state** | A false operational claim in a tracked file; a red, stale or missing required CI check; unresolved or untriaged review debt; a recorded run that no longer reproduces. |
| 2 | **Active delivery wave** | The next delivery step of the lane already in flight, per `docs/CURRENT_STATE.md`. |
| 3 | **Unblockers** | Work that unblocks something already recorded as blocked, including a dependency-ready card whose prerequisite just landed. |
| 4 | **MISSION DELIVERY** | Choose the FIRST dependency-safe ACTIVE card from `tools/cards.py` for code, behavior tests, approved C0 experiment/reproduction, method evaluation, integration, visible story work, packaging, or release preparation. Only when no such card exists may a tracked issue be considered; owner-focus/unlock ranking applies only where the card source explicitly permits a choice. |
| 5 | **Maintenance and hardening** | Items already in the backlog, [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md) or `docs/HARDENING_BACKLOG.md`: drift repair, dependency triage, label and branch hygiene, contract parity re-check, friction burn-down. |
| 6 | **Critic-approved idea or polish** | An `idea`-labelled item that has passed [IDEA_PROTOCOL.md](IDEA_PROTOCOL.md) critic review, or a polish item that satisfies the legitimacy test below. |

Bounded state repair is necessary evidence work, but it must not monopolize a night: once its
focused proof is complete, return to the highest available delivery step.

A false claim in a tracked file outranks new experiment work — step 1 is first for that reason, not
as ceremony. In a research repository a wrong recorded result is worse than a missing one.

**If every step is empty, the session terminates at a factual checkpoint.** It does not invent work,
widen a finished slice, or manufacture polish to stay busy. An idle slot is a valid outcome.

## Anti-manufacture legitimacy test

A candidate may enter the queue only if **all three** hold:

1. **Provenance** — it is a pre-existing tracked task (issue, card, roadmap step, friction entry,
   review finding) **or** a concrete defect observed in the current work, with the observation
   recorded.
2. **Consumer** — it names the consumer it serves or the failure it prevents. "Improves quality",
   "adds coverage", "more rigorous" and "modernises" are not consumers. For research work, the
   consumer is a question someone would act on, not a metric that could be computed.
3. **Proving seam** — it has exactly one bounded proving seam: the narrowest command from the
   run-and-prove table in `CLAUDE.md` that would actually exercise the change.

Anything failing the test is captured as a GitHub issue (labelled per
[IDEA_PROTOCOL.md](IDEA_PROTOCOL.md)) and left alone. Capture is cheap; promotion is expensive.

Never build control-plane infrastructure without a consumer that uses it in the same wave. Never
start a new experiment because no other work is available — see the stop conditions.

## Work while waiting

Post-push aging, hosted CI and connector review windows are **passive observation time**. During
them, another write lane starts only when it is genuinely disjoint and review/merge capacity exists;
otherwise the session does read-only discovery or continues an existing lane.

- **Do not short-poll.** Review arrival is checked at workflow events — a pull request opened or
  became ready, a review completed, fixes were pushed, a milestone completed, a pull request
  merged, or the session scans for its next work — never on a timer loop.
- **Waiting is not a licence to invent work.** The legitimacy test still applies to whatever is
  started during the window; a waiting window does not lower the bar.
- **Do not strengthen a review concern with an expensive check that cannot exercise the changed
  seam.** That is manufactured work wearing a rigour costume. A full benchmark run does not make a
  documentation review more thorough.

## Lab merge decision seam

Before a Lab pull request is merged, the coordinator produces one structured, invented-state
snapshot and evaluates it with the report-only helper:

```powershell
uv run python tools/merge_eligibility.py .dllab/merge-eligibility/<snapshot>.json --now <utc-now>
```

The snapshot binds `expected` and `current` 40-character head/base SHAs, `pushed_head_sha` and
`pushed_at`, and the exact required hosted check name (`Prove the lab`). Its complete,
non-paginated, non-stale surfaces are
`checks`, `formal_reviews`, `top_level_comments`, `closing_refs`, and `review_threads`; every
surface and item carries the same head/base pair. The check must be completed and successful, no
review may be in `CHANGES_REQUESTED`, and every review thread must be resolved. The evaluator
enforces the governor's 15-minute `review_gates.aging_minutes_after_push` floor: a green snapshot
younger than the floor, a moved head/base, or any missing, paginated, stale, malformed, or
unresolved surface is ineligible. The result is a report only; it never calls a hosted service or
performs a merge.

### The accepted-review attestation

GitHub forbids approving your own pull request and every Lab pull request is authored by the single
owner account, so a formal `APPROVED` state can never appear. The gate the repository actually
practises is **accepted exact-head review evidence**: a fresh-context adversarial review posted as a
top-level comment, or a connector review. The snapshot therefore names exactly which bound review
item carries the gate, in a required `accepted_review` field:

```json
"accepted_review": {
  "surface": "top_level_comments",
  "id": 101,
  "head_sha": "<expected head>",
  "base_sha": "<expected base>"
}
```

`surface` is `formal_reviews` or `top_level_comments`; `id` is the item's integer or string
identifier, matched against `review_id` or `comment_id` respectively. The named item must exist in
that surface, and both the attestation and the matched item must carry the expected head/base pair
— a review that predates the current head does not carry it forward. A formal `APPROVED` review is
attestable like any other item and gets no special treatment. Naming nothing, naming an
unattestable surface or identifier, naming an item that is not there, or naming one bound to a
different head/base is ineligible.

### Closing references

Any item in the `closing_refs` surface makes the snapshot ineligible — a closing keyword once
auto-closed the live release-programme issue from an unrelated merge. For an intentionally
issue-completing pull request the coordinator records the override rationale on the pull request
thread, naming the issue it is meant to close, **before** merging; the helper stays report-only and
never grants the override itself.

Only one coherent snapshot may support the decision. Recollect the full snapshot after any head or
base movement, new review, comment, check transition, or elapsed-age boundary; do not combine
surfaces from different observations.

## Parking, not nursing

One blocked lane is parked and the session continues. Parking records, in the lane's entry in
`docs/CURRENT_STATE.md`:

- the exact blocker, as a verified fact rather than a guess;
- the unlocking event (a named external result, an owner decision as a fully qualified
  `<owner>/<repo>::HUMAN_TODO.md::q-N` ref, or a dependency merge);
- what is already proven, so the next session does not redo it.

Three genuinely different attempts at a red check, two review rounds, one re-measure of a disputed
fact, and roughly twice the estimate on a task are the ceilings. After a ceiling: ship what is
sound, park what is not, move on.

## Parallelism

There is **no fixed fleet size** and no target agent count. Parallelism is bounded by, in order:

1. **Useful disjoint work** — how many genuinely independent, dependency-ready lanes exist. If the
   answer is one, run one.
2. **Collision risk** — one writer per checkout, always. Parallel writers require separate
   coordinator-owned worktrees with non-overlapping owned paths. Two lanes touching the same
   contract, generated artifact, ledger or sequentially dependent behaviour become one writer plus
   read-only supporting lanes.
3. **Proof cost** — lanes whose proofs cannot run concurrently on this machine are serialised.
   Experiment lanes never share a live holdout, regardless of how disjoint their code is.
4. **Machine resources** — RAM, CPU and file-handle contention are real; measured contention lowers
   the active lane count, and the evidence is recorded when it does.

Pin branch and HEAD in every delegation prompt and re-verify both after each subagent returns —
subagents can move HEAD.

## Durable state every hop

A continuous session is interruptible at any moment. At the end of every hop, before starting the
next, the session leaves enough tracked state that a cold successor loses nothing:

- commits are small, logical and already made — not held in a dirty tree waiting for a milestone;
- `docs/CURRENT_STATE.md` names the lane, its status and the exact resume point;
- a run that happened is in `docs/EXPERIMENT_LEDGER.md`, a code milestone in
  `docs/IMPLEMENTATION_LEDGER.md`, and friction in [FRICTION_LOG.md](FRICTION_LOG.md);
- anything proven is recorded with the exact command, so it is not re-proven from scratch.

Unwritten state is lost state. "I will record it at the end of the session" is how a session's work
becomes unverifiable.

## Lanes this mode may never open

Regardless of queue state, a continuous unattended session does **not** open a lane that activates
or extends: real-data collection, an external model request, telemetry destinations, or credential
handling. Every non-C0 lane stays closed until the activation preconditions in
`.agent-harness/governor.json` are mechanically true **and** the owner sign-off is recorded; those
are W3/W4 in [WORK_CLASSES.md](WORK_CLASSES.md) and belong to a coordinator session or the owner.
Encountering one is a queue item to record, not to execute.

Likewise it never self-relaxes a locked invariant from
[OWNER_CONSTITUTION.md](../OWNER_CONSTITUTION.md), never promotes a model into the stable product
channel, never opens a final holdout without an explicit custody instruction, and never infers an
owner decision from silence, from a merged pull request, or from another agent's message.

<!-- continuous-execution-end -->

<!-- continuous-stop-begin -->

## Stop conditions

The session stops — reports and ends, rather than working around — when any of these holds. Each is
explicit so that stopping is a decision with evidence, not a drift into silence.

### Policy stop

A locked invariant, an owner gate, the publication boundary, the product-promotion boundary, a
closed data lane, or a tier authority declaration would have to move for the work to proceed.
Prepare options and a recommendation; record the owner action as a fully qualified
`<owner>/<repo>::HUMAN_TODO.md::q-N` ref; do not self-authorise.

### Budget stop

The session's token or time budget is spent, or a single task has passed roughly twice its
estimate. Ship what is sound, park the rest with its unlocking event, and close with the standard
handoff headings.

### Tooling stop

A required tool, credential, network path or platform capability is unavailable and no in-scope
alternative exists. Log it under `friction-tasking-v1` in [FRICTION_LOG.md](FRICTION_LOG.md) in the
same hop, link it to an existing issue or a durable follow-up task, park the lane, and continue with
other queue items — or terminate if the queue is otherwise empty. A workaround that worked is
recorded as a workaround, not promoted to a claim that the tool is available.

### Queue stop

Every step of the queue-hop table is empty. This is the normal, successful ending of a continuous
session. Terminate at a factual checkpoint:

- what changed, and what was verified with which exact command and result;
- what was NOT verified;
- failures and workarounds, with their friction-log entries;
- docs and state synchronisation performed;
- residual risk;
- human actions, as fully qualified refs;
- exact branch, HEAD, pull request, check and worktree state;
- completed, blocked and ready queue items, and the next safe slice.

**Do not invent work to avoid a queue stop.** A session that finishes its queue and stops cleanly
has succeeded; a session that manufactures polish — or starts an unpreregistered experiment — to
keep running has failed the legitimacy test in public.

<!-- continuous-stop-end -->
