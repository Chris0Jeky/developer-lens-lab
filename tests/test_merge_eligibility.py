from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from tools.merge_eligibility import AGING_MINUTES_AFTER_PUSH, evaluate_merge_eligibility

HEAD = "a" * 40
BASE = "b" * 40
OTHER = "c" * 40
PUSHED_AT = "2026-08-10T12:00:00Z"
COLLECTED_AT = "2026-08-10T12:15:00Z"
NOW = datetime(2026, 8, 10, 12, 15, tzinfo=UTC)
PULL_REQUEST_NUMBER = 68
REVIEW_ID = 501
COMMENT_ID = 101


def _bound() -> dict[str, object]:
    return {"head_sha": HEAD, "base_sha": BASE}


def _surface(items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "complete": True,
        "paginated": False,
        "stale": False,
        "head_sha": HEAD,
        "base_sha": BASE,
        "pull_request_number": PULL_REQUEST_NUMBER,
        "items": items,
    }


def _snapshot() -> dict[str, object]:
    bound = _bound()
    return {
        "repository": "Chris0Jeky/developer-lens-lab",
        "pull_request_number": PULL_REQUEST_NUMBER,
        "expected": {"head_sha": HEAD, "base_sha": BASE},
        "current": {"head_sha": HEAD, "base_sha": BASE},
        "pushed_head_sha": HEAD,
        "pushed_at": PUSHED_AT,
        "collected_at": COLLECTED_AT,
        "required_check_name": "Prove the lab",
        "accepted_review": {
            **bound,
            "surface": "formal_reviews",
            "id": REVIEW_ID,
        },
        "surfaces": {
            "checks": _surface(
                [
                    {
                        **bound,
                        "name": "Prove the lab",
                        "status": "completed",
                        "conclusion": "success",
                    }
                ]
            ),
            "formal_reviews": _surface(
                [
                    {
                        **bound,
                        "review_id": REVIEW_ID,
                        "state": "APPROVED",
                    }
                ]
            ),
            "top_level_comments": _surface(
                [
                    {
                        **bound,
                        "comment_id": COMMENT_ID,
                    }
                ]
            ),
            "closing_refs": _surface([]),
            "review_threads": _surface(
                [
                    {
                        **bound,
                        "thread_id": "thread-1",
                        "resolved": True,
                    }
                ]
            ),
        },
    }


def _reasons(snapshot: dict[str, object]) -> tuple[str, ...]:
    report = evaluate_merge_eligibility(snapshot, now=NOW)
    return report.reasons


def _attestation(snapshot: dict[str, object]) -> dict[str, object]:
    return cast(dict[str, object], snapshot["accepted_review"])


def _items(snapshot: dict[str, object], surface: str) -> list[dict[str, object]]:
    surfaces = cast(dict[str, object], snapshot["surfaces"])
    named = cast(dict[str, object], surfaces[surface])
    return cast(list[dict[str, object]], named["items"])


def test_one_coherent_snapshot_passes_after_aging_floor() -> None:
    report = evaluate_merge_eligibility(_snapshot(), now=NOW)

    assert report.eligible
    assert report.reasons == ()
    assert report.age_minutes == 15
    assert report.required_age_minutes == 15


def test_green_proof_collected_before_fifteen_minutes_is_rejected() -> None:
    snapshot = _snapshot()
    snapshot["collected_at"] = "2026-08-10T12:14:59Z"

    report = evaluate_merge_eligibility(snapshot, now=NOW)

    assert not report.eligible
    assert "aging_floor_not_met" in report.reasons


def test_an_early_snapshot_cannot_ripen_by_being_evaluated_later() -> None:
    snapshot = _snapshot()
    snapshot["collected_at"] = "2026-08-10T12:05:00Z"
    later = datetime(2026, 8, 10, 12, 20, tzinfo=UTC)

    report = evaluate_merge_eligibility(snapshot, now=later)

    assert not report.eligible
    assert "aging_floor_not_met" in report.reasons
    assert report.age_minutes == 5


def test_missing_or_malformed_collected_at_fails_closed() -> None:
    missing = _snapshot()
    del missing["collected_at"]
    malformed = _snapshot()
    malformed["collected_at"] = "2026-08-10T12:15:00+00:00"

    assert "invalid_collected_at" in _reasons(missing)
    assert "invalid_collected_at" in _reasons(malformed)


def test_collection_after_the_observation_instant_is_refused() -> None:
    snapshot = _snapshot()
    snapshot["collected_at"] = "2026-08-10T12:16:00Z"

    assert _reasons(snapshot) == ("future_collected_at",)


def test_collection_before_the_push_is_refused() -> None:
    snapshot = _snapshot()
    snapshot["pushed_at"] = "2026-08-10T12:30:00Z"

    assert "future_pushed_at" in _reasons(snapshot)


def test_missing_pull_request_number_fails_closed() -> None:
    snapshot = _snapshot()
    del snapshot["pull_request_number"]

    reasons = _reasons(snapshot)

    assert "invalid_pull_request_number" in reasons
    assert "stale_surface_pull_request:checks" in reasons


def test_boolean_pull_request_number_is_not_an_identifier() -> None:
    snapshot = _snapshot()
    snapshot["pull_request_number"] = True

    assert "invalid_pull_request_number" in _reasons(snapshot)


