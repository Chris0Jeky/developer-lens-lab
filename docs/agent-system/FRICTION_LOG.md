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
- **occurrences:** 18 recorded — 2026-08-08 (bootstrap first proved: locked sync plus full gate),
  2026-08-09 (LAB-GOV-02 reused the same route from a clean checkout), 2026-08-09 (the release-gate
  sync reused its surviving confined bootstrap), 2026-08-09 (the post-dependency state-sync
  worktree bootstrapped its own copy), 2026-08-09 (the licence/package-identity worktree reused the
  route), 2026-08-09 (the community-files worktree used the installed Python module route), and
  2026-08-09 (the package-identity base refresh reused that module route after a stale literal
  bootstrap-path assumption failed before execution), 2026-08-09 (the package-smoke final gate
  first found its dev environment unsynced, then used the same module route for a locked sync),
  2026-08-09 (the release-evidence state worktree reused that reviewed Python 3.12 environment),
  2026-08-09 (the package-timeout worktree used the existing interpreter route for focused checks
  while leaving the unavailable locked `uv` gate for coordinator proof), and 2026-08-09 (the
  ignored-smoke-scan worktree reused the confined bootstrap for its full gate and package smoke),
  and 2026-08-09 (the bounded-diagnostics worktree reused that confined route for its full gate and
  package smoke), 2026-08-09 (the context-traversal-pruning worktree reused the confined route for
  its full gate and package smoke), 2026-08-09 (the PATH/uv-validation worktree reused the confined
  route for its full gate and package smoke), and 2026-08-09 (the diagnostic-redaction worktree
  reused the confined route for its full gate and package smoke), and 2026-08-09 (the
  diagnostic-state worktree used the installed Python module route for its docs-only gate), and
  2026-08-09 (the sdist-lineage builder again found no PATH uv and left full-gate proof to the
  coordinator), and 2026-08-09 (the wheel-contract test worktree used the confined route for its
  actual package smoke).
- **task:** lab issues #29 (release wave) and #5 (dependency triage), which both depend on a
  runnable locked environment.
- **promotion:** Promoted to canon prose in [MAINTENANCE_PROTOCOL.md](MAINTENANCE_PROTOCOL.md),
  which now states the confined-bootstrap route rather than declaring the gate unrunnable. Not
  promoted to an executable check: installing a toolchain is an environment action, not a
  repository invariant, and a check that bootstrapped `uv` as a side effect would hide the cost.

_Note 2026-08-09 (release-gate sync):_ The promoted route remained sufficient on the third
occurrence: the existing worktree-confined bootstrap ran the locked context verifier without a
new install or lockfile change.

_Note 2026-08-09 (release wave):_ The fourth through sixth isolated worktrees used the same
promoted route. This repeated cost stays environment debt: the existing maintenance-protocol
instruction is the cheapest truthful layer, and an automatic installer would hide network and
time side effects. FR-014 separately records that the sixth environment was not kept confined.

_Note 2026-08-09 (package-identity base refresh):_ The seventh occurrence first tried a literal
bootstrap path that was not present in that worktree, so no proving command ran. The already
installed `py -3 -m uv` 0.12.2 route was then verified directly and kept the project environment
worktree-local; no cache contents were enumerated or inspected.

_Note 2026-08-09 (package smoke):_ The eighth occurrence first ran the full gate with `--no-sync`;
`uv` created an empty project environment and could not resolve `dllab`, so no repository check ran.
A later bare `py -3` smoke selected the host's default Python outside the package's declared
`<3.14` range and failed before exercising the supported package seam. The promoted worktree-local
Python 3.12 bootstrap route then completed the locked full gate and isolated artifact smoke.

_Note 2026-08-09 (release-evidence and timeout follow-ups):_ The ninth and tenth isolated
worktrees again had no host-resolvable `uv`. The release-evidence state proof reused the reviewed
Python 3.12 environment for the same underlying gate commands; its first cross-worktree Pyright call
did not infer that interpreter, so the successful retry supplied the exact Python path explicitly.
The timeout builder used an existing interpreter for focused checks and left the full locked gate
for coordinator integration. The existing maintenance-protocol instruction remains the cheapest
enforcing layer; no new automatic installer or hidden network side effect is justified.

_Note 2026-08-09 (timeout integration proof):_ The tenth occurrence's coordinator pass first found
that the host had no explicit Python 3.12 launcher and the reusable reviewed Python 3.12 environment
had no `pip` or `uv` module. `ensurepip` plus the pinned `uv>=0.12.2,<0.13` constraint installed
`uv 0.12.3` inside that ignored environment; the timeout worktree then completed locked sync and the
full declared gate. `uv` warned that the bootstrap `VIRTUAL_ENV` differed from the task-local project
environment and correctly ignored it. This successful confined route is the existing promoted
workaround; no global install, lockfile change, or private/generated-byte inspection occurred.

_Note 2026-08-09 (ignored-smoke scan):_ The eleventh isolated worktree again lacked a directly
resolvable `uv` and Pyright for the builder's first focused proof. The coordinator reused the
confined `uv 0.12.3` bootstrap, created a task-local locked environment, and completed the full gate
plus actual package smoke. The same harmless bootstrap-versus-project `VIRTUAL_ENV` warning was
reported and ignored by `uv`; no global install, lockfile change, or ignored/protected-byte
inspection occurred. The promoted maintenance-protocol route remains the cheapest truthful layer.

_Note 2026-08-09 (bounded package diagnostics):_ The twelfth isolated worktree reused the same
confined `uv 0.12.3` bootstrap and task-local locked environment for the full gate plus actual
package smoke. `uv` again reported and ignored the harmless bootstrap-versus-project `VIRTUAL_ENV`
warning. A later direct Pyright invocation inherited the wrong interpreter context and failed before
providing a valid type-check signal; the retry used the confined route and explicit task-local
environment. No global install, lockfile change, or ignored/protected-byte inspection occurred; the
existing maintenance-protocol route remains the cheapest truthful layer.

_Note 2026-08-09 (context traversal pruning):_ The thirteenth isolated worktree lacked a directly
resolvable `uv`; the confined `uv 0.12.3` bootstrap created its task-local locked environment and
completed the code, test, type, documentation, hygiene, and diff gates. The first smoke invocation
then selected the task environment's Python-module fallback, which has no `uv` module, and failed
before building an artifact. Retrying only the smoke through the reviewed bootstrap interpreter
passed. No global install, lockfile change, or ignored/protected-byte inspection occurred; the
prepared PATH/version-validation slice addresses command selection separately.

