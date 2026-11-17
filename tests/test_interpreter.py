import pytest

from sipl.errors import ExecutionLimitError, UndefinedVariableError
from sipl.interpreter.runtime import run_program
from sipl.parser import parse


def test_multiplication_program() -> None:
    source = """
    begin
      R := 0;
      K := Y;
      while K > 0 do begin R := R + X; K := K - 1 end
    end
    """
    result = run_program(parse(source), {"X": 4, "Y": 3})
    assert result.state == {"X": 4, "Y": 3, "R": 12, "K": 0}


def test_if_and_negative_number() -> None:
    source = "begin if X > 0 then R := X else R := -1 end"
    assert run_program(parse(source), {"X": 2}).state["R"] == 2
    assert run_program(parse(source), {"X": 0}).state["R"] == -1


def test_undefined_variable_is_reported() -> None:
    with pytest.raises(UndefinedVariableError):
        run_program(parse("begin X := Y end"))


def test_infinite_loop_is_limited() -> None:
    with pytest.raises(ExecutionLimitError):
        run_program(parse("begin while X = X do skip end"), {"X": 1}, max_steps=20)

