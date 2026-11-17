class SiplError(Exception):
    pass


class SiplSyntaxError(SiplError):
    def __init__(self, message: str, line: int, column: int, context: str) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.context = context

    def __str__(self) -> str:
        return f"Syntax error at {self.line}:{self.column}: {self.message}\n{self.context}"


class SiplRuntimeError(SiplError):
    pass


class UndefinedVariableError(SiplRuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Variable '{name}' is undefined")
        self.name = name


class ExecutionLimitError(SiplRuntimeError):
    def __init__(self, limit: int) -> None:
        super().__init__(f"Execution step limit exceeded: {limit}")
        self.limit = limit

