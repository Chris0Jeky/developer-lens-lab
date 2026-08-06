from __future__ import annotations

import re
from datetime import datetime
from typing import Annotated, Literal, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

UTC_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$"


def _canonical_utc(value: str) -> str:
    if not re.fullmatch(UTC_PATTERN, value):
        raise ValueError("timestamp must be an RFC 3339 UTC instant ending in Z")
    datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    return value


CanonicalUtc = Annotated[
    str,
    StringConstraints(pattern=UTC_PATTERN),
    AfterValidator(_canonical_utc),
]
Code = Annotated[str, StringConstraints(pattern=r"^[A-Za-z][A-Za-z0-9_.-]{0,95}$")]
OpaqueId = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]{2,63}$")]
Sha256 = Annotated[str, StringConstraints(pattern=r"^sha256:[0-9a-f]{64}$")]
CommitSha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
AvailabilityState = Literal["present", "absent", "unsupported", "intentionally_omitted"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class TimeWindow(StrictModel):
    start: CanonicalUtc
    end: CanonicalUtc

    @model_validator(mode="after")
    def ordered(self) -> Self:
        start = datetime.fromisoformat(self.start.removesuffix("Z") + "+00:00")
        end = datetime.fromisoformat(self.end.removesuffix("Z") + "+00:00")
        if start >= end:
            raise ValueError("window start must be before end")
        return self


class AvailableWindow(StrictModel):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {"properties": {"state": {"const": "present"}}},
                    "then": {
                        "properties": {
                            "window": {"not": {"type": "null"}},
                            "reason_code": {"type": "null"},
                        }
                    },
                    "else": {
                        "properties": {
                            "window": {"type": "null"},
                            "reason_code": {"not": {"type": "null"}},
                        }
                    },
                }
            ]
        }
    )

    state: AvailabilityState
    window: TimeWindow | None
    reason_code: Code | None

    @model_validator(mode="after")
    def state_matches_window(self) -> Self:
        if self.state == "present":
            if self.window is None or self.reason_code is not None:
                raise ValueError("present availability requires a window and no reason_code")
        elif self.window is not None or self.reason_code is None:
            raise ValueError("non-present availability requires reason_code and no window")
        return self


class TemporalAvailability(StrictModel):
    event: AvailableWindow
    collection: AvailableWindow
    feature: AvailableWindow


class ArtifactRef(StrictModel):
    sha256: Sha256
    size_bytes: Annotated[int, Field(ge=0, le=10_000_000_000)]
    media_type: Literal["application/json", "application/x-parquet", "text/markdown"]


class MetricValue(StrictModel):
    model_config = ConfigDict(
        json_schema_extra={
            "allOf": [
                {
                    "if": {"properties": {"state": {"const": "present"}}},
                    "then": {
                        "properties": {
                            "value": {"not": {"type": "null"}},
                            "reason_code": {"type": "null"},
                        }
                    },
                    "else": {
                        "properties": {
                            "value": {"type": "null"},
                            "reason_code": {"not": {"type": "null"}},
                        }
                    },
                }
            ]
        }
    )

    metric_code: Code
    state: AvailabilityState
    value: Annotated[float, Field(allow_inf_nan=False)] | None
    reason_code: Code | None

    @model_validator(mode="after")
    def state_matches_value(self) -> Self:
        if self.state == "present":
            if self.value is None or self.reason_code is not None:
                raise ValueError("present metric requires a value and no reason_code")
        elif self.value is not None or self.reason_code is None:
            raise ValueError("non-present metric requires reason_code and no value")
        return self
