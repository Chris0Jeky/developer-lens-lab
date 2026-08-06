from pathlib import Path

from scripts.verify_hygiene import is_denied_generated_path


def test_generated_path_filter_matches_directories_not_module_names() -> None:
    assert is_denied_generated_path(Path("artifacts/run.json"))
    assert is_denied_generated_path(Path("reports/generated/result.md"))
    assert not is_denied_generated_path(Path("src/developer_lens_lab/artifacts.py"))
    assert not is_denied_generated_path(Path("tests/test_artifacts.py"))
