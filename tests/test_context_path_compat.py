from __future__ import annotations

import json
from pathlib import Path

import pytest

from developer_lens_lab.context.verify import verify_governor

ROOT = Path(__file__).resolve().parents[1]


def write_pin(root: Path, agent: str) -> str:
    payload = json.loads((ROOT / ".agent-harness/governor.json").read_bytes())
    payload["model_routing"]["implementer"]["agent"] = agent
    path = root / ".agent-harness/governor.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(payload["model_routing"]["implementer"]["model"])


def link(path: Path, target: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.symlink_to(target)
    except OSError:
        pytest.skip("file symlinks are unavailable on this host")


def test_missing_agent_is_a_controlled_resolution_failure(tmp_path: Path) -> None:
    write_pin(tmp_path, ".claude/agents/missing.md")
    failures = verify_governor(tmp_path)
    assert any(
        "model_routing.implementer" in failure and "could not be resolved" in failure
        for failure in failures
    )


def test_internal_agent_symlink_remains_supported(tmp_path: Path) -> None:
    model = write_pin(tmp_path, ".claude/agents/linked.md")
    target = tmp_path / "actual-agent.md"
    target.write_text(f"---\nname: fixture\nmodel: {model}\n---\n", encoding="utf-8")
    link(tmp_path / ".claude/agents/linked.md", target)
    assert not any("model_routing.implementer" in failure for failure in verify_governor(tmp_path))


def test_external_agent_symlink_remains_refused(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    model = write_pin(root, ".claude/agents/linked.md")
    target = tmp_path / "outside-agent.md"
    target.write_text(f"---\nname: fixture\nmodel: {model}\n---\n", encoding="utf-8")
    link(root / ".claude/agents/linked.md", target)
    assert any(
        "model_routing.implementer" in failure and "resolves outside" in failure
        for failure in verify_governor(root)
    )
