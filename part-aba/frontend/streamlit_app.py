import sys
from pathlib import Path

import streamlit as streamlit

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.parser import parse_framework
from backend.preferences import normal_reverse_attacks
from backend.reasoning import attacks_classic, create_arguments
from backend.validation import ValidationError

EXAMPLE = (ROOT / "backend" / "exemples" / "assignment_exemple.aba").read_text(
    encoding="utf-8"
)
streamlit.set_page_config(page_title="ABA Generator", page_icon="⚖️", layout="wide")
streamlit.markdown(
    """
    <style>
    .stAppDeployButton {display: none;}
    #MainMenu {visibility: hidden;}
    header [data-testid="stHeaderActionElements"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)
streamlit.title("ABA Generator")
streamlit.caption("Assumption-Based Argumentation — saisie, validation, arguments et attaques")

with streamlit.sidebar:
    streamlit.header("Options")
    to_non_circular = streamlit.checkbox("Convertir en non-circulaire", value=False)
    make_atomic = streamlit.checkbox("Convertir en atomique", value=False)
    streamlit.markdown("---")
    if streamlit.button("Charger l'exemple"):
        streamlit.session_state["framework_text"] = EXAMPLE

if "framework_text" not in streamlit.session_state:
    streamlit.session_state["framework_text"] = EXAMPLE

framework_text = streamlit.text_area(
    "Cadre ABA (format texte)",
    value=streamlit.session_state["framework_text"],
    height=320,
    key="framework_text_area",
)

validation_column, analysis_column, _ = streamlit.columns([1, 1, 4])
validate_button = validation_column.button("Valider")
analyze_button = analysis_column.button("Analyser", type="primary")


def analyze(raw: str):
    framework = parse_framework(raw)
    messages = []
    if to_non_circular:
        framework = framework.to_non_circular()
        messages.append("Converti en non-circulaire")
    if make_atomic:
        if not framework.isFlat():
            raise ValueError(
                "make_atomic exige un cadre plat (cochez aussi non-circulaire si besoin)."
            )
        framework = framework.make_atomic()
        messages.append("Converti en atomique")

    args = create_arguments(framework)
    classic_result = attacks_classic(framework, args)
    aba_plus_result = normal_reverse_attacks(framework, args)
    return framework, args, classic_result, aba_plus_result, messages


if validate_button or analyze_button:
    streamlit.session_state["framework_text"] = framework_text
    try:
        if validate_button and not analyze_button:
            framework = parse_framework(framework_text)
            streamlit.success("Cadre valide.")
            streamlit.code(framework.summary(), language="text")
        else:
            framework, args, classic_result, aba_plus_result, messages = analyze(framework_text)

            metric1, metric2, metric3, metric4 = streamlit.columns(4)
            metric1.metric("Flat", str(framework.isFlat()))
            metric2.metric("Circular", str(framework.contains_circular_dependenncies()))
            metric3.metric("Atomic", str(framework.isAtomic()))
            metric4.metric("Arguments", len(args))
            if messages:
                streamlit.info(" · ".join(messages))

            with streamlit.expander("Résumé du cadre", expanded=False):
                streamlit.code(framework.summary(), language="text")

            left, right = streamlit.columns(2)
            with left:
                streamlit.subheader("Arguments")
                for a in args:
                    streamlit.write(f"**{a.name}**: `{a.claim} ← {{{', '.join(sorted(a.assumptions))}}}`")

            with right:
                streamlit.subheader("Préférences")
                if not framework.preferences:
                    streamlit.write("_Aucune_")
                else:
                    for preferences, less_preferred_values in sorted(framework.preferences.items()):
                        for b in sorted(less_preferred_values):
                            streamlit.write(f"`{preferences} > {b}`")

            streamlit.subheader("Attaques classiques")
            if not classic_result:
                streamlit.write("_Aucune_")
            else:
                streamlit.dataframe(
                    [
                        {
                            "from": x.name,
                            "claim": x.claim,
                            "to": y.name,
                            "on": alpha,
                        }
                        for x, y, alpha in classic_result
                    ],
                    use_container_width=True,
                    hide_index=True,
                )

            column1, column2 = streamlit.columns(2)
            with column1:
                streamlit.subheader("Attaques normales (ABA+)")
                table_rows = [
                    {"from": x.name, "to": y.name, "on": alpha}
                    for x, y, alpha in aba_plus_result["normal"]
                ]
                if table_rows:
                    streamlit.dataframe(table_rows, use_container_width=True, hide_index=True)
                else:
                    streamlit.write("_Aucune_")
            with column2:
                streamlit.subheader("Attaques inverses (ABA+)")
                table_rows = [
                    {"from": x.name, "to": y.name, "on": alpha}
                    for x, y, alpha in aba_plus_result["reverse"]
                ]
                if table_rows:
                    streamlit.dataframe(table_rows, use_container_width=True, hide_index=True)
                else:
                    streamlit.write("_Aucune_")

    except ValidationError as e:
        streamlit.error("Erreurs de validation")
        for error in e.errors:
            streamlit.write(f"- {error}")
    except Exception as e:
        streamlit.error(str(e))
