from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pytest

from tools.merge_eligibility import (
    AGING_MINUTES_AFTER_PUSH,
    evaluate_merge_eligibility,
    main,
)

HEAD = "a" * 40
BASE = "b" * 40
OTHER = "c" * 40
PUSHED_AT = "2026-08-10T12:00:00Z"
COLLECTED_AT = "2026-08-10T12:15:00Z"
NOW = datetime(2026, 8, 10, 12, 15, tzinfo=UTC)
REVIEW_ID = 501
COMMENT_ID = 101
GOVERNOR = Path(__file__).resolve().parents[1] / ".agent-harness" / "governor.json"


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
                        "body": f"Fresh-context review of {HEAD}: no blocking findings.",
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
    assert report.snapshot_age_minutes == 0
    assert report.required_age_minutes == 15


def test_green_proof_before_fifteen_minutes_is_rejected() -> None:
    early = datetime(2026, 8, 10, 12, 14, 59, tzinfo=UTC)
    snapshot = _snapshot()
    snapshot["collected_at"] = "2026-08-10T12:14:59Z"

    report = evaluate_merge_eligibility(snapshot, now=early)

    assert not report.eligible
    assert "aging_floor_not_met" in report.reasons


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
    comment = _attest_the_comment(snapshot)
    # No formal review exists at all: the single-account repository cannot produce one.
    _items(snapshot, "formal_reviews").clear()

    report = evaluate_merge_eligibility(snapshot, now=NOW)

    assert HEAD in cast(str, comment["body"])
    assert report.eligible
    assert report.reasons == ()


def test_closing_reference_is_refused() -> None:
    snapshot = _snapshot()
    _items(snapshot, "closing_refs").append({"head_sha": HEAD, "base_sha": BASE, "ref": "issue-29"})

    assert _reasons(snapshot) == ("closing_reference_present:0",)


def _attest_the_comment(snapshot: dict[str, object]) -> dict[str, object]:
    attestation = _attestation(snapshot)
    attestation["surface"] = "top_level_comments"
    attestation["id"] = COMMENT_ID
    return _items(snapshot, "top_level_comments")[0]


def test_an_attested_comment_without_a_body_is_unanchored() -> None:
    snapshot = _snapshot()
    comment = _attest_the_comment(snapshot)
    del comment["body"]

    assert _reasons(snapshot) == ("unanchored_accepted_review",)


def test_an_attested_comment_citing_another_head_is_unanchored() -> None:
    snapshot = _snapshot()
    comment = _attest_the_comment(snapshot)
    comment["body"] = f"Fresh-context review of {OTHER}: no blocking findings."

    assert _reasons(snapshot) == ("unanchored_accepted_review",)


def test_a_formal_review_attestation_needs_no_body() -> None:
    snapshot = _snapshot()
    review = _items(snapshot, "formal_reviews")[0]

    report = evaluate_merge_eligibility(snapshot, now=NOW)

    assert "body" not in review
    assert report.eligible
    assert report.reasons == ()


def test_missing_review_state_never_reads_as_no_objection() -> None:
    snapshot = _snapshot()
    del _items(snapshot, "formal_reviews")[0]["state"]

    assert _reasons(snapshot) == ("invalid_review_state:0",)


def test_non_string_and_unknown_review_states_are_refused() -> None:
    snapshot = _snapshot()
    reviews = _items(snapshot, "formal_reviews")
    reviews[0]["state"] = 7
    reviews.append({"head_sha": HEAD, "base_sha": BASE, "review_id": 502, "state": "MERGED"})

    reasons = _reasons(snapshot)

    assert "invalid_review_state:0" in reasons
    assert "invalid_review_state:1" in reasons


def test_pending_formal_review_is_an_incomplete_record() -> None:
    snapshot = _snapshot()
    _items(snapshot, "formal_reviews")[0]["state"] = "PENDING"

    assert _reasons(snapshot) == ("pending_formal_review:0",)


def test_collecting_late_does_not_let_a_young_head_mature() -> None:
    # The defeat this binding closes: collect ten minutes after the push, then evaluate the same
    # snapshot later so that evaluation time alone would satisfy the floor.
    snapshot = _snapshot()
    snapshot["collected_at"] = "2026-08-10T12:10:00Z"
    later = datetime(2026, 8, 10, 12, 20, tzinfo=UTC)

    report = evaluate_merge_eligibility(snapshot, now=later)

    assert not report.eligible
    assert "aging_floor_not_met" in report.reasons
    assert report.age_minutes == 10
    assert report.snapshot_age_minutes == 10


