"""Report-only merge eligibility evaluation for a single hosted-state snapshot.

The evaluator deliberately has no GitHub or Git side effects.  Callers must provide one
coherent snapshot bound to a single pull request and its head/base pair; missing, paginated,
stale, or malformed surfaces fail closed.
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
# Head/base binding alone cannot separate two pull requests that share the same head and base
# commits, so every pull-request-scoped surface and item must also name the pull request it was
# collected from.  ``checks`` is deliberately absent: GitHub check runs are commit-scoped, not
# pull-request-scoped, so a ``pr_number`` stamped there would be collector-invented evidence rather
# than hosted state.
_PR_SCOPED_SURFACES = frozenset(
    {"formal_reviews", "top_level_comments", "closing_refs", "review_threads"}
)
# GitHub forbids approving your own pull request and every Lab pull request is authored by the
# single owner account, so a formal APPROVED state can never appear here.  The practiced gate is
# instead an accepted, exact-head review: a fresh-context review posted as a top-level comment, or
# a connector review.  The snapshot must therefore name which bound item carries that acceptance.
_ATTESTABLE_SURFACES: dict[str, str] = {
    "formal_reviews": "review_id",
    "top_level_comments": "comment_id",
}
# A closed vocabulary: an absent, non-string or unrecognised review state must never read as
# "not CHANGES_REQUESTED", which is the one way missing evidence could otherwise become a pass.
_REVIEW_STATES = frozenset({"APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED", "PENDING"})
# Identity and head/base binding say the attested review is the right record on the right commits;
# they say nothing about whether it still stands.  Only these two states carry acceptance, so a
# DISMISSED, superseded, or in-flight review can never be the item that opens the gate.
_ACCEPTED_REVIEW_STATES = frozenset({"APPROVED", "COMMENTED"})


@dataclass(frozen=True)
class MergeEligibilityReport:
    """Serialisable result of evaluating one snapshot."""

    eligible: bool
    reasons: tuple[str, ...]
    age_minutes: float | None
    snapshot_age_minutes: float | None
    required_age_minutes: int
    expected_head_sha: str | None
    expected_base_sha: str | None
    # A serialised report must name the pull request it evaluated, or two reports from head/base
    # twins are indistinguishable once separated from their snapshots.  This is a carried field
    # only: it is ``None`` exactly when the identity was unusable, which
    # ``invalid_pull_request_number`` has already refused.
    pull_request_number: int | None

    def as_dict(self) -> dict[str, object]:
        """Return a stable report suitable for a log or JSON response."""

        return {
            "eligible": self.eligible,
            "reasons": list(self.reasons),
            "age_minutes": self.age_minutes,
            "snapshot_age_minutes": self.snapshot_age_minutes,
            "required_age_minutes": self.required_age_minutes,
            "expected_head_sha": self.expected_head_sha,
            "expected_base_sha": self.expected_base_sha,
            "pull_request_number": self.pull_request_number,
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


def _pr_number(value: object) -> int | None:
    # ``bool`` is an ``int`` subclass, and GitHub numbers pull requests from one upward, so a
    # boolean or a non-positive number is a degenerate placeholder rather than an identity.
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None
    return value


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


def _identifier(value: object) -> int | str | None:
    # ``bool`` is an ``int`` subclass; a boolean is never a GitHub identifier.  Zero, a negative
    # number, and a blank string are sentinels rather than identities, and a sentinel that survived
    # here would match itself: an item whose identifier field was absent or empty could be attested
    # by an equally empty attestation, which is exactly the missing-evidence-as-pass shape.
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.strip():
        return value
    return None


def _same_identifier(left: int | str, right: object) -> bool:
    candidate = _identifier(right)
    if candidate is None:
        return False
    return type(candidate) is type(left) and candidate == left


def _bound_to_expected(
    record: Mapping[str, object],
    expected_head: str | None,
    expected_base: str | None,
) -> bool:
    head = _sha(record.get("head_sha"))
    base = _sha(record.get("base_sha"))
    if head is None or expected_head is None or head != expected_head:
        return False
    return base is not None and expected_base is not None and base == expected_base


def _bound_to_pr(record: Mapping[str, object], expected_pr: int | None) -> bool:
    number = _pr_number(record.get("pr_number"))
    if number is None or expected_pr is None:
        return False
    return number == expected_pr


def _cites_head(record: Mapping[str, object], expected_head: str | None) -> bool:
    """Report whether the item's text anchors itself to the expected head SHA."""

    body = _string(record.get("body"))
    if body is None or expected_head is None:
        return False
    return expected_head in body


