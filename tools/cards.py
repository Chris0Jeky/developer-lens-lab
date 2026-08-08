from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Card:
    id: str
    title: str
    status: str
    depends_on: tuple[str, ...] = ()
    outcome: str = ""


CARDS = (
    Card(
        "LAB-OS-01",
        "Repository OS and context verifier",
        "DONE",
        outcome="Fresh-agent resume",
    ),
    Card(
        "LAB-TOOL-01",
        "Python, uv, tooling, and CI",
        "DONE",
        ("LAB-OS-01",),
        "Locked checks",
    ),
    Card(
        "LAB-CONTRACT-01",
        "ResearchPack.v1 contracts",
        "DONE",
        ("LAB-OS-01",),
        "Pack validation",
    ),
    Card(
        "LAB-CONTRACT-02",
        "EvaluationBundle.v1 contracts",
        "DONE",
        ("LAB-OS-01",),
        "Decision bundle validation",
    ),
    Card(
        "LAB-ART-01",
        "Confined content-addressed artifact store",
        "DONE",
        ("LAB-TOOL-01",),
        "Replayable objects",
    ),
    Card(
        "LAB-WBC1-01",
        "Invented weekly-series smoke benchmark",
        "DONE",
        ("LAB-CONTRACT-01", "LAB-ART-01"),
        "Inspectible rejection decision",
    ),
    Card(
        "LAB-SYNC-01",
        "Generated product-contract snapshot",
        "DONE",
        ("LAB-CONTRACT-01",),
        "Pinned provenance",
    ),
    Card(
        "LAB-RUN-01",
        "Reproducible run manifest and replay",
        "DONE",
        ("LAB-ART-01",),
        "One-command replay",
    ),
    Card(
        "LAB-SPLIT-01",
        "Repository, time, and seed-family split engine",
        "DONE",
        ("LAB-CONTRACT-01",),
        "Leakage-safe splits",
    ),
    Card(
        "LAB-HOLDOUT-01",
        "Explicit final-holdout custody",
        "DONE",
        ("LAB-SPLIT-01",),
        "Single-use holdout",
    ),
    Card(
        "LAB-WBC1-02",
        "Rolling median and MAD baseline",
        "DONE",
        ("LAB-WBC1-01",),
        "Deterministic fallback",
    ),
    Card(
        "LAB-WBC1-03",
        "Online change-point candidate",
        "DONE",
        ("LAB-WBC1-02",),
        "Baseline comparison",
    ),
    Card(
        "LAB-WBC1-04",
        "PELT offline descriptive arm",
        "DONE",
        ("LAB-WBC1-02",),
        "Localisation evidence",
    ),
    Card(
        "LAB-WBC1-05",
        "Evaluation bundle and decision report",
        "DONE",
        ("LAB-WBC1-03",),
        "Reviewable result",
    ),
    Card(
        "LAB-WBC1-06",
        "WB-C1 late-review correctness debt (issue #6)",
        "DONE",
        ("LAB-WBC1-05",),
        "Reproducer-backed fixes",
    ),
    Card(
        "LAB-BRIDGE-01",
        "Product and lab compatibility fixture",
        "DONE",
        ("LAB-SYNC-01",),
        "Both-end proof",
    ),
    Card(
        "LAB-DEMO-01",
        "End-to-end smoke demo and runbook",
        "DONE",
        ("LAB-WBC1-05",),
        "Fresh-clone proof",
    ),
    Card(
        "LAB-CORPUS-01",
        "Public-repository sampler manifest",
        "BACKLOG",
        ("LAB-ACT-01",),
        "Quality pilot only",
    ),
    Card(
        "LAB-CORPUS-02",
        "Bounded public metadata collector",
        "BACKLOG",
        ("LAB-CORPUS-01", "LAB-ACT-01"),
        "No raw landing",
    ),
    Card(
        "LAB-CORPUS-03",
        "Normalizer and coverage profiler",
        "BACKLOG",
        ("LAB-CORPUS-02", "LAB-ACT-01"),
        "Explicit coverage",
    ),
    Card(
        "LAB-DQ-01",
        "Data-quality and candidate-support report",
        "PARKED",
        ("LAB-CORPUS-03",),
        "Expansion decision",
    ),
    Card(
        "LAB-GOV-01",
        "Research governor control plane",
        "DONE",
        ("LAB-OS-01",),
        "Governor seeded",
    ),
    Card(
        "LAB-ACT-01",
        "Real-data activation preconditions (tier flip, executable sinks and deny rules, "
        "secret scanning)",
        "BACKLOG",
        ("LAB-GOV-01",),
        "Non-C0 lanes unlocked",
    ),
    Card(
        "LAB-REL-01",
        "v0.1.0 release wave: AGPL and notices, community files, package metadata, "
        "dependency triage (issue #5), C0 release assets",
        "ACTIVE",
        ("LAB-GOV-01",),
        "Tagged v0.1.0",
    ),
    Card(
        "LAB-SURV-01",
        "Integration-tail survival study (product issue #174): KM + AFT over the product "
        "input contract",
        "BACKLOG",
        ("LAB-BRIDGE-01", "LAB-WBC1-06"),
        "Product-owned view + rich report",
    ),
    Card(
        "LAB-CONTRACT-03",
        "MethodTrialView representative-preference reconcile (issue #23; product-owned "
        "schema change)",
        "BACKLOG",
        ("LAB-BRIDGE-01",),
        "Contract-faithful preference declaration",
    ),
)