def test_a_snapshot_older_than_the_window_is_stale() -> None:
    snapshot = _snapshot()
    snapshot["collected_at"] = "2026-08-10T12:20:00Z"
    later = datetime(2026, 8, 10, 12, 36, tzinfo=UTC)

    report = evaluate_merge_eligibility(snapshot, now=later)

    assert report.reasons == ("stale_snapshot",)
    assert report.age_minutes == 20
    assert report.snapshot_age_minutes == 16


def test_a_snapshot_exactly_at_the_window_edge_is_usable() -> None:
    snapshot = _snapshot()
    edge = datetime(2026, 8, 10, 12, 30, tzinfo=UTC)

    report = evaluate_merge_eligibility(snapshot, now=edge)

    assert report.eligible
    assert report.snapshot_age_minutes == AGING_MINUTES_AFTER_PUSH


def test_missing_and_future_collection_times_are_refused() -> None:
    missing = _snapshot()
    del missing["collected_at"]
    future = _snapshot()
    future["collected_at"] = "2026-08-10T12:16:00Z"

    assert "invalid_collected_at" in _reasons(missing)
    assert "future_collected_at" in _reasons(future)


def test_a_push_after_collection_is_refused() -> None:
    snapshot = _snapshot()
    snapshot["pushed_at"] = "2026-08-10T12:16:00Z"
    snapshot["collected_at"] = "2026-08-10T12:15:00Z"

    assert "future_pushed_at" in _reasons(snapshot)


def test_identifier_matching_is_type_strict() -> None:
    quoted = _snapshot()
    _attestation(quoted)["id"] = "501"
    flipped = _snapshot()
    _items(flipped, "formal_reviews")[0]["review_id"] = "501"

    assert _reasons(quoted) == ("unknown_accepted_review",)
    assert _reasons(flipped) == ("unknown_accepted_review",)


def test_boolean_identifiers_are_never_valid() -> None:
    attested = _snapshot()
    _attestation(attested)["id"] = True
    item = _snapshot()
    _items(item, "formal_reviews")[0]["review_id"] = True

    attested_reasons = _reasons(attested)

    assert "invalid_accepted_review_id" in attested_reasons
    assert "unknown_accepted_review" not in attested_reasons
    assert _reasons(item) == ("unknown_accepted_review",)


def test_governor_aging_floor_matches_the_helper_constant() -> None:
    loaded = cast(dict[str, object], json.loads(GOVERNOR.read_text(encoding="utf-8")))
    gates = cast(dict[str, object], loaded["review_gates"])

    assert gates["aging_minutes_after_push"] == AGING_MINUTES_AFTER_PUSH


def _write(path: Path, payload: object) -> str:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_cli_reports_an_eligible_snapshot_without_failing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write(tmp_path / "snapshot.json", _snapshot())

    exit_code = main([path, "--now", COLLECTED_AT])
    printed = cast(dict[str, object], json.loads(capsys.readouterr().out))

    assert exit_code == 0
    assert printed["eligible"] is True
    assert printed["snapshot_age_minutes"] == 0


def test_cli_fails_on_an_ineligible_snapshot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    snapshot = _snapshot()
    _items(snapshot, "formal_reviews")[0]["state"] = "CHANGES_REQUESTED"
    path = _write(tmp_path / "snapshot.json", snapshot)

    exit_code = main([path, "--now", COLLECTED_AT])
    printed = cast(dict[str, object], json.loads(capsys.readouterr().out))

    assert exit_code == 1
    assert printed["reasons"] == ["changes_requested"]


def test_cli_read_failure_never_echoes_the_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    absent = tmp_path / "does-not-exist.json"

    exit_code = main([str(absent), "--now", COLLECTED_AT])
    out = capsys.readouterr().out

    assert exit_code == 1
    assert json.loads(out)["reasons"] == ["snapshot_read_failed"]
    assert str(absent) not in out
    assert absent.name not in out


def test_cli_rejects_a_non_object_snapshot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = _write(tmp_path / "snapshot.json", ["not", "an", "object"])

    exit_code = main([path, "--now", COLLECTED_AT])

    assert exit_code == 1
    assert json.loads(capsys.readouterr().out)["reasons"] == ["invalid_snapshot"]


@pytest.mark.parametrize("supplied", ["", "not-a-timestamp", "2026-08-10T12:15:00"])
def test_cli_refuses_an_unusable_observation_time(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], supplied: str
) -> None:
    # An empty --now must not fall back to the wall clock: supplied-but-unusable is not omitted.
    path = _write(tmp_path / "snapshot.json", _snapshot())

    exit_code = main([path, "--now", supplied])

    assert exit_code == 1
    assert json.loads(capsys.readouterr().out)["reasons"] == ["invalid_now"]
