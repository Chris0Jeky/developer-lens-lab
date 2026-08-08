import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_cards() -> ModuleType:
    # Load tools/cards.py directly by path: `tools` is not an installed package and the existing
    # suite only ever shelled out to it, so an on-disk import keeps the unit tests independent of
    # sys.path layout.
    spec = importlib.util.spec_from_file_location(
        "dll_cards_under_test", ROOT / "tools" / "cards.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the frozen @dataclass resolves string annotations via
    # sys.modules[cls.__module__], which raises if the module is not registered.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


cards = _load_cards()


def test_generated_task_programme_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "cards.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_real_cards_validate() -> None:
    # The shipped programme must pass its own validation with no argument (default = CARDS).
    cards._validate()


def test_unknown_status_fails_validation() -> None:
    bogus = (cards.Card("LAB-X-01", "Bogus", "WEIRD"),)
    with pytest.raises(ValueError, match="unknown status"):
        cards._validate(bogus)


def test_active_horizon_dependency_closure_still_enforced() -> None:
    # An ACTIVE card whose dependency is only BACKLOG is not dependency-closed and must fail.
    programme = (
        cards.Card("LAB-BASE-01", "Backlogged base", "BACKLOG"),
        cards.Card("LAB-WAVE-01", "Active dependent", "ACTIVE", ("LAB-BASE-01",)),
    )
    with pytest.raises(ValueError, match="not dependency-closed"):
        cards._validate(programme)


def test_more_than_six_active_cards_is_allowed() -> None:
    # The old six-card horizon cap is gone with the unbounded governor backlog; seven ACTIVE cards
    # with no unclosed dependencies must validate cleanly.
    programme = tuple(
        cards.Card(f"LAB-WAVE-{index:02d}", f"Active {index}", "ACTIVE") for index in range(7)
    )
    cards._validate(programme)


def test_backlog_card_may_depend_on_backlog_without_closure() -> None:
    # BACKLOG cards are outside the active horizon, so their dependencies are not closure-checked;
    # only unknown-dependency references fail.
    programme = (
        cards.Card("LAB-BASE-02", "Backlogged base", "BACKLOG"),
        cards.Card("LAB-BL-01", "Backlogged dependent", "BACKLOG", ("LAB-BASE-02",)),
    )
    cards._validate(programme)
