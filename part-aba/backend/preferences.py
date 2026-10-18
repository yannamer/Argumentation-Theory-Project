

from typing import Dict, List, Optional, Sequence, Tuple

from .aba_framework import ABAFramework, Argument, Literal
from .reasoning import create_arguments


def prefers(framework: ABAFramework, alpha: Literal, beta: Literal) -> bool:
    return beta in framework.preferences.get(alpha, set())


def lessPrefered(framework: ABAFramework, alpha: Literal, beta: Literal) -> bool:
    return prefers(framework, beta, alpha)


def new_preference(
    framework: ABAFramework, preferred: Literal, less_pref: Literal
) -> None:
    if preferred not in framework.assumptions or less_pref not in framework.assumptions:
        raise ValueError("Preferences must relate assumptions")
    if preferred == less_pref:
        raise ValueError("Irreflexive preference required")
    framework.preferences.setdefault(preferred, set()).add(less_pref)


def normal_reverse_attacks(
    framework: ABAFramework,
    arguments: Optional[Sequence[Argument]] = None,
) -> Dict[str, List[Tuple[Argument, Argument, Literal]]]:
   
    if arguments is None:
        arguments = create_arguments(framework)

    normal: List[Tuple[Argument, Argument, Literal]] = []
    reverse: List[Tuple[Argument, Argument, Literal]] = []

    for x in arguments:
        for y in arguments:
            for alpha in y.assumptions:
                if x.claim != framework.contraries.get(alpha):
                    continue
                if any(lessPrefered(framework, beta, alpha) for beta in x.assumptions):
                    reverse.append((y, x, alpha))
                else:
                    normal.append((x, y, alpha))

    return {"normal": normal, "reverse": reverse}
