from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from typing import cast

from tools.merge_eligibility import evaluate_merge_eligibility

HEAD = "a" * 40
BASE = "b" * 40
PUSHED_AT = "2026-08-10T12:00:00Z"
NOW = datetime(2026, 8, 10, 12, 15, tzinfo=UTC)


def _surface(items: list[dict[str, object]]) -> dict[str, object]:
    return {
        "complete": True,
        "paginated": False,
        "stale": False,
        "head_sha": HEAD,
        "base_sha": BASE,
        "items": items,
    }


def _snapshot() -> dict[str, object]:
    bound = {"head_sha": HEAD, "base_sha": BASE}
    return {
        "repository": "Chris0Jeky/developer-lens-lab",
        "expected": {"head_sha": HEAD, "base_sha": BASE},
        "current": {"head_sha": HEAD, "base_sha": BASE},
        "pushed_head_sha": HEAD,
        "pushed_at": PUSHED_AT,
        "required_check_name": "Prove the lab",
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
                        "state": "APPROVED",
                    }
                ]
            ),
            "top_level_comments": _surface(
                [
                    {
                        **bound,
                        "comment_id": 101,
                    }
                ]
            ),
            "closing_refs": _surface(
                [
                    {
                        **bound,
                        "ref": "issue-29",
                    }
                ]
            ),
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


def test_one_coherent_snapshot_passes_after_aging_floor() -> None:
    report = evaluate_merge_eligibility(_snapshot(), now=NOW)

    assert report.eligible
    assert report.reasons == ()
    assert report.age_minutes == 15
    assert report.required_age_minutes == 15


def test_green_proof_before_fifteen_minutes_is_rejected() -> None:
    early = datetime(2026, 8, 10, 12, 14, 59, tzinfo=UTC)

    report = evaluate_merge_eligibility(_snapshot(), now=early)

    assert not report.eligible
    assert "aging_floor_not_met" in report.reasons


def test_moved_head_is_rejected_even_when_surfaces_are_green() -> None:
    snapshot = _snapshot()
    current = cast(dict[str, object], snapshot["current"])
    current["head_sha"] = "c" * 40

    assert "moved_head" in _reasons(snapshot)


def test_push_timestamp_must_belong_to_expected_head() -> None:
    snapshot = _snapshot()
    snapshot["pushed_head_sha"] = "c" * 40

    assert "stale_pushed_head" in _reasons(snapshot)


def test_unresolved_thread_is_rejected() -> None:
    snapshot = _snapshot()
    surfaces = cast(dict[str, object], snapshot["surfaces"])
    threads = cast(dict[str, object], surfaces["review_threads"])
    items = cast(list[dict[str, object]], threads["items"])
    items[0]["resolved"] = False

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


def test_exact_required_check_name_and_formal_review_are_required() -> None:
    snapshot = deepcopy(_snapshot())
    snapshot["required_check_name"] = "check"
    surfaces = cast(dict[str, object], snapshot["surfaces"])
    checks = cast(dict[str, object], surfaces["checks"])
    check_items = cast(list[dict[str, object]], checks["items"])
    check_items[0]["name"] = "check"
    review_surface = cast(dict[str, object], surfaces["formal_reviews"])
    review_items = cast(list[dict[str, object]], review_surface["items"])
    review_items[0]["state"] = "CHANGES_REQUESTED"

    reasons = _reasons(snapshot)

    assert "wrong_required_check_name" in reasons
    assert "required_check_missing_or_duplicated" in reasons
    assert "formal_approval_missing" in reasons
    assert "changes_requested" in reasons
