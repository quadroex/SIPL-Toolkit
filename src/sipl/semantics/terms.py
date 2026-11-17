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


def semantic_term(program: Program) -> str:
    return statement_term(program.body)


def statement_term(statement: Statement) -> str:
    if isinstance(statement, Assignment):
        return f"AS^{statement.name}({expression_term(statement.expression)})"
    if isinstance(statement, Sequence):
        return " · ".join(statement_term(child) for child in statement.statements)
    if isinstance(statement, IfStatement):
        condition = condition_term(statement.condition)
        then_branch = statement_term(statement.then_branch)
        else_branch = statement_term(statement.else_branch)
        return f"IF({condition}, {then_branch}, {else_branch})"
    if isinstance(statement, WhileStatement):
        condition = condition_term(statement.condition)
        body = statement_term(statement.body)
        return f"WH({condition}, {body})"
    if isinstance(statement, Block):
        return f"({statement_term(statement.body)})"
    if isinstance(statement, Skip):
        return "id"
    raise TypeError(f"Unsupported statement: {type(statement).__name__}")


def expression_term(expression: Expression) -> str:
    if isinstance(expression, Number):
        return str(expression.value)
    if isinstance(expression, Variable):
        return f"{expression.name}⇒"
    if isinstance(expression, BinaryExpression):
        operations = {"+": "add", "-": "sub", "*": "mult"}
        operation = operations[expression.operator]
        left = expression_term(expression.left)
        right = expression_term(expression.right)
        return f"S²({operation}, {left}, {right})"
    raise TypeError(f"Unsupported expression: {type(expression).__name__}")


def condition_term(condition: Condition) -> str:
    if isinstance(condition, Comparison):
        operations = {"=": "eq", ">": "gr"}
        operation = operations[condition.operator]
        left = expression_term(condition.left)
        right = expression_term(condition.right)
        return f"S²({operation}, {left}, {right})"
    if isinstance(condition, LogicalOr):
        left = condition_term(condition.left)
        right = condition_term(condition.right)
        return f"S²(or, {left}, {right})"
    if isinstance(condition, LogicalNot):
        return f"S¹(neg, {condition_term(condition.operand)})"
    raise TypeError(f"Unsupported condition: {type(condition).__name__}")

