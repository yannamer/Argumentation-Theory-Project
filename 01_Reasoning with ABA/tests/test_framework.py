
from backend import ABAFramework, Rule, create_example


def test_framework_literals():
    framework = create_example()
    assert framework.literals == {"a", "b", "c", "q", "p", "r", "s", "t"}
    assert "p" in framework.literals
    assert "x" not in framework.literals


def test_assumptions_are_literals():
    framework = create_example()
    assert framework.assumptions <= framework.literals
    assert framework.assumptions == {"a", "b", "c"}


def test_contrary_mapping():
    framework = create_example()
    assert framework.contrary_of("a") == "r"
    assert framework.contrary_of("b") == "s"
    assert framework.contrary_of("c") == "t"


def test_rules_with_facts():
    framework = create_example()
    assert len(framework.rules) == 5
    r2 = next(r for r in framework.rules if r.name == "r2")
    assert r2.conclusion == "q"
    assert r2.premises == ()


def test_summary_includes_rules():
    framework = create_example()
    text = framework.summary()
    assert "r1: p <- q, a" in text
    assert "r2: q <-" in text
