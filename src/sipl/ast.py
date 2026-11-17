from dataclasses import dataclass, fields, is_dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceSpan:
    start: int
    end: int
    line: int
    column: int
    end_line: int
    end_column: int


@dataclass(frozen=True, slots=True)
class Node:
    span: SourceSpan


@dataclass(frozen=True, slots=True)
class Expression(Node):
    pass


@dataclass(frozen=True, slots=True)
class Number(Expression):
    value: int


@dataclass(frozen=True, slots=True)
class Variable(Expression):
    name: str


@dataclass(frozen=True, slots=True)
class BinaryExpression(Expression):
    operator: str
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class Condition(Node):
    pass


@dataclass(frozen=True, slots=True)
class Comparison(Condition):
    operator: str
    left: Expression
    right: Expression


@dataclass(frozen=True, slots=True)
class LogicalOr(Condition):
    left: Condition
    right: Condition


@dataclass(frozen=True, slots=True)
class LogicalNot(Condition):
    operand: Condition


@dataclass(frozen=True, slots=True)
class Statement(Node):
    pass


@dataclass(frozen=True, slots=True)
class Assignment(Statement):
    name: str
    expression: Expression


@dataclass(frozen=True, slots=True)
class Sequence(Statement):
    statements: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class IfStatement(Statement):
    condition: Condition
    then_branch: Statement
    else_branch: Statement


@dataclass(frozen=True, slots=True)
class WhileStatement(Statement):
    condition: Condition
    body: Statement


@dataclass(frozen=True, slots=True)
class Block(Statement):
    body: Statement


@dataclass(frozen=True, slots=True)
class Skip(Statement):
    pass


@dataclass(frozen=True, slots=True)
class Program(Node):
    body: Statement


def ast_to_dict(value: Any) -> Any:
    if isinstance(value, tuple):
        return [ast_to_dict(item) for item in value]
    if is_dataclass(value):
        result = {"type": type(value).__name__}
        for item in fields(value):
            result[item.name] = ast_to_dict(getattr(value, item.name))
        return result
    return value