_Note 2026-08-09 (PATH/uv validation):_ The fourteenth isolated worktree likewise had no PATH uv.
The confined `uv 0.12.3` bootstrap created its task-local locked environment for the full gate and
its reviewed interpreter ran the actual package smoke. The first full-gate attempt stopped at a real
test-type error before suite or smoke execution; after the typed test fix, the unchanged confined
route passed. No global install, lockfile change, or ignored/protected-byte inspection occurred.

_Note 2026-08-09 (diagnostic redaction):_ The fifteenth isolated worktree likewise had no PATH uv.
The confined `uv 0.12.3` bootstrap created its task-local locked environment and its reviewed
interpreter completed the full gate plus actual package smoke. No failed workaround, global install,
lockfile change, or ignored/protected-byte inspection occurred.

_Note 2026-08-09 (diagnostic state repair):_ The sixteenth isolated worktree likewise had no PATH
uv. The already installed `py -3 -m uv` 0.12.2 route was verified before creating the task-local
locked environment for the bounded documentation gate. The existing maintenance-protocol
instruction remains the cheapest truthful layer.

_Note 2026-08-09 (sdist lineage):_ The seventeenth isolated worktree likewise had no PATH uv or
task-environment Pyright. The builder completed focused tests and Ruff through available host
modules and left locked sync, Pyright, and actual package-smoke proof to the coordinator's promoted
confined route. No global install or lockfile change occurred.

_Note 2026-08-09 (wheel-contract tests):_ The eighteenth isolated worktree completed the declared
gate through the installed host-module route, then its first actual smoke stopped at compatible-uv
selection before artifact build. A worktree-confined `.venv/uv-bootstrap` installed the pinned
`uv 0.12.3`; putting that executable on the task process PATH let the unchanged smoke pass. No
lockfile, global tool, tracked file, protected byte, or generated artifact byte was inspected.

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

### FR-009 — inline `gh` quoting is fragile in PowerShell

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Inline `gh` arguments containing nested GraphQL, multiline Markdown or quoted jq
  literals lost quoting expected by the downstream parser under PowerShell.
- **impact:** Review-thread state and PR-body accuracy are merge-gate inputs. Shell boundary damage
  can interrupt a ready merge or make a successful write look unverifiable.
- **workaround:** The first occurrence used GraphQL variables. Later multiline bodies were piped to
  `gh ... --body-file -`, and JSON verification used PowerShell `ConvertFrom-Json` instead of an
  inline quoted jq literal.
- **occurrences:** 5 independent occurrences — 2026-08-09 (an inline GraphQL repository string),
  2026-08-09 (a multiline PR body passed as one argument), 2026-08-09 (a quoted jq literal), and
  2026-08-09 (an inline post-merge GraphQL repository string), and 2026-08-09 (Markdown code ticks
  terminated an outer JavaScript command wrapper before PowerShell started).
- **task:** lab issue #34 tracks prompt-operating-system post-review hardening and the external
  Windows review-tool boundary.
- **promotion:** Not durably promoted. Binding GraphQL variables, streaming multiline Markdown
  through `--body-file -`, and parsing JSON with `ConvertFrom-Json` worked in this session, but no
  executable prompt currently requires that route. Issue #34 owns the smallest prompt/canon
  enforcement; a repository helper cannot wrap the unrelated `gh` payload shapes safely.

_Note 2026-08-09 (release-gate park):_ The second and third occurrences happened while parking PR
#37. All intended GitHub writes were subsequently re-read successfully; neither quoting failure
changed repository refs or release authority.

_Note 2026-08-09 (post-merge sweep):_ The fourth occurrence failed before returning review-thread
data. The promoted GraphQL-variable form was used for the retry; the failed query did not change a
repository ref or review thread.

_Note 2026-08-09 (package-smoke publish):_ The fifth occurrence failed in the orchestration parser
before the shell, Git, or GitHub ran. The retry removed Markdown code ticks from the inline body;
no repository or remote state changed in the failed attempt.

_Note 2026-08-09 (late-review reconciliation):_ Exact-head review showed that the active-session
route was not durable enforcement. The status and promotion field now record task debt rather than
claiming that a fresh session inherits the workaround.

### FR-010 — a later native command can mask an earlier failure in PowerShell

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A missing requested Python runtime failed, but a following successful
  `git diff --check` became the shell invocation's final exit status and made the combined command
  appear successful.
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
- **promotion:** Not durably promoted. This session set `$ErrorActionPreference = 'Stop'` and
  `$PSNativeCommandUseErrorActionPreference = $true` for multi-command probes and retained explicit
  `$LASTEXITCODE` guards, but no executable prompt currently requires that preamble. Issue #34 owns
  the smallest prompt/canon enforcement; a repository helper cannot enforce arbitrary external
  command compositions that bypass it.

_Note 2026-08-09 (late-review reconciliation):_ Exact-head review showed that the active-session
preamble was not durable enforcement. The status and promotion field now record task debt until an
applicable executable instruction installs the guard.

### FR-011 — a worktree cannot create itself from a not-yet-existing working directory

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A worktree-creation invocation selected the intended new worktree path as its command
  working directory before that directory existed, so the process could not start and Git never ran.
- **impact:** The bounded state-sync lane did not begin on the first attempt, although no ref or
  filesystem state changed.
- **workaround:** From the existing coordinator checkout, run
  `git worktree add --detach <path> origin/main`, then run `git switch -c <branch>` from the newly
  created worktree as a separate invocation.
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
- **status:** `promoted`
- **symptom:** A patch intended to promote FR-010 matched the first repeated
  `status: workaround-documented` field in the file and changed FR-001 instead.
- **impact:** Repeated schema fields in this append-only log make a syntactically valid patch able
  to touch the wrong entry unless its heading is part of the match context.
- **workaround:** Inspect the exact diff immediately, then reapply with the entry heading in the
  patch context. FR-010 was corrected before commit. FR-001's resulting `promoted` status is also
  truthful because its promotion field already records the maintenance-protocol promotion.