def test_surface_from_another_pull_request_is_refused() -> None:
    snapshot = _snapshot()
    surfaces = cast(dict[str, object], snapshot["surfaces"])
    reviews = cast(dict[str, object], surfaces["formal_reviews"])
    reviews["pull_request_number"] = PULL_REQUEST_NUMBER + 1

    assert _reasons(snapshot) == ("stale_surface_pull_request:formal_reviews",)


def test_aging_floor_matches_the_governor_policy() -> None:
    # The only I/O in this module: tracked, invented-safe governor config, read so the duplicated
    # floor cannot drift away from the policy it claims to enforce.
    governor = Path(__file__).resolve().parents[1] / ".agent-harness" / "governor.json"
    with governor.open(encoding="utf-8") as handle:
        payload: object = json.load(handle)
    gates = cast(dict[str, object], cast(dict[str, object], payload)["review_gates"])

    assert AGING_MINUTES_AFTER_PUSH == gates["aging_minutes_after_push"]


def test_moved_head_is_rejected_even_when_surfaces_are_green() -> None:
    snapshot = _snapshot()
    current = cast(dict[str, object], snapshot["current"])
    current["head_sha"] = OTHER

    assert "moved_head" in _reasons(snapshot)


def test_push_timestamp_must_belong_to_expected_head() -> None:
    snapshot = _snapshot()
    snapshot["pushed_head_sha"] = OTHER

    assert "stale_pushed_head" in _reasons(snapshot)


def test_unresolved_thread_is_rejected() -> None:
    snapshot = _snapshot()
    _items(snapshot, "review_threads")[0]["resolved"] = False

    assert "unresolved_review_thread:0" in _reasons(snapshot)


def test_missing_paginated_and_stale_surfaces_fail_closed() -> None:
    snapshot = _snapshot()
    surfaces = cast(dict[str, object], snapshot["surfaces"])
    del surfaces["top_level_comments"]
    checks = cast(dict[str, object], surfaces["checks"])
    checks["paginated"] = True
    reviews = cast(dict[str, object], surfaces["formal_reviews"])
    reviews["stale"] = True

    reasons = _reasons(snapshot)

    assert "missing_surface:top_level_comments" in reasons
    assert "paginated_surface:checks" in reasons
    assert "stale_surface:formal_reviews" in reasons


def test_exact_required_check_name_is_required() -> None:
    snapshot = deepcopy(_snapshot())
    snapshot["required_check_name"] = "check"
    _items(snapshot, "checks")[0]["name"] = "check"

    reasons = _reasons(snapshot)

    assert "wrong_required_check_name" in reasons
    assert "required_check_missing_or_duplicated" in reasons


def test_changes_requested_is_refused_despite_a_valid_attestation() -> None:
    snapshot = _snapshot()
    _items(snapshot, "formal_reviews")[0]["state"] = "CHANGES_REQUESTED"

    assert _reasons(snapshot) == ("changes_requested",)


def test_unrecognised_formal_review_states_fail_closed() -> None:
    snapshot = _snapshot()
    reviews = _items(snapshot, "formal_reviews")
    del reviews[0]["state"]
    reviews.append({**_bound(), "review_id": REVIEW_ID + 1, "state": "PENDING"})

    reasons = _reasons(snapshot)

    assert "invalid_review_state:0" in reasons
    assert "invalid_review_state:1" in reasons
    assert "changes_requested" not in reasons


def test_missing_attestation_is_refused() -> None:
    snapshot = _snapshot()
    del snapshot["accepted_review"]

    assert _reasons(snapshot) == ("missing_accepted_review",)


def test_attestation_naming_an_absent_item_is_refused() -> None:
    snapshot = _snapshot()
    _attestation(snapshot)["id"] = 999

    assert _reasons(snapshot) == ("unknown_accepted_review",)


def test_attestation_bound_to_another_head_is_refused() -> None:
    snapshot = _snapshot()
    _attestation(snapshot)["head_sha"] = OTHER

    assert _reasons(snapshot) == ("stale_accepted_review",)


def test_attestation_matching_a_misbound_item_is_refused() -> None:
    snapshot = _snapshot()
    _items(snapshot, "formal_reviews")[0]["base_sha"] = OTHER

    reasons = _reasons(snapshot)

    assert "stale_item_base:formal_reviews:0" in reasons
    assert "stale_accepted_review" in reasons


def test_unattestable_surface_and_identifier_are_refused() -> None:
    snapshot = _snapshot()
    attestation = _attestation(snapshot)
    attestation["surface"] = "review_threads"
    attestation["id"] = None

    reasons = _reasons(snapshot)

    assert "invalid_accepted_review_surface" in reasons
    assert "invalid_accepted_review_id" in reasons
    assert "unknown_accepted_review" not in reasons


def test_top_level_comment_review_satisfies_the_gate() -> None:
    snapshot = _snapshot()
    attestation = _attestation(snapshot)
    attestation["surface"] = "top_level_comments"
    attestation["id"] = COMMENT_ID
    # No formal review exists at all: the single-account repository cannot produce one.
    _items(snapshot, "formal_reviews").clear()

    report = evaluate_merge_eligibility(snapshot, now=NOW)

    assert report.eligible
    assert report.reasons == ()


def test_closing_reference_is_refused() -> None:
    snapshot = _snapshot()
    _items(snapshot, "closing_refs").append({"head_sha": HEAD, "base_sha": BASE, "ref": "issue-29"})

    assert _reasons(snapshot) == ("closing_reference_present:0",)
