import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_module_entrypoint_runs_example() -> None:
    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "sipl",
            "run",
            str(ROOT / "examples" / "multiply.sipl"),
            "--state",
            "X=3,Y=4",
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert process.returncode == 0
    assert json.loads(process.stdout)["state"]["R"] == 12


def test_module_entrypoint_reports_syntax_error(tmp_path: Path) -> None:
    path = tmp_path / "invalid.sipl"
    path.write_text("begin skip", encoding="utf-8")
    process = subprocess.run(
        [sys.executable, "-m", "sipl", "check", str(path), "--json"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert process.returncode == 2
    assert json.loads(process.stderr)["error"]["type"] == "SiplSyntaxError"
