# Friction log

The repository's record of what keeps costing sessions time. It exists because a workaround that is
only remembered is a workaround that will be rediscovered — expensively — by the next session.

Foundational rule (`friction-tasking-v1`, carried verbatim by every active prompt in
[PROMPT_LIBRARY.md](PROMPT_LIBRARY.md)):

> Every material workaround, tooling hiccup, repeated friction or surprising divergence is logged
> here in the SAME hop, and linked to an existing issue or card or given a durable follow-up task.
> Capture is not permission to detour: log it, link it, continue the slice. At the second
> independent occurrence, choose or propose the cheapest layer that actually enforces the fix, or
> record why it stays task debt.

Burn-down prompt: `DL-P12-FRICTION-BURNDOWN`. Loop context: [README.md](README.md). Recurring
checks: [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md). Continuous execution:
[CONTINUOUS_WORK_PROTOCOL.md](CONTINUOUS_WORK_PROTOCOL.md). Cross-repository:
[CROSS_REPO_CONTRACT.md](CROSS_REPO_CONTRACT.md).

## Schema and rules

This log is **append-only**. New entries are added at the end with the next free `FR-NNN`. An
existing entry is never deleted or rewritten; only its `status`, `occurrences`, `task` and
`promotion` fields may change, and a substantive change adds a dated note under the entry.

Each entry carries exactly these fields:

| Field | Meaning |
|---|---|
| `id` | `FR-NNN`, assigned in order, never reused. |
| `first-seen` | ISO date of the first recorded occurrence. |
| `status` | `open` · `workaround-documented` · `promoted` · `owner-gated` · `resolved`. |
| `symptom` | What was observed, factually, without inference. |
| `impact` | What it costs a session when it happens. |
| `workaround` | What was actually done instead, or `none`. |
| `occurrences` | Count plus the dates or artifacts that record them. |
| `task` | The linked issue, card or owner action — a fully qualified ref for anything cross-repository or human-only. |
| `promotion` | The enforcement layer chosen, or the recorded reason it stays task debt. |

Rules that bind entries:

1. **Never mark an entry `resolved` by inference.** Age, a merged pull request, a quiet session, or
   another agent's prose are not proof. Resolution needs a passing check, an enforced rule, or an
   inspected setting, and the proof is named in `promotion`.
2. **Human-only friction stays `owner-gated`** — local machine hygiene, credentials, legal and
   aesthetic sign-off cannot be closed by an agent. Keep the `HUMAN_TODO.md` link live.
3. **No volatile detail.** No process IDs, absolute local paths, tokens, environment values, or
   private identifiers. An entry must be readable in a public repository.
4. **One occurrence is task debt, not a pattern.** Promotion is considered at the second
   independent occurrence, using the cheapest layer that actually enforces the fix: session memory
   → canon prose → agent/skill definition → executable check → CI → structural change. Prune the
   superseded copy in the same commit.

## Entries

### FR-001 — no repository-wide `uv` on the host; a confined bootstrap works

- **first-seen:** 2026-08-08
- **status:** `promoted`
- **symptom:** No `uv` executable is resolvable on this host's PATH, so the `uv …` commands in the
  run-and-prove table of `CLAUDE.md` cannot be invoked as written. A worktree-confined bootstrap —
  a standard-library virtual environment, `pip install "uv>=0.12.2,<0.13"` into it, and the literal
  `uv` executable from that environment configured for a confined worktree-local project
  environment — resolves `uv 0.12.3` and runs `uv sync --locked --all-groups` and the full declared
  gate successfully.
- **impact:** A session that reads the run-and-prove table literally concludes the repository cannot
  be proven on this host, and either skips the gate or parks work that is actually runnable. The
  bootstrap itself costs a few minutes once per checkout.
- **workaround:** Bootstrap the confined `uv` as above and run the declared gate through it. The
  bootstrap environment is gitignored; `uv.lock` is never modified as a side effect.
- **occurrences:** 5 recorded — 2026-08-08 (bootstrap first proved: locked sync plus full gate),
  2026-08-09 (LAB-GOV-02 reused the same route from a clean checkout), 2026-08-09 (the release-gate
  sync reused its surviving confined bootstrap), 2026-08-09 (the post-dependency state-sync
  worktree bootstrapped its own copy), and 2026-08-09 (the licence/package-identity worktree reused
  the route).
- **task:** lab issues #29 (release wave) and #5 (dependency triage), which both depend on a
  runnable locked environment.
