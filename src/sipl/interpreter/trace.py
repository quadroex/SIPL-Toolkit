from dataclasses import dataclass, field
from typing import Any

from sipl.ast import SourceSpan


@dataclass(frozen=True, slots=True)
class TraceEvent:
    event: str
    step: int
    span: SourceSpan | None
    state_before: dict[str, int]
    state_after: dict[str, int]
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        span = None
        if self.span is not None:
            span = {
                "start": self.span.start,
                "end": self.span.end,
                "line": self.span.line,
                "column": self.span.column,
                "end_line": self.span.end_line,
                "end_column": self.span.end_column,
            }
        return {
            "event": self.event,
            "step": self.step,
            "span": span,
            "state_before": dict(self.state_before),
            "state_after": dict(self.state_after),
            "details": dict(self.details),
        }


def format_event(event: TraceEvent) -> str:
    location = ""
    if event.span is not None:
        location = f" {event.span.line}:{event.span.column}"
    details = ""
    if event.details:
        values = ", ".join(f"{key}={value}" for key, value in event.details.items())
        details = f" {values}"
    return f"[{event.step}] {event.event}{location}{details}"

