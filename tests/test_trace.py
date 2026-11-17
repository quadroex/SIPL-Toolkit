import json
from pathlib import Path

import pytest

from sipl.cli import main
from sipl.errors import ExecutionLimitError
from sipl.interpreter.runtime import Interpreter, run_program
from sipl.interpreter.trace import format_event
from sipl.parser import parse


def test_trace_contains_required_events() -> None:
    program = parse("begin X := 2; while X > 0 do X := X - 1 end")
    result = run_program(program)
    names = [event.event for event in result.trace]
    assert "BeforeStatement" in names
    assert "AfterStatement" in names
    assert "VariableChanged" in names
    assert "ConditionChecked" in names
    assert names[-1] == "ProgramFinished"
    changes = [event for event in result.trace if event.event == "VariableChanged"]
    assert changes[-1].details == {"name": "X", "old": 1, "new": 0}
    assert "VariableChanged" in format_event(changes[-1])
    assert "name=X" in format_event(changes[-1])


def test_limit_event_is_recorded() -> None:
    interpreter = Interpreter({"X": 1}, max_steps=8)
    with pytest.raises(ExecutionLimitError):
        interpreter.run(parse("begin while X = X do skip end"))
    assert interpreter.events[-1].event == "StepLimitExceeded"


def test_trace_json_command(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "trace.sipl"
    path.write_text("begin X := 1 end", encoding="utf-8")
    assert main(["trace", str(path), "--json"]) == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    events = result["events"]
    assert result["ok"] is True
    assert events[-1]["event"] == "ProgramFinished"
    assert events[1]["event"] == "VariableChanged"


def test_trace_text_command(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "trace.sipl"
    path.write_text("begin skip end", encoding="utf-8")
    assert main(["trace", str(path)]) == 0
    captured = capsys.readouterr()
    assert "BeforeStatement" in captured.out
    assert "ProgramFinished" in captured.out
