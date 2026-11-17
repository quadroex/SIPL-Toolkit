from sipl.parser import parse
from sipl.semantics.terms import semantic_term


def test_assignment_term() -> None:
    program = parse("begin X := X + 1 end")
    assert semantic_term(program) == "AS^X(S²(add, X⇒, 1))"


def test_loop_term_matches_course_notation() -> None:
    program = parse(
        "begin R := 0; K := Y; "
        "while K > 0 do begin R := R + X; K := K - 1 end end"
    )
    assert semantic_term(program) == (
        "AS^R(0) · AS^K(Y⇒) · "
        "WH(S²(gr, K⇒, 0), (AS^R(S²(add, R⇒, X⇒)) · AS^K(S²(sub, K⇒, 1))))"
    )


def test_if_not_or_term() -> None:
    program = parse("begin if not X = 0 or Y > 0 then skip else R := -1 end")
    assert semantic_term(program) == (
        "IF(S²(or, S¹(neg, S²(eq, X⇒, 0)), S²(gr, Y⇒, 0)), id, AS^R(-1))"
    )

