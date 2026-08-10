from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

from developer_lens_lab.schemas import check_schemas

REQUIRED_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent-harness/tier.json",
    ".agent-harness/governor.json",
    ".agent-harness/prompt-parity.json",
    "docs/OWNER_CONSTITUTION.md",
    "docs/agent-system/README.md",
    "docs/agent-system/WORK_CLASSES.md",
    "docs/agent-system/EXPERIMENT_PROTOCOL.md",
    "docs/agent-system/DATASET_PROTOCOL.md",
    "docs/agent-system/MAINTENANCE_PROTOCOL.md",
    "docs/agent-system/IDEA_PROTOCOL.md",
    "docs/agent-system/PROMPT_LIBRARY.md",
    "docs/agent-system/CONTINUOUS_WORK_PROTOCOL.md",
    "docs/agent-system/FRICTION_LOG.md",
    "docs/agent-system/CROSS_REPO_CONTRACT.md",
    ".claude/agents/dll-implementer.md",
    ".claude/agents/dll-mechanic.md",
    ".claude/agents/dll-reviewer.md",
    ".claude/agents/dll-scout.md",
    ".claude/settings.json",
    ".claude/skills/developer-lens-lab-continuation/SKILL.md",
    "HUMAN_TODO.md",
    "README.md",
    "docs/CURRENT_STATE.md",
    "docs/IMPLEMENTATION_LEDGER.md",
    "docs/EXPERIMENT_LEDGER.md",
    "docs/FAILURE_ARCHIVE.md",
    "docs/OPERATING_MODEL.md",
    "docs/PRODUCT_BOUNDARY.md",
    "docs/DATA_POLICY.md",
    "docs/CONTRACTS.md",
    "docs/RESEARCH_PROGRAMME.md",
    "docs/CORPUS_PIPELINE.md",
    "docs/REPRODUCIBILITY.md",
    "docs/REVIEW_PROTOCOL.md",
    "docs/HARDENING_BACKLOG.md",
    "docs/ROADMAP.md",
    ".agents/skills/developer-lens-lab-continuation/SKILL.md",
    ".agents/skills/developer-lens-lab-continuation/agents/openai.yaml",
    "schemas/research-pack/v1/consumer.schema.json",
    "schemas/evaluation-bundle/v1/schema.json",
)

