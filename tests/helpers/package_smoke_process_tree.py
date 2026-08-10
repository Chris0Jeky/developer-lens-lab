"""Invented child/grandchild fixture for package-smoke process-tree tests."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


def _lock_one_byte(path: Path, ready_path: Path) -> None:
    with path.open("w+b") as lock_file:
        lock_file.write(b"x")
        lock_file.flush()
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.lockf(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB, 1)
        ready_path.write_text("ready", encoding="utf-8")
        time.sleep(30)


def main() -> int:
    lock_path = Path(sys.argv[1])
    ready_path = Path(sys.argv[2])
    if len(sys.argv) == 4 and sys.argv[3] == "--grandchild":
        _lock_one_byte(lock_path, ready_path)
        return 0
    subprocess.Popen([sys.executable, __file__, str(lock_path), str(ready_path), "--grandchild"])
    deadline = time.monotonic() + 5
    while not ready_path.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    time.sleep(30)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
