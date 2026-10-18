
class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        message = "Invalid ABA framework:"
        for e in errors:
            message = message + "\n- " + e
        super().__init__(message)


def validate_framework(framework):
    errors = []

    # A must be a subset of L
    for a in framework.assumptions:
        if a not in framework.literals:
            errors.append("Assumption " + str(a) + " is not in L")

    # every assumption needs a contrary, and the contrary must be in L
    for a in framework.assumptions:
        if a not in framework.contraries:
            errors.append("Missing contrary for assumption " + str(a))
        elif framework.contraries[a] not in framework.literals:
            errors.append("Contrary of " + str(a) + " (" + str(framework.contraries[a]) + ") is not in L")

    # contraries should only be defined for assumptions
    for key in framework.contraries:
        if key not in framework.assumptions:
            errors.append("Contrary defined for non-assumption " + str(key))

    # check the rules
    for rule in framework.rules:
        if rule.conclusion not in framework.literals:
            errors.append("Conclusion not in L: " + str(rule))
        for p in rule.premises:
            if p not in framework.literals:
                errors.append("Premise " + str(p) + " not in L: " + str(rule))

    # preferences are only between assumptions (ABA+)
    for preferred in framework.preferences:
        if preferred not in framework.assumptions:
            errors.append("Preference on non-assumption " + str(preferred))
        for b in framework.preferences[preferred]:
            if b not in framework.assumptions:
                errors.append("Preference target " + str(b) + " is not an assumption")

    if len(errors) > 0:
        raise ValidationError(errors)