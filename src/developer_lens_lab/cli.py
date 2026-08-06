from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated

import typer

from developer_lens_lab.context import verify_repository

app = typer.Typer(help="Developer Lens Lab command line.", no_args_is_help=True)
context_app = typer.Typer(help="Verify repository authority and generated context.")
tasks_app = typer.Typer(help="Check or render the generated task programme.")
app.add_typer(context_app, name="context")
app.add_typer(tasks_app, name="tasks")


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
