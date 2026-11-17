import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from sipl.ast import ast_to_dict
from sipl.errors import SiplRuntimeError, SiplSyntaxError
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


def _write_or_print(content: str, output: str | None) -> None:
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path}")
    else:
        print(content)


def _configure_streams() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")


def _print_json(value: object, stream: TextIO | None = None) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2), file=stream or sys.stdout)


def _error_payload(error: Exception) -> dict[str, object]:
    payload: dict[str, object] = {
        "ok": False,
        "error": {"type": type(error).__name__, "message": str(error)},
    }
    if isinstance(error, SiplSyntaxError):
        payload["error"] = {
            "type": type(error).__name__,
            "message": error.message,
            "line": error.line,
            "column": error.column,
            "context": error.context,
        }
    return payload


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sipl", description="SIPL language toolkit")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="Check SIPL syntax")
    check.add_argument("file")
    check.add_argument("--json", action="store_true")

    parse_command = commands.add_parser("parse", help="Print the AST as JSON")
    parse_command.add_argument("file")
    parse_command.add_argument("--output")

    run = commands.add_parser("run", help="Execute a SIPL program")
    run.add_argument("file")
    run.add_argument("--state", default="")
    run.add_argument("--max-steps", type=int, default=10_000)
    run.add_argument("--json", action="store_true")

    trace = commands.add_parser("trace", help="Execute a program and print trace events")
    trace.add_argument("file")
    trace.add_argument("--state", default="")
    trace.add_argument("--max-steps", type=int, default=10_000)
    trace.add_argument("--json", action="store_true")

    term = commands.add_parser("term", help="Build the semantic term")
    term.add_argument("file")
    term.add_argument("--json", action="store_true")

    tree = commands.add_parser("tree", help="Export the parse tree")
    tree.add_argument("file")
    tree.add_argument("--format", choices=["text", "json", "dot", "svg"], default="text")
    tree.add_argument("--output")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_streams()
    args = build_argument_parser().parse_args(argv)
    try:
        source = _source(args.file)
        program = parse(source)
        if args.command == "check":
            if args.json:
                _print_json({"command": "check", "ok": True})
            else:
                print("Syntax is valid.")
            return 0
        if args.command == "parse":
            content = json.dumps(ast_to_dict(program), ensure_ascii=False, indent=2)
            _write_or_print(content, args.output)
            return 0
        if args.command == "run":
            result = run_program(program, _state(args.state), args.max_steps)
            if args.json:
                _print_json(
                    {
                        "command": "run",
                        "ok": True,
                        "state": result.state,
                        "steps": result.steps,
                    }
                )
            else:
                for name, value in sorted(result.state.items()):
                    print(f"{name} = {value}")
            return 0
        if args.command == "trace":
            result = run_program(program, _state(args.state), args.max_steps)
            if args.json:
                events = [event.to_dict() for event in result.trace]
                _print_json(
                    {
                        "command": "trace",
                        "ok": True,
                        "state": result.state,
                        "steps": result.steps,
                        "events": events,
                    }
                )
            else:
                for event in result.trace:
                    print(format_event(event))
            return 0
        if args.command == "term":
            term = semantic_term(program)
            if args.json:
                _print_json({"command": "term", "ok": True, "term": term})
            else:
                print(term)
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
            _write_or_print(content, args.output)
            return 0
    except SiplSyntaxError as error:
        if getattr(args, "json", False):
            _print_json(_error_payload(error), sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        return 2
    except SiplRuntimeError as error:
        if getattr(args, "json", False):
            _print_json(_error_payload(error), sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        return 3
    except (OSError, ValueError) as error:
        if getattr(args, "json", False):
            _print_json(_error_payload(error), sys.stderr)
        else:
            print(str(error), file=sys.stderr)
        return 4
    return 1

