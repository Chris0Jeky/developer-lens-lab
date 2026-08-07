"""Deterministic, standalone WB-C1 reports."""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportArgumentType=false

# The rich standalone renderer intentionally keeps CSS/SVG fragments readable as
# stable literals; these lines are not executable logic and exceed the project
# line length by design.
# ruff: noqa: E501, RUF001

from __future__ import annotations

import html
import math
from collections.abc import Mapping, Sequence
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


# The MethodTrial view is intentionally rendered from a plain mapping.  Keeping this
# adapter free of a pydantic import means the report can be opened from a copied JSON
# artifact as well as from the exporter.
def _view_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _metric_value(metric: Any) -> float | None:
    if not isinstance(metric, Mapping) or metric.get("status") != "measured":
        return None
    value = metric.get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _fmt_number(value: Any, digits: int = 2) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "unavailable"
    number = float(value)
    if not math.isfinite(number):
        return "unavailable"
    return f"{number:.{digits}f}".rstrip("0").rstrip(".")


def _fmt_metric(metric: Any, digits: int = 2) -> str:
    value = _metric_value(metric)
    if value is not None:
        return _fmt_number(value, digits)
    if isinstance(metric, Mapping):
        return _view_text(metric.get("reason"), "unavailable")
    return "unavailable"


def _false_alert_delta(view: Mapping[str, Any]) -> str:
    scorecard = view.get("scorecard", {})
    baseline = scorecard.get("baseline", {}) if isinstance(scorecard, Mapping) else {}
    candidate = scorecard.get("candidate", {}) if isinstance(scorecard, Mapping) else {}
    before = (
        _metric_value(baseline.get("false_alerts_per_year"))
        if isinstance(baseline, Mapping)
        else None
    )
    after = (
        _metric_value(candidate.get("false_alerts_per_year"))
        if isinstance(candidate, Mapping)
        else None
    )
    if before is None or after is None or before == 0:
        return "unavailable"
    return f"{(after - before) / before * 100:.1f}% more false alerts"


def _safe_html(value: Any, default: str = "") -> str:
    return html.escape(_view_text(value, default), quote=True)


def _metric_cell(metric: Any) -> str:
    value = _fmt_metric(metric)
    if isinstance(metric, Mapping) and metric.get("status") != "measured":
        return f'<span class="muted">{_safe_html(value)}</span>'
    return _safe_html(value)


