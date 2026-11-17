import json
from pathlib import Path

from sipl.cli import main


def test_check_command(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "ok.sipl"
    path.write_text("begin skip end", encoding="utf-8")
    assert main(["check", str(path)]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "Syntax is valid."


def test_run_command(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "run.sipl"
    path.write_text("begin R := X + 1 end", encoding="utf-8")
    assert main(["run", str(path), "--state", "X=4", "--json"]) == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["state"] == {"R": 5, "X": 4}
    assert result["steps"] == 1


def test_json_syntax_error(tmp_path: Path, capsys: object) -> None:
    path = tmp_path / "bad.sipl"
    path.write_text("begin X := end", encoding="utf-8")
    assert main(["check", str(path), "--json"]) == 2
    captured = capsys.readouterr()
    result = json.loads(captured.err)
    assert result["ok"] is False
    assert result["error"]["type"] == "SiplSyntaxError"
    assert result["error"]["line"] == 1

