"""MethodTrial publication must preserve its source artifact store."""

from pathlib import Path

import pytest

from developer_lens_lab.wbc1 import export as export_module
from developer_lens_lab.wbc1.runner import run_benchmark

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "run_demo"
REFUSAL = "MethodTrial output must not overwrite the source artifact store"


@pytest.fixture
def composed_view(monkeypatch: pytest.MonkeyPatch) -> None:
    # Isolate destination policy from the separately tested projection composer.
    def compose(*args: object, **kwargs: object) -> dict[str, object]:
        return {}

    monkeypatch.setattr(export_module, "compose_method_trial_view", compose)


@pytest.mark.parametrize("custom_store", [False, True])
@pytest.mark.parametrize("name", ["run.json", "custody.json", "objects/ab/" + "ab" * 32])
def test_refuses_source_records_before_publication(
    tmp_path: Path, composed_view: None, custom_store: bool, name: str
) -> None:
    store = tmp_path / ("custom-store" if custom_store else ".dllab")
    destination = store / "scopes" / RUN_ID / name
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"invented source evidence\n")
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(
            RUN_ID,
            root=tmp_path,
            artifact_root=store if custom_store else None,
            output=destination,
        )
    assert destination.read_bytes() == b"invented source evidence\n"
    assert not list(destination.parent.glob(".dllab-export-*"))


def test_valid_run_manifest_cannot_be_replaced(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def permit_invented_run(_root: Path) -> None:
        return None

    def invented_commit(_root: Path) -> str:
        return "a" * 40

    monkeypatch.setattr(
        "developer_lens_lab.wbc1.runner._ensure_reproducible_tree", permit_invented_run
    )
    monkeypatch.setattr("developer_lens_lab.wbc1.runner._git_commit", invented_commit)
    store = tmp_path / "source"
    run = run_benchmark(root=ROOT, artifact_root=store, run_id=RUN_ID)
    before = run.manifest_path.read_bytes()
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(
            RUN_ID, root=ROOT, artifact_root=store, output=run.manifest_path
        )
    assert run.manifest_path.read_bytes() == before


@pytest.mark.parametrize("custom_store", [False, True])
def test_refuses_new_output_through_dotdot_parent_alias(
    tmp_path: Path, composed_view: None, custom_store: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    store = tmp_path / ("custom-store" if custom_store else ".dllab")
    (store / "scopes" / RUN_ID).mkdir(parents=True)
    destination = store / "scopes" / RUN_ID / ".." / "new" / "view.json"
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(
            RUN_ID,
            root=tmp_path,
            artifact_root=Path(store.name) if custom_store else None,
            output=destination,
        )
    assert not (store / "scopes" / "new").exists()


def test_relative_destination_and_custom_store_parent_alias(
    tmp_path: Path, composed_view: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    store = tmp_path / "source"
    store.mkdir()
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(
            RUN_ID,
            root=tmp_path,
            artifact_root=Path("source/../source"),
            output=Path("source/view.json"),
        )
    assert not (store / "view.json").exists()


def test_store_root_itself_is_refused(tmp_path: Path, composed_view: None) -> None:
    store = tmp_path / ".dllab"
    store.mkdir()
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(RUN_ID, root=tmp_path, output=store)
    assert store.is_dir()


@pytest.mark.parametrize("custom_store", [False, True])
def test_external_outputs_remain_supported(
    tmp_path: Path, composed_view: None, custom_store: bool
) -> None:
    store = tmp_path / ("custom-store" if custom_store else ".dllab")
    for output in (
        None,
        tmp_path / "reports" / "view.json",
        Path(str(store) + "-copy") / "view.json",
    ):
        result = export_module.export_method_trial(
            RUN_ID,
            root=tmp_path,
            artifact_root=store if custom_store else None,
            output=output,
        )
        assert result.output_path.read_bytes() == result.payload == b"{}\n"


def _symlink(link: Path, target: Path, *, directory: bool = False) -> None:
    try:
        link.symlink_to(target, target_is_directory=directory)
    except OSError:
        pytest.skip("symlinks are unavailable on this host")


def test_refuses_output_through_symlinked_parent(tmp_path: Path, composed_view: None) -> None:
    store = tmp_path / ".dllab"
    store.mkdir()
    alias = tmp_path / "alias"
    _symlink(alias, store, directory=True)
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(RUN_ID, root=tmp_path, output=alias / "view.json")
    assert not (store / "view.json").exists()


def test_external_final_symlink_is_replaced_without_touching_source(
    tmp_path: Path, composed_view: None
) -> None:
    target = tmp_path / ".dllab" / "scopes" / RUN_ID / "run.json"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"invented source evidence\n")
    destination = tmp_path / "view.json"
    _symlink(destination, target)
    result = export_module.export_method_trial(RUN_ID, root=tmp_path, output=destination)
    assert not destination.is_symlink()
    assert destination.read_bytes() == result.payload
    assert target.read_bytes() == b"invented source evidence\n"


def test_final_symlink_inside_store_is_refused(tmp_path: Path, composed_view: None) -> None:
    store = tmp_path / ".dllab"
    store.mkdir()
    target = tmp_path / "keep.json"
    target.write_bytes(b"invented external evidence\n")
    destination = store / "view.json"
    _symlink(destination, target)
    with pytest.raises(ValueError, match=REFUSAL):
        export_module.export_method_trial(RUN_ID, root=tmp_path, output=destination)
    assert destination.is_symlink()
    assert target.read_bytes() == b"invented external evidence\n"
