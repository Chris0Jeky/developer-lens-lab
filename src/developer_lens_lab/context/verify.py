from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from developer_lens_lab.schemas import check_schemas

REQUIRED_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".agent-harness/tier.json",
    ".agent-harness/governor.json",
    "docs/OWNER_CONSTITUTION.md",
    "docs/agent-system/README.md",
    "docs/agent-system/WORK_CLASSES.md",
    "docs/agent-system/EXPERIMENT_PROTOCOL.md",
    "docs/agent-system/DATASET_PROTOCOL.md",
    "docs/agent-system/MAINTENANCE_PROTOCOL.md",
    "docs/agent-system/IDEA_PROTOCOL.md",
    "docs/agent-system/PROMPT_LIBRARY.md",
    ".claude/agents/dll-implementer.md",
    ".claude/agents/dll-mechanic.md",
    ".claude/agents/dll-reviewer.md",
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
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "artifacts",
    "htmlcov",
    "site",
}


@dataclass(frozen=True)
class VerificationReport:
    failures: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.failures


def verify_markdown_links(root: Path) -> list[str]:
    failures: list[str] = []
    for path in sorted(root.rglob("*.md")):
        relative_parts = path.relative_to(root).parts
        if any(part in SKIPPED_MARKDOWN_PARTS for part in relative_parts):
            continue
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
GOVERNOR_REQUIRED_FOCUS = (
    "research",
    "story_product",
    "distribution",
    "community",
    "realdata_standalone",
)
GOVERNOR_PIN_ROLES = ("implementer", "reviewer", "mechanic")


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


def _verify_governor_pins(routing: dict[str, object], root: Path) -> list[str]:
    failures: list[str] = []
    for role in GOVERNOR_PIN_ROLES:
        role_raw = routing.get(role)
        if not isinstance(role_raw, dict):
            continue
        role_cfg = cast(dict[str, object], role_raw)
        agent_rel = role_cfg.get("agent")
        model = role_cfg.get("model")
        if not isinstance(agent_rel, str) or not isinstance(model, str):
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
            if not isinstance(target, str) or not (root / target).is_file():
                failures.append(
                    f"governor.json authority {name!r} must point at an existing repo file"
                )
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
    missing_focus = [axis for axis in GOVERNOR_REQUIRED_FOCUS if axis not in focus]
    if missing_focus:
        failures.append(f"governor.json focus is missing required axes: {missing_focus}")
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
SHARED_SKILL_MARKERS = ("shared:evaluation-integrity", "shared:protected-data-defaults")
SKILL_PARITY_FILES = (
    ".claude/skills/developer-lens-lab-continuation/SKILL.md",
    ".agents/skills/developer-lens-lab-continuation/SKILL.md",
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
    if (root / "developer_lens_lab_bootstrap_agent_prompt.md").exists():
        failures.append("the commissioning prompt must not become a competing repo authority")
    failures.extend(_verify_tier(root))
    failures.extend(verify_governor(root))
    failures.extend(verify_skill_parity(root))
    failures.extend(verify_context_budget(root))
    failures.extend(verify_markdown_links(root))
    if (root / "tools" / "cards.py").is_file():
        failures.extend(_verify_cards(root))
    failures.extend(check_schemas(root))
    return VerificationReport(tuple(failures))