- **promotion:** Promoted to canon prose in [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md),
  which now states the confined-bootstrap route rather than declaring the gate unrunnable. Not
  promoted to an executable check: installing a toolchain is an environment action, not a
  repository invariant, and a check that bootstrapped `uv` as a side effect would hide the cost.

_Note 2026-08-09 (release-gate sync):_ The promoted route remained sufficient on the third
occurrence: the existing worktree-confined bootstrap ran the locked context verifier without a
new install or lockfile change.

_Note 2026-08-09 (release wave):_ The fourth and fifth isolated worktrees used the same promoted
route. This repeated cost stays environment debt: the existing maintenance-protocol instruction is
the cheapest truthful layer, and an automatic installer would hide network and time side effects.

### FR-002 — a stale "tooling-blocked" claim outlived the proof that removed it

- **first-seen:** 2026-08-09
- **status:** `promoted`
- **symptom:** [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md) asserted that on this host `uv` is
  unavailable and therefore dependency re-locking is tooling-blocked. That claim remained in a
  tracked file after FR-001 had already proved a working confined `uv` route, so a tracked authority
  file was stating a blocker that no longer existed.
- **impact:** A false operational claim in a tracked file is the highest-priority repair class in
  [CONTINUOUS_WORK_PROTOCOL.md](CONTINUOUS_WORK_PROTOCOL.md) precisely because of this shape: it
  causes later sessions to park runnable work without re-testing the blocker. `docs/CURRENT_STATE.md`
  had already been corrected; the protocol file had not.
- **workaround:** none — corrected rather than worked around.
- **occurrences:** 1 recorded — 2026-08-09 (found during LAB-GOV-02 while reading the maintenance
  protocol for the prompt-system rewrite).
- **task:** lab issues #33 (this control-plane card, which corrected the text) and #29 (the release
  wave whose dependency work the stale claim was blocking).
- **promotion:** Corrected in place in the same commit that recorded it. The general rule — a
  blocker claim is re-tested before it is inherited, and a disproved blocker is corrected in the
  same hop — is carried by the RECONCILE phase in
  [CONTINUOUS_WORK_PROTOCOL.md](CONTINUOUS_WORK_PROTOCOL.md) and by `DL-P04-RESUME-RECONCILE`. Not
  promoted to an executable check: no verifier can decide whether a prose blocker is still true.

### FR-003 — declared Windows directory-symlink test skips have never been narrowed

- **first-seen:** 2026-08-09
- **status:** `open`
- **symptom:** `docs/IMPLEMENTATION_LEDGER.md` records "pre-existing Windows directory-symlink
  skips" as a standing, accepted part of many proving passes across multiple milestones. The skip
  count is recorded, but no entry records the exact skipped test identities, the precise platform
  condition, or a proof that the skipped behaviour is genuinely untestable on this platform rather
  than merely unimplemented.
- **impact:** A recurring skip that is described but never narrowed becomes invisible: it is
  reported as normal in every handoff, so no session ever asks whether it hides a real coverage gap
  on the platform the repository is actually developed on.
- **workaround:** none — the skips are reported honestly in each proving pass, which is why they are
  visible enough to log here. Reporting is not the same as understanding.
- **occurrences:** 1 recorded as friction — 2026-08-09 (LAB-GOV-02), though the underlying skips
  appear in many recorded proving passes.
- **task:** lab issue #33 records it; it stays task debt until a bounded slice narrows it to exact
  test identities and a stated platform condition.
- **promotion:** Deliberately NOT promoted yet. Promotion needs the second independent occurrence
  and, more importantly, a narrowed cause: an executable assertion about a skip whose reason is
  unproved would pin the symptom rather than enforce the property.

_Note 2026-08-09 (LAB-GOV-02):_ the full gate run for this card names the three skips exactly, so
they are no longer anonymous: `tests/test_contract_sync.py` skips with "directory symlinks are
unavailable on this host", and `tests/test_method_trial_export.py` and `tests/test_wbc1_runner.py`
each skip with "file symlinks are unavailable on this host". Two distinct conditions, not one. Still
unproved is *why* the host cannot create them and whether the skipped behaviour is genuinely
untestable here or merely unexercised; the entry stays `open` for that reason.

### FR-004 — concurrent-writer hazard in the lab checkout (cross-repository, owner-gated)

