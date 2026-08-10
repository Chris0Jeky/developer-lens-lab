"""Report-only merge eligibility evaluation for a single hosted-state snapshot.

The evaluator deliberately has no GitHub or Git side effects.  Callers must provide one
coherent, head/base-bound snapshot; missing, paginated, stale, or malformed surfaces fail
closed.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import cast

REPOSITORY = "Chris0Jeky/developer-lens-lab"
REQUIRED_CHECK_NAME = "Prove the lab"
AGING_MINUTES_AFTER_PUSH = 15
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SURFACES = ("checks", "formal_reviews", "top_level_comments", "closing_refs", "review_threads")


@dataclass(frozen=True)
class MergeEligibilityReport:
    """Serialisable result of evaluating one snapshot."""

    eligible: bool
    reasons: tuple[str, ...]
    age_minutes: float | None
    required_age_minutes: int
    expected_head_sha: str | None
    expected_base_sha: str | None

    def as_dict(self) -> dict[str, object]:
        """Return a stable report suitable for a log or JSON response."""

        return {
            "eligible": self.eligible,
            "reasons": list(self.reasons),
            "age_minutes": self.age_minutes,
            "required_age_minutes": self.required_age_minutes,
            "expected_head_sha": self.expected_head_sha,
            "expected_base_sha": self.expected_base_sha,
        }


def _mapping(value: object) -> Mapping[str, object] | None:
    if not isinstance(value, Mapping):
        return None
    return cast(Mapping[str, object], value)


def _string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _sha(value: object) -> str | None:
    candidate = _string(value)
    return candidate if candidate is not None and _SHA_RE.fullmatch(candidate) else None


def _surface_items(surface: Mapping[str, object], name: str, reasons: list[str]) -> list[object]:
    complete = surface.get("complete")
    paginated = surface.get("paginated")
    stale = surface.get("stale")
    if complete is not True:
        reasons.append(f"incomplete_surface:{name}")
    if paginated is not False:
        reasons.append(f"paginated_surface:{name}")
    if stale is not False:
        reasons.append(f"stale_surface:{name}")
    items = surface.get("items")
    if not isinstance(items, list):
        reasons.append(f"missing_items:{name}")
        return []
    return cast(list[object], items)


def _parse_timestamp(value: object) -> datetime | None:
    raw = _string(value)
    if raw is None or not raw.endswith("Z"):
        return None
    try:
        parsed = datetime.fromisoformat(raw[:-1] + "+00:00")
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(UTC)


def evaluate_merge_eligibility(
    snapshot: Mapping[str, object],
    *,
    now: datetime | None = None,
) -> MergeEligibilityReport:
    """Evaluate a structured snapshot without mutating or contacting any service.

    ``now`` is injectable so synthetic tests and offline reports remain deterministic.  The
    snapshot shape is documented by ``CONTINUOUS_WORK_PROTOCOL.md``.
    """

    reasons: list[str] = []
    expected_head: str | None = None
    expected_base: str | None = None

    if _string(snapshot.get("repository")) != REPOSITORY:
        reasons.append("wrong_repository")

    expected = _mapping(snapshot.get("expected"))
    current = _mapping(snapshot.get("current"))
    if expected is None:
        reasons.append("missing_expected_head_base")
    else:
        expected_head = _sha(expected.get("head_sha"))
        expected_base = _sha(expected.get("base_sha"))
        if expected_head is None:
            reasons.append("invalid_expected_head_sha")
        if expected_base is None:
            reasons.append("invalid_expected_base_sha")
    if current is None:
        reasons.append("missing_current_head_base")
    else:
        current_head = _sha(current.get("head_sha"))
        current_base = _sha(current.get("base_sha"))
        if current_head is None:
            reasons.append("invalid_current_head_sha")
        elif expected_head is not None and current_head != expected_head:
            reasons.append("moved_head")
        if current_base is None:
            reasons.append("invalid_current_base_sha")
        elif expected_base is not None and current_base != expected_base:
            reasons.append("moved_base")

    pushed_at = _parse_timestamp(snapshot.get("pushed_at"))
    pushed_head = _sha(snapshot.get("pushed_head_sha"))
    if pushed_head is None:
        reasons.append("invalid_pushed_head_sha")
    elif expected_head is not None and pushed_head != expected_head:
        reasons.append("stale_pushed_head")
    observed_at = now or datetime.now(UTC)
    if observed_at.tzinfo is None:
        reasons.append("naive_observation_time")
        observed_at = observed_at.replace(tzinfo=UTC)
    observed_at = observed_at.astimezone(UTC)
    age_minutes: float | None = None
    if pushed_at is None:
        reasons.append("invalid_pushed_at")
    else:
        age = observed_at - pushed_at
        age_minutes = age.total_seconds() / 60
        if age < timedelta(0):
            reasons.append("future_pushed_at")
        elif age_minutes < AGING_MINUTES_AFTER_PUSH:
            reasons.append("aging_floor_not_met")

    if _string(snapshot.get("required_check_name")) != REQUIRED_CHECK_NAME:
        reasons.append("wrong_required_check_name")

    surfaces_value = _mapping(snapshot.get("surfaces"))
    if surfaces_value is None:
        reasons.append("missing_surfaces")
        surfaces: Mapping[str, object] = {}
    else:
        surfaces = surfaces_value

    surface_items: dict[str, list[object]] = {}
    for name in _SURFACES:
        surface = _mapping(surfaces.get(name))
        if surface is None:
            reasons.append(f"missing_surface:{name}")
            surface_items[name] = []
            continue
        surface_head = _sha(surface.get("head_sha"))
        surface_base = _sha(surface.get("base_sha"))
        if surface_head is None or expected_head is None or surface_head != expected_head:
            reasons.append(f"stale_surface_head:{name}")
        if surface_base is None or expected_base is None or surface_base != expected_base:
            reasons.append(f"stale_surface_base:{name}")
        surface_items[name] = _surface_items(surface, name, reasons)

    for name, items in surface_items.items():
        for index, item in enumerate(items):
            record = _mapping(item)
            if record is None:
                reasons.append(f"malformed_item:{name}:{index}")
                continue
            item_head = _sha(record.get("head_sha"))
            item_base = _sha(record.get("base_sha"))
            if item_head is None or expected_head is None or item_head != expected_head:
                reasons.append(f"stale_item_head:{name}:{index}")
            if item_base is None or expected_base is None or item_base != expected_base:
                reasons.append(f"stale_item_base:{name}:{index}")

    checks = surface_items["checks"]
    matching_checks: list[Mapping[str, object]] = []
    for item in checks:
        record = _mapping(item)
        if record is not None and _string(record.get("name")) == REQUIRED_CHECK_NAME:
            matching_checks.append(record)
    if len(matching_checks) != 1:
        reasons.append("required_check_missing_or_duplicated")
    else:
        check = matching_checks[0]
        if _string(check.get("status")) != "completed":
            reasons.append("required_check_not_completed")
        if _string(check.get("conclusion")) != "success":
            reasons.append("required_check_not_green")

    reviews = surface_items["formal_reviews"]
    review_states = {
        _string(record.get("state")) for item in reviews if (record := _mapping(item)) is not None
    }
    if "APPROVED" not in review_states:
        reasons.append("formal_approval_missing")
    if "CHANGES_REQUESTED" in review_states:
        reasons.append("changes_requested")

    for index, item in enumerate(surface_items["review_threads"]):
        record = _mapping(item)
        if record is not None and record.get("resolved") is not True:
            reasons.append(f"unresolved_review_thread:{index}")

    # Keep the report deterministic for callers that want to display or compare it.
    unique_reasons = tuple(dict.fromkeys(reasons))
    return MergeEligibilityReport(
        eligible=not unique_reasons,
        reasons=unique_reasons,
        age_minutes=age_minutes,
        required_age_minutes=AGING_MINUTES_AFTER_PUSH,
        expected_head_sha=expected_head,
        expected_base_sha=expected_base,
    )


def _load_snapshot(path: str) -> Mapping[str, object]:
    with open(path, encoding="utf-8") as handle:
        loaded = json.load(handle)
    snapshot = _mapping(loaded)
    if snapshot is None:
        raise ValueError("snapshot must be a JSON object")
    return snapshot


def main(argv: Sequence[str] | None = None) -> int:
    """Print a report and return non-zero when the snapshot is not eligible."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", help="path to one structured JSON snapshot")
    parser.add_argument("--now", help="UTC observation time as an RFC3339 Z timestamp")
    args = parser.parse_args(argv)
    try:
        snapshot = _load_snapshot(args.snapshot)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(json.dumps({"eligible": False, "reasons": [f"invalid_snapshot:{error}"]}))
        return 1
    observation = _parse_timestamp(args.now) if args.now else None
    if args.now and observation is None:
        print(json.dumps({"eligible": False, "reasons": ["invalid_now"]}))
        return 1
    report = evaluate_merge_eligibility(snapshot, now=observation)
    print(json.dumps(report.as_dict(), sort_keys=True))
    return 0 if report.eligible else 1


if __name__ == "__main__":
    raise SystemExit(main())
