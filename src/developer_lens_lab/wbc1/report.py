"""Deterministic, standalone WB-C1 reports."""

from __future__ import annotations

import html
from typing import Any

from developer_lens_lab.contracts import EvaluationBundle


def _bundle_payload(bundle: EvaluationBundle) -> dict[str, Any]:
    return bundle.model_dump(mode="json")


def build_markdown(bundle: EvaluationBundle) -> str:
    """Render a stable Markdown report without paths, timestamps, or external links."""
    payload = _bundle_payload(bundle)
    decision = payload["decision"]
    dataset = payload["dataset_card"]
    preregistration = payload["preregistration"]
    baseline = payload["baseline_results"]
    candidate = payload["candidate_results"]
    calibration = payload["calibration"]
    calibration_metrics = ", ".join(
        f"{metric['metric_code']}={metric.get('value')}" for metric in calibration["metrics"]
    )
    lines = [
        "# WB-C1 benchmark report",
        "",
        f"- Bundle: `{payload['bundle_id']}`",
        f"- Decision: **{decision['outcome']}**",
        f"- Acceptance gate: `{str(decision['acceptance_gate_passed']).lower()}`",
        f"- Primary metric: `{preregistration['primary_metric_code']}`",
        f"- Invented systems: `{dataset['system_count']}`",
        f"- Weekly observations: `{dataset['observation_count']}`",
        "",
        "## Primary results",
        "",
        "| Method | Metrics |",
        "| --- | --- |",
    ]
    for label, result in (("Baseline", baseline), ("Candidate", candidate)):
        metrics = ", ".join(
            f"{metric['domain_code']}:{metric['metric_code']}={metric.get('value')}"
            for metric in result["metrics"]
        )
        lines.append(f"| {label} | {metrics} |")
    lines.extend(
        [
            "",
            "## Calibration and method boundary",
            "",
            f"- Candidate calibration: `{calibration['status']}`",
            f"- Calibration metrics: `{calibration_metrics or 'none'}`",
            "- PELT is an offline descriptive arm; no online delay is attributed to it.",
            "- This C0 invented benchmark can reject a candidate but cannot promote one.",
            "",
            "## Decision reasons",
            "",
            *[f"- `{reason}`" for reason in decision["reason_codes"]],
            "",
        ]
    )
    return "\n".join(lines)


def build_html(bundle: EvaluationBundle) -> str:
    """Render a standalone HTML report with no external assets."""
    markdown = build_markdown(bundle)
    title = html.escape(f"WB-C1 benchmark report - {bundle.bundle_id}")
    body = html.escape(markdown)
    return (
        "<!doctype html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        f"<title>{title}</title></head>\n"
        f"<body><pre>{body}</pre></body></html>\n"
    )
