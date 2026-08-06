# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.contracts import ArtifactRef, ResearchPack
from developer_lens_lab.wbc1.generator import build_benchmark_dataset
from developer_lens_lab.wbc1.runner import (
    RunnerError,
    build_report,
    reproduce_run,
    run_benchmark,
)

ROOT = Path(__file__).resolve().parents[1]


def _permit_test_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    def permit(_root: Path) -> None:
        return None

    def fixed_commit(_root: Path) -> str:
        return "a" * 40

    monkeypatch.setattr("developer_lens_lab.wbc1.runner._ensure_reproducible_tree", permit)
    monkeypatch.setattr("developer_lens_lab.wbc1.runner._git_commit", fixed_commit)


def _manifest(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_smoke_run_materializes_complete_pack_and_reproduces(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="wbc1_test")
    manifest = _manifest(result.manifest_path)
    store = ArtifactStore(tmp_path)

    pack_ref = ArtifactRef.model_validate(manifest["research_pack"])
    pack = ResearchPack.model_validate_json(store.get_bytes(result.scope, pack_ref))
    coverage_ref = ArtifactRef.model_validate(manifest["research_pack_coverage"])
    repository_week_ref = ArtifactRef.model_validate(manifest["research_pack_repository_week"])
    coverage = pq.ParquetFile(pa.BufferReader(store.get_bytes(result.scope, coverage_ref)))
    repository_week = pq.ParquetFile(
        pa.BufferReader(store.get_bytes(result.scope, repository_week_ref))
    )

    dataset = build_benchmark_dataset(smoke=True)
    holdout = dataset.open_final_holdout()
    all_series = dataset.train.series + dataset.test.series + holdout.series
    expected_rows = sum(int(series.observed.sum()) for series in all_series)

    assert pack.relations.coverage.state == "present"
    assert pack.relations.repository_week.state == "present"
    assert coverage.metadata.num_rows == len(all_series) == 54
    assert repository_week.metadata.num_rows == expected_rows
    assert pack.relations.repository_week.row_count == expected_rows
    assert pack.feature_registry[0].feature_id == "DL.WEEK.SYSTEM_SIGNAL_INDEX.v1"
    assert pack.feature_registry[0].value_kind == "ratio"
    assert result.bundle.dataset_card.observation_count == len(all_series) * 104
    assert result.bundle.preregistration.primary_metric_code == "false_alerts_per_year"
    assert result.bundle.calibration.status == "measured"
    assert {ref.media_type for ref in result.bundle.artifact_manifest} >= {
        "application/json",
        "application/x-parquet",
        "text/markdown",
        "text/html",
    }
    assert reproduce_run(result.manifest_path, root=ROOT)
    manifest_text = result.manifest_path.read_text(encoding="utf-8")
    assert "C:\\" not in manifest_text
    assert str(ROOT) not in manifest_text
    report_text = store.get_bytes(result.scope, result.markdown_artifact).decode("utf-8")
    assert "http://" not in report_text and "https://" not in report_text
    assert "offline descriptive arm" in report_text
    assert build_report(result.run_id, artifact_root=tmp_path) == (
        result.markdown_artifact,
        result.html_artifact,
    )


def test_reproduction_recomputes_result_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _permit_test_tree(monkeypatch)
    result = run_benchmark(root=ROOT, artifact_root=tmp_path, run_id="wbc1_tamper")
    manifest = _manifest(result.manifest_path)
    manifest["candidate"] = manifest["baseline"]
    result.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RunnerError, match="candidate results"):
        reproduce_run(result.manifest_path, root=ROOT)


def test_benchmark_requires_a_synchronized_vendor_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _permit_test_tree(monkeypatch)
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")

    with pytest.raises(RunnerError, match="vendor producer snapshot absent"):
        run_benchmark(root=tmp_path, artifact_root=tmp_path / "objects")