ALLOWED_TIER_KEYS = {
    "tier",
    "name",
    "authority",
    "public_synthetic_publication",
    "flags",
    "budgets",
    "human_todo",
    "last_reviewed",
}
ALLOWED_FLAGS = {
    "sensitive_data",
    "wave_mode",
    "dormant_production",
    "relaxed_work_loss_guards",
}
LOCAL_LINK_RE = re.compile(r"\[[^]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
SKIPPED_MARKDOWN_PARTS = {
    ".dllab",
    ".git",
    ".package-smoke",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "artifacts",
    "htmlcov",
    "site",
}

CURRENT_STATE_REQUIRED_KEYS = (
    "updated",
    "phase",
    "posture",
    "repository",
    "branch",
    "head",
    "active_wave",
    "delivered",
    "next_safe_slice",
    "release_and_owner_gates",
    "capabilities",
    "canonical_evidence",
    "blockers",
    "late_review_debt",
    "exact_resume_point",
)
CURRENT_STATE_MAPPING_KEYS = ("capabilities", "canonical_evidence")


@dataclass(frozen=True)
class VerificationReport:
    failures: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.failures


def _markdown_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for directory, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = sorted(
            dirname for dirname in dirnames if dirname not in SKIPPED_MARKDOWN_PARTS
        )
        directory_path = Path(directory)
        paths.extend(
            directory_path / filename
            for filename in filenames
            if (directory_path / filename).match("*.md")
        )
    return sorted(paths)


def verify_markdown_links(root: Path) -> list[str]:
    failures: list[str] = []
    for path in _markdown_files(root):
        relative_parts = path.relative_to(root).parts
        if relative_parts[:2] == ("reports", "generated"):
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK_RE.findall(text):
            target = raw_target.split("#", 1)[0].replace("%20", " ")
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                failures.append(f"broken local link in {path.relative_to(root)}: {raw_target}")
    return failures


def verify_current_state_yaml(root: Path) -> list[str]:
    """Validate the single machine-readable CURRENT_STATE.md YAML fence."""
    path = root / "docs" / "CURRENT_STATE.md"
    if not path.is_file():
        return ["missing docs/CURRENT_STATE.md"]
    lines = path.read_text(encoding="utf-8").splitlines()
    openings = [index for index, line in enumerate(lines) if line.strip() == "```yaml"]
    if len(openings) != 1:
        return [
            f"docs/CURRENT_STATE.md must contain exactly one YAML fence (found {len(openings)})"
        ]
    opening = openings[0]
    closing = next(
        (index for index, line in enumerate(lines) if index > opening and line.strip() == "```"),
        None,
    )
    if closing is None:
        return [
            "docs/CURRENT_STATE.md must contain exactly one closing YAML fence "
            f"after line {opening + 1}"
        ]
    body = "\n".join(lines[opening + 1 : closing])
    try:
        payload: object = yaml.safe_load(body)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        line = opening + 2 + getattr(mark, "line", 0)
        problem = getattr(exc, "problem", "invalid YAML")
        return [f"docs/CURRENT_STATE.md:{line}: invalid YAML: {problem}"]
    if not isinstance(payload, dict):
        return [f"docs/CURRENT_STATE.md:{opening + 2}: YAML top level must be a mapping"]
    mapping = cast(dict[object, object], payload)
    if not all(isinstance(key, str) for key in mapping):
        return [f"docs/CURRENT_STATE.md:{opening + 2}: YAML keys must be strings"]
    values = cast(dict[str, object], mapping)
    failures = [
        f"docs/CURRENT_STATE.md:{opening + 2}: YAML missing required key {key!r}"
        for key in CURRENT_STATE_REQUIRED_KEYS
        if key not in values
    ]
    for key in CURRENT_STATE_MAPPING_KEYS:
        if key in values and not isinstance(values[key], dict):
            failures.append(
                f"docs/CURRENT_STATE.md:{opening + 2}: YAML key {key!r} must be a mapping"
            )
    active_wave = values.get("active_wave")
    if active_wave is not None and not isinstance(active_wave, list):
        failures.append(
            f"docs/CURRENT_STATE.md:{opening + 2}: YAML key 'active_wave' must be a list"
        )
    delivered = values.get("delivered")
    if delivered is not None:
        if not isinstance(delivered, list):
            failures.append(
                f"docs/CURRENT_STATE.md:{opening + 2}: YAML key 'delivered' must be a list"
            )
        else:
            delivered_items = cast(list[object], delivered)
            for index, item in enumerate(delivered_items, start=1):
                if not isinstance(item, dict):
                    failures.append(
                        f"docs/CURRENT_STATE.md:{opening + 2}: delivered entry "
                        f"{index} must be a one-key mapping"
                    )
                else:
                    item_mapping = cast(dict[object, object], item)
                    if len(item_mapping) != 1 or not all(
                        isinstance(item_key, str) and isinstance(item_value, str)
                        for item_key, item_value in item_mapping.items()
                    ):
                        failures.append(
                            f"docs/CURRENT_STATE.md:{opening + 2}: delivered entry "
                            f"{index} must contain exactly one string key and value"
                        )
    return failures


def _verify_tier(root: Path) -> list[str]:
    path = root / ".agent-harness" / "tier.json"
    try:
        payload_raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid tier.json: {exc}"]
    if not isinstance(payload_raw, dict):
        return ["invalid tier.json: top level must be a string-keyed object"]
    payload_mapping = cast(dict[object, object], payload_raw)
    if not all(isinstance(key, str) for key in payload_mapping):
        return ["invalid tier.json: top level must be a string-keyed object"]
    payload = cast(dict[str, object], payload_mapping)
    failures: list[str] = []
    unknown = set(payload) - ALLOWED_TIER_KEYS
    if unknown:
        failures.append(f"unsupported tier.json keys: {sorted(unknown)}")
    flags_raw = payload.get("flags")
    if not isinstance(flags_raw, dict):
        flags: dict[str, object] = {}
    else:
        flags_mapping = cast(dict[object, object], flags_raw)
        flags = (
            cast(dict[str, object], flags_mapping)
            if all(isinstance(key, str) for key in flags_mapping)
            else {}
        )
    if set(flags) != ALLOWED_FLAGS:
        failures.append("tier.json flags must exactly match the supported harness flags")
    if payload.get("tier") != 1:
        failures.append("bootstrap tier must remain T1 while the repository stores C0 only")
    if flags.get("sensitive_data") is not False:
        failures.append("sensitive_data must stay false while tracked/runtime scope is C0 only")
    publication = payload.get("public_synthetic_publication")
    if publication != {
        "remote": "origin",
        "repository": "Chris0Jeky/developer-lens-lab",
    }:
        failures.append("public synthetic publication must use the declared owner/repository route")
    return failures


# The governor policy (.agent-harness/governor.json, schema dllab-governor.v1) is the durable
# machine-readable half of the constitution. These checks keep it structurally honest and, above
# all, keep the two invariants a silent self-relaxation would target — the locked-invariant list
# and the model-pin coherence — harness-enforced rather than prose-only.
GOVERNOR_SCHEMA = "dllab-governor.v1"
GOVERNOR_REQUIRED_KEYS = (
    "purpose",
    "authorities",
    "focus",
    "model_routing",
    "risk_classes",
    "experiment_lifecycle",
    "data_lanes",
    "activation_preconditions",
    "review_gates",
    "queues",
    "cross_repo",
    "self_evolution",
    "generated_indexes",
    "runtime_state",
)
# Hardcoded so a governor edit that drops one of these locked invariants fails loudly here rather
# than relaxing itself silently. Order matches docs/OWNER_CONSTITUTION.md.
GOVERNOR_LOCKED_INVARIANTS = (
    "secret prohibition",
    "data authority",
    "private-output locality",
    "missingness honesty",
    "deterministic fallback",
    "holdout integrity",
    "model-output labelling",
    "owner-only decisions",
    "stable-product promotion boundary",
    "review/merge gates",
)
# The constitution's binding attention allocation. Pinned by value, not merely by presence: a
# reallocation is a reviewed constitution edit, so the verifier is expected to move with it.
GOVERNOR_REQUIRED_FOCUS = (
    ("research", 7),
    ("story_product", 5),
    ("distribution", 3),
    ("community", 2),
    ("realdata_standalone", 0),
)
GOVERNOR_PIN_ROLES = ("scout", "implementer", "reviewer", "mechanic")
# Lane statuses are hardcoded until LAB-ACT-01 replaces them with executable activation state.
# Until then this is the only thing stopping a non-synthetic lane from being flipped open by an
# unreviewed edit, so the pin is deliberately exact rather than a presence check.
GOVERNOR_LANE_STATUSES = (
    ("S_synthetic", "active"),
    ("O_own_private", "authorised_awaiting_preconditions"),
    ("C_curated_public", "authorised_awaiting_preconditions"),
    ("P_publishable_c0", "active_with_release_review"),
)
# Identity, not just count: seven copies of "ok" satisfy a length floor while deleting every real
# precondition. Each token must appear in at least one item (case-insensitive substring).
GOVERNOR_ACTIVATION_TOKENS = (
    "tier.json",
    "sink",
    "deny rules",
    "secret scanning",
    "dependency",
    "retention",
    "owner",
)
GOVERNOR_REQUIRED_REVIEW_TRIGGERS = (
    "non-trivial code",
    "methodology",
    "contracts",
    "governor changes",
)


def _agent_frontmatter_model(path: Path) -> str | None:
    """Return the value of the first ``model:`` line inside a leading ``---`` frontmatter block.

    Minimal parse (no YAML dependency): the file must open with a ``---`` fence, and the model
    line is read from inside the first fenced block. Returns None if the file is unreadable, has
    no leading frontmatter block, or declares no ``model:`` line.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.startswith("---\n"):
        return None
    end = normalized.find("\n---", len("---\n"))
    if end == -1:
        return None
    block = normalized[len("---\n") : end + 1]
    for line in block.split("\n"):
        if line.startswith("model:"):
            return line[len("model:") :].strip()
    return None


def _routed_models(routing: dict[str, object]) -> list[tuple[str, str]]:
    """Every ``(role, model_id)`` a routing entry actually routes work to.

    Covers both the singular ``model`` key and the plural ``models`` list (``governor_lite``), so
    a prohibited model cannot be reintroduced through whichever key the check ignored.
    """
    routed: list[tuple[str, str]] = []
    for role, entry_raw in routing.items():
        if not isinstance(entry_raw, dict):
            continue
        entry = cast(dict[str, object], entry_raw)
        model = entry.get("model")
        if isinstance(model, str):
            routed.append((role, model))
        models_raw = entry.get("models")
        if isinstance(models_raw, list):
            routed.extend(
                (role, item) for item in cast(list[object], models_raw) if isinstance(item, str)
            )
    return routed


def _verify_governor_pins(routing: dict[str, object], root: Path) -> list[str]:
    failures: list[str] = []
    for role in GOVERNOR_PIN_ROLES:
        role_raw = routing.get(role)
        if not isinstance(role_raw, dict):
            failures.append(
                f"governor.json model_routing.{role} must declare agent and model for pin coherence"
            )
            continue
        role_cfg = cast(dict[str, object], role_raw)
        agent_rel = role_cfg.get("agent")
        model = role_cfg.get("model")
        # A missing/blank agent or model must fail loudly: silently skipping it would let a pinned
        # role drop its pin and keep the coherence check green — the exact gap this check closes.
        if not isinstance(agent_rel, str) or not isinstance(model, str):
            failures.append(
                f"governor.json model_routing.{role} must declare agent and model for pin coherence"
            )
            continue
        agent_model = _agent_frontmatter_model(root / agent_rel)
        if agent_model is None:
            failures.append(
                f"governor.json model_routing.{role} agent {agent_rel!r} has no readable "
                "frontmatter model: line to check the pin against"
            )
        elif agent_model != model:
            failures.append(
                f"governor.json model_routing.{role} declares model {model!r} but {agent_rel} "
                f"frontmatter declares {agent_model!r}"
            )
    return failures


def _verify_authority_path(name: str, target: object, root: Path) -> list[str]:
    """An authority must name an in-repo file.

    An absolute path or a ``..`` escape would point the governor's own authority list outside the
    repository — at a machine-local file no reviewer sees — so containment is checked before
    existence, and both produce a failure.
    """
    if not isinstance(target, str) or not target:
        return [f"governor.json authority {name!r} must be a repo-relative file path string"]
    resolved_root = root.resolve()
    resolved = (resolved_root / target).resolve()
    if not resolved.is_relative_to(resolved_root):
        return [
            f"governor.json authority {name!r} must stay inside the repository; "
            f"{target!r} resolves outside it"
        ]
    if not resolved.is_file():
        return [f"governor.json authority {name!r} must point at an existing repo file"]
    return []


def _verify_governor_lanes(payload: dict[str, object]) -> list[str]:
    lanes_raw = payload.get("data_lanes")
    if not isinstance(lanes_raw, dict):
        return ["governor.json data_lanes must be an object of declared lanes"]
    lanes = cast(dict[str, object], lanes_raw)
    failures: list[str] = []
    for lane, expected_status in GOVERNOR_LANE_STATUSES:
        lane_raw = lanes.get(lane)
        if not isinstance(lane_raw, dict):
            failures.append(f"governor.json data_lanes.{lane} must be an object declaring a status")
            continue
        status = cast(dict[str, object], lane_raw).get("status")
        if not isinstance(status, str):
            failures.append(f"governor.json data_lanes.{lane}.status must be a string")
        elif status != expected_status:
            failures.append(
                f"governor.json data_lanes.{lane}.status must remain {expected_status!r}, "
                f"not {status!r}"
            )
    return failures


# Presence-only key checks let a gate be emptied while verification stays green (an
# activation_preconditions with zero items, or a zeroed aging window, still "exists"). These floors
# pin the values themselves so weakening a gate is a verification failure, not a quiet edit.
GOVERNOR_MIN_ACTIVATION_ITEMS = 7
GOVERNOR_MIN_AGING_MINUTES = 15
GOVERNOR_MAX_FIX_ROUNDS = 2


def _verify_governor_gate_values(payload: dict[str, object]) -> list[str]:
    failures: list[str] = []
    preconditions_raw = payload.get("activation_preconditions")
    if not isinstance(preconditions_raw, dict):
        failures.append("governor.json activation_preconditions must be an object with items")
    else:
        preconditions = cast(dict[str, object], preconditions_raw)
        items_raw = preconditions.get("items")
        items = (
            [item for item in cast(list[object], items_raw) if isinstance(item, str)]
            if isinstance(items_raw, list)
            else None
        )
        if items is None or len(items) < GOVERNOR_MIN_ACTIVATION_ITEMS:
            failures.append(
                "governor.json activation_preconditions.items must be a list of at least "
                f"{GOVERNOR_MIN_ACTIVATION_ITEMS} precondition strings"
            )
        else:
            haystack = " | ".join(items).lower()
            missing_tokens = [
                token for token in GOVERNOR_ACTIVATION_TOKENS if token.lower() not in haystack
            ]
            if missing_tokens:
                failures.append(
                    "governor.json activation_preconditions.items must still cover every "
                    f"precondition subject; missing: {missing_tokens}"
                )
    gates_raw = payload.get("review_gates")
    if not isinstance(gates_raw, dict):
        failures.append("governor.json review_gates must be an object")
        return failures
    gates = cast(dict[str, object], gates_raw)
    aging = gates.get("aging_minutes_after_push")
    # bool is an int subclass; True would otherwise pass as a 1-minute aging window.
    if isinstance(aging, bool) or not isinstance(aging, int) or aging < GOVERNOR_MIN_AGING_MINUTES:
        failures.append(
            "governor.json review_gates.aging_minutes_after_push must be an integer of at least "
            f"{GOVERNOR_MIN_AGING_MINUTES}"
        )
    ceiling = gates.get("fix_round_ceiling")
    if (
        isinstance(ceiling, bool)
        or not isinstance(ceiling, int)
        or not 1 <= ceiling <= GOVERNOR_MAX_FIX_ROUNDS
    ):
        failures.append(
            "governor.json review_gates.fix_round_ceiling must be an integer between 1 and "
            f"{GOVERNOR_MAX_FIX_ROUNDS}"
        )
    triggers_raw = gates.get("fresh_context_review_required_for")
    triggers = (
        {item for item in cast(list[object], triggers_raw) if isinstance(item, str)}
        if isinstance(triggers_raw, list)
        else None
    )
    if triggers is None:
        failures.append(
            "governor.json review_gates.fresh_context_review_required_for must be a list of "
            "review triggers"
        )
    else:
        missing_triggers = [
            trigger for trigger in GOVERNOR_REQUIRED_REVIEW_TRIGGERS if trigger not in triggers
        ]
        if missing_triggers:
            failures.append(
                "governor.json review_gates.fresh_context_review_required_for must retain every "
                f"required trigger; missing: {missing_triggers}"
            )
    # Exactly True: a falsy or truthy-but-non-boolean value would quietly drop the sweep.
    if gates.get("post_merge_late_comment_sweep") is not True:
        failures.append("governor.json review_gates.post_merge_late_comment_sweep must be true")
    return failures


def verify_governor(root: Path) -> list[str]:
    path = root / ".agent-harness" / "governor.json"
    try:
        payload_raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid governor.json: {exc}"]
    if not isinstance(payload_raw, dict):
        return ["invalid governor.json: top level must be a string-keyed object"]
    payload_mapping = cast(dict[object, object], payload_raw)
    if not all(isinstance(key, str) for key in payload_mapping):
        return ["invalid governor.json: top level must be a string-keyed object"]
    payload = cast(dict[str, object], payload_mapping)
    failures: list[str] = []
    if payload.get("schema") != GOVERNOR_SCHEMA:
        failures.append(f'governor.json schema must be "{GOVERNOR_SCHEMA}"')
    for key in GOVERNOR_REQUIRED_KEYS:
        if key not in payload:
            failures.append(f"governor.json is missing required key: {key}")
    authorities_raw = payload.get("authorities")
    if not isinstance(authorities_raw, dict):
        failures.append("governor.json authorities must be an object of repo-relative files")
    else:
        authorities = cast(dict[str, object], authorities_raw)
        for name, target in authorities.items():
            failures.extend(_verify_authority_path(name, target, root))
    routing_raw = payload.get("model_routing")
    routing = cast(dict[str, object], routing_raw) if isinstance(routing_raw, dict) else {}
    prohibited_raw = routing.get("prohibited_models")
    prohibited = (
        [item for item in cast(list[object], prohibited_raw) if isinstance(item, str)]
        if isinstance(prohibited_raw, list)
        else []
    )
    if "haiku" not in prohibited:
        failures.append('governor.json model_routing.prohibited_models must include "haiku"')
    # Listing a prohibition is not enforcing it: a routed model id that carries a prohibited token
    # (e.g. "claude-haiku-4-5" against "haiku") must fail, or the list is prose. Case-insensitive
    # substring, because model ids embed the family name rather than equalling it.
    for role, routed_model in _routed_models(routing):
        for token in prohibited:
            if token.lower() in routed_model.lower():
                failures.append(
                    f"governor.json model_routing.{role} routes to {routed_model!r}, which "
                    f"contains the prohibited model token {token!r}"
                )
    evolution_raw = payload.get("self_evolution")
    evolution = cast(dict[str, object], evolution_raw) if isinstance(evolution_raw, dict) else {}
    locked_raw = evolution.get("may_never_self_relax")
    if not isinstance(locked_raw, list):
        failures.append(
            "governor.json self_evolution.may_never_self_relax must be a list of locked invariants"
        )
    else:
        locked = {item for item in cast(list[object], locked_raw) if isinstance(item, str)}
        missing = [invariant for invariant in GOVERNOR_LOCKED_INVARIANTS if invariant not in locked]
        if missing:
            failures.append(
                "governor.json self_evolution.may_never_self_relax must retain every locked "
                f"invariant; missing: {missing}"
            )
    focus_raw = payload.get("focus")
    focus = cast(dict[str, object], focus_raw) if isinstance(focus_raw, dict) else {}
    for axis, expected_weight in GOVERNOR_REQUIRED_FOCUS:
        if axis not in focus:
            failures.append(f"governor.json focus is missing required axis: {axis}")
            continue
        weight = focus[axis]
        # bool is an int subclass; True must not satisfy a weight of 1.
        if isinstance(weight, bool) or not isinstance(weight, int) or weight != expected_weight:
            failures.append(
                f"governor.json focus.{axis} must be the constitution's allocated weight "
                f"{expected_weight}, not {weight!r}"
            )
    failures.extend(_verify_governor_lanes(payload))
    failures.extend(_verify_governor_gate_values(payload))
    failures.extend(_verify_governor_pins(routing, root))
    return failures


def _verify_cards(root: Path) -> list[str]:
    result = subprocess.run(
        [sys.executable, str(root / "tools" / "cards.py"), "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    message = (result.stdout + result.stderr).strip()
    return [f"generated task cards drifted: {message}"]


# Committed Claude settings must deny `Read` on the local generated-artifact sinks so that part of
# the protected-data rule (CLAUDE.md, docs/DATA_POLICY.md) is harness-enforced rather than prose.
# This mirrors the developer-lens product deny rules and shares their scope: only the `Read` tool
# on the confined store and generated output. `.dllab` is the confined C0 artifact store;
# `artifacts/` and `reports/generated/` are gitignored run output. Broader coverage (Grep/Glob,
# `.env`/keys, scattered artifacts) is tracked in docs/HARDENING_BACKLOG.md, not claimed here.
REQUIRED_SETTINGS_READ_DENY = (
    "Read(./.dllab/**)",
    "Read(./artifacts/**)",
    "Read(./reports/generated/**)",
)


# Every named block that must stay byte-identical between the two SKILL.md copies. Each entry is
# guarded independently so a new shared block only needs its marker pair added here plus the two
# marker lines wrapped around the paragraph in both files.
SHARED_SKILL_MARKERS = (
    "shared:evaluation-integrity",
    "shared:protected-data-defaults",
    "shared:continuation-friction-tasking-v1",
)
SKILL_PARITY_FILES = (
    ".claude/skills/developer-lens-lab-continuation/SKILL.md",
    ".agents/skills/developer-lens-lab-continuation/SKILL.md",
)

AGENT_FRICTION_MARKER = "shared:agent-friction-tasking-v1"
AGENT_FRICTION_FILES = (
    ".claude/agents/dll-implementer.md",
    ".claude/agents/dll-mechanic.md",
    ".claude/agents/dll-reviewer.md",
    ".claude/agents/dll-scout.md",
)
AGENT_FRICTION_REQUIRED_CLAUSES = (
    "docs/agent-system/FRICTION_LOG.md in the same hop and links to an existing issue, card, or "
    "durable",
    "A write-capable role appends it; a read-only role reports it as a required coordinator "
    "same-hop",
    "Capture never widens scope",
    "Never record a PID, absolute local path, token, or private",
)


def verify_one_shared_block(root: Path, marker: str) -> list[str]:
    label = marker.removeprefix("shared:")
    start_marker = f"<!-- {marker} start -->"
    end_marker = f"<!-- {marker} end -->"
    failures: list[str] = []
    blocks: list[str] = []
    for rel in SKILL_PARITY_FILES:
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            failures.append(f"{rel}: missing shared {label} marker(s)")
            continue
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        # Require exactly one ordered pair. A duplicate pair (e.g. a copy/paste while extending the
        # section) would otherwise leave find() comparing only the first block, silently ignoring a
        # divergent second one — a false pass in a check whose whole job is to catch divergence.
        if normalized.count(start_marker) != 1 or normalized.count(end_marker) != 1:
            failures.append(f"{rel}: expected exactly one shared {label} marker pair")
            continue
        start = normalized.find(start_marker)
        end = normalized.find(end_marker)
        if end <= start:
            failures.append(f"{rel}: shared {label} markers are out of order")
            continue
        block = normalized[start + len(start_marker) : end].strip()
        blocks.append(block)
    if len(blocks) == len(SKILL_PARITY_FILES) and len(set(blocks)) > 1:
        failures.append(f"shared {label} section drifted between the two SKILL.md copies")
    return failures


def verify_skill_parity(root: Path) -> list[str]:
    failures: list[str] = []
    for marker in SHARED_SKILL_MARKERS:
        failures.extend(verify_one_shared_block(root, marker))
    return failures


def verify_agent_friction_parity(root: Path) -> list[str]:
    """Require one identical, role-aware friction block across all lab Claude agents."""
    start_marker = f"<!-- {AGENT_FRICTION_MARKER} start -->"
    end_marker = f"<!-- {AGENT_FRICTION_MARKER} end -->"
    failures: list[str] = []
    blocks: list[tuple[str, str]] = []
    for rel in AGENT_FRICTION_FILES:
        path = root / rel
        try:
            normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
        except OSError:
            failures.append(f"{rel}: missing agent friction marker(s)")
            continue
        start_count = normalized.count(start_marker)
        end_count = normalized.count(end_marker)
        if start_count != 1 or end_count != 1:
            failures.append(
                f"{rel}: expected exactly one agent friction marker pair "
                f"(found {start_count}/{end_count})"
            )
            continue
        start = normalized.find(start_marker)
        end = normalized.find(end_marker)
        if end <= start:
            failures.append(f"{rel}: agent friction markers are out of order")
            continue
        body = normalized[start + len(start_marker) : end]
        blocks.append((rel, body))
        for clause in AGENT_FRICTION_REQUIRED_CLAUSES:
            if clause not in body:
                failures.append(f"{rel}: agent friction block is missing required clause: {clause}")
    if len(blocks) == len(AGENT_FRICTION_FILES) and len({body for _, body in blocks}) > 1:
        failures.append(
            f"agent friction block bytes drift between {blocks[0][0]} and other agent files"
        )
    return failures


# --- Prompt operating system parity ------------------------------------------------------------
#
# The prompt library is the only executable-prompt surface, and its spine is shared byte-for-byte
# with Chris0Jeky/developer-lens through the repo-neutral parity manifest. Everything below exists
# because prose parity is not parity: the manifest pins the shared block bodies by SHA-256, so a
# block edited in one prompt (or drifting from the product side) fails here instead of silently
# giving the two repositories different operating rules.
PROMPT_PARITY_MANIFEST = ".agent-harness/prompt-parity.json"
PROMPT_LIBRARY = "docs/agent-system/PROMPT_LIBRARY.md"
CONTINUOUS_WORK_PROTOCOL = "docs/agent-system/CONTINUOUS_WORK_PROTOCOL.md"
LAB_REPOSITORY_SLUG = "Chris0Jeky/developer-lens-lab"

# Pinned in code, not merely read from the manifest: the manifest is a copied artifact, so a
# truncated or reordered copy must fail rather than redefine what this repository requires.
COMMON_PROMPT_IDS = (
    "DL-P01-FLAGSHIP-GOVERNOR",
    "DL-P02-GOVERNOR-LITE",
    "DL-P03-OVERNIGHT-CONTINUOUS",
    "DL-P04-RESUME-RECONCILE",
    "DL-P05-BOUNDED-IMPLEMENTER",
    "DL-P06-INDEPENDENT-REVIEWER",
    "DL-P07-MECHANICAL-SWEEP",
    "DL-P08-CI-REVIEW-RECOVERY",
    "DL-P09-RELEASE-CURATOR",
    "DL-P10-CROSS-REPO-COORDINATOR",
    "DL-P11-DISCOVERY-IDEA-MINER",
    "DL-P12-FRICTION-BURNDOWN",
)
LAB_EXTENSION_PROMPT_IDS = (
    "DL-LX01-LAB-EXPERIMENT-HARNESS",
    "DL-LX02-LAB-EVALUATION-REPRODUCIBILITY",
)
SHARED_BLOCK_IDS = ("runtime-bootstrap-v1", "friction-tasking-v1")
CONTINUOUS_PROMPT_ID = "DL-P03-OVERNIGHT-CONTINUOUS"

# The dual-runtime contract, as literal substrings. A prompt that names neither runtime is not
# copy-ready: pasted cold it leaves the agent to guess which canon binds it and which agents exist.
REQUIRED_CLAUDE_CLAUSE = (
    "CLAUDE.md",
    "Opus 5 low",
    "dll-implementer",
    "dll-reviewer",
    "dll-mechanic",
)
REQUIRED_CODEX_CLAUSE = ("AGENTS.md", "developer-lens-lab-continuation", "Sol/Terra/Luna")

CONTINUOUS_MARKER_PAIRS = (
    ("<!-- continuous-execution-begin -->", "<!-- continuous-execution-end -->"),
    ("<!-- continuous-impact-begin -->", "<!-- continuous-impact-end -->"),
    ("<!-- continuous-stop-begin -->", "<!-- continuous-stop-end -->"),
)
# The overnight launcher is the flagship delivery governor, not a documentation-maintenance
# default. These literal clauses make that role mechanically reviewable without altering the
# product-shared prompt spine or its parity manifest.
P03_DELIVERY_TOKENS = (
    "FLAGSHIP DELIVERY GOVERNOR",
    "IMPACT CONTRACT",
    "MISSION DELIVERY",
    "coordinator does not write research implementation code",
    "C0 invented data only",
    "EXPERIMENT_LEDGER",
    "FAILURE_ARCHIVE",
)
ALLOWED_PROMPT_CLASSIFICATIONS = ("redirect", "historical")

PROMPT_MARKER_RE = re.compile(r"<!-- prompt-id: (\S+) status: (\S+) -->")
TEXT_FENCE_RE = re.compile(r"^```text$", re.M)
PROMPT_CLASSIFICATION_RE = re.compile(r"<!-- prompt-classification: (\S+) -->")
# A bare q-N and its fully qualified form. Counting both and comparing is what makes an unqualified
# ref fail: product q-8 and lab q-8 are different gates, so an ambiguous ref is a real defect.
BARE_HUMAN_REF_RE = re.compile(r"q-\d+")
QUALIFIED_HUMAN_REF_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+::HUMAN_TODO\.md::q-\d+")


def normalize_newlines(text: str) -> str:
    """CRLF and CR collapsed to LF so digests are stable across platforms and checkouts."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def shared_block_digest(body: str) -> str:
    """The manifest's declared digest input: the exact block body, LF-normalized, UTF-8, no
    trailing newline."""
    return hashlib.sha256(normalize_newlines(body).encode("utf-8")).hexdigest()


def shared_blocks_in(library_text: str) -> dict[str, str]:
    """Map each declared shared-block ID to its fenced body, for blocks present in the library."""
    normalized = normalize_newlines(library_text)
    blocks: dict[str, str] = {}
    for block_id in SHARED_BLOCK_IDS:
        pattern = rf"<!-- shared-block: {re.escape(block_id)} -->\n\n```text\n(.*?)\n```"
        match = re.search(pattern, normalized, re.S)
        if match is not None:
            blocks[block_id] = match.group(1)
    return blocks


def prompt_entries(library_text: str) -> list[tuple[str, str, str]]:
    """Every ``(prompt_id, status, body)`` in document order.

    The body is the single fenced ``text`` block that must immediately follow the marker; a marker
    with no following fence yields an empty body so the caller reports it rather than crashing.
    """
    normalized = normalize_newlines(library_text)
    entries: list[tuple[str, str, str]] = []
    for match in PROMPT_MARKER_RE.finditer(normalized):
        remainder = normalized[match.end() :]
        body_match = re.match(r"\n\n```text\n(.*?)\n```", remainder, re.S)
        entries.append((match.group(1), match.group(2), body_match.group(1) if body_match else ""))
    return entries


def _str_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    items = cast(list[object], value)
    if not all(isinstance(item, str) for item in items):
        return None
    return cast(list[str], items)


def verify_parity_manifest(payload: object) -> list[str]:
    """Structural and identity checks on the repo-neutral parity manifest.

    Pure so the malformed shapes can be tested without a repository: the manifest is copied between
    repositories, and a copy that lost its schema version, its ordering or this repository's entry
    must fail loudly rather than degrade into an unchecked file.
    """
    if not isinstance(payload, dict):
        return ["prompt-parity.json: top level must be a string-keyed object"]
    mapping = cast(dict[object, object], payload)
    if not all(isinstance(key, str) for key in mapping):
        return ["prompt-parity.json: top level must be a string-keyed object"]
    manifest = cast(dict[str, object], mapping)
    failures: list[str] = []
    if manifest.get("manifest_schema_version") != 1:
        failures.append("prompt-parity.json: manifest_schema_version must be 1")
    common = _str_list(manifest.get("common_prompt_ids"))
    if common is None or tuple(common) != COMMON_PROMPT_IDS:
        failures.append(
            "prompt-parity.json: common_prompt_ids must equal the code-pinned common IDs, in order"
        )
    continuous = _str_list(manifest.get("continuous_prompt_ids"))
    if continuous is None or CONTINUOUS_PROMPT_ID not in continuous:
        failures.append(
            f"prompt-parity.json: continuous_prompt_ids must include {CONTINUOUS_PROMPT_ID}"
        )
    blocks_raw = manifest.get("shared_blocks")
    if not isinstance(blocks_raw, list):
        failures.append("prompt-parity.json: shared_blocks must be a list of {id, sha256} objects")
    else:
        block_ids: list[str] = []
        for entry_raw in cast(list[object], blocks_raw):
            if not isinstance(entry_raw, dict):
                failures.append("prompt-parity.json: each shared_blocks entry must be an object")
                continue
            entry = cast(dict[str, object], entry_raw)
            block_id = entry.get("id")
            digest = entry.get("sha256")
            if not isinstance(block_id, str) or not isinstance(digest, str):
                failures.append(
                    "prompt-parity.json: each shared_blocks entry needs string id and sha256"
                )
                continue
            block_ids.append(block_id)
        if block_ids and tuple(block_ids) != SHARED_BLOCK_IDS:
            failures.append(
                "prompt-parity.json: shared_blocks must declare the code-pinned block IDs, in order"
            )
    failures.extend(_verify_manifest_repository_entry(manifest))
    return failures


def _verify_manifest_repository_entry(manifest: dict[str, object]) -> list[str]:
    repositories_raw = manifest.get("repositories")
    if not isinstance(repositories_raw, list):
        return ["prompt-parity.json: repositories must be a list containing this repository"]
    for entry_raw in cast(list[object], repositories_raw):
        if not isinstance(entry_raw, dict):
            continue
        entry = cast(dict[str, object], entry_raw)
        if entry.get("slug") != LAB_REPOSITORY_SLUG:
            continue
        failures: list[str] = []
        if entry.get("role") != "lab":
            failures.append(f"prompt-parity.json: {LAB_REPOSITORY_SLUG} role must be 'lab'")
        extensions = _str_list(entry.get("extension_prompt_ids"))
        if extensions is None or tuple(extensions) != LAB_EXTENSION_PROMPT_IDS:
            failures.append(
                "prompt-parity.json: lab extension_prompt_ids must equal the code-pinned lab "
                "extension IDs, in order"
            )
        for key, expected in (
            ("prompt_library", PROMPT_LIBRARY),
            ("continuous_work_protocol", CONTINUOUS_WORK_PROTOCOL),
            ("friction_log", "docs/agent-system/FRICTION_LOG.md"),
        ):
            if entry.get(key) != expected:
                failures.append(f"prompt-parity.json: lab {key} must be {expected!r}")
        return failures
    return [f"prompt-parity.json: repositories must contain an entry for {LAB_REPOSITORY_SLUG}"]


def verify_prompt_library(library_text: str, digests: dict[str, str]) -> list[str]:
    """Every structural and content rule the library itself must satisfy.

    ``digests`` maps shared-block ID to the manifest's declared SHA-256. Pure on text so each
    failure mode (drifted digest, duplicated marker, missing runtime clause, bare human ref) can be
    tested directly.
    """
    normalized = normalize_newlines(library_text)
    expected_ids = COMMON_PROMPT_IDS + LAB_EXTENSION_PROMPT_IDS
    failures: list[str] = []

    blocks = shared_blocks_in(normalized)
    for block_id in SHARED_BLOCK_IDS:
        body = blocks.get(block_id)
        if body is None:
            failures.append(f"{PROMPT_LIBRARY}: missing shared block {block_id}")
            continue
        expected_digest = digests.get(block_id)
        actual = shared_block_digest(body)
        if expected_digest is not None and actual != expected_digest:
            failures.append(
                f"{PROMPT_LIBRARY}: shared block {block_id} digest {actual} does not match the "
                f"manifest digest {expected_digest}; the block has drifted from the product side"
            )

    entries = prompt_entries(normalized)
    found_ids = [prompt_id for prompt_id, _, _ in entries]
    duplicates = sorted({pid for pid in found_ids if found_ids.count(pid) > 1})
    if duplicates:
        failures.append(f"{PROMPT_LIBRARY}: duplicate prompt markers: {duplicates}")
    if tuple(found_ids) != expected_ids:
        missing = [pid for pid in expected_ids if pid not in found_ids]
        extra = [pid for pid in found_ids if pid not in expected_ids]
        failures.append(
            f"{PROMPT_LIBRARY}: prompt markers must equal the code-pinned IDs in manifest order; "
            f"missing: {missing}; unexpected: {extra}"
        )

    # One fence per shared block plus one per prompt. A stray or duplicated fence means a prompt
    # body is ambiguous, which is exactly when a pasted prompt silently loses half its rules.
    expected_fences = len(SHARED_BLOCK_IDS) + len(entries)
    actual_fences = len(TEXT_FENCE_RE.findall(normalized))
    if actual_fences != expected_fences:
        failures.append(
            f"{PROMPT_LIBRARY}: expected exactly {expected_fences} text fences "
            f"(one per shared block and one per prompt), found {actual_fences}"
        )

    for prompt_id, status, body in entries:
        if status != "active":
            continue
        if not body:
            failures.append(f"{PROMPT_LIBRARY}: {prompt_id} has no fenced text body")
            continue
        failures.extend(_verify_active_body(prompt_id, body, blocks))
    return failures


def _verify_active_body(prompt_id: str, body: str, blocks: dict[str, str]) -> list[str]:
    failures: list[str] = []
    # Clause tokens are checked against the body with the shared blocks REMOVED. Several tokens
    # ("CLAUDE.md", "AGENTS.md", "Sol/Terra/Luna") also occur inside runtime-bootstrap-v1, so
    # checking the whole body would let the shared spine alone satisfy the check and a prompt
    # carrying no lab routing clause at all would pass.
    outside = body
    for block_id, block_body in blocks.items():
        count = body.count(block_body)
        if count != 1:
            failures.append(
                f"{PROMPT_LIBRARY}: {prompt_id} must carry exactly one copy of shared block "
                f"{block_id}, found {count}"
            )
        outside = outside.replace(block_body, "")
    for token in REQUIRED_CLAUDE_CLAUSE:
        if token not in outside:
            failures.append(
                f"{PROMPT_LIBRARY}: {prompt_id} is missing Claude runtime clause token {token!r}"
            )
    for token in REQUIRED_CODEX_CLAUSE:
        if token not in outside:
            failures.append(
                f"{PROMPT_LIBRARY}: {prompt_id} is missing the Codex runtime clause token {token!r}"
            )
    bare = len(BARE_HUMAN_REF_RE.findall(body))
    qualified = len(QUALIFIED_HUMAN_REF_RE.findall(body))
    if bare != qualified:
        failures.append(
            f"{PROMPT_LIBRARY}: {prompt_id} cites {bare - qualified} unqualified human ref(s); use "
            "<owner>/<repo>::HUMAN_TODO.md::q-N, because product q-8 and lab q-8 differ"
        )
    if prompt_id == CONTINUOUS_PROMPT_ID:
        for token in P03_DELIVERY_TOKENS:
            if token not in outside:
                failures.append(
                    f"{PROMPT_LIBRARY}: {prompt_id} is missing flagship delivery token {token!r}"
                )
    return failures


def verify_continuous_protocol(text: str) -> list[str]:
    """Each marker pair appears exactly once and in order.

    Reversed or duplicated markers are checked explicitly: a duplicated pair would let a reader (or
    a future extractor) see only the first region and miss a second, divergent one.
    """
    normalized = normalize_newlines(text)
    failures: list[str] = []
    for start_marker, end_marker in CONTINUOUS_MARKER_PAIRS:
        if normalized.count(start_marker) != 1 or normalized.count(end_marker) != 1:
            failures.append(
                f"{CONTINUOUS_WORK_PROTOCOL}: expected exactly one {start_marker} / {end_marker} "
                "marker pair"
            )
            continue
        if normalized.find(end_marker) <= normalized.find(start_marker):
            failures.append(
                f"{CONTINUOUS_WORK_PROTOCOL}: {start_marker} / {end_marker} are out of order"
            )
    return failures


def verify_prompt_classifications(root: Path) -> list[str]:
    """Any prompt-shaped document that declares a classification must declare a supported one.

    The library is the only executable-prompt surface; other prompt-shaped documents opt into
    `redirect` or `historical` so a reader can tell at a glance that they are not to be pasted.
    """
    failures: list[str] = []
    for path in _markdown_files(root):
        for classification in PROMPT_CLASSIFICATION_RE.findall(path.read_text(encoding="utf-8")):
            if classification not in ALLOWED_PROMPT_CLASSIFICATIONS:
                failures.append(
                    f"{path.relative_to(root)}: prompt-classification {classification!r} must be "
                    f"one of {list(ALLOWED_PROMPT_CLASSIFICATIONS)}"
                )
    return failures


def verify_prompt_parity(root: Path) -> list[str]:
    manifest_path = root / PROMPT_PARITY_MANIFEST
    library_path = root / PROMPT_LIBRARY
    continuous_path = root / CONTINUOUS_WORK_PROTOCOL
    try:
        manifest_payload: object = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid {PROMPT_PARITY_MANIFEST}: {exc}"]
    failures = verify_parity_manifest(manifest_payload)

    digests: dict[str, str] = {}
    if isinstance(manifest_payload, dict):
        blocks_raw = cast(dict[str, object], manifest_payload).get("shared_blocks")
        if isinstance(blocks_raw, list):
            for entry_raw in cast(list[object], blocks_raw):
                if not isinstance(entry_raw, dict):
                    continue
                entry = cast(dict[str, object], entry_raw)
                block_id = entry.get("id")
                digest = entry.get("sha256")
                if isinstance(block_id, str) and isinstance(digest, str):
                    digests[block_id] = digest
    try:
        library_text = library_path.read_text(encoding="utf-8")
    except OSError:
        return [*failures, f"missing required file: {PROMPT_LIBRARY}"]
    failures.extend(verify_prompt_library(library_text, digests))
    try:
        continuous_text = continuous_path.read_text(encoding="utf-8")
    except OSError:
        return [*failures, f"missing required file: {CONTINUOUS_WORK_PROTOCOL}"]
    failures.extend(verify_continuous_protocol(continuous_text))
    failures.extend(verify_prompt_classifications(root))
    return failures


CONTEXT_BUDGET_FILES = ("AGENTS.md", "CLAUDE.md")
CHARS_PER_TOKEN = 4  # standard ~4-chars/token English heuristic; a deterministic estimate, not an exact count  # noqa: E501


def verify_context_budget(root: Path) -> list[str]:
    path = root / ".agent-harness" / "tier.json"
    try:
        payload_raw: object = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload_raw, dict):
        return []
    payload = cast("dict[str, object]", payload_raw)
    # Distinguish an absent budgets key (legitimately unenforced) from a present-but-malformed
    # container. A non-object budgets (string/list/null/number/bool) silently disabled the check
    # before, the same "nothing enforces it" gap the present-but-invalid-value branch below closes.
    # _verify_tier validates only top-level keys, not the budgets container type, so this is the
    # sole reporter of a malformed container.
    if "budgets" not in payload:
        return []
    budgets_raw = payload["budgets"]
    if not isinstance(budgets_raw, dict):
        return ["tier.json budgets must be an object to declare a standing-context budget"]
    budgets = cast("dict[str, object]", budgets_raw)
    if "standing_context_tokens" not in budgets:
        return []
    # A declared-but-unusable budget must fail loudly, not silently disable the check;
    # a corrupted value would otherwise revert to the "nothing enforces it" gap. _verify_tier
    # validates only top-level keys, so the value itself is validated here.
    budget = budgets["standing_context_tokens"]
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
        return [
            "tier.json budgets.standing_context_tokens must be a positive integer to enforce "
            "the standing-context budget"
        ]
    total_chars = 0
    for name in CONTEXT_BUDGET_FILES:
        candidate = root / name
        if candidate.is_file():
            total_chars += len(candidate.read_text(encoding="utf-8"))
    estimate = math.ceil(total_chars / CHARS_PER_TOKEN)
    if estimate > budget:
        return [
            f"standing context (AGENTS.md+CLAUDE.md) ~{estimate} tokens exceeds the declared "
            f"standing_context_tokens budget of {budget}"
        ]
    return []


