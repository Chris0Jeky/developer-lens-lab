from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from developer_lens_lab.wbc1.export import compose_method_trial_view

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "bundle",
    "baseline",
    "candidate",
    "pelt",
    "custody",
    "research_pack",
    "research_pack_coverage",
    "research_pack_repository_week",
)


@pytest.mark.parametrize("smoke", [False, None, 1, "true"], ids=["full", "absent", "int", "str"])
def test_method_trial_view_refuses_non_smoke_runs_before_projection(
    tmp_path: Path, smoke: object
) -> None:
    # The view pins the smoke recipe and a --smoke command; anything else is false provenance.
    manifest: dict[str, Any] = {field: {} for field in REQUIRED}
    if smoke is not None:
        manifest["smoke"] = smoke

    with pytest.raises(ValueError, match="smoke runs only"):
        compose_method_trial_view("run_full", root=ROOT, artifact_root=tmp_path, manifest=manifest)
