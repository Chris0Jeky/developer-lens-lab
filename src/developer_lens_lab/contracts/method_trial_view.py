# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from jsonschema import Draft202012Validator

METHOD_TRIAL_SCHEMA_VERSION = "DeveloperLensMethodTrialView.v1"
METHOD_TRIAL_VENDOR_ROOT = Path("vendor/developer-lens/method-trial-view/v1")


class MethodTrialViewError(ValueError):
    """Raised when a MethodTrialView does not satisfy the pinned product schema."""


def method_trial_schema(root: Path) -> dict[str, Any]:
    path = root / METHOD_TRIAL_VENDOR_ROOT / "schema.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MethodTrialViewError(f"MethodTrialView schema is unavailable: {path.name}") from exc
    if not isinstance(value, dict):
        raise MethodTrialViewError("MethodTrialView schema must be an object")
    return cast(dict[str, Any], value)


def validate_method_trial_view(value: object, *, root: Path) -> dict[str, Any]:
    schema = method_trial_schema(root)
    try:
        Draft202012Validator(schema).validate(value)
    except Exception as exc:  # jsonschema exceptions vary by version
        raise MethodTrialViewError(str(exc)) from exc
    if not isinstance(value, dict) or value.get("schema_version") != METHOD_TRIAL_SCHEMA_VERSION:
        raise MethodTrialViewError("unsupported MethodTrialView schema version")
    return cast(dict[str, Any], value)
