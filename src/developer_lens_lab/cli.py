from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from developer_lens_lab.artifacts import ArtifactError, ArtifactStore
from developer_lens_lab.context import verify_repository
from developer_lens_lab.contract_sync import (
    ContractSyncError,
    sync_method_trial_view_contract,
    sync_product_contract,
)
from developer_lens_lab.schemas import check_schemas, render_schemas
from developer_lens_lab.validation import (
    ManifestError,
    explain_validation_error,
    profile_research_pack,
    validate_evaluation_bundle,
    validate_pack_artifacts,
    validate_research_pack,
)
from developer_lens_lab.wbc1.export import export_method_trial
from developer_lens_lab.wbc1.runner import RunnerError, build_report, reproduce_run, run_benchmark

app = typer.Typer(help="Developer Lens Lab command line.", no_args_is_help=True)
context_app = typer.Typer(help="Verify repository authority and generated context.")
tasks_app = typer.Typer(help="Check or render the generated task programme.")
contracts_app = typer.Typer(help="Synchronize and verify versioned interchange contracts.")
pack_app = typer.Typer(help="Validate or profile a ResearchPack.")
bundle_app = typer.Typer(help="Validate an EvaluationBundle.")
benchmark_app = typer.Typer(help="Run deterministic synthetic benchmarks.")
run_app = typer.Typer(help="Reproduce recorded benchmark runs.")
report_app = typer.Typer(help="Build deterministic benchmark reports.")
export_app = typer.Typer(help="Export product-owned presentation views.")
demo_app = typer.Typer(help="Materialize deterministic demo presentation artifacts.")
app.add_typer(context_app, name="context")
app.add_typer(tasks_app, name="tasks")
app.add_typer(contracts_app, name="contracts")
app.add_typer(pack_app, name="pack")
app.add_typer(bundle_app, name="bundle")
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(run_app, name="run")
app.add_typer(report_app, name="report")
app.add_typer(export_app, name="export")
app.add_typer(demo_app, name="demo")


def _repo_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise typer.BadParameter("run from inside a developer-lens-lab checkout")


@app.command()
def doctor(as_json: Annotated[bool, typer.Option("--json")] = False) -> None:
    """Report prerequisites without creating or changing them."""
    root = _repo_root()
    report = verify_repository(root)
    payload = {
        "ok": report.ok,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "repo": root.name,
        "artifact_root": ".dllab (absent until an explicit command writes an artifact)",
        "network_collection": "disabled",
        "failures": list(report.failures),
    }
    if as_json:
        typer.echo(json.dumps(payload, sort_keys=True))
    else:
        typer.echo("Developer Lens Lab doctor")
        typer.echo(f"context: {'ok' if report.ok else 'failed'}")
        typer.echo(f"Python: {payload['python']}")
        typer.echo(str(payload["artifact_root"]))
        typer.echo("network collection: disabled")
        for failure in report.failures:
            typer.echo(f"- {failure}")
    if not report.ok:
        raise typer.Exit(code=1)


@context_app.command("verify")
def context_verify() -> None:
    """Fail when authority files, links, or generated context drift."""
    report = verify_repository(_repo_root())
    if report.ok:
        typer.echo("context verification passed")
        return
    for failure in report.failures:
        typer.echo(f"ERROR: {failure}", err=True)
    raise typer.Exit(code=1)


def _run_cards(flag: str) -> None:
    root = _repo_root()
    result = subprocess.run(
        [sys.executable, str(root / "tools" / "cards.py"), flag],
        cwd=root,
        check=False,
    )
    if result.returncode:
        raise typer.Exit(code=result.returncode)


@tasks_app.command("check")
def tasks_check() -> None:
    """Check generated task artifacts and active-horizon invariants."""
    _run_cards("--check")


@tasks_app.command("render")
def tasks_render() -> None:
    """Render task artifacts from the single Python source."""
    _run_cards("--render")


@contracts_app.command("render")
def contracts_render() -> None:
    """Render deterministic lab-owned and consumer-mirror JSON Schemas."""
    render_schemas(_repo_root())
    typer.echo("rendered contract schemas")


@contracts_app.command("check")
def contracts_check() -> None:
    """Fail when generated contract schemas drift from strict models."""
    failures = check_schemas(_repo_root())
    if failures:
        for failure in failures:
            typer.echo(f"ERROR: {failure}", err=True)
        raise typer.Exit(code=1)
    typer.echo("generated contract schemas are current")