# ACTIVE and IN_REVIEW prerequisites deliberately permit speculative stacked work. They do not
# mean the prerequisite is complete or allow dependent work to merge ahead of it.
STACKABLE_DEPENDENCY_STATUSES = {"ACTIVE", "IN_REVIEW", "DONE"}

# The governor (constitution v2) runs an unbounded opportunity backlog behind the active wave, so
# there is no fixed active-horizon cap. Status is still a closed vocabulary: BACKLOG is authorized
# opportunity-backlog work not yet promoted into the wave; OWNER_GATED and PARKED remain explicit
# holds; ACTIVE/IN_REVIEW are the wave; DONE is landed.
ALLOWED_STATUSES = {"DONE", "ACTIVE", "IN_REVIEW", "BACKLOG", "OWNER_GATED", "PARKED"}


def _validate(cards: tuple[Card, ...] = CARDS) -> None:
    by_id = {card.id: card for card in cards}
    if len(by_id) != len(cards):
        raise ValueError("duplicate card ID")
    for card in cards:
        if card.status not in ALLOWED_STATUSES:
            raise ValueError(f"{card.id} has unknown status: {card.status}")
    horizon = {card.id for card in cards if card.status in {"ACTIVE", "IN_REVIEW"}}
    for card in cards:
        unknown = set(card.depends_on) - set(by_id)
        if unknown:
            raise ValueError(f"{card.id} has unknown dependencies: {sorted(unknown)}")
        if card.id in horizon:
            inactive_dependencies = {
                dependency
                for dependency in card.depends_on
                if by_id[dependency].status not in STACKABLE_DEPENDENCY_STATUSES
            }
            if inactive_dependencies:
                raise ValueError(
                    f"{card.id} active horizon is not dependency-closed: "
                    f"{sorted(inactive_dependencies)}"
                )


def _json_text() -> str:
    payload = {
        "schema_version": "lab-task-programme.v2",
        "active_limit": None,
        "cards": [{**asdict(card), "depends_on": list(card.depends_on)} for card in CARDS],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _markdown_text() -> str:
    lines = [
        "# Generated task-card index",
        "",
        "Generated from `tools/cards.py`; do not edit by hand.",
        "",
        "| Card | Title | Status | Depends on | Outcome |",
        "|---|---|---|---|---|",
    ]
    for card in CARDS:
        dependencies = ", ".join(card.depends_on) or "—"
        lines.append(
            f"| `{card.id}` | {card.title} | {card.status} | {dependencies} | {card.outcome} |"
        )
    return "\n".join(lines) + "\n"


def outputs(root: Path) -> dict[Path, str]:
    return {
        root / "generated" / "task-cards.json": _json_text(),
        root / "docs" / "CARD_INDEX.md": _markdown_text(),
    }


def render(root: Path) -> None:
    _validate()
    for path, content in outputs(root).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"rendered {path.relative_to(root)}")


def check(root: Path) -> int:
    _validate()
    failures: list[str] = []
    for path, expected in outputs(root).items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(root)}")
        elif path.read_text(encoding="utf-8") != expected:
            failures.append(f"drifted {path.relative_to(root)}")
    for failure in failures:
        print(f"ERROR: {failure}")
    if not failures:
        print("task programme is current and dependency-closed")
        return 0
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--render", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.render:
        render(root)
        return 0
    return check(root)


if __name__ == "__main__":
    raise SystemExit(main())