- **occurrences:** 2 independent occurrences — 2026-08-09 (the FR-010 promotion update) and
  2026-08-09 (the PR #41 owner-gate review fix initially changed FR-003 instead of FR-014).
- **task:** lab issue #34 owns prompt-operating-system and friction-ledger hardening.
- **promotion:** Promoted to mandatory heading-anchored patch context plus immediate exact-diff
  inspection for repeated-field Markdown ledgers. A schema-aware updater stays task debt: it cannot
  infer which semantically intended entry a caller meant to target, while the heading anchor makes
  that intent explicit at the cheapest enforceable boundary.

_Note 2026-08-09 (second occurrence):_ Exact-diff inspection caught the wrong FR-003 status before
commit. FR-003 was restored to `open`, and the corrected patch included both the FR-014 heading and
its field.

### FR-014 — a confined bootstrap environment escaped its worktree

- **first-seen:** 2026-08-09
- **status:** `owner-gated`
- **symptom:** The community-files proof created a project environment inside its worktree, then
  moved that environment and created a second environment in a public temporary root outside the
  worktree after a package-local link failed. The moved environment's internal path became stale.
- **impact:** The repository rule that every lane writes only inside its own project directory was
  breached, and two disposable environments now remain outside coordinator-owned worktrees.
- **workaround:** None. A coordinator cleanup command was denied before execution, so no directory
  was removed and the lane is parked rather than bypassing the deny floor.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the community-files context proof.
- **task:** `Chris0Jeky/developer-lens-lab::HUMAN_TODO.md::q-13` owns the physical cleanup; lab issue
  #34 records the boundary and the requirement to keep future bootstrap environments worktree-local.
- **promotion:** Kept owner-gated because the existing worktree rule already forbids the move and
  the agent cleanup route was denied. Unlocking event: direct verification that the exact q-13
  directories were removed; no release or data lane depends on them.

_Note 2026-08-09 (exact-head review):_ The two exact directory names were rechecked as present
without listing or inspecting their contents. PR #41's first fix round added q-13 and the fully
qualified link after the connector correctly identified this as human-only machine hygiene.

_Note 2026-08-09 (late-review reconciliation):_ The live q-13 action no longer tracks the local
target names. The private owner handoff retains the exact cleanup targets; the public repository
retains only the bounded action and its authority limits.

### FR-015 — the dependency-light verifier seam does not include the CLI wrapper

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A narrow state-document proof imported `developer_lens_lab.cli.context_verify`
  through the global Python interpreter, but that interpreter does not include the CLI-only `typer`
  dependency, so import failed before repository verification began.
- **impact:** The first proof command supplied no verifier result. No repository or protected data
  changed, and the verifier implementation itself remained available.
- **workaround:** With `PYTHONPATH=src`, import `verify_repository` from
  `developer_lens_lab.context` directly and fail on its returned report, then run
  `git diff --check`. This is the same verifier used by `dllab context verify` without importing the
  optional command wrapper.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the post-release-prompt state sync.
- **task:** lab issue #34 owns prompt-operating-system and friction-ledger hardening; issue #29 owns
  the current release-preparation proof boundary.
- **promotion:** Deliberately NOT promoted after one occurrence. If the CLI-wrapper import recurs in
  a dependency-light proof, add a checked context-only entry point rather than relying on an
  incidental global package set.

### FR-016 — `gh pr view --repo` does not infer the current branch

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Immediately after `gh pr create` returned the new pull-request URL, a follow-up
  `gh pr view --repo ...` call without a number failed with `argument required when using the
  --repo flag` instead of inferring the checked-out branch.
- **impact:** A successful pull-request write can be followed by a failed verification read, leaving
  its exact head, base, draft state, and hosted-check state unverified if the URL is not retained.
- **workaround:** Capture the number printed by `gh pr create` and pass that exact number to every
  `gh pr view --repo` verification read.
- **occurrences:** 1 independent occurrence — 2026-08-09 while opening the community-files PR.
- **task:** lab issue #34 tracks the external Windows/GitHub CLI workflow boundary.
- **promotion:** Deliberately NOT promoted after one occurrence. If it recurs, add a checked wrapper
  that captures the created PR URL/number and performs the exact numbered re-read.

### FR-017 - PowerShell lacks `Get-Date -AsUTC`

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Windows PowerShell rejected `Get-Date -AsUTC` because that parameter is unavailable
  in the host version.
- **impact:** A timestamp probe failed before any repository state changed, briefly interrupting
  the bounded issue #29 release-evidence lane.
- **workaround:** Use `[DateTime]::UtcNow.ToString('o')` for an equivalent UTC timestamp.
- **occurrences:** 1 independent occurrence - 2026-08-09 during the issue #29 package-smoke lane.
- **task:** Lab issue #29 owns the release-evidence boundary.
- **promotion:** Deliberately NOT promoted after one occurrence. If an independent recurrence
  appears, consider a compatibility helper at the smallest shared command layer.

### FR-018 — a live issue checkpoint abbreviated a cross-repository human action

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A release-wave issue comment fully qualified one Lab human action, then referred to a
  second Lab action by number alone. The required repository prefix was therefore absent from one
  live operational reference.
- **impact:** A later coordinator could attribute the shorthand to the product repository and route
  the machine-hygiene action through the wrong owner gate.
- **workaround:** The same comment was re-read and patched immediately so every human action carries
  its complete owner/repository/file reference. No authority, ref, gate status or release action
  changed.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the issue #29 package-smoke update.
- **task:** Lab issue #34 owns prompt-system and cross-repository human-reference hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. The tracked active-prompt verifier
  already rejects a bare reference in prompt bodies; if an independent outbound-comment recurrence
  appears, add a body preflight at the narrow GitHub-write boundary rather than another reminder.

### FR-019 — current-head replay changes hashes embedded with Lab provenance

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** The automated invented-C0 replay was internally deterministic at current Lab main,
  but its printed JSON, Markdown and HTML hashes differed from the frozen canonical ledger hashes.
  The exporter includes `lab_commit` in provenance, so a new Lab head changes release bytes even
  when the research decision and synthetic inputs are unchanged.
- **impact:** Issue #29 cannot truthfully publish both the frozen hashes and current-head candidate
  bytes. Treating either set as interchangeable would break reproducibility and release provenance.
- **workaround:** Record both evidence sets without opening ignored candidate bytes; stop before
  Lane-P content review, publication or tagging until a bounded slice explicitly selects the frozen
  producer or a reviewed current-head provenance contract.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the issue #29 C0 evidence packet.
- **task:** Lab issue #29 owns the selected C0 release exhibit and its pre-tag provenance decision.
- **promotion:** No new structure was needed: the constitution, issue #29 and tracked hashes already
  pin the frozen producer. A future current-head exhibit would require a separately reviewed
  cross-repository contract/authority change, not an inferred hash refresh.

_Closure 2026-08-09:_ A detached automated replay at producer
`0ef193070a9b80b81cef5a1710a1d65e0b271c15` exactly matched the frozen JSON, Markdown and HTML
hashes. The current-head candidate stays rejected; Lane-P content review and publication remain
separate, unverified gates.

### FR-020 — PowerShell automatic `$args` swallowed a helper's command array

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A task-local proving helper named its explicit command-array parameter `Args`.
  PowerShell's case-insensitive automatic `$args` variable took precedence, so the wrapper invoked
  `uv run` without the intended command and exited before any repository check ran.
- **impact:** The proving pass stopped at its first command and had to be rerun with an unambiguous
  parameter name; no evidence from the failed wrapper was usable.
- **workaround:** Name explicit array parameters `CommandArgs` (or another non-automatic name) and
  splat that variable into the command.
- **occurrences:** 1 independent occurrence — 2026-08-09 during the bounded package-diagnostics
  post-documentation proof.
- **task:** lab issue #34 tracks external Windows and command-wrapper workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. The one-line parameter rename is
  the cheapest current workaround; a second independent occurrence should add a checked shared
  wrapper or lint rule at the command boundary.

_Note 2026-08-09 (bounded package diagnostics):_ The failed helper changed no repository ref or
protected output. The retry used `CommandArgs` and the same confined environment.

### FR-021 — managed PowerShell failed to start under transient resource pressure

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Two consecutive task-wrapper launches failed before PowerShell loaded, reporting
  Windows error `0x800705af`. The intended Git/GitHub publication command and the follow-up machine
  guidance read therefore never started.
- **impact:** A fully proved branch could not be published from the coordinator process at that
  workflow boundary; neither failed launch produced repository or GitHub evidence.
- **workaround:** Preserve the clean branch and hand the exact bounded commit/publication command to
  a fresh worker process. Do not short-poll the failing shell or broaden the task.
- **occurrences:** 1 independent occurrence — 2026-08-09 during PATH/uv-validation publication;
  both failed starts were retries of the same operation.
- **task:** lab issue #34 tracks external Windows and command-wrapper workflow hardening.
- **promotion:** Deliberately NOT promoted after one independent occurrence. If a separate session
  reproduces the startup failure, add the machine's existing resource-hygiene sweep at the narrow
  pre-publication boundary or record why it remains machine debt.

_Note 2026-08-09 (PATH/uv validation):_ Both failures occurred before a command or manifest read;
no tracked file, Git ref, GitHub object, ignored output, or protected byte changed in either attempt.

### FR-022 — a full-history agent fork cannot also override the worker role

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** The first publication handoff requested both a full-history fork and an explicit
  worker role. The orchestrator rejected that combination before creating an agent.
- **impact:** The alternate publication process did not start on the first attempt; no delegated
  proof or Git/GitHub action occurred.
- **workaround:** Use a no-history worker fork with a context-complete bounded task brief when a role
  override is required.
- **occurrences:** 1 independent occurrence — 2026-08-09 while recovering the PATH/uv-validation
  publication lane from FR-021.
- **task:** lab issue #34 tracks external agent-routing and command-wrapper workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. The corrected invocation is the
  cheapest layer; a second independent recurrence should move the compatibility rule into the
  routing skill or its executable schema.

_Note 2026-08-09 (PATH/uv validation):_ Rejection happened before agent creation and changed no
tracked file beyond this friction record, Git ref, GitHub object, ignored output, or protected byte.

### FR-023 — a completed builder thread could not accept the blocking fix follow-up

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** The first attempt to return PR #52's blocking review fix to its completed builder was
  rejected because that agent thread had reached its turn limit.
- **impact:** The blocking fix did not start on the original handoff; no code, test or ref changed in
  the failed delegation.
- **workaround:** Spawn a fresh bounded writer on the same preserved worktree with the exact head,
  owned files, finding, and proving seam.
- **occurrences:** 1 independent occurrence — 2026-08-09 during PR #52's first fix round.
- **task:** lab issue #34 tracks external agent-routing and command-wrapper workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. A second independent thread-limit
  handoff should move the fresh-writer fallback into the routing skill or its executable schema.

_Note 2026-08-09 (diagnostic redaction):_ The fresh writer committed the bounded fix without
reverting the completed builder's work; the failed follow-up changed no Git or GitHub state.

### FR-024 — a piped GitHub comment body arrived empty

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A single-line PR #52 review checkpoint piped to `gh pr comment --body-file -` reached
  GitHub as an empty body and was rejected before comment creation.
- **impact:** The first attempt recorded no review checkpoint and required one bounded retry.
- **workaround:** Pass a quoting-safe single-line body directly with `--body`, then re-read the
  resulting comment URL.
- **occurrences:** 1 independent occurrence — 2026-08-09 during PR #52 review triage.
- **task:** lab issue #34 tracks external Windows and GitHub command-boundary hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. If stdin body loss recurs, add a
  checked body-file helper at the GitHub-write boundary rather than another prose reminder.

_Note 2026-08-09 (diagnostic redaction):_ Direct-body retry created the intended review checkpoint;
the rejected empty-body request changed no GitHub comment, repository ref, or protected output.

### FR-025 — the final pre-merge snapshot omitted a newly arrived top-level comment

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** PR #52 received a top-level exact-head comment at 19:47:58Z that set a conservative
  19:58:52Z eligibility checkpoint. The coordinator's final snapshot queried head, base, hosted
  proof, closing refs, and review threads but not top-level comments, and the merge began at
  19:48:10Z.
- **impact:** The merge satisfied the session prompt's three-minute floor, exact-head proof, and
  final review, but occurred before the newly stated conservative checkpoint and required an
  explicit post-merge process reconciliation. FR-028 separately records the constitution's
  unsatisfied 15-minute exact-head age.
- **workaround:** Re-read top-level comments together with head, base, hosted checks, reviews,
  closing refs, and review threads in every final merge snapshot. Preserve the completed merge and
  record any late signal factually rather than rewriting refs.
- **occurrences:** 1 independent occurrence — Lab PR #52 on 2026-08-09.
- **task:** lab issue #34 tracks the checked GitHub merge-snapshot boundary.
- **promotion:** Deliberately NOT promoted after one occurrence. If an independent omission recurs,
  add one reusable checked pre-merge snapshot helper that returns all required surfaces together.

_Note 2026-08-09 (diagnostic redaction merge):_ Exact final head
`46961957e09bb976b34beb41fee5e69d89d21076` and hosted run `31332413187` were green, both threads
were resolved, and the 19:51Z delayed sweep found no new defect. PR #52 records the reconciliation;
no ref rewrite or unmerge was attempted.

### FR-026 — a PowerShell DateTime comparison inverted the sweep-threshold result

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A post-merge guard compared a UTC `DateTime` value with a parsed `Z` literal and
  incorrectly reported that the already elapsed 19:51:10Z threshold had not elapsed.
- **impact:** The first delayed-sweep command stopped before querying GitHub and required one
  corrected retry.
- **workaround:** Use `DateTimeOffset::UtcNow` and parse the threshold as `DateTimeOffset` before
  comparing absolute instants.
- **occurrences:** 1 independent occurrence — Lab PR #52 delayed sweep on 2026-08-09.
- **task:** lab issue #34 tracks external Windows command-boundary workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. A second independent recurrence
  should add a small checked UTC-threshold helper at the workflow boundary.

_Note 2026-08-09 (diagnostic redaction merge):_ The failed guard ran no GitHub query and changed no
tracked file, Git ref, GitHub object, ignored output, or protected byte; the `DateTimeOffset` retry
completed the single delayed sweep.

### FR-027 — an optional missing path made a read-only ripgrep probe exit nonzero

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A command-table discovery probe named a conventional `Makefile` alongside known
  tracked files. The repository has no such path, so ripgrep printed the useful matches but exited
  nonzero after reporting the missing file.
- **impact:** The read-only probe was classified as failed and required one exact-file read before
  the declared documentation commands were confirmed.
- **workaround:** Resolve optional candidate paths before passing them to ripgrep, or search only
  paths already returned by the repository file inventory.
- **occurrences:** 1 independent occurrence — diagnostic-state proof discovery on 2026-08-09.
- **task:** lab issue #34 tracks external Windows command-boundary workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. A second independent recurrence
  should move optional-path filtering into the smallest reusable repository-discovery helper.

_Note 2026-08-09 (diagnostic state repair):_ The failed read changed no tracked file, Git ref,
GitHub object, ignored output, or protected byte; the direct `CLAUDE.md` read supplied the same
command-table evidence.

### FR-028 — the merge path again failed to enforce 15-minute exact-head aging

- **first-seen:** 2026-08-09
- **status:** `open`
- **symptom:** PR #51 merged after at most 8m59s at its exact head, and PR #52 merged 4m18s after
  its final docs-head push. Both were below the owner constitution's 15-minute exact-head aging
  rule even though their hosted proof and accepted exact-head review evidence were green.
- **impact:** Two merges shortened the constitution's observation window; post-merge review found
  no implementation defect, but the completed merges cannot retroactively satisfy that gate.
- **workaround:** Reconcile each completed merge without rewriting refs, and treat 15 minutes as an
  unconditional exact-head floor for every later merge in this session.
- **occurrences:** 2 independent occurrences — Lab PR #51 and Lab PR #52 on 2026-08-09.
- **task:** lab issue #29 tracks release-wave merge-eligibility hardening; issue comment
  `5231583712` records the first occurrence.
- **promotion:** The selected enforcement layer is one checked, event-driven pre-merge snapshot
  that refuses eligibility before 15 minutes and returns head, base, hosted checks, accepted review
  evidence, top-level comments, closing refs, and review threads together. Implementation remains
  bounded task debt on issue #29; no third prose-only workaround is acceptable.

_Note 2026-08-09 (diagnostic state repair):_ PR #52 final head
`46961957e09bb976b34beb41fee5e69d89d21076` stayed green and its delayed sweep found no new defect.
The process miss is recorded without rewriting the completed merge or claiming retroactive proof.

### FR-029 — a concurrent closeout PR remained open after its state claims diverged

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** PR #53 remained open against obsolete base
  `02a41cac4a461a93d53b481d34c96a48e29291e5` while live main and replacement PR #54 advanced the
  same three state files. It had two unresolved blocking threads and a friction-ID collision with
  already merged history.
- **impact:** Merging or mechanically rebasing the branch could have restored stale resume claims,
  exposed machine-local identifiers, or overwritten append-only friction history.
- **workaround:** Confirm the still-relevant aging and worktree-preservation evidence remained on
  issue #29, reduce the public inventory to generic state classes, reconcile and resolve both
  threads, and archive PR #53 without merging or rewriting its commits.
- **occurrences:** 1 independent occurrence — Lab PR #53 on 2026-08-09.
- **task:** lab issue #29 retains the preservation and aging evidence; PR #54 carries the live state.
- **promotion:** Resolved by the inspected GitHub state: PR #53 is closed, both review threads are
  resolved, its commits were not merged or rewritten, and PR #54 is based on live main. The normal
  live open-PR inventory remains the cheapest enforcing layer.

_Note 2026-08-09 (diagnostic state repair):_ The archived branch and its worktree remain preserved;
ignored and untracked contents were not inspected, and no branch was deleted.

### FR-030 — the GitHub GraphQL quota exhausted during an exact-head review window

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** The first post-push refresh for Lab PR #54 failed before returning PR state because
  the authenticated GitHub GraphQL quota had reached zero. The core REST quota remained available;
  GitHub reported the GraphQL reset at 2026-08-09T20:31:54Z.
- **impact:** Head, base, checks, top-level comments, and thread resolution could not be refreshed
  atomically through the normal query during the passive review window.
- **workaround:** Keep useful local work moving, use REST only for evidence it can represent, and
  defer the final all-surface merge snapshot until GraphQL has reset. Never merge from the stale
  pre-exhaustion snapshot.
- **occurrences:** 1 independent occurrence — Lab PR #54 on 2026-08-09.
- **task:** lab issue #34 tracks external GitHub and command-boundary workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. A second independent exhaustion
  should add quota-aware admission to the selected checked pre-merge snapshot helper rather than
  another polling loop.

_Note 2026-08-09 (diagnostic state repair):_ The failed GraphQL call made no GitHub or repository
change. The exact reset instant came from the read-only REST rate-limit endpoint, and the lane
remains in passive observation while disjoint local proof continues.

### FR-031 — bare Python selection again could not host the package-smoke uv command

- **first-seen:** 2026-08-09
- **status:** `open`
- **symptom:** A bare `py -3` package-smoke invocation selected the host's unsupported newest
  Python and saw `uv` only through user-site loading, which the confined smoke environment disables.
  Inferring the interpreter named by the preceding project sync also failed because that interpreter
  did not contain the `uv` module. Both attempts stopped at command validation before artifact build.
- **impact:** Actual package-smoke proof required two failed interpreter-selection attempts before
  the already reviewed confined bootstrap route was selected explicitly.
- **workaround:** Put the reviewed worktree-confined `uv` executable on the task process PATH and
  invoke the smoke through the task-local supported Python environment. The unchanged smoke then
  built and exercised the sdist-derived wheel successfully.
- **occurrences:** 3 independent occurrences — the initial built-artifact smoke, the sdist-lineage
  integration proof, and the wheel-contract integration proof on 2026-08-09.
- **task:** lab issue #29 owns package-smoke hardening; lab issue #34 tracks external command-route
  friction.
- **promotion:** At the second occurrence, the selected enforcement layer is a checked package-smoke
  launcher that passes one already validated `uv` executable explicitly instead of inferring it
  from the host launcher. Implementation remains bounded task debt; the successful explicit route
  is the interim workaround.

_Note 2026-08-09 (sdist lineage):_ The explicit confined `uv 0.12.2` plus task-local Python route
completed the actual smoke in 87.5 seconds. Neither failed selection built an artifact, changed a
tracked file or lockfile, or surfaced ignored, generated, protected, credential, or private bytes.

_Note 2026-08-09 (wheel-contract tests):_ The installed host-module route completed sync and the
full declared gate, but the task environment still had neither compatible PATH uv nor a current-
interpreter uv module for actual smoke. The explicit confined `uv 0.12.3` PATH route then passed.
The third recurrence keeps the checked-launcher implementation as bounded issue #34 task debt; no
failed selection built an artifact or surfaced ignored, generated, protected, credential, or
private bytes.

### FR-032 — the first post-resolution GraphQL snapshot timed out during TLS setup

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** After all three PR #54 review-thread resolution mutations succeeded, the following
  read-only all-surface GraphQL query failed with a TLS handshake timeout before returning evidence.
- **impact:** Thread mutations had completed but the coordinator lacked the required confirming
  snapshot and could not safely proceed from the pre-resolution state.
- **workaround:** Retry once with a smaller query, then join its thread/head/base/comment/closing-ref
  result to the exact-head REST check-run result. Park if the bounded retry also fails.
- **occurrences:** 1 independent occurrence — Lab PR #54 final snapshot on 2026-08-09.
- **task:** lab issue #34 tracks external GitHub and command-boundary workflow hardening.
- **promotion:** Deliberately NOT promoted after one occurrence. A second independent TLS timeout
  should add bounded retry/result joining to the selected checked pre-merge snapshot helper.

_Note 2026-08-09 (state reconciliation merge):_ The smaller retry succeeded, confirmed all three
threads resolved, zero closing refs, unchanged exact head/base, and green hosted proof. The failed
read changed no GitHub object, tracked file, Git ref, ignored output, or protected byte.

### FR-033 — concurrent observer lacked PR merge-operation context

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A concurrent observer's successful final PR #54 snapshot reported state `MERGED` at
  20:33:27Z before that observer received the root governor's merge-operation context. GitHub merge
  metadata alone did not identify which concurrent process issued the request.
- **impact:** Acting from the earlier open-state snapshot could have attempted a redundant merge or
  produced false attribution in the durable ledger.
- **workaround:** Treat the new live state as authoritative, verify the merge commit and origin/main,
  reconcile available concurrent-process operation evidence, and make no duplicate merge or ref
  rewrite attempt.
- **occurrences:** 2 independent occurrences — Lab PR #54 and PR #55 on 2026-08-09.
- **task:** lab issue #34 tracks the ownership-token or merge-lease preflight; comment `5233753580`
  supplies the first occurrence's direct merge-operation correction.
- **promotion:** The first occurrence was resolved by direct operation evidence: a root governor
  issued the exact-head REST merge and GitHub returned the recorded merge commit. The second
  occurrence selects an ownership token or merge lease checked by a preflight as the cheapest
  enforceable layer; issue #34 retains the implementation task.

_Note 2026-08-09 (state reconciliation merge):_ The transition occurred only after exact-head run
`31333721317` succeeded, the final review was clean, all threads were resolved, and the 15-minute
age elapsed. Merge commit `7fea25023d0704aea685e243708328264b9bcaad` is live on origin/main;
no code or gate defect is known.

_Correction 2026-08-09 (concurrent-context reconciliation):_ The original symptom captured only
this observer's local command history and must not be read as evidence that no coordinator issued
the merge. Issue #34 comment `5233753580` records the other root governor's exact REST request
(`sha=a4eefd9cc4963f684c0376543600969c45d6d057`, merge method `merge`) and GitHub's successful
`7fea25023d0704aea685e243708328264b9bcaad` response. Human attribution remains unverified.

_Note 2026-08-09 (PR #55 concurrent-context recurrence):_ The final observer snapshot saw PR #55
as `MERGED` before that observer issued its own merge command. GitHub metadata names only the
account, so no process or actor is inferred. This is the second independent FR-033 occurrence.
The cheapest enforceable follow-up is an ownership token or merge lease checked by a preflight
that records the operation owner before a merge request and requires the final snapshot to carry
that token; issue #34 retains this task. Until that helper exists, the workaround remains exact
head/base/check/thread/closing-ref snapshots plus no duplicate merge attempt.

_Note 2026-08-09 (PR #55 delayed sweep):_ The 21:25:06Z post-merge sweep found no late review,
comment, thread, or closing-reference debt. The occurrence is safely reconciled, but status remains
`workaround-documented` until issue #34's ownership-token or merge-lease preflight is implemented.

### FR-034 — a combined state patch used one stale context hunk

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A combined three-file patch for the PR #54 merge checkpoint could not find one
  expected current-state line and failed atomically before changing any file.
- **impact:** The first documentation-sync attempt produced no update and required an exact reread
  plus smaller file-scoped patches.
- **workaround:** Re-read the narrow mismatched region and apply exact file-scoped patches, retaining
  atomic failure as the guard against partial state updates.
- **occurrences:** 4 independent occurrences — the stale combined hunk during sdist current-base
  state sync, the ambiguous FR-033 status hunk during PR #55 review correction, and the
  unanchored FR-033 occurrence and status edits during PR #55 post-merge reconciliation on 2026-08-09.
- **task:** lab issue #34 tracks external patch-context and command-boundary workflow hardening.
- **promotion:** At the second occurrence, the selected enforcement layer was an exact section-header
  anchor plus a pre-stage diff assertion. The third occurrence shows that an ad-hoc command does not
  reliably enforce that guard; a checked state-sync helper is now the selected task-debt layer on
  issue #34.

_Note 2026-08-09 (sdist current-base integration):_ The failed combined patch changed no tracked
file, Git ref, GitHub object, ignored output, or protected byte; the exact file-scoped retries
applied the intended factual update.

_Note 2026-08-09 (PR #55 review correction):_ An unanchored status hunk matched FR-005 instead of
FR-033. The immediate diff inspection caught it before staging; an exact header-scoped patch restored
FR-005 and changed only FR-033. No commit, push, GitHub object, ignored output, or protected byte
contained the transient edit.

_Note 2026-08-09 (same correction hop):_ The first full-section wording patch used an assumed impact
line and failed atomically. Narrow exact-line retries changed the title, symptom, and workaround;
the failed attempt changed no file, ref, GitHub object, ignored output, or protected byte.

_Note 2026-08-09 (PR #55 post-merge reconciliation):_ An unanchored occurrence-count patch
temporarily matched FR-030 instead of FR-033. The diff inspection caught and restored FR-030 before
staging; an exact FR-033 header-scoped patch then changed only the intended entry. No commit, push,
GitHub object, ignored output, or protected byte contained the transient edit.

_Note 2026-08-09 (same reconciliation, fourth occurrence):_ A later unanchored status patch matched
FR-004 instead of FR-033. The required pre-stage inspection caught it, restored FR-004, and applied
the FR-033 status under its exact section header. No commit, push, GitHub object, ignored output, or
protected byte contained the transient edit. This recurrence strengthens issue #34's checked-helper
task; hand-authored status/occurrence patches are not an enforcing layer.

### FR-035 — an unannounced post-merge state worktree appeared at live main

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** After integrating PR #54, the worktree inventory contained a newly registered
  `docs/postmerge-state-20260809` branch at the exact live-main merge with no tracked changes and no
  open pull request. It was absent from the coordinator's earlier inventory.
- **impact:** An unrecognized state worktree could represent a competing writer and create
  overlapping documentation edits if publication continued without reconciliation.
- **workaround:** Verify only tracked status, head, live-main identity, and open-PR state; because
  all match and no writer is active, preserve the worktree without inspecting ignored content or
  deleting it, and keep the sdist branch as the sole active writer.
- **occurrences:** 1 independent occurrence — sdist current-base integration on 2026-08-09.
- **task:** lab issue #29 tracks retained-worktree reconciliation and safe cleanup.
- **promotion:** Deliberately NOT promoted after one occurrence. A second independent unannounced
  writer/worktree should add an ownership token or checked writer registry at worktree creation.

_Note 2026-08-09 (sdist current-base integration):_ The observed branch and origin/main both point
to `7fea25023d0704aea685e243708328264b9bcaad`; tracked status is clean and the repository has zero
open pull requests. No ignored or untracked content was enumerated or inspected, and the worktree
was not removed.

_Note 2026-08-09 (concurrent-context reconciliation):_ Issue #34 later proved that another root
governor process was active around the PR #54 merge. "Unannounced" describes missing coordination
context for this observer, not an unidentified external actor. The clean retained worktree facts and
ownership-token follow-up remain unchanged.

### FR-036 — proof-command lookup named absent optional paths

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A bounded `rg` lookup named `pyproject.toml`, `Makefile`, and an optional
  `docs/agent-system/CURRENT_STATE.md` path that are absent from this checkout. It printed the useful
  `CLAUDE.md` matches but exited 2 because at least one explicit path did not exist.
- **impact:** The lookup's process status was red even though the canonical run-and-prove commands
  were recovered; no proof command or repository state was affected.
- **workaround:** Use the canonical commands printed from `CLAUDE.md`; when probing optional files,
  derive candidate paths from tracked-file inventory first.
- **occurrences:** 2 independent occurrences — PR #55 correction proof lookup and the wheel-contract
  proof-command lookup on 2026-08-09.
- **task:** lab issue #34 tracks command-boundary hardening and reusable preflight checks.
- **promotion:** At the second occurrence, the selected enforcing layer is a tracked-file inventory
  preflight before passing explicit paths to `rg`; a checked wrapper remains bounded task debt on
  issue #34.

_Correction 2026-08-10 (PR #56 P2 triage):_ The original entry recorded the wrong native exit code.
`pyproject.toml` exists and was read successfully; `Makefile` and the optional
`docs/agent-system/CURRENT_STATE.md` path are absent. Ripgrep returns exit 2 for an explicit missing
path even when another named path matches. This correction supersedes only the exit-status claim.

_Note 2026-08-09 (wheel-contract proof lookup):_ A combined lookup named absent
`MAINTENANCE_PROTOCOL.md` alongside tracked paths. Ripgrep printed the path error and returned exit 2;
the next lookup must derive every explicit candidate from tracked-file inventory first. No file, ref,
GitHub object, ignored output, or protected byte changed.

### FR-037 — inline PowerShell status assertion misquoted Markdown backticks

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** An inline regex intended to compare friction-entry statuses embedded Markdown
  backticks inside a double-quoted PowerShell command and failed at parse time.
- **impact:** The pre-stage assertion did not run on its first attempt; the shell parsed no
  repository mutation and changed no file, ref, GitHub object, ignored output, or protected byte.
- **workaround:** Replace the inline regex with fixed header-and-context inspection plus the full
  scoped diff before staging.
- **occurrences:** 1 independent occurrence — PR #55 correction pre-stage assertion on 2026-08-09.
- **task:** lab issue #34 tracks command-boundary hardening and reusable preflight checks.
- **promotion:** Deliberately not promoted after one occurrence. If it recurs, use a checked script
  file rather than adding more inline shell escaping.

### FR-038 — PR-comment shell body omitted the orchestration wrapper

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** A PR-comment attempt supplied PowerShell directly to the JavaScript orchestration
  cell instead of calling the nested shell tool, so the JavaScript parser rejected the body.
- **impact:** The intended review-triage comment was not posted on the first attempt; parsing stopped
  before any shell command, GitHub write, repository mutation, ignored-output access, or protected
  byte access.
- **workaround:** Invoke the PowerShell body through the nested shell tool, then verify the returned
  comment URL before treating the external write as complete.
- **occurrences:** 1 independent occurrence — PR #55 fix-round triage on 2026-08-09.
- **task:** lab issue #34 tracks command-boundary hardening and reusable preflight checks.
- **promotion:** Deliberately not promoted after one occurrence. If it recurs, use a checked PR
  triage helper rather than hand-authoring the orchestration wrapper.

### FR-039 — strict MkDocs emits an upstream Material-for-MkDocs warning

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** The strict documentation build emitted the upstream Material-for-MkDocs warning
  about forthcoming MkDocs 2.0 incompatibilities while still completing successfully.
- **impact:** Proof output contains a non-failing upstream compatibility warning that can be
  mistaken for a repository documentation failure.
- **workaround:** Keep the declared MkDocs/Material version bounds, record the warning separately,
  and use the process exit status plus the generated documentation result for pass/fail.
- **occurrences:** 3 independent occurrences — PR #55 correction/finalization proof, PR #55
  post-merge reconciliation, and issue #58 current-base full-gate proof on 2026-08-09.
- **task:** lab issue #34 tracks reusable proof-command and tooling-boundary hardening.
- **promotion:** At the second occurrence this remains task debt rather than a suppression rule:
  the warning is emitted upstream while the pinned build succeeds, and hiding it would remove useful
  upgrade evidence. Dependency-range maintenance on issue #34 is the cheapest effective layer if
  the pinned dependency changes or the warning becomes an actionable failure.

_Note 2026-08-09 (issue #58 current-base proof):_ The strict build passed again with the same
upstream warning after the PyYAML lock refresh. No MkDocs/Material bound, generated documentation
content, release evidence, or publication state was changed or inspected.

### FR-040 — focused Ruff format check found new line wrapping

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** The focused Ruff format check rejected two newly added line layouts in the verifier
  and tests.
- **impact:** The format gate stopped before Ruff lint and Pyright; no semantic or protected-data
  behavior was affected.
- **workaround:** Run the repository-pinned Ruff formatter on the two changed Python files, then
  rerun the focused format, lint, type, and test checks.
- **occurrences:** 2 independent occurrences — the issue #58 writer change and the coordinator's
  closing-fence refinement on 2026-08-09.
- **task:** lab issue #58 owns the focused verifier and test changes.
- **promotion:** At the second occurrence, the repository-pinned formatter remains the cheapest
  enforcing layer and must run before the focused format check on changed Python files.

_Note 2026-08-09 (coordinator review):_ The focused check rejected the iterator layout added while
allowing unrelated later Markdown fences. The pinned formatter made only the mechanical layout
change before the focused lint, type, and test proofs; no protected or ignored content was read.

### FR-041 — package-smoke script ignored a help probe

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** Invoking the package-smoke script with `--help` did not print usage or reject the
  unknown flag; its zero-argument entry point started the normal smoke path instead.
- **impact:** A command-discovery probe unexpectedly reached environment validation and produced a
  failed attempt before the intended proof command was run.
- **workaround:** Treat the tracked script's zero-argument `main` as the command contract and run it
  only with the reviewed confined `uv` directory on PATH; use tracked source for discovery.
- **occurrences:** 1 independent occurrence — issue #58 package proof on 2026-08-09.
- **task:** lab issue #34 tracks checked command discovery; lab issue #29 owns package-smoke
  hardening.
- **promotion:** Deliberately not promoted after one occurrence. If command-line use expands, add an
  explicit argument parser or a checked wrapper rather than relying on ignored arguments.

### FR-042 — canonical replay was attempted before its clean-tree precondition

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** The issue #58 canonical invented replay was started while its already-verified
  friction-log reconciliation remained uncommitted, so the runner rejected the tracked-dirty tree.
- **impact:** The first replay attempt stopped before creating a run and had to be repeated after the
  documentation commit.
- **workaround:** Finish the scoped documentation proof and commit first, confirm tracked status is
  clean, then run the same replay in a disposable synthetic artifact root.
- **occurrences:** 1 independent occurrence — issue #58 environment proof on 2026-08-09.
- **task:** lab issue #58 owns the current replay; lab issue #34 tracks reusable proof sequencing.
- **promotion:** Deliberately not promoted after one occurrence; the runner's clean-tree refusal is
  the effective guard. Promote only if orchestration repeatedly orders replay before final staging.

### FR-043 — expected ripgrep no-match left the proof wrapper red

- **first-seen:** 2026-08-09
- **status:** `workaround-documented`
- **symptom:** A tracked friction lookup correctly found no prior clean-replay entry and returned
  ripgrep's documented no-match status, but the PowerShell wrapper retained that status after
  classifying it as acceptable, so orchestration reported the read-only command as failed.
- **impact:** The lookup result was usable but appeared as a red command and required explicit
  reconciliation before the friction entry could be selected.
- **workaround:** After accepting a no-match result, terminate the wrapper with an explicit success
  status; retain nonzero status only for an actual search error.
- **occurrences:** 1 independent occurrence — issue #58 friction lookup on 2026-08-09.
- **task:** lab issue #34 tracks checked command-boundary and search helpers.
- **promotion:** Deliberately not promoted after one occurrence. If it recurs, add the explicit
  no-match normalization to the checked search helper instead of repeating shell glue.

### FR-044 — PowerShell hashtable interpolation supplied an invalid review-thread ID

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** The first PR #59 review-reply loop passed a hashtable's string representation plus
  the literal member suffix to GraphQL instead of the stored review-thread ID.
- **impact:** The issue #34 tracking comment succeeded, but the first thread reply failed before any
  reply or resolution mutation occurred.
- **workaround:** Read each indexed hashtable value into an explicitly typed scalar before passing
  it as a GraphQL variable, then verify every returned reply URL and resolved state.
- **occurrences:** 1 independent occurrence — PR #59 review triage on 2026-08-09.
- **task:** lab issue #34 tracks checked GitHub mutation wrappers and command-boundary hardening.
- **promotion:** Deliberately not promoted after one occurrence. If it recurs, replace the ad-hoc
  loop with a checked typed thread-triage helper.

### FR-045 — YAML comment syntax truncated the active-wave issue reference

- **first-seen:** 2026-08-09
- **status:** `resolved`
- **symptom:** PyYAML accepted the active-wave lane's plain scalar but treated the space before its
  `#29` issue reference as a comment, so the parsed value silently lost the task identifier.
- **impact:** Context verification passed a machine-readable resume block whose active lane no
  longer named the GitHub issue that owns it.
- **workaround:** Represent the lane as a folded scalar and assert that safe loading preserves the
  complete issue-bearing value.
- **occurrences:** 1 independent occurrence — PR #59 exact-final-head review on 2026-08-09.
- **task:** lab issue #58 owns the current repair; lab issue #34 tracks deeper YAML semantic
  validation.
- **promotion:** Deliberately not promoted after one occurrence; the focused repository-state
  regression is the cheapest enforcing layer for this canonical field.
