from pathlib import Path

from developer_lens_lab.context import verify_repository


def main() -> int:
    report = verify_repository(Path(__file__).resolve().parents[1])
    for failure in report.failures:
        print(f"ERROR: {failure}")
    if report.ok:
        print("context verification passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
