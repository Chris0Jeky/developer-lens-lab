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
        "IN_REVIEW",
        outcome="Fresh-agent resume",
    ),
    Card(
        "LAB-TOOL-01",
        "Python, uv, tooling, and CI",
        "IN_REVIEW",
        ("LAB-OS-01",),
        "Locked checks",
    ),
    Card(
        "LAB-CONTRACT-01", "ResearchPack.v1 contracts", "ACTIVE", ("LAB-OS-01",), "Pack validation"
    ),
    Card(
        "LAB-CONTRACT-02",
        "EvaluationBundle.v1 contracts",
        "ACTIVE",
        ("LAB-OS-01",),
        "Decision bundle validation",
    ),
    Card(
        "LAB-ART-01",
        "Confined content-addressed artifact store",
        "ACTIVE",
        ("LAB-TOOL-01",),
        "Replayable objects",
    ),
    Card(
        "LAB-WBC1-01",
        "Invented weekly-series smoke benchmark",
        "ACTIVE",
        ("LAB-CONTRACT-01", "LAB-ART-01"),
        "Inspectible rejection decision",
    ),
    Card(
        "LAB-SYNC-01",
        "Generated product-contract snapshot",
        "QUEUED",
        ("LAB-CONTRACT-01",),
        "Pinned provenance",
    ),
    Card(
        "LAB-RUN-01",
        "Reproducible run manifest and replay",
        "QUEUED",
        ("LAB-ART-01",),
        "One-command replay",
    ),
    Card(
        "LAB-SPLIT-01",
        "Repository, time, and seed-family split engine",
        "QUEUED",
        ("LAB-CONTRACT-01",),
        "Leakage-safe splits",
    ),
    Card(
        "LAB-HOLDOUT-01",
        "Explicit final-holdout custody",
        "QUEUED",
        ("LAB-SPLIT-01",),
        "Single-use holdout",
    ),
    Card(
        "LAB-WBC1-02",
        "Rolling median and MAD baseline",
        "QUEUED",
        ("LAB-WBC1-01",),
        "Deterministic fallback",
    ),
    Card(
        "LAB-WBC1-03",
        "Online change-point candidate",
        "QUEUED",
        ("LAB-WBC1-02",),
        "Baseline comparison",
    ),
    Card(
        "LAB-WBC1-04",
        "PELT offline descriptive arm",
        "QUEUED",
        ("LAB-WBC1-02",),
        "Localisation evidence",
    ),
    Card(
        "LAB-WBC1-05",
        "Evaluation bundle and decision report",
        "QUEUED",
        ("LAB-WBC1-03",),
        "Reviewable result",
    ),
    Card(
        "LAB-BRIDGE-01",
        "Product and lab compatibility fixture",
        "QUEUED",
        ("LAB-SYNC-01",),
        "Both-end proof",
    ),
    Card(
        "LAB-DEMO-01",
        "End-to-end smoke demo and runbook",
        "QUEUED",
        ("LAB-WBC1-05",),
        "Fresh-clone proof",
    ),
    Card(
        "LAB-CORPUS-01",
        "Public-repository sampler manifest",
        "OWNER_GATED",
        outcome="Quality pilot only",
    ),
    Card(
        "LAB-CORPUS-02",
        "Bounded public metadata collector",
        "OWNER_GATED",
        ("LAB-CORPUS-01",),
        "No raw landing",
    ),
    Card(
        "LAB-CORPUS-03",
        "Normalizer and coverage profiler",
        "OWNER_GATED",
        ("LAB-CORPUS-02",),
        "Explicit coverage",
    ),
    Card(
        "LAB-DQ-01",
        "Data-quality and candidate-support report",
        "PARKED",
        ("LAB-CORPUS-03",),
        "Expansion decision",
    ),
)


def _validate() -> None:
    by_id = {card.id: card for card in CARDS}
    if len(by_id) != len(CARDS):
        raise ValueError("duplicate card ID")
    horizon = {card.id for card in CARDS if card.status in {"ACTIVE", "IN_REVIEW"}}
    if len(horizon) > 6:
        raise ValueError("active horizon exceeds six cards")
    for card in CARDS:
        unknown = set(card.depends_on) - set(by_id)
        if unknown:
            raise ValueError(f"{card.id} has unknown dependencies: {sorted(unknown)}")
        if card.id in horizon:
            inactive_dependencies = {
                dependency
                for dependency in card.depends_on
                if by_id[dependency].status not in {"ACTIVE", "IN_REVIEW", "DONE"}
            }
            if inactive_dependencies:
                raise ValueError(
                    f"{card.id} active horizon is not dependency-closed: "
                    f"{sorted(inactive_dependencies)}"
                )


def _json_text() -> str:
    payload = {
        "schema_version": "lab-task-programme.v1",
        "active_limit": 6,
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
