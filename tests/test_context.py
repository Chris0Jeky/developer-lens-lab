from pathlib import Path

from developer_lens_lab.context import verify_repository

ROOT = Path(__file__).resolve().parents[1]


def test_repository_context_is_valid() -> None:
    report = verify_repository(ROOT)
    assert report.ok, report.failures
