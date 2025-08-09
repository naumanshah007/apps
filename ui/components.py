from __future__ import annotations

from typing import Dict, List

import pandas as pd
import streamlit as st


def render_header(branding: Dict[str, str]) -> None:
    st.sidebar.image(branding.get("logo_url", ""), width=180)
    st.sidebar.markdown(f"**{branding.get('hospital_name', 'Hospital')}**")
    st.sidebar.markdown(branding.get("address", ""))
    st.sidebar.markdown(f"Email: {branding.get('email','')} | Phone: {branding.get('phone','')}")


def render_question(rule: pd.Series) -> any:
    st.markdown(f"**{rule['QuestionText']}**")
    ans_type = str(rule.get("AnswerType", "")).strip().lower()
    key = f"q_{rule['RuleID']}"
    if ans_type in {"yes/no", "yesno", "boolean", "bool"}:
        return st.radio("Select one", ["Yes", "No"], horizontal=True, key=key)
    elif ans_type in {"multi", "multi-choice", "multichoice"}:
        options = [o.strip() for o in str(rule.get("Options", "")).split(",") if o.strip()]
        return st.selectbox("Choose option", options, key=key)
    elif ans_type in {"numeric", "number"}:
        return st.number_input("Enter value", value=0.0, key=key)
    else:
        # Default to boolean
        return st.radio("Select one", ["Yes", "No"], horizontal=True, key=key)


def render_admin_table(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_integrity_report(report: Dict[str, List[str]]) -> None:
    for k, v in report.items():
        st.markdown(f"**{k}**: {len(v)}")
        if v:
            st.code("\n".join(v))