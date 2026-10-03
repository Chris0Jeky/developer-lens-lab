"""JCS-compatible finding transport; existing artifact hashes keep their original format."""

from __future__ import annotations

import json
import math
from decimal import Decimal
from typing import cast

import orjson


def _number(value: int | float) -> str:
    if isinstance(value, int):
        if abs(value) > 9_007_199_254_740_991:
            raise ValueError("integer exceeds the interoperable JSON range")
        return str(value)
    if not math.isfinite(value):
        raise ValueError("canonical JSON requires finite numbers")
    if value == 0:
        return "0"
    # orjson supplies shortest-round-trip digits. ECMAScript uses fixed notation
    # from 1e-6 through values below 1e21; its exponent has no leading zeroes.
    parts = Decimal(orjson.dumps(value).decode("ascii")).as_tuple()
    digits = "".join(str(digit) for digit in parts.digits).rstrip("0")
    position = len(parts.digits) + int(parts.exponent)
    sign = "-" if parts.sign else ""
    if 0 < position <= 21:
        if position >= len(digits):
            body = digits + "0" * (position - len(digits))
        else:
            body = digits[:position] + "." + digits[position:]
    elif -6 < position <= 0:
        body = "0." + "0" * -position + digits
    else:
        exponent = position - 1
        fraction = "." + digits[1:] if len(digits) > 1 else ""
        body = digits[0] + fraction + "e" + ("+" if exponent >= 0 else "") + str(exponent)
    return sign + body


def _string(value: str) -> str:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError("canonical JSON rejects lone surrogates") from exc
    return json.dumps(value, ensure_ascii=False)


def _render(value: object, *, pretty: bool, depth: int = 0) -> str:
    if depth > 100:
        raise ValueError("canonical JSON exceeds the nesting limit")
    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is str:
        return _string(value)
    if type(value) in (int, float):
        return _number(cast(int | float, value))
    if type(value) not in (dict, list):
        raise ValueError("canonical JSON contains an unsupported value")
    separator = ": " if pretty else ":"
    if type(value) is dict:
        mapping = cast(dict[object, object], value)
        if any(type(key) is not str for key in mapping):
            raise ValueError("canonical JSON object keys must be strings")
        # Validate keys before UTF-16 sorting, so lone surrogates fail uniformly.
        for key in mapping:
            _string(cast(str, key))
        keys = sorted(cast(dict[str, object], mapping), key=lambda key: key.encode("utf-16be"))
        parts = [
            _string(key) + separator + _render(mapping[key], pretty=pretty, depth=depth + 1)
            for key in keys
        ]
        left, right = "{", "}"
    else:
        parts = [
            _render(item, pretty=pretty, depth=depth + 1) for item in cast(list[object], value)
        ]
        left, right = "[", "]"
    if not parts:
        return left + right
    if not pretty:
        return left + ",".join(parts) + right
    indent = "  " * (depth + 1)
    return left + "\n" + indent + (",\n" + indent).join(parts) + "\n" + "  " * depth + right


def canonical_bytes(value: object) -> bytes:
    """Serialize a JSON value with JCS key ordering and ECMAScript number formatting."""
    return _render(value, pretty=False).encode("utf-8")


def stable_bytes(value: object) -> bytes:
    """Match the producer's two-space, sorted JSON file convention plus one LF."""
    return (_render(value, pretty=True) + "\n").encode("utf-8")
