from __future__ import annotations

import argparse
from pathlib import Path

from developer_lens_lab.schemas import check_schemas, render_schemas


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--render", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.render:
        render_schemas(root)
        print("rendered contract schemas")
        return 0
    failures = check_schemas(root)
    for failure in failures:
        print(f"ERROR: {failure}")
    if failures:
        return 1
    print("generated contract schemas are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
