"""Run identity must be accepted before benchmark work or custody side effects."""

from __future__ import annotations

from pathlib import Path
from typing import NoReturn

import pytest

from developer_lens_lab.artifacts import ArtifactStore
from developer_lens_lab.wbc1 import runner
from developer_lens_lab.wbc1.runner import RunnerError, run_benchmark


def _block_benchmark_work(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected(*_args: object, **_kwargs: object) -> NoReturn:
        pytest.fail("run identity was not rejected before benchmark work")

    for target in (
        "developer_lens_lab.wbc1.runner._ensure_reproducible_tree",
        "developer_lens_lab.wbc1.runner._load_vendor_snapshot",
        "developer_lens_lab.wbc1.runner.build_benchmark_dataset",
        "developer_lens_lab.wbc1.runner.prepare_evaluation",
        "developer_lens_lab.wbc1.runner.run_evaluation",
        "developer_lens_lab.artifacts.ArtifactStore.reserve_scope",
        "developer_lens_lab.wbc1.generator.BenchmarkDataset.open_final_holdout",
    ):
        monkeypatch.setattr(target, unexpected)


@pytest.mark.parametrize("smoke", [True, False], ids=["smoke", "full"])
@pytest.mark.parametrize(
    "run_id",
    [
        "",
        "a",
        "ab",
        "../invented/private",
        "/invented/private",
        r"~invented\private",
        "invented/child",
        r"invented\child",
        "UPPERCASE",
        "run-name",
        "12345678",
        "_run0000",
        "\u00e9un00001",
        "run_0001\n",
        " run_0001 ",
        " \t\n",
        "a" * 65,
    ],
)
def test_invalid_run_ids_fail_before_benchmark_work_without_creating_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, smoke: bool, run_id: str
) -> None:
    _block_benchmark_work(monkeypatch)
    artifact_root = tmp_path / "uncreated-store"

    with pytest.raises(RunnerError) as exc_info:
        run_benchmark(
            smoke=smoke,
            root=tmp_path / "uncreated-repo",
            artifact_root=artifact_root,
            run_id=run_id,
        )

    assert str(exc_info.value) == "run_id must be an opaque lowercase identifier"
    assert exc_info.value.__cause__ is None
    assert not artifact_root.exists()
    assert not (tmp_path / "uncreated-repo").exists()


@pytest.mark.parametrize("run_id", ["abc", "abcdefg"])
def test_smoke_ids_shorter_than_the_projection_minimum_fail_before_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, run_id: str
) -> None:
    _block_benchmark_work(monkeypatch)

    with pytest.raises(RunnerError) as exc_info:
        run_benchmark(root=tmp_path, run_id=run_id)

    assert str(exc_info.value) == "smoke run_id must contain at least 8 characters"
    assert not (tmp_path / ".dllab").exists()


class _PreflightCompleteError(Exception):
    """Stop accepted runs at vendor loading without starting a benchmark."""


@pytest.mark.parametrize(
    ("smoke", "run_id", "expected"),
    [
        (True, "abcdefgh", "abcdefgh"),
        (True, "run_0001", "run_0001"),
        (True, "a" * 64, "a" * 64),
        (False, "abc", "abc"),
        (False, "a_1", "a_1"),
        (True, None, "wbc1_smoke"),
        (False, None, "wbc1_full"),
    ],
    ids=[
        "smoke-min",
        "smoke-underscore",
        "smoke-max",
        "full-min",
        "full-underscore",
        "smoke-default",
        "full-default",
    ],
)
def test_accepted_run_ids_are_validated_before_vendor_continuation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    smoke: bool,
    run_id: str | None,
    expected: str,
) -> None:
    _block_benchmark_work(monkeypatch)
    validated: list[str] = []
    scope_root = ArtifactStore.scope_root

    def validate_scope(store: ArtifactStore, scope_id: str) -> Path:
        result = scope_root(store, scope_id)
        validated.append(scope_id)
        return result

    def allow_tree(_root: Path) -> None:
        pass

    def stop_at_vendor(_root: Path) -> NoReturn:
        assert validated == [expected]
        raise _PreflightCompleteError

    monkeypatch.setattr(ArtifactStore, "scope_root", validate_scope)
    monkeypatch.setattr(runner, "_ensure_reproducible_tree", allow_tree)
    monkeypatch.setattr(runner, "_load_vendor_snapshot", stop_at_vendor)
    artifact_root = tmp_path / "uncreated-store"

    with pytest.raises(_PreflightCompleteError):
        run_benchmark(smoke=smoke, root=tmp_path, artifact_root=artifact_root, run_id=run_id)

    assert not artifact_root.exists()