def _evaluate_accepted_review(
    snapshot: Mapping[str, object],
    surface_items: Mapping[str, list[object]],
    expected_head: str | None,
    expected_base: str | None,
    expected_pr: int | None,
    reasons: list[str],
) -> None:
    """Require one named, exact-head review item to carry the acceptance."""

    attestation = _mapping(snapshot.get("accepted_review"))
    if attestation is None:
        reasons.append("missing_accepted_review")
        return

    surface_name = _string(attestation.get("surface"))
    identifier_field = _ATTESTABLE_SURFACES.get(surface_name) if surface_name is not None else None
    if identifier_field is None:
        reasons.append("invalid_accepted_review_surface")

    identifier = _identifier(attestation.get("id"))
    if identifier is None:
        reasons.append("invalid_accepted_review_id")

    if not _bound_to_expected(attestation, expected_head, expected_base):
        reasons.append("stale_accepted_review")

    if not _bound_to_pr(attestation, expected_pr):
        reasons.append("wrong_accepted_review_pr")

    if identifier_field is None or identifier is None or surface_name is None:
        return

    matches = [
        record
        for item in surface_items.get(surface_name, [])
        if (record := _mapping(item)) is not None
        and _same_identifier(identifier, record.get(identifier_field))
    ]
    if not matches:
        reasons.append("unknown_accepted_review")
        return
    for record in matches:
        if not _bound_to_expected(record, expected_head, expected_base):
            reasons.append("stale_accepted_review")
        # The general review-state loop refuses an objection anywhere on the surface; this refuses
        # an attested item that never carried acceptance in the first place.
        if (
            surface_name == "formal_reviews"
            and _string(record.get("state")) not in _ACCEPTED_REVIEW_STATES
        ):
            reasons.append("unacceptable_accepted_review_state")
        # A top-level comment has no native commit anchor; CONTINUOUS_WORK_PROTOCOL.md records why
        # the attested one must cite the expected head in its own text.
        if surface_name == "top_level_comments" and not _cites_head(record, expected_head):
            reasons.append("unanchored_accepted_review")


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

    # The pull-request number is the snapshot's one immutable identity: head and base SHAs can be
    # shared by two pull requests, and a branch can be reused, but a number is never reissued.
    pull_request = _mapping(snapshot.get("pull_request"))
    expected_pr = _pr_number(pull_request.get("number")) if pull_request is not None else None
    if expected_pr is None:
        reasons.append("invalid_pull_request_number")

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

    # Aging is a property of when the snapshot was COLLECTED, not of when it is evaluated: a
    # snapshot collected minutes after the push cannot mature by being read later.  The same
    # constant bounds how long a collected snapshot stays usable, because the validity window and
    # the aging floor are the same observation quantum.
    collected_at = _parse_timestamp(snapshot.get("collected_at"))
    snapshot_age_minutes: float | None = None
    if collected_at is None:
        reasons.append("invalid_collected_at")
    else:
        snapshot_age = observed_at - collected_at
        snapshot_age_minutes = snapshot_age.total_seconds() / 60
        if snapshot_age < timedelta(0):
            reasons.append("future_collected_at")
        elif snapshot_age_minutes > AGING_MINUTES_AFTER_PUSH:
            reasons.append("stale_snapshot")

    age_minutes: float | None = None
    if pushed_at is None:
        reasons.append("invalid_pushed_at")
    elif collected_at is not None:
        age = collected_at - pushed_at
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
        if name in _PR_SCOPED_SURFACES and not _bound_to_pr(surface, expected_pr):
            reasons.append(f"wrong_surface_pr:{name}")
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
            if name in _PR_SCOPED_SURFACES and not _bound_to_pr(record, expected_pr):
                reasons.append(f"wrong_item_pr:{name}:{index}")

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

    review_states: set[str] = set()
    for index, item in enumerate(surface_items["formal_reviews"]):
        record = _mapping(item)
        state = _string(record.get("state")) if record is not None else None
        if state is None or state not in _REVIEW_STATES:
            reasons.append(f"invalid_review_state:{index}")
            continue
        if state == "PENDING":
            # An in-flight review is an incomplete record, not an absent objection.
            reasons.append(f"pending_formal_review:{index}")
        review_states.add(state)
    if "CHANGES_REQUESTED" in review_states:
        reasons.append("changes_requested")

    _evaluate_accepted_review(
        snapshot, surface_items, expected_head, expected_base, expected_pr, reasons
    )

    # A closing keyword once auto-closed a live programme issue from an unrelated merge, so any
    # closing reference is refused here; an intentional issue-completing merge needs a coordinator
    # override recorded outside this report-only tool.
    for index in range(len(surface_items["closing_refs"])):
        reasons.append(f"closing_reference_present:{index}")

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
        snapshot_age_minutes=snapshot_age_minutes,
        required_age_minutes=AGING_MINUTES_AFTER_PUSH,
        expected_head_sha=expected_head,
        expected_base_sha=expected_base,
        pull_request_number=expected_pr,
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
    except OSError:
        # Do not echo filesystem paths into a report; they are outside the snapshot contract.
        print(json.dumps({"eligible": False, "reasons": ["snapshot_read_failed"]}))
        return 1
    except (ValueError, json.JSONDecodeError):
        print(json.dumps({"eligible": False, "reasons": ["invalid_snapshot"]}))
        return 1
    # An empty ``--now`` is a supplied-but-unusable value, not an omitted one; falling back to the
    # wall clock there would silently relax the observation time the caller asked for.
    observation = _parse_timestamp(args.now) if args.now is not None else None
    if args.now is not None and observation is None:
        print(json.dumps({"eligible": False, "reasons": ["invalid_now"]}))
        return 1
    report = evaluate_merge_eligibility(snapshot, now=observation)
    print(json.dumps(report.as_dict(), sort_keys=True))
    return 0 if report.eligible else 1


if __name__ == "__main__":
    raise SystemExit(main())
