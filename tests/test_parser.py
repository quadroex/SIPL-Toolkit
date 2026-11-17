import pytest

from sipl.ast import Assignment, BinaryExpression, Program, Sequence
from sipl.errors import SiplSyntaxError
from sipl.parser import parse


def test_parser_builds_program_and_sequence() -> None:
    program = parse("begin X := 1; Y := X + 2 end")
    assert isinstance(program, Program)
    assert isinstance(program.body, Sequence)
    assert len(program.body.statements) == 2


def test_multiplication_has_higher_priority() -> None:
    program = parse("begin X := 1 + 2 * 3 end")
    assignment = program.body
    assert isinstance(assignment, Assignment)
    expression = assignment.expression
    assert isinstance(expression, BinaryExpression)
    assert expression.operator == "+"
    assert isinstance(expression.right, BinaryExpression)
    assert expression.right.operator == "*"


def test_syntax_error_contains_position() -> None:
    with pytest.raises(SiplSyntaxError) as caught:
        parse("begin X := end")
    assert caught.value.line == 1
    assert caught.value.column > 0