def _svg_timeline(case: Mapping[str, Any], index: int) -> str:
    """Build one accessible, deterministic timeline SVG (no external assets)."""
    points = case.get("points", [])
    if not isinstance(points, Sequence) or isinstance(points, (str, bytes)):
        points = []
    points = list(points)
    width, height = 760, 230
    left, right, top, bottom = 44, 18, 24, 42
    plot_w, plot_h = width - left - right, height - top - bottom
    observed: list[tuple[int, float]] = []
    for n, point in enumerate(points):
        if not isinstance(point, Mapping):
            continue
        datum = point.get("observed")
        if isinstance(datum, Mapping) and datum.get("state") == "observed":
            value = datum.get("value")
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and math.isfinite(float(value))
            ):
                observed.append((n, float(value)))
    values = [value for _, value in observed]
    low = min(values) if values else 0.0
    high = max(values) if values else 1.0
    span = high - low or 1.0
    count = max(len(points), 1)

    def x(n: int) -> float:
        return left + (plot_w * n / max(count - 1, 1))

    def y(value: float) -> float:
        return top + plot_h * (1 - (value - low) / span)

    title = _safe_html(f"{_view_text(case.get('title'), 'Case')} timeline")
    desc = _safe_html(
        f"{_view_text(case.get('summary'), '')} {_view_text(len(points), '0')} points; "
        "missing observations are gaps. Legend: observed signal is a blue line, "
        "baseline alerts are triangles, BOCPD alerts are squares, and vertical or "
        "diamond markers identify planted changes, offline PELT boundaries, and confounds."
    )
    fragments = [
        f'<svg class="timeline" role="img" aria-labelledby="timeline-title-{index} timeline-desc-{index}" viewBox="0 0 {width} {height}">',
        f'<title id="timeline-title-{index}">{title}</title>',
        f'<desc id="timeline-desc-{index}">{desc}</desc>',
        f'<rect class="plot" x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" rx="8"/>',
        f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{width - right}" y2="{top + plot_h}"/>',
        '<text class="axis-label" x="44" y="218">week index →</text>',
        f'<text class="axis-label" x="{left}" y="16">observed signal ({_safe_html(_fmt_number(low))}–{_safe_html(_fmt_number(high))})</text>',
    ]
    # Draw a separate polyline per observed run, preserving visible missing gaps.
    runs: list[list[tuple[int, float]]] = []
    run: list[tuple[int, float]] = []
    observed_by_index = {n: value for n, value in observed}
    for n in range(len(points)):
        if n in observed_by_index:
            run.append((n, observed_by_index[n]))
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    for segment in runs:
        coords = " ".join(f"{x(n):.2f},{y(value):.2f}" for n, value in segment)
        fragments.append(f'<polyline class="signal" points="{coords}"/>')
    for n, point in enumerate(points):
        if not isinstance(point, Mapping):
            continue
        px = x(n)
        observed_data = point.get("observed")
        if isinstance(observed_data, Mapping) and observed_data.get("state") == "missing":
            fragments.append(
                f'<line class="missing" x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{top + plot_h}"/>'
            )
            fragments.append(
                f'<text class="missing-label" x="{px:.2f}" y="{top + 12}" text-anchor="middle">×</text>'
            )
        baseline = point.get("baseline")
        if isinstance(baseline, Mapping) and baseline.get("alert") is True:
            observed_value = (
                observed_data.get("value")
                if isinstance(observed_data, Mapping) and observed_data.get("state") == "observed"
                else None
            )
            signal_y = (
                y(float(observed_value))
                if isinstance(observed_value, (int, float))
                and not isinstance(observed_value, bool)
                and math.isfinite(float(observed_value))
                else top + 12
            )
            marker_y = min(max(signal_y - 7, top + 6), top + plot_h - 6)
            fragments.append(
                f'<path class="baseline-alert" d="M {px - 5:.2f} {marker_y + 5:.2f} L {px:.2f} {marker_y - 5:.2f} L {px + 5:.2f} {marker_y + 5:.2f} Z"/>'
            )
        candidate = point.get("candidate")
        if isinstance(candidate, Mapping) and candidate.get("alert") is True:
            observed_value = (
                observed_data.get("value")
                if isinstance(observed_data, Mapping) and observed_data.get("state") == "observed"
                else None
            )
            signal_y = (
                y(float(observed_value))
                if isinstance(observed_value, (int, float))
                and not isinstance(observed_value, bool)
                and math.isfinite(float(observed_value))
                else top + 26
            )
            marker_y = min(max(signal_y + 7, top + 5), top + plot_h - 5)
            fragments.append(
                f'<rect class="candidate-alert" x="{px - 4:.2f}" y="{marker_y - 4:.2f}" width="8" height="8"/>'
            )
        if _view_text(point.get("planted_marker"), "none") != "none":
            fragments.append(
                f'<line class="planted" x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{top + plot_h}"/>'
            )
        if _view_text(point.get("confound_marker"), "none") != "none":
            fragments.append(
                f'<path class="confound" d="M {px:.2f} {top + 8:.2f} l 6 6 l -6 6 l -6 -6 Z"/>'
            )
        pelt = point.get("pelt_marker")
        if isinstance(pelt, Mapping) and pelt.get("boundary") is True:
            fragments.append(
                f'<line class="pelt" x1="{px:.2f}" y1="{top}" x2="{px:.2f}" y2="{top + plot_h}"/>'
            )
    fragments.extend(
        [
            '<g class="legend" role="group" aria-label="Timeline legend">',
            '<line class="signal" x1="510" y1="190" x2="540" y2="190"/><text x="546" y="194">observed signal</text>',
            '<path class="baseline-alert" d="M 510 208 l 5 -10 l 5 10 Z"/><text x="522" y="212">baseline alert (triangle)</text>',
            '<rect class="candidate-alert" x="650" y="200" width="9" height="9"/><text x="665" y="208">BOCPD alert (square)</text>',
            '<text class="legend-note" x="510" y="226">◆ confound · │ planted · ⋮ PELT offline descriptive · × missing</text>',
            "</g></svg>",
        ]
    )
    return "".join(fragments)


