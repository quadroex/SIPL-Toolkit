import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from sipl.ast import ast_to_dict
from sipl.errors import SiplError
from sipl.interpreter.runtime import run_program
from sipl.parser import parse


def _state(value: str) -> dict[str, int]:
    if not value.strip():
        return {}
    result: dict[str, int] = {}
    for part in value.split(","):
        name, separator, raw = part.partition("=")
        if not separator or not name.strip():
            raise ValueError(f"Invalid state item: {part}")
        result[name.strip()] = int(raw.strip())
    return result


def _source(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sipl", description="SIPL language toolkit")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="Check SIPL syntax")
    check.add_argument("file")

    parse_command = commands.add_parser("parse", help="Print the AST as JSON")
    parse_command.add_argument("file")

    run = commands.add_parser("run", help="Execute a SIPL program")
    run.add_argument("file")
    run.add_argument("--state", default="")
    run.add_argument("--max-steps", type=int, default=10_000)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        source = _source(args.file)
        program = parse(source)
        if args.command == "check":
            print("Syntax is valid.")
            return 0
        if args.command == "parse":
            print(json.dumps(ast_to_dict(program), ensure_ascii=False, indent=2))
            return 0
        if args.command == "run":
            result = run_program(program, _state(args.state), args.max_steps)
            print(json.dumps(result.state, ensure_ascii=False, sort_keys=True))
            return 0
    except SiplError as error:
        print(str(error), file=sys.stderr)
        return 3
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 4
    return 1

