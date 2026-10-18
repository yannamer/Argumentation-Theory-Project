from backend import create_example
from backend.preferences import new_preference, normal_reverse_attacks, prefers


def test_preference_relation():
    framework = create_example()
    new_preference(framework, "b", "a")
    assert prefers(framework, "b", "a")
    assert framework.lessPrefered("a", "b")


def test_preference_attacks():
    framework = create_example(preferences={"b": {"a"}, "c": {"a"}})
    result = normal_reverse_attacks(framework)
    assert any(
        x.claim == "b" and y.claim == "s" and alpha == "b"
        for x, y, alpha in result["reverse"]
    )
    assert any(
        x.claim == "r" and alpha == "a" for x, y, alpha in result["normal"]
    )
