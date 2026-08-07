from __future__ import annotations

import json
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
    if settings.is_file() and "bypassPermissions" in settings.read_text(encoding="utf-8"):
        failures.append(
            "committed .claude/settings.json must not carry bypassPermissions; "
            "it belongs in gitignored .claude/settings.local.json"
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
    failures.extend(verify_markdown_links(root))
    if (root / "tools" / "cards.py").is_file():
        failures.extend(_verify_cards(root))
    failures.extend(check_schemas(root))
    return VerificationReport(tuple(failures))
