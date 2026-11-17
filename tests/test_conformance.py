import pytest

from sipl.errors import SiplSyntaxError
from sipl.parser import parse

VALID_PROGRAMS = [
    "begin skip end",
    "begin X := 1 end",
    "begin X := -1 end",
    "begin X := 1; Y := 2 end",
    "begin X := 1 + 2 - 3 * 4 end",
    "begin X := (1 + 2) * 3 end",
    "begin if X > 0 then Y := X else Y := 0 end",
    "begin while X > 0 do X := X - 1 end",
    "begin begin X := 1; Y := 2 end end",
    "begin if X = 0 or Y > 0 then skip else X := 1 end",
    "begin if not X = 0 then skip else X := 0 end",
    "begin if ¬(X = 0 ∨ Y > 0) then skip else X := 0 end",
]


INVALID_PROGRAMS = [
    "",
    "skip",
    "begin skip",
    "begin X := end",
    "begin X := 1; end",
    "begin X := 1;; Y := 2 end",
    "begin if X > 0 then skip end",
    "begin while X > 0 skip end",
    "begin X := 1 / 2 end",
    "begin while X do skip end",
    "begin X := (1 + 2 end",
    "begin if X > 0 then skip else end",
]


@pytest.mark.parametrize("source", VALID_PROGRAMS)
def test_valid_programs(source: str) -> None:
    assert parse(source).body is not None


@pytest.mark.parametrize("source", INVALID_PROGRAMS)
def test_invalid_programs(source: str) -> None:
    with pytest.raises(SiplSyntaxError):
        parse(source)
