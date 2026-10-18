
from pathlib import Path

import pytest

from backend.parser import parse_framework, parse_framework_file
from backend.validation import ValidationError

EXAMPLE = (
    Path(__file__).resolve().parents[1]
    / "backend"
    / "exemples"
    / "assignment_exemple.aba"
)

SAMPLE = """
L: a, b, c, q, p, r, s, t
A: a, b, c
contrary(a) = r
contrary(b) = s
contrary(c) = t
r1: p <- q, a
r2: q <-
r3: r <- b, c
r4: t <- p, c
r5: s <- t
preferences: b > a, c > a
"""


def test_parse_example():
    framework = parse_framework(SAMPLE)
    assert framework.assumptions == {"a", "b", "c"}
    assert framework.contrary_of("a") == "r"
    assert any(r.name == "r2" and r.premises == () for r in framework.rules)
    assert "a" in framework.preferences["b"]


def test_parse_framework_file():
    framework = parse_framework_file(str(EXAMPLE))
    assert len(framework.rules) == 5


def test_invalid_syntax():
    with pytest.raises(ValidationError):
        parse_framework("L: a\nthis is not valid\n")


def test_missing_literals():
    with pytest.raises(ValidationError) as error:
        parse_framework("A: a\ncontrary(a) = a\nr1: a <-\n")
    assert any("Missing L" in e for e in error.value.errors)