- **first-seen:** 2026-08-07
- **status:** `resolved`
- **symptom:** A process other than the owning session was observed running Git operations inside
  the `developer-lens-lab` working directory mid-slice. A competing writer in the same working
  directory can corrupt a branch between an agent's read and its commit, and lane ownership cannot
  be verified from inside a session.
- **impact:** All lab-side merges are treated as human-gated: an agent cannot prove, from inside the
  affected checkout, that the remote head it merges is the head it reviewed. Work is prepared and
  parked rather than merged, which lengthens every lab lane.
- **workaround:** Lab work is prepared from a verified isolated worktree and parked as a pull
  request for a human to merge. Isolation makes *preparation* safe; it does not make a *merge* safe
  while a competing writer can still race the remote.
- **occurrences:** 1 recorded on the lab side — 2026-08-07. The product-side log records the wider
  pattern; this entry is the lab-side view of the same hazard.
- **task:** `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8`. This is the **product** register's
  `q-8`; the lab's own `q-8` is an unrelated gate about publishing real-data studies, and the two
  must never be conflated.
- **promotion:** The specific product merge-blocking owner gate is resolved by direct owner closure,
  mechanically clean `claude agents --json --all`, and report-only MCP-hygiene evidence. The
  immutable `impact` and `workaround` text is **HISTORICAL** for periods when the product gate was
  open; it is not a current parking instruction while this status is `resolved`.
  The enforceable conditional parking rule remains promoted in
  [CROSS_REPO_CONTRACT.md](CROSS_REPO_CONTRACT.md),
  [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md) and every active prompt's LAB MERGE GATE line;
  it re-enables if `Chris0Jeky/developer-lens::HUMAN_TODO.md::q-8` is later open. The underlying
  collision risk remains handled by the one-writer/worktree rules.

