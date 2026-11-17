from dataclasses import dataclass

from sipl.ast import (
    Assignment,
    BinaryExpression,
    Block,
    Comparison,
    Condition,
    Expression,
    IfStatement,
    LogicalNot,
    LogicalOr,
    Number,
    Program,
    Sequence,
    Skip,
    Statement,
    Variable,
    WhileStatement,
)
from sipl.errors import ExecutionLimitError, SiplRuntimeError, UndefinedVariableError


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    state: dict[str, int]
    steps: int


class Interpreter:
    def __init__(self, state: dict[str, int] | None = None, max_steps: int = 10_000) -> None:
        self.state = dict(state or {})
        self.max_steps = max_steps
        self.steps = 0

    def run(self, program: Program) -> RuntimeResult:
        self._execute(program.body)
        return RuntimeResult(dict(self.state), self.steps)

    def _tick(self) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise ExecutionLimitError(self.max_steps)

    def _execute(self, statement: Statement) -> None:
        self._tick()
        if isinstance(statement, Assignment):
            self.state[statement.name] = self._expression(statement.expression)
            return
        if isinstance(statement, Sequence):
            for child in statement.statements:
                self._execute(child)
            return
        if isinstance(statement, IfStatement):
            branch = (
                statement.then_branch
                if self._condition(statement.condition)
                else statement.else_branch
            )
            self._execute(branch)
            return
        if isinstance(statement, WhileStatement):
            while self._condition(statement.condition):
                self._execute(statement.body)
                self._tick()
            return
        if isinstance(statement, Block):
            self._execute(statement.body)
            return
        if isinstance(statement, Skip):
            return
        raise SiplRuntimeError(f"Unsupported statement: {type(statement).__name__}")

    def _expression(self, expression: Expression) -> int:
        if isinstance(expression, Number):
            return expression.value
        if isinstance(expression, Variable):
            if expression.name not in self.state:
                raise UndefinedVariableError(expression.name)
            return self.state[expression.name]
        if isinstance(expression, BinaryExpression):
            left = self._expression(expression.left)
            right = self._expression(expression.right)
            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right
        raise SiplRuntimeError(f"Unsupported expression: {type(expression).__name__}")

    def _condition(self, condition: Condition) -> bool:
        if isinstance(condition, Comparison):
            left = self._expression(condition.left)
            right = self._expression(condition.right)
            if condition.operator == "=":
                return left == right
            if condition.operator == ">":
                return left > right
        if isinstance(condition, LogicalOr):
            return self._condition(condition.left) or self._condition(condition.right)
        if isinstance(condition, LogicalNot):
            return not self._condition(condition.operand)
        raise SiplRuntimeError(f"Unsupported condition: {type(condition).__name__}")


def run_program(
    program: Program,
    state: dict[str, int] | None = None,
    max_steps: int = 10_000,
) -> RuntimeResult:
    return Interpreter(state, max_steps).run(program)

