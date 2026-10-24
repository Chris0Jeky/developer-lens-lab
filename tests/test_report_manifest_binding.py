"""Full reports must belong to the requested run before rendering or publication."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from developer_lens_lab.artifacts import ArtifactStore, canonical_json_bytes
from developer_lens_lab.contracts import EvaluationBundle
from developer_lens_lab.wbc1 import runner
from developer_lens_lab.wbc1.report import build_html, build_markdown

from .factories import evaluation_bundle

RUN_ID = "requested_run"


def _full_report_manifest(tmp_path: Path, *, bundle_run_id: str = RUN_ID) -> dict[str, Any]:
    payload = evaluation_bundle()
    payload["run_manifest"]["run_id"] = bundle_run_id
    bundle = EvaluationBundle.model_validate_json(canonical_json_bytes(payload))
    store = ArtifactStore(tmp_path)
    return {
        "schema_version": "DeveloperLensWbc1Run.v1",
        "run_id": RUN_ID,
        "smoke": False,
        "bundle": store.put_json(RUN_ID, bundle.model_dump(mode="json")).model_dump(mode="json"),
        "markdown": store.put_text(RUN_ID, build_markdown(bundle), "text/markdown").model_dump(
            mode="json"
        ),
        "html": store.put_text(RUN_ID, build_html(bundle), "text/html").model_dump(mode="json"),
    }


def _assert_rejected_before_render_or_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifest: object, message: str
) -> None:
    store = ArtifactStore(tmp_path)
    store.write_scope_file_once(RUN_ID, "run.json", canonical_json_bytes(manifest))
    render_markdown = Mock(wraps=runner.build_markdown)
    render_html = Mock(wraps=runner.build_html)
    monkeypatch.setattr(runner, "build_markdown", render_markdown)
    monkeypatch.setattr(runner, "build_html", render_html)
    with (
        patch.object(
            ArtifactStore, "put_text", autospec=True, side_effect=ArtifactStore.put_text
        ) as put_text,
        patch.object(
            ArtifactStore,
            "write_scope_file_once",
            autospec=True,
            side_effect=ArtifactStore.write_scope_file_once,
        ) as write_once,
        patch.object(
            ArtifactStore,
            "write_scope_file",
            autospec=True,
            side_effect=ArtifactStore.write_scope_file,
        ) as write_force,
    ):
        with pytest.raises(runner.RunnerError, match=message):
            runner.build_report(RUN_ID, artifact_root=tmp_path)

        for operation in (render_markdown, render_html, put_text, write_once, write_force):
            operation.assert_not_called()
    assert not (store.scope_root(RUN_ID) / "report.md").exists()
    assert not (store.scope_root(RUN_ID) / "report.html").exists()


@pytest.mark.parametrize("manifest", [None, [], "manifest", 1, True])
def test_report_manifest_must_be_an_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, manifest: object
) -> None:
    _assert_rejected_before_render_or_write(tmp_path, monkeypatch, manifest, "must be an object")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema_version", "UNSUPPORTED", "unsupported WB-C1 run manifest"),
        ("schema_version", None, "unsupported WB-C1 run manifest"),
        ("run_id", "other_run", "run manifest.*requested run"),
        ("run_id", None, "run manifest.*requested run"),
    ],
)
def test_full_report_rejects_manifest_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, field: str, value: object, message: str
) -> None:
    manifest = _full_report_manifest(tmp_path)
    if value is None:
        del manifest[field]
    else:
        manifest[field] = value
    _assert_rejected_before_render_or_write(tmp_path, monkeypatch, manifest, message)


def test_full_report_rejects_foreign_bundle(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _full_report_manifest(tmp_path, bundle_run_id="run_demo")
    _assert_rejected_before_render_or_write(
        tmp_path, monkeypatch, manifest, "EvaluationBundle.*requested run"
    )


def test_full_report_rejects_f7_manifest_even_with_matching_report_hashes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = _full_report_manifest(tmp_path, bundle_run_id="run_demo")
    manifest.update(schema_version="UNSUPPORTED", run_id="other_run")
    _assert_rejected_before_render_or_write(
        tmp_path, monkeypatch, manifest, "unsupported WB-C1 run manifest"
    )


def test_valid_full_report_retains_recorded_hashes_and_publishes(tmp_path: Path) -> None:
    manifest = _full_report_manifest(tmp_path)
    store = ArtifactStore(tmp_path)
    store.write_scope_file_once(RUN_ID, "run.json", canonical_json_bytes(manifest))

    markdown_ref, html_ref = runner.build_report(RUN_ID, artifact_root=tmp_path)

    assert markdown_ref.model_dump(mode="json") == manifest["markdown"]
    assert html_ref.model_dump(mode="json") == manifest["html"]
    assert (store.scope_root(RUN_ID) / "report.md").read_bytes() == store.get_bytes(
        RUN_ID, markdown_ref
    )
    assert (store.scope_root(RUN_ID) / "report.html").read_bytes() == store.get_bytes(
        RUN_ID, html_ref
    )
