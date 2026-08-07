from __future__ import annotations

from typing import Any

from developer_lens_lab.wbc1.report import (
    build_method_trial_html,
    build_method_trial_markdown,
)


def _metric(value: float | None, reason: str = "not_measured") -> dict[str, Any]:
    if value is None:
        return {"status": "unavailable", "reason": reason}
    return {"status": "value", "value": value}


def _view() -> dict[str, Any]:
    points: list[dict[str, Any]] = []
    for index in range(52):
        missing = index == 12
        points.append(
            {
                "relative_week_index": index,
                "relative_week_label": f"week-{index:03d}",
                "observed": (
                    {"state": "missing", "reason": "instrumentation_gap"}
                    if missing
                    else {"state": "observed", "value": 10.0 + index / 10}
                ),
                "planted_marker": "level" if index == 25 else "none",
                "confound_marker": "parser_shift" if index == 35 else "none",
                "baseline": {
                    "alert": index in (20, 30),
                    "score": _metric(0.2 + index / 100),
                    "threshold": _metric(0.9),
                },
                "candidate": {
                    "alert": index in (21, 30),
                    "probability": _metric(0.3 + index / 100),
                    "threshold": _metric(0.8),
                },
                "pelt_marker": {
                    "evaluation_mode": "offline_descriptive",
                    "boundary": index == 25,
                },
            }
        )
    cases = [
        {
            "order": order,
            "role": role,
            "scenario_code": scenario,
            "selection_rule": {"code": "fixed_window", "label": "Fixed", "deterministic": True},
            "title": title,
            "summary": summary,
            "points": points,
        }
        for order, (role, scenario, title, summary) in enumerate(
            (
                ("no_change_control", "no_change", "No-change control", "Ordinary variation."),
                ("planted_change", "level", "Planted level change", "Known change boundary."),
                (
                    "instrumentation_confound",
                    "parser_shift",
                    "Instrumentation confound",
                    "Missingness stays visible.",
                ),
            ),
            start=1,
        )
    ]
    return {
        "schema_version": "DeveloperLensMethodTrialView.v1",
        "trial": {
            "trial_id": "trial-synthetic-01",
            "title": "WB-C1 method trial <safe>",
            "question": "Can the candidate reduce false alerts without worsening detection?",
            "classification": "C0",
            "evidence_label": "Invented weekly system series only.",
        },
        "dataset": {
            "system_count": 3,
            "weekly_opportunity_count": 156,
            "observed_count": 150,
            "absent_count": 6,
            "scenario_codes": ["no_change", "level", "parser_shift"],
            "limitations": ["Synthetic only."],
        },
        "methods": {
            "baseline": {
                "role": "baseline",
                "method_code": "rolling_median_mad",
                "display_name": "Rolling median and MAD",
                "description": "Robust baseline.",
                "deterministic": True,
                "parameter_summary": "Fixed cooldown.",
            },
            "candidate": {
                "role": "candidate",
                "method_code": "bocpd_gaussian",
                "display_name": "Gaussian BOCPD",
                "description": "Bayesian candidate.",
                "deterministic": True,
                "parameter_summary": "Fixed prior.",
            },
            "offline_pelt": {
                "role": "offline_descriptive",
                "method_code": "pelt",
                "display_name": "PELT descriptive marker",
                "description": "Offline only.",
                "deterministic": True,
                "parameter_summary": "Fixed penalty.",
            },
        },
        "scorecard": {
            "baseline": {
                "false_alerts_per_year": _metric(2.966666666666667),
                "detection_rate": _metric(1.0),
                "detection_delay_weeks": _metric(None),
                "median_detection_delay_weeks": _metric(None),
                "coverage_confound_false_alert_rate": _metric(None),
                "calibration_brier": _metric(None),
            },
            "candidate": {
                "false_alerts_per_year": _metric(4.2),
                "detection_rate": _metric(1.0),
                "detection_delay_weeks": _metric(None),
                "median_detection_delay_weeks": _metric(None),
                "coverage_confound_false_alert_rate": _metric(None),
                "calibration_brier": _metric(0.2),
            },
            "threshold_selection": {"baseline": {}, "candidate": {}},
        },
        "acceptance_gates": [
            {
                "order": n,
                "code": f"gate-{n}",
                "label": f"Gate {n}",
                "outcome": "pass" if n in (3, 6) else "fail",
                "reason_code": f"G{n}",
                "reason": "Synthetic reason.",
            }
            for n in range(1, 8)
        ],
        "decision": {
            "outcome": "reject",
            "candidate_promoted": False,
            "fallback": {"method_code": "rolling_median_mad", "retained": True},
            "reason_codes": ["G1"],
            "summary": "Candidate rejected.",
            "why_simple_baseline_won": "The baseline has fewer false alerts with equal detection.",
        },
        "representative_cases": cases,
        "representative_selection": {
            "version": "v1",
            "partition": "final_holdout",
            "planted_preference": ["level"],
            "confound_preference": ["parser_shift"],
            "tie_break": "lexical",
            "missing_role_policy": "fail_export",
            "aliases_not_exposed": True,
        },
        "claims": {
            "supported": [{"code": "same_detection_on_c0", "display_text": "Detection matches."}],
            "unsupported": [{"code": "model_promotion", "display_text": "No model promotion."}],
            "limitations": [{"code": "c0_synthetic_only", "display_text": "Synthetic only."}],
        },
        "deferred_caveats": [
            {"code": f"caveat_{n}", "display_text": f"Deferred issue-6 caveat {n}."}
            for n in range(1, 7)
        ],
        "reproducibility": {
            "product_contract_commit": "3ac919f" * 6 + "3ac9",
            "product_research_pack_commit": "4" * 40,
            "lab_commit": "5" * 40,
            "run_id": "run-synthetic-01",
            "recipe_code": "wbc1-smoke-c0-v1",
            "digests": {
                "schema": "sha256:" + "a" * 64,
                "evaluation_bundle": "sha256:" + "b" * 64,
                "custody": "sha256:" + "c" * 64,
                "research_pack": "sha256:" + "d" * 64,
            },
            "commands": {
                "benchmark": "uv run dllab benchmark wb-c1 --smoke",
                "reproduce": "uv run dllab run reproduce run-synthetic-01",
                "export": "uv run dllab export method-trial run-synthetic-01",
                "report": "uv run dllab report build run-synthetic-01",
            },
            "verification": {
                "local": "passed",
                "product_hosted": "not_run",
                "lab_hosted": "not_run",
            },
        },
    }


def test_method_trial_reports_are_deterministic_and_complete() -> None:
    view = _view()
    markdown = build_method_trial_markdown(view)
    html = build_method_trial_html(view)
    assert markdown == build_method_trial_markdown(view)
    assert html == build_method_trial_html(view)
    assert "41.6% more false alerts" in markdown
    assert "41.6% more false alerts" in html
    assert "Seven-gate ladder" in markdown
    assert html.count("<svg ") == 3
    assert html.count('role="img"') == 3
    assert html.count('<title id="timeline-title-') == 3
    assert html.count('<desc id="timeline-desc-') == 3
    assert all(f"Deferred issue-6 caveat {n}." in html for n in range(1, 7))
    assert "offline descriptive" in html
    assert "<pre" not in html
    assert "<script" not in html
    assert "<link" not in html
    assert "http://" not in html and "https://" not in html
    assert "<safe>" not in html
    for marker in ("baseline-alert", "candidate-alert", "planted", "confound", "pelt", "missing"):
        assert marker in html
