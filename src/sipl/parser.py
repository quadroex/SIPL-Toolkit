from pathlib import Path
from typing import Any

from lark import Lark, Transformer, UnexpectedInput, v_args
from lark.tree import Meta

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
from sipl.errors import SiplSyntaxError


def _span(meta: Meta) -> SourceSpan:
    return SourceSpan(
        start=meta.start_pos,
        end=meta.end_pos,
        line=meta.line,
        column=meta.column,
        end_line=meta.end_line,
        end_column=meta.end_column,
    )


@v_args(meta=True)
class AstBuilder(Transformer[Any, Any]):
    def program(self, meta: Meta, items: list[Any]) -> Program:
        return Program(_span(meta), items[0])

    def sequence(self, meta: Meta, items: list[Any]) -> Statement:
        statements = tuple(item for item in items if isinstance(item, Statement))
        if len(statements) == 1:
            return statements[0]
        return Sequence(_span(meta), statements)

    def assignment(self, meta: Meta, items: list[Any]) -> Assignment:
        return Assignment(_span(meta), str(items[0]), items[1])

    def if_statement(self, meta: Meta, items: list[Any]) -> IfStatement:
        return IfStatement(_span(meta), items[0], items[1], items[2])

    def while_statement(self, meta: Meta, items: list[Any]) -> WhileStatement:
        return WhileStatement(_span(meta), items[0], items[1])

    def block(self, meta: Meta, items: list[Any]) -> Block:
        return Block(_span(meta), items[0])

    def skip(self, meta: Meta, items: list[Any]) -> Skip:
        return Skip(_span(meta))

    def number(self, meta: Meta, items: list[Any]) -> Number:
        return Number(_span(meta), int(items[0]))

    def negative_number(self, meta: Meta, items: list[Any]) -> Number:
        return Number(_span(meta), -int(items[1]))

    def variable(self, meta: Meta, items: list[Any]) -> Variable:
        return Variable(_span(meta), str(items[0]))

    def grouped_expression(self, meta: Meta, items: list[Any]) -> Expression:
        expression = items[0]
        if not isinstance(expression, Expression):
            raise TypeError("Expected an expression")
        return expression

    def add(self, meta: Meta, items: list[Any]) -> BinaryExpression:
        return BinaryExpression(_span(meta), "+", items[0], items[2])

    def subtract(self, meta: Meta, items: list[Any]) -> BinaryExpression:
        return BinaryExpression(_span(meta), "-", items[0], items[2])

    def multiply(self, meta: Meta, items: list[Any]) -> BinaryExpression:
        return BinaryExpression(_span(meta), "*", items[0], items[2])

    def equal(self, meta: Meta, items: list[Any]) -> Comparison:
        return Comparison(_span(meta), "=", items[0], items[2])

    def greater(self, meta: Meta, items: list[Any]) -> Comparison:
        return Comparison(_span(meta), ">", items[0], items[2])

    def logical_or(self, meta: Meta, items: list[Any]) -> LogicalOr:
        return LogicalOr(_span(meta), items[0], items[2])

    def logical_not(self, meta: Meta, items: list[Any]) -> LogicalNot:
        operand = next(item for item in items if isinstance(item, Condition))
        return LogicalNot(_span(meta), operand)

    def grouped_condition(self, meta: Meta, items: list[Any]) -> Condition:
        condition = items[0]
        if not isinstance(condition, Condition):
            raise TypeError("Expected a condition")
        return condition


class SiplParser:
    def __init__(self, grammar_path: Path | None = None) -> None:
        path = grammar_path or Path(__file__).resolve().parents[2] / "grammar" / "sipl.lark"
        grammar = path.read_text(encoding="utf-8")
        self._parser = Lark(
            grammar,
            parser="lalr",
            start="program",
            propagate_positions=True,
            maybe_placeholders=False,
        )

    def parse_tree(self, source: str) -> Any:
        try:
            return self._parser.parse(source)
        except UnexpectedInput as error:
            context = error.get_context(source, span=40).rstrip()
            expected = sorted(getattr(error, "expected", []))
            message = "unexpected input"
            if expected:
                message = f"expected one of: {', '.join(expected)}"
            raise SiplSyntaxError(message, error.line, error.column, context) from error

    def parse(self, source: str) -> Program:
        tree = self.parse_tree(source)
        result = AstBuilder().transform(tree)
        if not isinstance(result, Program):
            raise TypeError("Parser did not produce a Program node")
        return result


_default_parser: SiplParser | None = None


def _get_parser() -> SiplParser:
    global _default_parser
    if _default_parser is None:
        _default_parser = SiplParser()
    return _default_parser


def parse_tree(source: str) -> Any:
    return _get_parser().parse_tree(source)


def parse(source: str) -> Program:
    return _get_parser().parse(source)

