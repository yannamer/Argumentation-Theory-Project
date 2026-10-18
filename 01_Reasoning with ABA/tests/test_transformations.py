
from backend import ABAFramework, Rule, create_example
from backend.transformations import contains_circular_dependenncies, isAtomic, make_atomic, to_non_circular


def test_example_has_no_cycles():
    framework = create_example()
    assert framework.isFlat()
    assert not contains_circular_dependenncies(framework)


def test_remove_cycles_twice():
    framework = create_example()
    framework_without_cycles = to_non_circular(framework)
    assert not contains_circular_dependenncies(framework_without_cycles)
    assert framework_without_cycles.assumptions == framework.assumptions


def test_atomic_transformation():
    framework = create_example()
    atomic_framework = make_atomic(framework)
    assert isAtomic(atomic_framework)
    assert atomic_framework.isFlat()


def test_remove_cycles_from_framework():
    framework = ABAFramework.from_components(
        literals={"a", "p", "q", "r"},
        assumptions={"a"},
        contraries={"a": "r"},
        rules=[
            Rule("p", ("q",), "r1"),
            Rule("q", ("p",), "r2"),
            Rule("r", ("a",), "r3"),
        ],
    )
    assert contains_circular_dependenncies(framework)
    framework_without_cycles = to_non_circular(framework)
    assert not contains_circular_dependenncies(framework_without_cycles)
