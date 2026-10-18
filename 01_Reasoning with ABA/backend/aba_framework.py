from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

# a literal is just a string like "a" or "p"
Literal = str


@dataclass(frozen=True)
class Rule:
    conclusion: Literal
    premises: Tuple = ()
    name: Optional[str] = None

    def __str__(self):
        # example: r1: p <- q, a
        body = ", ".join(self.premises)
        label = self.name + ": " if self.name else ""
        return (label + self.conclusion + " <- " + body).rstrip()


@dataclass(frozen=True)
class Argument:
    claim: Literal
    assumptions: frozenset
    usedRules: Tuple = ()
    name: Optional[str] = None

    def __str__(self):
        assumptionText = "{" + ", ".join(sorted(self.assumptions)) + "}"
        label = self.name or "Arg(" + self.claim + ")"
        return label + ": " + self.claim + " <- " + assumptionText


@dataclass
class ABAFramework:
    literals: Set[Literal]
    assumptions: Set[Literal]
    contraries: Dict[Literal, Literal]
    rules: List[Rule]
    preferences: Optional[Dict[Literal, Set[Literal]]] = None

    @classmethod
    def from_components(cls, literals, assumptions, contraries, rules,
                        preferences=None, validate=True):
        # build the framework, converting everything to the right type
        if preferences is None:
            preferences = {}
        framework = cls(
            literals=set(literals),
            assumptions=set(assumptions),
            contraries=dict(contraries),
            rules=list(rules),
            preferences={k: set(v) for k, v in preferences.items()},
        )
        if validate:
            framework.validate()
        return framework

    def validate(self):
        # imported here to avoid circular import
        from .validation import validate_framework
        validate_framework(self)

    def isFlat(self):
        # flat = no assumption is the conclusion of a rule
        conclusions = set()
        for rule in self.rules:
            conclusions.add(rule.conclusion)
        return self.assumptions.isdisjoint(conclusions)

    def contrary_of(self, assumption):
        return self.contraries[assumption]

    # --- preferences ---
    def prefers(self, alpha, beta):
        from . import preferences as preferencesModule
        return preferencesModule.prefers(self, alpha, beta)

    def lessPrefered(self, alpha, beta):
        from . import preferences as preferencesModule
        return preferencesModule.lessPrefered(self, alpha, beta)

    def new_preference(self, preferred, lessPrefered):
        from . import preferences as preferencesModule
        preferencesModule.new_preference(self, preferred, lessPrefered)

    def normal_reverse_attacks(self, arguments=None):
        from . import preferences as preferencesModule
        return preferencesModule.normal_reverse_attacks(self, arguments)

    # --- transformations ---
    def graphDependency(self):
        from . import transformations as transformationsModule
        return transformationsModule.graphDependency(self)

    def contains_circular_dependenncies(self):
        from . import transformations as transformationsModule
        return transformationsModule.contains_circular_dependenncies(self)

    def to_non_circular(self):
        from . import transformations as transformationsModule
        return transformationsModule.to_non_circular(self)

    def isAtomic(self):
        from . import transformations as transformationsModule
        return transformationsModule.isAtomic(self)

    def make_atomic(self):
        from . import transformations as transformationsModule
        return transformationsModule.make_atomic(self)

    # --- reasoning ---
    def create_arguments(self):
        from . import reasoning as reasoningModule
        return reasoningModule.create_arguments(self)

    def attacks_classic(self, arguments=None):
        from . import reasoning as reasoningModule
        return reasoningModule.attacks_classic(self, arguments)

    # --- output ---
    def summary(self):
        lines = []
        lines.append("ABA Framework")
        lines.append("  L = {" + ", ".join(sorted(self.literals)) + "}")
        lines.append("  A = {" + ", ".join(sorted(self.assumptions)) + "}")
        lines.append("  Contraries:")
        for assumptionName in sorted(self.contraries):
            lines.append("    contrary(" + assumptionName + ") = " + self.contraries[assumptionName])
        lines.append("  Rules:")
        for rule in self.rules:
            lines.append("    " + str(rule))
        return "\n".join(lines)

    def to_dict(self):
        rules = []
        for rule in self.rules:
            rules.append({
                "name": rule.name,
                "conclusion": rule.conclusion,
                "premises": list(rule.premises),
            })
        return {
            "literals": sorted(self.literals),
            "assumptions": sorted(self.assumptions),
            "contraries": dict(sorted(self.contraries.items())),
            "rules": rules,
            "preferences": {k: sorted(v) for k, v in sorted(self.preferences.items())},
        }


def create_example(preferences=None):
    # example from the course
    literalsSet = {"a", "b", "c", "q", "p", "r", "s", "t"}
    assumptions_set = {"a", "b", "c"}
    contraries = {"a": "r", "b": "s", "c": "t"}
    rulesList = [
        Rule("p", ("q", "a"), "r1"),
        Rule("q", (), "r2"),
        Rule("r", ("b", "c"), "r3"),
        Rule("t", ("p", "c"), "r4"),
        Rule("s", ("t",), "r5"),
    ]
    return ABAFramework.from_components(literalsSet, assumptions_set, contraries, rulesList, preferences)