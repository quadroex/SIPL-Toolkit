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
    assert main(["run", str(path), "--state", "X=4"]) == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == '{"R": 5, "X": 4}'

