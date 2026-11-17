from dataclasses import dataclass, field
from html import escape
from typing import Any

from lark import Token, Tree


def _compact(value: str, limit: int = 34) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _tree_span(value: Tree[Any]) -> dict[str, int] | None:
    meta = value.meta
    if not hasattr(meta, "start_pos"):
        return None
    return {
        "start": meta.start_pos,
        "end": meta.end_pos,
        "line": meta.line,
        "column": meta.column,
        "end_line": meta.end_line,
        "end_column": meta.end_column,
    }


def _token_span(value: Token) -> dict[str, int] | None:
    if value.start_pos is None or value.end_pos is None:
        return None
    return {
        "start": value.start_pos,
        "end": value.end_pos,
        "line": value.line or 0,
        "column": value.column or 0,
        "end_line": value.end_line or 0,
        "end_column": value.end_column or 0,
    }


def _fragment(source: str, span: dict[str, int] | None) -> str:
    if span is None:
        return ""
    return source[span["start"] : span["end"]]


def tree_to_dict(value: Tree[Any] | Token, source: str) -> dict[str, Any]:
    if isinstance(value, Token):
        span = _token_span(value)
        return {
            "type": value.type,
            "value": str(value),
            "span": span,
            "source": _fragment(source, span),
            "children": [],
        }
    span = _tree_span(value)
    return {
        "type": str(value.data),
        "span": span,
        "source": _fragment(source, span),
        "children": [tree_to_dict(child, source) for child in value.children],
    }


def tree_to_text(value: Tree[Any] | Token, source: str) -> str:
    lines: list[str] = []

    def visit(node: Tree[Any] | Token, depth: int) -> None:
        data = tree_to_dict(node, source)
        span = data["span"]
        location = ""
        if span is not None:
            location = f" [{span['line']}:{span['column']}]"
        token = f" = {data['value']}" if "value" in data else ""
        fragment = _compact(data["source"])
        lines.append(f"{'  ' * depth}{data['type']}{token}{location} \"{fragment}\"")
        if isinstance(node, Tree):
            for child in node.children:
                visit(child, depth + 1)

    visit(value, 0)
    return "\n".join(lines)


@dataclass(slots=True)
class _VisualNode:
    identifier: int
    label: str
    fragment: str
    line: int
    column: int
    children: list["_VisualNode"] = field(default_factory=list)
    x: float = 0.0
    depth: int = 0


def _visual_tree(value: Tree[Any] | Token, source: str) -> _VisualNode:
    counter = 0

    def build(node: Tree[Any] | Token, depth: int) -> _VisualNode:
        nonlocal counter
        data = tree_to_dict(node, source)
        identifier = counter
        counter += 1
        span = data["span"] or {}
        label = data["type"]
        if "value" in data:
            label = f"{label}: {data['value']}"
        result = _VisualNode(
            identifier,
            label,
            _compact(data["source"], 26),
            span.get("line", 0),
            span.get("column", 0),
            depth=depth,
        )
        if isinstance(node, Tree):
            result.children = [build(child, depth + 1) for child in node.children]
        return result

    return build(value, 0)


def _flatten(root: _VisualNode) -> list[_VisualNode]:
    result: list[_VisualNode] = []

    def visit(node: _VisualNode) -> None:
        result.append(node)
        for child in node.children:
            visit(child)

    visit(root)
    return result


def tree_to_dot(value: Tree[Any] | Token, source: str) -> str:
    root = _visual_tree(value, source)
    lines = ["digraph SIPLParseTree {", "  rankdir=TB;", "  node [shape=box];"]
    for node in _flatten(root):
        label = f"{node.label}\\n{node.line}:{node.column}\\n{node.fragment}"
        label = label.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  n{node.identifier} [label="{label}"];')
        for child in node.children:
            lines.append(f"  n{node.identifier} -> n{child.identifier};")
    lines.append("}")
    return "\n".join(lines)


def tree_to_svg(value: Tree[Any] | Token, source: str) -> str:
    root = _visual_tree(value, source)
    leaf_index = 0

    def place(node: _VisualNode) -> None:
        nonlocal leaf_index
        for child in node.children:
            place(child)
        if node.children:
            node.x = sum(child.x for child in node.children) / len(node.children)
        else:
            node.x = 90 + leaf_index * 160
            leaf_index += 1

    place(root)
    nodes = _flatten(root)
    width = max(800, 180 + max((node.x for node in nodes), default=0))
    height = 100 + max((node.depth for node in nodes), default=0) * 110
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for node in nodes:
        y = 30 + node.depth * 110
        for child in node.children:
            child_y = 30 + child.depth * 110
            parts.append(
                f'<line x1="{node.x:.1f}" y1="{y + 58}" '
                f'x2="{child.x:.1f}" y2="{child_y}" stroke="#555"/>'
            )
    for node in nodes:
        y = 30 + node.depth * 110
        parts.append(
            f'<rect x="{node.x - 72:.1f}" y="{y}" width="144" height="58" '
            'rx="5" fill="white" stroke="black"/>'
        )
        parts.append(
            f'<text x="{node.x:.1f}" y="{y + 19}" text-anchor="middle" '
            f'font-family="Arial" font-size="12">{escape(node.label)}</text>'
        )
        parts.append(
            f'<text x="{node.x:.1f}" y="{y + 36}" text-anchor="middle" '
            f'font-family="Arial" font-size="10">{node.line}:{node.column}</text>'
        )
        parts.append(
            f'<text x="{node.x:.1f}" y="{y + 51}" text-anchor="middle" '
            f'font-family="Arial" font-size="9">{escape(node.fragment)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)

