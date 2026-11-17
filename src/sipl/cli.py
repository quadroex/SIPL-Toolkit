import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from sipl.ast import ast_to_dict
from sipl.errors import SiplError
from sipl.interpreter.runtime import run_program
from sipl.interpreter.trace import format_event
from sipl.parser import parse, parse_tree
from sipl.semantics.terms import semantic_term
from sipl.visualization.parse_tree import tree_to_dict, tree_to_dot, tree_to_svg, tree_to_text


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

    trace = commands.add_parser("trace", help="Execute a program and print trace events")
    trace.add_argument("file")
    trace.add_argument("--state", default="")
    trace.add_argument("--max-steps", type=int, default=10_000)
    trace.add_argument("--json", action="store_true")

    term = commands.add_parser("term", help="Build the semantic term")
    term.add_argument("file")

    tree = commands.add_parser("tree", help="Export the parse tree")
    tree.add_argument("file")
    tree.add_argument("--format", choices=["text", "json", "dot", "svg"], default="text")
    tree.add_argument("--output")

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
        if args.command == "trace":
            result = run_program(program, _state(args.state), args.max_steps)
            if args.json:
                events = [event.to_dict() for event in result.trace]
                print(json.dumps(events, ensure_ascii=False, indent=2))
            else:
                for event in result.trace:
                    print(format_event(event))
            return 0
        if args.command == "term":
            print(semantic_term(program))
            return 0
        if args.command == "tree":
            tree = parse_tree(source)
            exporters = {
                "text": lambda: tree_to_text(tree, source),
                "json": lambda: json.dumps(
                    tree_to_dict(tree, source), ensure_ascii=False, indent=2
                ),
                "dot": lambda: tree_to_dot(tree, source),
                "svg": lambda: tree_to_svg(tree, source),
            }
            content = exporters[args.format]()
            if args.output:
                Path(args.output).write_text(content, encoding="utf-8")
                print(f"Wrote {args.output}")
            else:
                print(content)
            return 0
    except SiplError as error:
        print(str(error), file=sys.stderr)
        return 3
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 4
    return 1