@contracts_app.command("sync")
def contracts_sync(
    source: Annotated[
        Path,
        typer.Option("--from", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ],
    ref: Annotated[str, typer.Option("--ref")],
) -> None:
    """Copy the pinned producer schema and invented fixture from Developer Lens Git objects."""
    try:
        provenance = sync_product_contract(_repo_root(), source, ref)
    except (ContractSyncError, ValidationError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: contract sync failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"synchronized {provenance.relative_to(_repo_root())}")


@contracts_app.command("sync-method-trial")
def contracts_sync_method_trial(
    source: Annotated[
        Path,
        typer.Option("--from", exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    ],
    ref: Annotated[str, typer.Option("--ref")],
    check_only: Annotated[bool, typer.Option("--check-only")] = False,
) -> None:
    """Pin the product-owned MethodTrialView schema snapshot."""
    try:
        provenance = sync_method_trial_view_contract(
            _repo_root(), source, ref, check_only=check_only
        )
    except (ContractSyncError, OSError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: MethodTrialView sync failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    action = "verified" if check_only else "synchronized"
    typer.echo(f"{action} {provenance.relative_to(_repo_root())}")


@pack_app.command("validate")
def pack_validate(
    manifest: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)],
    artifact_root: Annotated[Path | None, typer.Option("--artifact-root")] = None,
) -> None:
    """Validate a C0 ResearchPack and optionally verify its scoped Parquet objects."""
    try:
        pack = validate_research_pack(manifest)
        if artifact_root is not None:
            validate_pack_artifacts(pack, ArtifactStore(artifact_root))
    except (ArtifactError, ManifestError, OSError, ValidationError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: {explain_validation_error(exc)}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"valid {pack.schema_version} {pack.pack_id}")


@pack_app.command("profile")
def pack_profile(
    manifest: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)],
) -> None:
    """Report relation states without coercing unavailable evidence to zero."""
    try:
        profile = profile_research_pack(validate_research_pack(manifest))
    except (ManifestError, OSError, ValidationError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: {explain_validation_error(exc)}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps(profile, sort_keys=True))


@bundle_app.command("validate")
def bundle_validate(
    manifest: Annotated[Path, typer.Argument(exists=True, file_okay=True, dir_okay=False)],
) -> None:
    """Validate a path-free EvaluationBundle decision record."""
    try:
        bundle = validate_evaluation_bundle(manifest)
    except (ManifestError, OSError, ValidationError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: {explain_validation_error(exc)}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"valid {bundle.schema_version} {bundle.bundle_id}")


@benchmark_app.command("wb-c1")
def benchmark_wb_c1(
    smoke: Annotated[bool, typer.Option("--smoke/--full")] = True,
    run_id: Annotated[str | None, typer.Option("--run-id")] = None,
) -> None:
    """Run the invented WB-C1 benchmark after a producer snapshot is synchronized."""
    try:
        result = run_benchmark(smoke=smoke, run_id=run_id)
    except (RunnerError, ArtifactError, OSError, ValidationError) as exc:
        typer.echo(f"ERROR: WB-C1 benchmark failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"completed {result.run_id}: {result.manifest_path}")


@run_app.command("reproduce")
def run_reproduce(
    run_id_or_manifest: Annotated[str, typer.Argument()],
) -> None:
    """Recompute a run and compare its deterministic bundle bytes."""
    try:
        resolved = Path(run_id_or_manifest)
        if not resolved.is_file():
            resolved = _repo_root() / ".dllab" / "scopes" / run_id_or_manifest / "run.json"
        if not resolved.is_file():
            raise RunnerError(f"run manifest not found: {run_id_or_manifest}")
        matched = reproduce_run(resolved)
    except (RunnerError, ArtifactError, OSError, ValidationError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: reproduction failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    if not matched:
        typer.echo("ERROR: reproduced bundle differs from recorded bytes", err=True)
        raise typer.Exit(code=1)
    typer.echo("reproduction matched deterministic bundle")


@report_app.command("build")
def report_build(
    run_id: Annotated[str, typer.Argument()],
    artifact_root: Annotated[Path | None, typer.Option("--artifact-root")] = None,
) -> None:
    """Build and verify standalone Markdown and HTML reports for a run."""
    try:
        markdown, html_ref = build_report(
            run_id, artifact_root=artifact_root or (_repo_root() / ".dllab")
        )
    except (RunnerError, ArtifactError, OSError, ValidationError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: report build failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"report markdown={markdown.sha256} html={html_ref.sha256}")


@export_app.command("method-trial")
def export_method_trial_command(
    run_id: Annotated[str, typer.Argument()],
    output: Annotated[Path | None, typer.Option("--output")] = None,
) -> None:
    """Export a deterministic MethodTrialView for a validated synthetic run."""
    try:
        result = export_method_trial(run_id, output=output, root=_repo_root())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: MethodTrialView export failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"exported {result.output_path} sha256={result.sha256}")


@demo_app.command("export")
def demo_export_command(
    run_id: Annotated[str, typer.Argument()],
    output: Annotated[Path, typer.Option("--output")],
) -> None:
    """Export the canonical MethodTrialView for a recorded synthetic run."""
    try:
        result = export_method_trial(run_id, output=output, root=_repo_root())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        typer.echo(f"ERROR: demo export failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"exported path={result.output_path} sha256={result.sha256}")
