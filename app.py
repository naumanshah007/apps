import os
import json
from typing import Dict

import pandas as pd
import streamlit as st
import yaml

from engine.rules_loader import load_rules_excel, normalize_rules, integrity_checks
from engine.decision_engine import DecisionEngine
from ui.components import render_header, render_question, render_admin_table, render_integrity_report
from utils.pdf import build_pdf_summary
from connectors.storage import get_storage

RULES_DEFAULT_PATH = os.path.abspath("./data/screening_rules_master_integrated.xlsx")
START_RULE_ID = "F1-01"


@st.cache_data(show_spinner=False)
def _load_rules(path: str) -> pd.DataFrame:
    df = load_rules_excel(path)
    return normalize_rules(df)


def load_branding() -> Dict[str, str]:
    path = os.path.abspath("./config/branding.yaml")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


branding = load_branding()
render_header(branding)

st.title("Cervical Screening Pathways")

page = st.sidebar.radio("Navigate", ["Home", "Screening", "Summary", "Admin"], index=0)

if page == "Home":
    st.markdown("Upload a rules Excel or use the default. Then go to Screening.")
    uploaded = st.file_uploader("Upload rules Excel", type=["xlsx"])
    if uploaded:
        tmp_path = os.path.abspath("./data/uploaded_rules.xlsx")
        os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
        with open(tmp_path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.session_state["rules_path"] = tmp_path
        st.success("Rules uploaded.")
    st.markdown(f"Default rules: `{RULES_DEFAULT_PATH}`")

elif page == "Screening":
    path = st.session_state.get("rules_path", RULES_DEFAULT_PATH)
    if not os.path.exists(path):
        st.warning("Rules file not found. Please upload one on Home page.")
        st.stop()

    rules_df = _load_rules(path)
    # Integrity check at load
    report = integrity_checks(rules_df, START_RULE_ID)
    if report.orphan_nodes and len(rules_df) > 0:
        st.info("Rules have orphans. Check Admin page.")

    if "engine" not in st.session_state:
        st.session_state.engine = DecisionEngine(rules_df, START_RULE_ID)
        st.session_state.audit = []

    engine = st.session_state.engine

    rule = engine.get_current_rule()
    if rule is None and engine.state.outcome is None:
        st.warning("Start node missing or flow ended without outcome.")
        if st.button("Restart"):
            st.session_state.engine = DecisionEngine(rules_df, START_RULE_ID)
            st.session_state.audit = []
        st.stop()

    if engine.state.outcome:
        st.success(f"Outcome: {engine.state.outcome}")
        if st.button("Save & Export PDF"):
            storage = get_storage()
            pdf_bytes = build_pdf_summary(branding, engine.state.outcome, engine.state.answers)
            path_saved = storage.save_report("screening-summary", pdf_bytes)
            st.success(f"Saved PDF to {path_saved}")
        if st.button("Restart Flow"):
            st.session_state.engine = DecisionEngine(rules_df, START_RULE_ID)
            st.session_state.audit = []
        st.stop()

    if rule is not None:
        answer = render_question(rule)
        if st.button("Next"):
            # Normalize Yes/No
            if isinstance(answer, str) and answer.lower() in {"yes", "no"}:
                engine.answer_current(True if answer.lower() == "yes" else False)
            else:
                engine.answer_current(answer)

            # Save audit
            st.session_state.audit = engine.state.answers
            st.rerun()

elif page == "Summary":
    st.header("Session Summary")
    engine = st.session_state.get("engine")
    if not engine:
        st.info("No session started.")
        st.stop()
    st.markdown(f"Outcome: **{engine.state.outcome or 'In progress'}**")
    st.dataframe(pd.DataFrame(engine.state.answers), use_container_width=True)

    if st.button("Export PDF"):
        storage = get_storage()
        pdf_bytes = build_pdf_summary(branding, engine.state.outcome, engine.state.answers)
        path_saved = storage.save_report("screening-summary", pdf_bytes)
        st.success(f"Saved PDF to {path_saved}")

elif page == "Admin":
    st.header("Admin")
    path = st.session_state.get("rules_path", RULES_DEFAULT_PATH)
    if not os.path.exists(path):
        st.warning("Rules file not found.")
        st.stop()
    rules_df = _load_rules(path)
    render_admin_table(rules_df)

    from engine.rules_loader import IntegrityReport

    report = integrity_checks(rules_df, START_RULE_ID)
    render_integrity_report(
        {
            "Missing required columns": report.missing_required_columns,
            "Missing OnTrue/OnFalse": report.missing_on_true_false,
            "Actions missing Outcome": report.missing_outcome_for_actions,
            "Invalid references": report.invalid_references,
            "Orphan nodes": report.orphan_nodes,
        }
    )

    st.markdown("Health: OK")