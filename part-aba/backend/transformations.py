from .aba_framework import ABAFramework, Rule


def graphDependency(framework):
    # for each literal, the set of literals it depends on
    graph = {}
    for lit in framework.literals:
        graph[lit] = set()

    for rule in framework.rules:
        for p in rule.premises:
            graph[rule.conclusion].add(p)

    return graph


def contains_circular_dependenncies(framework):
    graph = graphDependency(framework)
    # assumptions can't be part of a cycle, so we only look at the others
    nodes = framework.literals - framework.assumptions

    visiting = set()  
    done = set()      

    def visit_node(u):
        visiting.add(u)
        for v in graph.get(u, set()):
            if v not in nodes:
                continue
            if v in visiting:
                return True
            if v not in done:
                if visit_node(v):
                    return True
        visiting.remove(u)
        done.add(u)
        return False

    for n in nodes:
        if n not in done:
            if visit_node(n):
                return True
    return False


def get_level_name(framework, lit, k):
    if lit in framework.assumptions:
        return lit
    return lit + "#" + str(k)


def to_non_circular(framework):
    if not contains_circular_dependenncies(framework):
        return ABAFramework.from_components(
            framework.literals, framework.assumptions, framework.contraries, framework.rules, framework.preferences
        )

    non_assumptions = sorted(framework.literals - framework.assumptions)
    depth = len(non_assumptions)
    if depth < 1:
        depth = 1

    new_literals = set(framework.assumptions)
    new_rules = []

    # one copy of every literal for each level
    for k in range(depth):
        for s in non_assumptions:
            new_literals.add(get_level_name(framework, s, k))

    # the original literal points to its level 0 copy
    for s in non_assumptions:
        new_literals.add(s)
        new_rules.append(Rule(s, (get_level_name(framework, s, 0),), "alias_" + s))

    # rules with an assumption as conclusion are kept as they are (only once)
    for rule in framework.rules:
        if rule.conclusion in framework.assumptions:
            new_rules.append(rule)

    # copy the other rules for each level
    for k in range(depth):
        for rule in framework.rules:
            if rule.conclusion in framework.assumptions:
                continue

            body = []
            too_deep = False
            for p in rule.premises:
                if p in framework.assumptions:
                    body.append(p)
                elif k + 1 >= depth:
                    # no level left for this premise, so we skip the rule
                    too_deep = True
                    break
                else:
                    body.append(get_level_name(framework, p, k + 1))

            if too_deep:
                continue

            new_name = None
            if rule.name:
                new_name = rule.name + "_L" + str(k)
            new_rules.append(
                Rule(get_level_name(framework, rule.conclusion, k), tuple(body), new_name)
            )

    return ABAFramework.from_components(
        new_literals, framework.assumptions, framework.contraries, new_rules, framework.preferences
    )


def isAtomic(framework):
    # atomic = flat and every body is empty or a single assumption
    if not framework.isFlat():
        return False

    for rule in framework.rules:
        if len(rule.premises) == 0:
            continue
        if len(rule.premises) != 1:
            return False
        if rule.premises[0] not in framework.assumptions:
            return False

    return True


def make_atomic(framework):
    if not framework.isFlat():
        raise ValueError("make_atomic() requires a flat ABA framework")

    # already atomic, return a copy
    if isAtomic(framework):
        return ABAFramework.from_components(
            framework.literals, framework.assumptions, framework.contraries, framework.rules, framework.preferences
        )

    new_literals = set(framework.literals)
    new_assumptions = set(framework.assumptions)
    new_contraries = dict(framework.contraries)
    new_rules = []
    body_of = {} 

    i = 0
    for rule in framework.rules:
        # rules that are already atomic stay the same
        if len(rule.premises) == 0:
            new_rules.append(rule)
        elif len(rule.premises) == 1 and rule.premises[0] in framework.assumptions:
            new_rules.append(rule)
        else:
            # replace the body by a new assumption
            if rule.name:
                label = rule.name
            else:
                label = str(i)
            active_rule = "a_" + label
            fail_r = "fail_" + label

            new_literals.add(active_rule)
            new_literals.add(fail_r)
            new_assumptions.add(active_rule)
            new_contraries[active_rule] = fail_r

            new_rules.append(Rule(rule.conclusion, (active_rule,), rule.name))
            body_of[active_rule] = rule.premises
        i = i + 1

    atomic_framework = ABAFramework.from_components(
        new_literals, new_assumptions, new_contraries, new_rules, framework.preferences
    )
    atomic_framework._atomic_bodies = body_of
    return atomic_framework