def verify_settings_deny(payload: object) -> list[str]:
    deny_rules: set[str] = set()
    if isinstance(payload, dict):
        permissions = cast("dict[str, object]", payload).get("permissions")
        if isinstance(permissions, dict):
            deny = cast("dict[str, object]", permissions).get("deny")
            if isinstance(deny, list):
                deny_rules = {rule for rule in cast("list[object]", deny) if isinstance(rule, str)}
    return [
        f'committed .claude/settings.json must deny "{rule}" so the protected-data rule is '
        "harness-enforced (docs/DATA_POLICY.md)"
        for rule in REQUIRED_SETTINGS_READ_DENY
        if rule not in deny_rules
    ]


def verify_repository(root: Path) -> VerificationReport:
    root = root.resolve()
    failures = [
        f"missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()
    ]
    for cold_start_name in ("AGENTS.md", "CLAUDE.md"):
        cold_start = root / cold_start_name
        if cold_start.is_file() and len(cold_start.read_text(encoding="utf-8").splitlines()) > 100:
            failures.append(f"{cold_start_name} exceeds the 100-line cold-start budget")
    adapter = root / "AGENTS.md"
    if adapter.is_file() and "CLAUDE.md" not in adapter.read_text(encoding="utf-8"):
        failures.append("AGENTS.md must name CLAUDE.md as the shared canon")
    canon = root / "CLAUDE.md"
    if canon.is_file() and "## Protected-data rule" not in canon.read_text(encoding="utf-8"):
        failures.append("CLAUDE.md must carry the protected-data rule section")
    settings = root / ".claude" / "settings.json"
    if settings.is_file():
        try:
            settings_payload: object = json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f".claude/settings.json is not valid JSON: {exc}")
        else:
            if "bypassPermissions" in json.dumps(settings_payload):
                failures.append(
                    "committed .claude/settings.json must not carry bypassPermissions; "
                    "it belongs in gitignored .claude/settings.local.json"
                )
            failures.extend(verify_settings_deny(settings_payload))
    tracked_local = subprocess.run(
        ["git", "ls-files", "--cached", "--", ".claude/settings.local.json"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if tracked_local.returncode == 0 and tracked_local.stdout.strip():
        failures.append(
            ".claude/settings.local.json is tracked; machine-local trust settings must stay "
            "gitignored"
        )
    current = root / "docs" / "CURRENT_STATE.md"
    if current.is_file():
        text = current.read_text(encoding="utf-8")
        if text.count("exact_resume_point:") != 1:
            failures.append("CURRENT_STATE.md must contain exactly one exact_resume_point")
        if "live git and ci outrank this file" not in text.lower():
            failures.append("CURRENT_STATE.md must state the live-evidence precedence rule")
    failures.extend(verify_current_state_yaml(root))
    if (root / "developer_lens_lab_bootstrap_agent_prompt.md").exists():
        failures.append("the commissioning prompt must not become a competing repo authority")
    failures.extend(_verify_tier(root))
    failures.extend(verify_governor(root))
    failures.extend(verify_skill_parity(root))
    failures.extend(verify_agent_friction_parity(root))
    failures.extend(verify_prompt_parity(root))
    failures.extend(verify_context_budget(root))
    failures.extend(verify_markdown_links(root))
    if (root / "tools" / "cards.py").is_file():
        failures.extend(_verify_cards(root))
    failures.extend(check_schemas(root))
    return VerificationReport(tuple(failures))
