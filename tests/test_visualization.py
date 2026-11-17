import json
import xml.etree.ElementTree as element_tree
from pathlib import Path

from sipl.cli import main
from sipl.parser import parse_tree
from sipl.visualization.parse_tree import tree_to_dict, tree_to_dot, tree_to_svg, tree_to_text

SOURCE = "begin X := 1 + 2 end"


def test_tree_dictionary_contains_source_spans() -> None:
    data = tree_to_dict(parse_tree(SOURCE), SOURCE)
    assert data["type"] == "program"
    assert data["span"]["line"] == 1
    assert data["source"] == SOURCE
    assert data["children"]


def test_text_dot_and_svg_exports() -> None:
    tree = parse_tree(SOURCE)
    text = tree_to_text(tree, SOURCE)
    dot = tree_to_dot(tree, SOURCE)
    svg = tree_to_svg(tree, SOURCE)
    assert "program [1:1]" in text
    assert "digraph SIPLParseTree" in dot
    assert "program\\n1:1" in dot
    assert svg.startswith("<svg")
    assert "program" in svg
    assert element_tree.fromstring(svg).tag.endswith("svg")


def test_tree_json_cli(tmp_path: Path, capsys: object) -> None:
    source_path = tmp_path / "program.sipl"
    output_path = tmp_path / "tree.json"
    source_path.write_text(SOURCE, encoding="utf-8")
    assert main(
        ["tree", str(source_path), "--format", "json", "--output", str(output_path)]
    ) == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("Wrote")
    assert json.loads(output_path.read_text(encoding="utf-8"))["type"] == "program"

