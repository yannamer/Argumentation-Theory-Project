

from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .aba_framework import ABAFramework, Rule, create_example
from .parser import parse_framework
from .reasoning import argument_to_dict, attack_to_dict, attacks_classic, create_arguments
from .preferences import normal_reverse_attacks
from .validation import ValidationError

app = FastAPI(
    title="ABA Generator API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RuleIn(BaseModel):
    conclusion: str
    premises: List[str] = Field(default_factory=list)
    name: Optional[str] = None


class FrameworkIn(BaseModel):
    literals: List[str]
    assumptions: List[str]
    contraries: Dict[str, str]
    rules: List[RuleIn]
    preferences: Dict[str, List[str]] = Field(default_factory=dict)


class TextIn(BaseModel):
    text: str


class AnalyzeOptions(BaseModel):
    to_non_circular: bool = False
    to_atomic: bool = False
    with_preferences: bool = True


def build_from_json(data: FrameworkIn) -> ABAFramework:
    prefs = {k: set(v) for k, v in data.preferences.items()}
    rules = [
        Rule(r.conclusion, tuple(r.premises), r.name) for r in data.rules
    ]
    return ABAFramework.from_components(
        data.literals,
        data.assumptions,
        data.contraries,
        rules,
        preferences=prefs or None,
    )


def analyze(framework: ABAFramework, opts: AnalyzeOptions) -> dict:
    working = framework
    messages: List[str] = []

    if opts.to_non_circular:
        working = working.to_non_circular()
        messages.append("Converted to non-circular")
    if opts.to_atomic:
        if not working.isFlat():
            raise HTTPException(
                status_code=400,
                detail="make_atomic requires a flat framework (try non-circular first)",
            )
        working = working.make_atomic()
        messages.append("Converted to atomic")

    args = create_arguments(working)
    classical = attacks_classic(working, args)
    result = {
        "framework": working.to_dict(),
        "flat": working.isFlat(),
        "circular": working.contains_circular_dependenncies(),
        "atomic": working.isAtomic(),
        "notes": messages,
        "arguments": [argument_to_dict(a) for a in args],
        "attacks_classic": [
            attack_to_dict(x, y, alpha) for x, y, alpha in classical
        ],
        "preferences": {
            k: sorted(v) for k, v in sorted(working.preferences.items())
        },
        "normal_attacks": [],
        "reverse_attacks": [],
        "errors": [],
    }

    if opts.with_preferences:
        aba_plus = normal_reverse_attacks(working, args)
        result["normal_attacks"] = [
            attack_to_dict(x, y, alpha, "normal")
            for x, y, alpha in aba_plus["normal"]
        ]
        result["reverse_attacks"] = [
            attack_to_dict(x, y, alpha, "reverse")
            for x, y, alpha in aba_plus["reverse"]
        ]
    return result


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/example")
def get_example():
    framework = create_example(preferences={"b": {"a"}, "c": {"a"}})
    return analyze(framework, AnalyzeOptions())


@app.post("/api/validate")
def validate_endpoint(data: FrameworkIn):
    try:
        framework = build_from_json(data)
        return {"ok": True, "framework": framework.to_dict(), "errors": []}
    except ValidationError as e:
        return {"ok": False, "framework": None, "errors": e.errors}
    except ValueError as e:
        return {"ok": False, "framework": None, "errors": [str(e)]}


@app.post("/api/parse")
def parse_endpoint(data: TextIn):
    try:
        framework = parse_framework(data.text)
        return {"ok": True, "framework": framework.to_dict(), "errors": []}
    except ValidationError as e:
        return {"ok": False, "framework": None, "errors": e.errors}
    except ValueError as e:
        return {"ok": False, "framework": None, "errors": [str(e)]}


@app.post("/api/analyze")
def analyze_json(data: FrameworkIn, to_non_circular: bool = False, to_atomic: bool = False):
    try:
        framework = build_from_json(data)
        return analyze(
            framework,
            AnalyzeOptions(to_non_circular=to_non_circular, to_atomic=to_atomic),
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={"errors": e.errors}) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"errors": [str(e)]}) from e


@app.post("/api/analyze-text")
def analyze_text(
    data: TextIn, to_non_circular: bool = False, to_atomic: bool = False
):
    try:
        framework = parse_framework(data.text)
        return analyze(
            framework,
            AnalyzeOptions(to_non_circular=to_non_circular, to_atomic=to_atomic),
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={"errors": e.errors}) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"errors": [str(e)]}) from e