def build_method_trial_markdown(view: Mapping[str, Any]) -> str:
    """Render the pinned MethodTrial view as deterministic, portable Markdown."""
    trial = view.get("trial", {})
    dataset = view.get("dataset", {})
    methods = view.get("methods", {})
    scorecard = view.get("scorecard", {})
    decision = view.get("decision", {})
    lines = [
        f"# {_view_text(trial.get('title'), 'Method trial')}",
        "",
        f"**{_view_text(trial.get('classification'), 'C0')} · {_view_text(decision.get('outcome'), 'unknown').upper()}** — {_view_text(trial.get('evidence_label'))}",
        "",
        "## Question and design",
        "",
        _view_text(trial.get("question")),
        "",
        f"{_view_text(dataset.get('system_count'), 0)} systems · {_view_text(dataset.get('weekly_opportunity_count'), 0)} weekly opportunities · {_view_text(dataset.get('observed_count'), 0)} observed / {_view_text(dataset.get('absent_count'), 0)} absent.",
        "",
        "## Method cards",
        "",
    ]
    for key in ("baseline", "candidate", "offline_pelt"):
        method = methods.get(key, {}) if isinstance(methods, Mapping) else {}
        lines.extend(
            [
                f"### {_view_text(method.get('display_name'), key)}",
                "",
                _view_text(method.get("description")),
                f"Parameters: {_view_text(method.get('parameter_summary'))}",
                "",
            ]
        )
    lines.extend(
        [
            "## Paired canonical scorecard",
            "",
            "| Metric | Baseline | Gaussian BOCPD |",
            "| --- | ---: | ---: |",
        ]
    )
    for key, label in (
        ("false_alerts_per_year", "False alerts / year"),
        ("detection_rate", "Detection rate"),
        ("median_detection_delay_weeks", "Median delay (weeks)"),
        ("coverage_confound_false_alert_rate", "Confound false-alert rate"),
        ("calibration_brier", "Calibration Brier"),
    ):
        b = (
            scorecard.get("baseline", {}).get(key)
            if isinstance(scorecard.get("baseline"), Mapping)
            else None
        )
        c = (
            scorecard.get("candidate", {}).get(key)
            if isinstance(scorecard.get("candidate"), Mapping)
            else None
        )
        lines.append(f"| {label} | {_fmt_metric(b)} | {_fmt_metric(c)} |")
    lines.extend(["", f"**({_false_alert_delta(view)})**", "", "## Seven-gate ladder", ""])
    for gate in sorted(
        view.get("acceptance_gates", []),
        key=lambda item: item.get("order", 0) if isinstance(item, Mapping) else 0,
    ):
        if isinstance(gate, Mapping):
            lines.append(
                f"{gate.get('order', '?')}. **{_view_text(gate.get('label'))}** — {_view_text(gate.get('outcome')).replace('_', ' ')}. {_view_text(gate.get('reason'))}"
            )
    lines.extend(
        [
            "",
            "## Why the baseline won",
            "",
            _view_text(decision.get("why_simple_baseline_won")),
            "",
            "## Representative timelines",
            "",
        ]
    )
    for case in sorted(
        view.get("representative_cases", []),
        key=lambda item: item.get("order", 0) if isinstance(item, Mapping) else 0,
    )[:3]:
        if isinstance(case, Mapping):
            lines.extend(
                [f"### {_view_text(case.get('title'))}", "", _view_text(case.get("summary")), ""]
            )
    claims = view.get("claims", {})
    for key, heading in (
        ("supported", "Supported claims"),
        ("unsupported", "Unsupported claims"),
        ("limitations", "Limitations"),
    ):
        lines.extend([f"## {heading}", ""])
        for claim in claims.get(key, []) if isinstance(claims, Mapping) else []:
            if isinstance(claim, Mapping):
                lines.append(f"- {_view_text(claim.get('display_text'))}")
        lines.append("")
    lines.extend(["## Deferred issue-6 caveats", ""])
    for caveat in view.get("deferred_caveats", []):
        if isinstance(caveat, Mapping):
            lines.append(f"- {_view_text(caveat.get('display_text'))}")
    repro = view.get("reproducibility", {})
    lines.extend(
        [
            "",
            "## Reproducibility",
            "",
            f"Product contract: `{_view_text(repro.get('product_contract_commit'))}` · Research pack: `{_view_text(repro.get('product_research_pack_commit'))}` · Lab: `{_view_text(repro.get('lab_commit'))}` · Run: `{_view_text(repro.get('run_id'))}`",
            "",
            f"Recipe: `{_view_text(repro.get('recipe_code'))}`",
        ]
    )
    if isinstance(repro.get("commands"), Mapping):
        lines.extend(
            [
                "",
                *[
                    f"- `{_view_text(repro['commands'][name])}`"
                    for name in sorted(repro["commands"])
                ],
            ]
        )
    if isinstance(repro.get("digests"), Mapping):
        lines.extend(
            [
                "",
                "Source digests:",
                *[
                    f"- `{_view_text(name)}`: `{_view_text(repro['digests'][name])}`"
                    for name in sorted(repro["digests"])
                ],
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def build_method_trial_html(view: Mapping[str, Any]) -> str:
    """Render a rich standalone MethodTrial story using only inline CSS/SVG."""
    trial = view.get("trial", {})
    dataset = view.get("dataset", {})
    methods = view.get("methods", {})
    scorecard = view.get("scorecard", {})
    decision = view.get("decision", {})
    outcome = _view_text(decision.get("outcome"), "unknown")
    cards: list[str] = []
    for key in ("baseline", "candidate", "offline_pelt"):
        method = methods.get(key, {}) if isinstance(methods, Mapping) else {}
        cards.append(
            f'<article class="method-card"><p class="eyebrow">{_safe_html(method.get("role"), key)}</p><h3>{_safe_html(method.get("display_name"), key)}</h3><p>{_safe_html(method.get("description"))}</p><p class="muted">{_safe_html(method.get("parameter_summary"))}</p></article>'
        )
    score_rows: list[str] = []
    metric_labels = (
        ("false_alerts_per_year", "False alerts / year"),
        ("detection_rate", "Detection rate"),
        ("median_detection_delay_weeks", "Median delay (weeks)"),
        ("coverage_confound_false_alert_rate", "Confound false-alert rate"),
        ("calibration_brier", "Calibration Brier"),
    )
    for key, label in metric_labels:
        b = (
            scorecard.get("baseline", {}).get(key)
            if isinstance(scorecard.get("baseline"), Mapping)
            else None
        )
        c = (
            scorecard.get("candidate", {}).get(key)
            if isinstance(scorecard.get("candidate"), Mapping)
            else None
        )
        score_rows.append(
            f'<tr><th scope="row">{_safe_html(label)}</th><td>{_metric_cell(b)}</td><td>{_metric_cell(c)}</td></tr>'
        )
    gates: list[str] = []
    for gate in sorted(
        view.get("acceptance_gates", []),
        key=lambda item: item.get("order", 0) if isinstance(item, Mapping) else 0,
    ):
        if isinstance(gate, Mapping):
            state = _view_text(gate.get("outcome"), "unknown")
            gates.append(
                f'<li class="gate gate-{_safe_html(state)}"><span class="gate-number">{_safe_html(gate.get("order"))}</span><div><strong>{_safe_html(gate.get("label"))}</strong><p>{_safe_html(gate.get("reason"))}</p></div><span class="gate-state">{_safe_html(state.replace("_", " "))}</span></li>'
            )
    case_sections: list[str] = []
    for n, case in enumerate(
        sorted(
            view.get("representative_cases", []),
            key=lambda item: item.get("order", 0) if isinstance(item, Mapping) else 0,
        )[:3],
        start=1,
    ):
        if isinstance(case, Mapping):
            case_sections.append(
                f'<article class="case"><div class="case-heading"><div><p class="eyebrow">Case {n} · {_safe_html(case.get("scenario_code"))}</p><h3>{_safe_html(case.get("title"))}</h3><p>{_safe_html(case.get("summary"))}</p></div><span class="chip">{_safe_html(len(case.get("points", [])))} points</span></div>{_svg_timeline(case, n)}</article>'
            )

    def claim_list(key: str) -> str:
        claims = (
            view.get("claims", {}).get(key, []) if isinstance(view.get("claims"), Mapping) else []
        )
        return "".join(
            f"<li>{_safe_html(item.get('display_text'))}</li>"
            for item in claims
            if isinstance(item, Mapping)
        )

    repro = view.get("reproducibility", {})
    commands = (
        "".join(
            f"<li><code>{_safe_html(repro['commands'][name])}</code></li>"
            for name in sorted(repro.get("commands", {}))
        )
        if isinstance(repro.get("commands"), Mapping)
        else ""
    )
    digests = (
        "".join(
            f"<li><span>{_safe_html(name)}</span><code>{_safe_html(repro['digests'][name])}</code></li>"
            for name in sorted(repro.get("digests", {}))
        )
        if isinstance(repro.get("digests"), Mapping)
        else ""
    )
    caveats = "".join(
        f"<li>{_safe_html(item.get('display_text'))}</li>"
        for item in view.get("deferred_caveats", [])
        if isinstance(item, Mapping)
    )
    css = """
    :root{color-scheme:light;--ink:#172033;--muted:#64708a;--line:#dbe2ef;--paper:#f6f8fc;--card:#fff;--accent:#3567e8;--green:#16794d;--red:#bb3b4c;--gold:#a86b00}
    *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}main{max-width:1120px;margin:0 auto;padding:44px 28px 70px}h1,h2,h3,p{margin-top:0}h1{font-size:clamp(2rem,4vw,3.4rem);line-height:1.05;letter-spacing:-.04em;margin-bottom:16px}h2{font-size:1.45rem;margin:46px 0 14px}h3{margin-bottom:8px}.hero{padding:34px;border:1px solid var(--line);border-radius:22px;background:linear-gradient(135deg,#fff 0%,#edf3ff 100%);box-shadow:0 12px 32px #24345a12}.badge{display:inline-flex;gap:9px;align-items:center;border-radius:99px;padding:6px 12px;background:#172033;color:white;font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}.verdict{color:var(--red)}.muted{color:var(--muted)}.eyebrow{font-size:.75rem;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;font-weight:700;margin-bottom:7px}.lede{font-size:1.14rem;max-width:820px}.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}.method-card,.case,.panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;box-shadow:0 5px 14px #24345a0a}.method-card{min-height:180px}.method-card:first-child{border-top:4px solid var(--green)}.method-card:nth-child(2){border-top:4px solid var(--accent)}.method-card:nth-child(3){border-top:4px solid var(--gold)}.callout{display:inline-block;margin-top:14px;padding:10px 14px;border-radius:10px;background:#fff2df;color:#7d4a00;font-weight:700}.scorecard{overflow:auto}.scorecard table{width:100%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden}.scorecard th,.scorecard td{padding:12px 14px;border-bottom:1px solid var(--line);text-align:right}.scorecard th:first-child{text-align:left}.scorecard thead{background:#eef3ff}.scorecard tbody tr:last-child>*{border-bottom:0}.gate-ladder{list-style:none;padding:0;display:grid;gap:9px}.gate{display:grid;grid-template-columns:34px 1fr auto;gap:12px;align-items:center;padding:11px 14px;border:1px solid var(--line);border-radius:11px;background:var(--card)}.gate-number{display:grid;place-items:center;width:27px;height:27px;border-radius:50%;background:#e7edff;color:#254eb5;font-weight:800}.gate p{margin:3px 0 0;color:var(--muted);font-size:.9rem}.gate-state{font-size:.75rem;font-weight:800;text-transform:uppercase;letter-spacing:.05em}.gate-fail{border-left:4px solid var(--red)}.gate-pass{border-left:4px solid var(--green)}.gate-not_applicable{border-left:4px solid var(--gold)}.case{padding:0;overflow:hidden}.case-heading{padding:20px;display:flex;justify-content:space-between;gap:20px}.chip{height:max-content;border:1px solid var(--line);border-radius:99px;padding:5px 10px;color:var(--muted);font-size:.8rem;white-space:nowrap}.timeline{display:block;width:100%;min-height:230px;background:#fbfcff;border-top:1px solid var(--line)}.plot{fill:#f7f9fe;stroke:#dce4f2}.axis{stroke:#9ba8bd}.axis-label,.missing-label,.legend text{font:11px system-ui,sans-serif;fill:#53617a}.signal{fill:none;stroke:#3567e8;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}.missing{stroke:#c4ccda;stroke-width:1;stroke-dasharray:2 4}.missing-label{fill:#9ba8bd;font-weight:800}.baseline-alert{fill:#bb3b4c;stroke:#7d2330;stroke-width:1}.candidate-alert{fill:#f2a32b;stroke:#81520b;stroke-width:1}.planted{stroke:#16794d;stroke-width:2;stroke-dasharray:6 4}.confound{fill:#8b5cf6;stroke:#5731a5;stroke-width:1}.pelt{stroke:#172033;stroke-width:1.5;stroke-dasharray:1 5}.legend-note{font-size:10px!important}.columns{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}.list{margin:0;padding-left:20px}.list li{margin:6px 0}.repro{display:grid;gap:8px}.repro ul{list-style:none;padding:0;margin:0}.repro li{display:flex;justify-content:space-between;gap:15px;padding:7px 0;border-bottom:1px solid var(--line);overflow-wrap:anywhere}.repro code{font:12px/1.4 ui-monospace,SFMono-Regular,Consolas,monospace;color:#35425a}footer{margin-top:46px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);padding-top:16px}
    """
    return (
        """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>"""
        + _safe_html(trial.get("title"), "Method trial")
        + """</title><style>"""
        + css
        + """</style></head><body><main>
<section class="hero"><span class="badge"><span class="verdict">●</span>"""
        + _safe_html(trial.get("classification"), "C0")
        + """ · """
        + _safe_html(outcome.upper())
        + """</span><h1>"""
        + _safe_html(trial.get("title"), "Method trial")
        + """</h1><p class="lede">"""
        + _safe_html(trial.get("evidence_label"))
        + """</p><p><strong>Question:</strong> """
        + _safe_html(trial.get("question"))
        + """</p><span class="callout">"""
        + _safe_html(_false_alert_delta(view))
        + """ · baseline retained</span></section>
<h2>Design at a glance</h2><section class="panel"><p>"""
        + _safe_html(trial.get("question"))
        + """</p><p class="muted">"""
        + _safe_html(dataset.get("system_count"), "0")
        + """ systems · """
        + _safe_html(dataset.get("weekly_opportunity_count"), "0")
        + """ weekly opportunities · """
        + _safe_html(dataset.get("observed_count"), "0")
        + """ observed / """
        + _safe_html(dataset.get("absent_count"), "0")
        + """ absent. Evidence stays C0 and invented.</p></section>
<h2>Method cards</h2><section class="grid">"""
        + "".join(cards)
        + """</section>
<h2>Paired canonical scorecard</h2><section class="scorecard"><table><thead><tr><th scope="col">Metric</th><th scope="col">Rolling median + MAD</th><th scope="col">Gaussian BOCPD</th></tr></thead><tbody>"""
        + "".join(score_rows)
        + """</tbody></table></section>
<h2>Seven-gate ladder</h2><ol class="gate-ladder">"""
        + "".join(gates)
        + """</ol>
<h2>Why the baseline won</h2><section class="panel"><p>"""
        + _safe_html(decision.get("why_simple_baseline_won"))
        + """</p><p class="muted">"""
        + _safe_html(decision.get("summary"))
        + """</p></section>
<h2>Representative timelines</h2><section class="grid">"""
        + "".join(case_sections)
        + """</section>
<h2>Claims and boundaries</h2><section class="columns"><article class="panel"><h3>Supported</h3><ul class="list">"""
        + claim_list("supported")
        + """</ul></article><article class="panel"><h3>Unsupported</h3><ul class="list">"""
        + claim_list("unsupported")
        + """</ul></article><article class="panel"><h3>Limitations</h3><ul class="list">"""
        + claim_list("limitations")
        + """</ul></article></section>
<h2>Deferred issue-6 caveats</h2><section class="panel"><ol class="list">"""
        + caveats
        + """</ol></section>
<h2>Reproducibility</h2><section class="panel repro"><p><strong>Commits</strong>: <code>"""
        + _safe_html(repro.get("product_contract_commit"))
        + """</code> · <code>"""
        + _safe_html(repro.get("product_research_pack_commit"))
        + """</code> · <code>"""
        + _safe_html(repro.get("lab_commit"))
        + """</code></p><p><strong>Run</strong>: <code>"""
        + _safe_html(repro.get("run_id"))
        + """</code> · recipe <code>"""
        + _safe_html(repro.get("recipe_code"))
        + """</code></p><h3>Commands</h3><ul>"""
        + commands
        + """</ul><h3>Source digests</h3><ul>"""
        + digests
        + """</ul></section>
<footer>Deterministic synthetic research evidence; no model promotion or product authority.</footer></main></body></html>
"""
    )
