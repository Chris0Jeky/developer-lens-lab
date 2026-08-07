from __future__ import annotations

import re
import subprocess
from pathlib import Path

DENIED_SUFFIXES = {".db", ".sqlite", ".sqlite3", ".parquet", ".arrow", ".feather", ".pem", ".key"}
DENIED_TOP_LEVEL_DIRS = {".dllab", ".venv", "artifacts"}
MAX_TRACKED_BYTES = 1_000_000


def is_denied_generated_path(relative: Path) -> bool:
    return bool(
        (relative.parts and relative.parts[0] in DENIED_TOP_LEVEL_DIRS)
        or relative.parts[:2] == ("reports", "generated")
    )


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    paths = [Path(raw.decode("utf-8")) for raw in result.stdout.split(b"\0") if raw]
    failures: list[str] = []
    token_patterns = (
        re.compile("gh" + "[opusr]_" + r"[A-Za-z0-9]{20,}"),
        re.compile("sk" + "-" + r"[A-Za-z0-9]{20,}"),
    )
    local_path_marker = "C:" + "\\Users\\"
    for relative in paths:
        normalized = relative.as_posix()
        if relative.suffix.lower() in DENIED_SUFFIXES:
            failures.append(f"tracked data/key artifact: {normalized}")
            continue
        if is_denied_generated_path(relative):
            failures.append(f"tracked generated/private path: {normalized}")
            continue
        path = root / relative
        if path.stat().st_size > MAX_TRACKED_BYTES:
            failures.append(f"tracked file exceeds 1 MB: {normalized}")
            continue
        if path.suffix.lower() not in {".md", ".py", ".toml", ".yml", ".yaml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        if local_path_marker in text:
            failures.append(f"absolute user path in tracked text: {normalized}")
        if any(pattern.search(text) for pattern in token_patterns):
            failures.append(f"credential-shaped token in tracked text: {normalized}")
    for failure in failures:
        print(f"ERROR: {failure}")
    if not failures:
        print("repository hygiene verification passed")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
