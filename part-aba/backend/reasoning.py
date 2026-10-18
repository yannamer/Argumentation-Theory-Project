
from typing import Dict, List, Optional, Sequence, Set, Tuple

from .aba_framework import ABAFramework, Argument, Literal, Rule


def is_atomic_body(
    framework: ABAFramework,
    support: frozenset,
    atomic_bodies: Dict[Literal, Tuple[Literal, ...]],
    supports: Dict[Literal, Set[frozenset]],
) -> bool:
    if not atomic_bodies:
        return True
    for a in support:
        body = atomic_bodies.get(a)
        if body is None:
            continue
        rest = frozenset(x for x in support if x != a)
        for lit in body:
            if lit in framework.assumptions:
                if lit not in support:
                    return False
            else:
                if not any(s <= rest for s in supports.get(lit, ())):
                    return False
    return True


def create_arguments(framework: ABAFramework) -> List[Argument]:
    supports: Dict[Literal, Set[frozenset]] = {lit: set() for lit in framework.literals}
    traces: Dict[Tuple[Literal, frozenset], Tuple[Rule, ...]] = {}

    for a in framework.assumptions:
        s = frozenset({a})
        supports[a].add(s)
        traces[(a, s)] = ()

    atomic_bodies: Dict[Literal, Tuple[Literal, ...]] = getattr(
        framework, "_atomic_bodies", {}
    )

    changed = True
    while changed:
        changed = False
        for rule in framework.rules:
            if not rule.premises:
                empty = frozenset()
                if empty not in supports[rule.conclusion]:
                    supports[rule.conclusion].add(empty)
                    traces[(rule.conclusion, empty)] = (rule,)
                    changed = True
                continue

            premise_supports: List[Set[frozenset]] = []
            ok = True
            for premise in rule.premises:
                ps = supports.get(premise)
                if not ps:
                    ok = False
                    break
                premise_supports.append(ps)
            if not ok:
                continue

            def combine_arguments(i: int, accumulated: frozenset, used: Tuple[Rule, ...]) -> None:
                nonlocal changed
                if i == len(premise_supports):
                    if not is_atomic_body(framework, accumulated, atomic_bodies, supports):
                        return
                    if accumulated not in supports[rule.conclusion]:
                        supports[rule.conclusion].add(accumulated)
                        traces[(rule.conclusion, accumulated)] = used + (rule,)
                        changed = True
                    return
                for s in premise_supports[i]:
                    combine_arguments(i + 1, accumulated | s, used)

            combine_arguments(0, frozenset(), ())

    arguments: List[Argument] = []
    index = 1
    for claim in sorted(supports):
        for support in sorted(supports[claim], key=lambda s: (len(s), sorted(s))):
            arguments.append(
                Argument(
                    claim=claim,
                    assumptions=support,
                    usedRules=traces.get((claim, support), ()),
                    name=f"A{index}",
                )
            )
            index += 1
    return arguments


def attacks_classic(
    framework: ABAFramework,
    arguments: Optional[Sequence[Argument]] = None,
) -> List[Tuple[Argument, Argument, Literal]]:
    """X attacks Y on alpha if claim(X) = contrary(alpha) and alpha in Y."""
    if arguments is None:
        arguments = create_arguments(framework)
    attacks = []
    for x in arguments:
        for y in arguments:
            for alpha in y.assumptions:
                if x.claim == framework.contraries.get(alpha):
                    attacks.append((x, y, alpha))
    return attacks


def argument_to_dict(arg: Argument) -> dict:
    return {
        "name": arg.name,
        "claim": arg.claim,
        "assumptions": sorted(arg.assumptions),
        "rules": [str(r) for r in arg.usedRules],
    }


def attack_to_dict(
    x: Argument, y: Argument, alpha: Literal, kind: str = "classical"
) -> dict:
    return {
        "from": x.name,
        "to": y.name,
        "on": alpha,
        "kind": kind,
        "from_claim": x.claim,
        "to_claim": y.claim,
    }