_Note 2026-08-09 (PR #36 fix round 1):_ This supersedes the old current-impact/`owner-gated`
wording only for the specific product q-8 merge-blocking owner gate. Direct owner closure plus the
mechanically clean `claude agents --json --all` and report-only MCP-hygiene evidence resolve that
gate; they do not erase the general concurrent-writer collision risk, which remains governed by
one-writer/worktree rules and the re-enabled conditional parking rule if the fully qualified product
q-8 reopens. The immutable `impact` and `workaround` text is **HISTORICAL** for the period when the
product gate was open, not a current parking instruction while status is `resolved`; it does not
alter `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-8`.

### FR-005 — agent floor rejects heredoc stdin and unresolvable recursive-delete targets

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Two shell forms were refused by the agent floor during ordinary work in this
  repository: a heredoc redirected into an interpreter's stdin (`… <<'EOF'`), refused as a dynamic
  redirect target that cannot be inspected safely; and a recursive delete whose target the floor
  could not resolve.
- **impact:** Small per-occurrence cost, but it interrupts the natural way of running a short
  throwaway script or clearing a generated directory, and a session that has not seen it before
  spends time diagnosing it as a repository problem rather than a floor rule.
- **workaround:** Write the throwaway script to a file under the gitignored bootstrap directory and
  run the interpreter against that path; delete generated paths with an explicitly resolvable target
  or leave gitignored build output in place. Both are cheap and leave the tracked tree clean.
- **occurrences:** 1 recorded — 2026-08-09 (LAB-GOV-02, both forms in the same session).
- **task:** lab issue #33 records it; no repository change is required.
- **promotion:** Deliberately NOT promoted. This is agent-harness behaviour, not a repository
  invariant: the cheapest layer is session memory, which is outside this repository's enforcement
  ladder. Revisit only if it recurs in a way that costs a lane rather than a minute.

_Note 2026-08-09 (LAB-GOV-02):_ a third form appeared in the same session — holding an executable
path in a shell variable and invoking it (`$UV run …`) is refused as a dynamic executable name. The
workaround is identical: invoke the literal interpreter or executable path. This strengthens the
`occurrences` picture but does not change the promotion decision, since all three forms share one
cheap workaround and none of them blocked a lane.

### FR-006 — orchestration wall-clock timeout terminated a session after its work was complete

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A 30-minute orchestration wrapper around an agent session expired and terminated the
  owned agent process. The timeout fired *after* the session's final gate subprocess had already
  exited and the tracked tree was clean, so every commit survived; what was lost was the session's
  own closing report, not repository work. The wall-clock limit is a property of the wrapper, not of
  any repository command.
- **impact:** The real cost is epistemic, not mechanical. A terminated session leaves recorded
  claims — here, an implementation-ledger entry asserting a green full gate at an exact head — with
  no live witness that they were ever true. A successor that trusts such a claim inherits an
  unverified assertion; one that re-proves everything from scratch pays for the whole gate again.
  The full declared gate costs roughly 2 minutes of wall clock on this host, most of it pytest.
- **workaround:** Resume in the same checkout rather than a fresh clone, and reconcile instead of
  assuming: verify branch, HEAD, base and tree cleanliness against the pins first, then re-run the
  narrowest proof for the slice before the full gate. The worktree-confined `uv` bootstrap from
  FR-001 survives process termination, so no re-bootstrap is needed — reuse
  `.venv/uv-bootstrap` with the confined worktree-local project environment configured for the
  bootstrap. On 2026-08-09 this route
  re-confirmed the prior session's claim exactly: 78 context tests, then the full gate green at the
  unchanged head `a4702354cfb7a029d77af5a61ec518982d7f5262`, with `uv.lock` untouched. The ledger
  claim was therefore accurate and required no correction.
- **occurrences:** 1 recorded — 2026-08-09 (LAB-GOV-02 prompt-system slice).
- **task:** lab issue #33 (LAB-GOV-02), the slice that was in flight when the wrapper expired.
- **promotion:** Deliberately NOT promoted. The controllable half is already canon: committing in
  small logical increments and writing durable state every hop is what made this timeout cost a
  report rather than a slice — see the "Durable state every hop" section of
  [CONTINUOUS_WORK_PROTOCOL.md](CONTINUOUS_WORK_PROTOCOL.md). The uncontrollable half is an external
  wrapper budget, which no repository check can enforce. Revisit only if a timeout lands mid-write
  and leaves a dirty tree, which would be a materially different failure.

### FR-007 — Claude runtime denied writes to the committed agent surface

- **first-seen:** 2026-08-09
- **status:** `promoted`
- **symptom:** The required mechanical delegation could not write a committed `.claude/agents`
  file because the Claude runtime denied that surface. The same denial had already occurred in the
  sibling product repository.
- **impact:** The prescribed Claude mechanic lane cannot complete agent-file parity changes even
  when the recipe is bounded and the target is tracked. Without a defined fallback, the coordinator
  would either lose the parity slice or be tempted to bypass the runtime boundary.
- **workaround:** The coordinator used the Codex implementation fallback in the isolated writer
  worktree, preserving one writer and the exact bounded recipe; no runtime boundary was bypassed.
- **occurrences:** 2 recorded — 2026-08-09 (product and lab prompt-operating-system slices).
- **task:** lab issue #33 (LAB-GOV-02), with the corresponding product issue #214.
- **promotion:** Promoted to the Codex fallback plus executable parity: `dll-scout` is now pinned in
  `.agent-harness/governor.json`, all four lab Claude agents require one byte-identical friction
  block, and both continuation skills require one byte-identical continuation-friction block. The
  context verifier and focused tests fail on missing, duplicate, reversed, or drifted blocks. This
  is the cheapest repository-enforced half; the runtime denial itself remains an external boundary.

### FR-008 — bundled review-thread reader needs UTF-8 mode on Windows

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** The bundled GitHub review-thread reader failed while decoding non-ASCII review text
  through the host's default Windows code page, so its otherwise successful GraphQL response could
  not be parsed.
- **impact:** Unresolved inline review state is a merge-gate input. Without an explicit encoding,
  the failure can make a complete thread read look unavailable and tempt a flat-comment fallback
  that omits resolution state.
- **workaround:** Run the reader with Python UTF-8 mode enabled for that invocation. The same
  read-only command then returned both unresolved PR #36 threads with their resolution and line
  anchors intact.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the PR #36 review sweep.
- **task:** lab issue #34 records prompt-operating-system post-review hardening; keep this external
  tooling wrinkle there unless it recurs independently.
- **promotion:** Deliberately NOT promoted after one occurrence. The reader belongs to an external
  skill bundle rather than this repository; a second independent occurrence should be reported to
  that bundle and should make UTF-8 decoding explicit at the tool boundary.

### FR-009 — inline GraphQL quoting is fragile in PowerShell

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** An inline `gh api graphql` query containing the hyphenated repository name lost the
  string quoting expected by GraphQL under PowerShell and returned a type-coercion error instead of
  the requested review-thread state.
- **impact:** Review-thread state is a merge-gate input, so a shell-quoting failure can interrupt an
  otherwise ready merge boundary.
- **workaround:** Use the REST review, inline-comment, and issue-comment endpoints for the bounded
  empty-thread check, or pass GraphQL values as variables instead of embedding repository strings.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the PR #38 merge-boundary sweep.
- **task:** lab issue #34 tracks prompt-operating-system post-review hardening and the external
  Windows review-tool boundary.
- **promotion:** Deliberately NOT promoted after one occurrence. If it recurs independently, move
  the canonical thread query into the reviewed helper with variable binding rather than adding
  more shell-specific escaping guidance.

### FR-010 — a later native command can mask an earlier failure in PowerShell

- **first-seen:** 2026-08-09
- **status:** `promoted`
- **symptom:** A missing requested Python runtime failed, but a following successful
  `git diff --check` became the shell invocation's final exit status and made the combined command appear
  successful.
- **impact:** A proving command can be reported green even though the command that exercised the
  changed seam never ran.
- **workaround:** Check `$LASTEXITCODE` immediately after each required native proving command and
  exit on failure before starting the next command. The release-gate sync then used the promoted
  confined-bootstrap route and produced a real context-verifier pass.
- **occurrences:** 2 independent occurrences — 2026-08-09 (a missing Python runtime was masked by
  a later diff check), 2026-08-09 (an unsupported PowerShell `Get-Date` option was masked by later
  successful GitHub reads).
- **task:** lab issue #29 owns the release-evidence boundary; retain explicit per-command failure
  guards in its remaining proving commands.
- **promotion:** Promoted to the active-session PowerShell preamble for every multi-command probe:
  set `$ErrorActionPreference = 'Stop'` and `$PSNativeCommandUseErrorActionPreference = $true`, while
  retaining explicit `$LASTEXITCODE` guards where portability matters. This belongs at the
  orchestration shell boundary rather than in a repository helper: the failures were arbitrary
  external command compositions, and a repo script could not enforce callers that bypass it.

### FR-011 — a worktree cannot create itself from a not-yet-existing working directory

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A worktree-creation invocation selected the intended new worktree path as its command
  working directory before that directory existed, so the process could not start and Git never ran.
- **impact:** The bounded state-sync lane did not begin on the first attempt, although no ref or
  filesystem state changed.
- **workaround:** Run `git worktree add --detach origin/main` from the existing coordinator checkout,
  then run `git switch -c` from the newly created worktree as a separate invocation.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the post-dependency state sync.
- **task:** lab issue #29 owns the active release wave and its isolated-worktree execution evidence.
- **promotion:** Deliberately NOT promoted after one occurrence. The canonical two-step worktree
  rule already exists; if this invocation error recurs, put creation and branch setup in a checked
  helper instead of adding more prose.

### FR-012 — locked environment creation exceeded the narrow docs-proof window

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Two attempts to create the full locked project environment for a two-file state sync
  exceeded the 120-second shell window before `dllab context verify` could start; a later
  `--no-sync` invocation confirmed that the environment was still incomplete.
- **impact:** The narrow documentation proof can spend more time installing heavy runtime packages
  than reading the changed authority files, and a timeout supplies no verifier result.
- **workaround:** In a separate gitignored Python 3.13 context environment, install the lock-pinned
  `pydantic` and `jsonschema` versions, set `PYTHONPATH=src`, and call `verify_repository` directly.
  That exercised the same repository verifier and passed, followed by `git diff --check`.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the post-dependency state sync.
- **task:** lab issue #29 owns the current release-preparation proof boundary.
- **promotion:** Deliberately NOT promoted after one occurrence. If the full environment blocks a
  second narrow docs proof, add a lock-pinned context-only dependency group or checked wrapper;
  until then, keep the explicit lightweight invocation as task debt.

### FR-013 — an under-anchored patch matched the wrong repeated field

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A patch intended to promote FR-010 matched the first repeated
  `status: workaround-documented` field in the file and changed FR-001 instead.
- **impact:** Repeated schema fields in this append-only log make a syntactically valid patch able
  to touch the wrong entry unless its heading is part of the match context.
- **workaround:** Inspect the exact diff immediately, then reapply with the entry heading in the
  patch context. FR-010 was corrected before commit. FR-001's resulting `promoted` status is also
  truthful because its promotion field already records the maintenance-protocol promotion.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the FR-010 promotion update.
- **task:** lab issue #29 owns the current release-wave evidence edits.
- **promotion:** Deliberately NOT promoted after one occurrence. If it recurs independently, add a
  schema-aware friction-log updater or structural check rather than relying on textual patch order.
