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
    SourceSpan,
    Statement,
    Variable,
    WhileStatement,
)
from sipl.errors import ExecutionLimitError, SiplRuntimeError, UndefinedVariableError
from sipl.interpreter.trace import TraceEvent


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    state: dict[str, int]
    steps: int
    trace: tuple[TraceEvent, ...]


class Interpreter:
    def __init__(self, state: dict[str, int] | None = None, max_steps: int = 10_000) -> None:
        self.state = dict(state or {})
        self.max_steps = max_steps
        self.steps = 0
        self.events: list[TraceEvent] = []

    def run(self, program: Program) -> RuntimeResult:
        self._execute(program.body)
        self._event("ProgramFinished", None, self.state, self.state)
        return RuntimeResult(dict(self.state), self.steps, tuple(self.events))

    def _advance(self, span: SourceSpan | None = None) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            self._event("StepLimitExceeded", span, self.state, self.state)
            raise ExecutionLimitError(self.max_steps)

    def _event(
        self,
        event: str,
        span: SourceSpan | None,
        state_before: dict[str, int],
        state_after: dict[str, int],
        details: dict[str, object] | None = None,
    ) -> None:
        self.events.append(
            TraceEvent(
                event,
                self.steps,
                span,
                dict(state_before),
                dict(state_after),
                dict(details or {}),
            )
        )

    def _execute(self, statement: Statement) -> None:
        self._advance(statement.span)
        before = dict(self.state)
        self._event(
            "BeforeStatement",
            statement.span,
            before,
            before,
            {"statement": type(statement).__name__},
        )
        if isinstance(statement, Assignment):
            old_value = self.state.get(statement.name)
            new_value = self._expression(statement.expression)
            self.state[statement.name] = new_value
            self._event(
                "VariableChanged",
                statement.span,
                before,
                self.state,
                {"name": statement.name, "old": old_value, "new": new_value},
            )
        elif isinstance(statement, Sequence):
            for child in statement.statements:
                self._execute(child)
        elif isinstance(statement, IfStatement):
            condition = self._checked_condition(statement.condition)
            branch = (
                statement.then_branch
                if condition
                else statement.else_branch
            )
            self._execute(branch)
        elif isinstance(statement, WhileStatement):
            while self._checked_condition(statement.condition):
                self._execute(statement.body)
        elif isinstance(statement, Block):
            self._execute(statement.body)
        elif not isinstance(statement, Skip):
            raise SiplRuntimeError(f"Unsupported statement: {type(statement).__name__}")
        self._event(
            "AfterStatement",
            statement.span,
            before,
            self.state,
            {"statement": type(statement).__name__},
        )

    def _checked_condition(self, condition: Condition) -> bool:
        self._advance(condition.span)
        result = self._condition(condition)
        self._event(
            "ConditionChecked",
            condition.span,
            self.state,
            self.state,
            {"result": result},
        )
        return result

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

