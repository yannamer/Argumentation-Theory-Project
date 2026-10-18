
import re
from backend.aba_framework import ABAFramework, Rule
from backend.validation import ValidationError


def parse_framework(framework_text: str, validate: bool = True) -> ABAFramework:
    literals = set()
    assumptions = set()
    contraries = {}
    rules = []
    preferences = {}
    errors = []

    for line in framework_text.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("L:"):
            literals = set(line.split(":", 1)[1].strip(" []").split(","))
            literals = {x.strip() for x in literals if x.strip()}

        elif line.startswith("A:"):
            assumptions = set(line.split(":", 1)[1].strip(" []").split(","))
            assumptions = {x.strip() for x in assumptions if x.strip()}

        elif line.startswith("C("):
            match = re.fullmatch(r"C\((\w+)\):\s*(\w+)", line)
            if match:
                assumption, contrary = match.groups()
                contraries[assumption] = contrary
            else:
                errors.append(f"Syntaxe incorrecte : {line}")

        elif line.startswith("contrary("):
            match = re.fullmatch(r"contrary\((\w+)\)\s*=\s*(\w+)", line)
            if match:
                assumption, contrary = match.groups()
                contraries[assumption] = contrary
            else:
                errors.append(f"Syntaxe incorrecte : {line}")

        elif line.startswith(("PREF:", "preferences:")):
            prefix = "PREF:" if line.startswith("PREF:") else "preferences:"
            pairs = re.findall(r"(\w+)\s*>\s*(\w+)", line[len(prefix):])
            for preferred, lesser in pairs:
                preferences.setdefault(preferred, set()).add(lesser)

        elif "<-" in line:
            match = re.fullmatch(
                r"(?:\[(\w+)\]:\s*|(\w+):\s*)?(\w+)\s*<-\s*(.*)",
                line,
            )
            if match:
                bracket_name, colon_name, conclusion, body = match.groups()
                premises = tuple(
                    x.strip() for x in body.split(",") if x.strip()
                )
                rules.append(Rule(
                    conclusion=conclusion,
                    premises=premises,
                    name=bracket_name or colon_name,
                ))
            else:
                errors.append(f"Règle incorrecte : {line}")

        else:
            errors.append(f"Syntaxe non reconnue : {line}")

    if not literals:
        errors.append("Missing L: L: est absent ou vide")
    if not assumptions:
        errors.append("A: est absent ou vide")
    if not contraries:
        errors.append("Aucun contraire défini")
    if not rules:
        errors.append("Aucune règle définie")

    if errors:
        raise ValidationError(errors)

    return ABAFramework.from_components(
        literals=literals,
        assumptions=assumptions,
        contraries=contraries,
        rules=rules,
        preferences=preferences or None,
        validate=validate,
    )


def parse_framework_file(path: str, validate: bool = True) -> ABAFramework:
    with open(path, encoding="utf-8") as file_path:
        return parse_framework(file_path.read(), validate=validate)
