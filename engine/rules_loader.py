from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

import pandas as pd

REQUIRED_COLUMNS = [
    "RuleID",
    "Variable",
    "QuestionText",
    "AnswerType",
    "Options",
    "OnTrueNext",
    "OnFalseNext",
    "Outcome",
    "Notes",
    "SourceFigure",
]


@dataclass
class IntegrityReport:
    missing_required_columns: List[str]
    missing_on_true_false: List[str]
    missing_outcome_for_actions: List[str]
    invalid_references: List[str]
    orphan_nodes: List[str]
    start_node: Optional[str]


def load_rules_excel(path: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name="Rules")
    return df


def normalize_rules(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    # Fill NaN to empty strings for string columns
    for col in REQUIRED_COLUMNS:
        if df[col].dtype == object:
            df[col] = df[col].fillna("")
    return df[REQUIRED_COLUMNS]


def integrity_checks(df: pd.DataFrame, start_rule_id: str) -> IntegrityReport:
    df = normalize_rules(df)

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]

    # Actions must have Outcome filled and no routing
    is_action = df["AnswerType"].str.strip().str.lower() == "action"
    missing_outcome_for_actions = df.loc[is_action & (df["Outcome"].str.strip() == ""), "RuleID"].tolist()

    # Non-actions must have both routes
    non_action = ~is_action
    missing_on_true_false = df.loc[
        non_action & ((df["OnTrueNext"].str.strip() == "") | (df["OnFalseNext"].str.strip() == "")),
        "RuleID",
    ].tolist()

    # Reference validation
    all_ids: Set[str] = set(df["RuleID"].astype(str))
    refs: Set[str] = set()
    for col in ["OnTrueNext", "OnFalseNext"]:
        refs.update([v for v in df[col].astype(str).tolist() if v.strip()])
    invalid_refs = sorted([r for r in refs if r not in all_ids])

    # Orphan detection from start node
    visited: Set[str] = set()
    stack: List[str] = []
    if start_rule_id in all_ids:
        stack = [start_rule_id]
    while stack:
        rid = stack.pop()
        if rid in visited:
            continue
        visited.add(rid)
        row = df.loc[df["RuleID"] == rid]
        if row.empty:
            continue
        if (row.iloc[0]["AnswerType"].strip().lower() == "action"):
            continue
        for nxt_col in ["OnTrueNext", "OnFalseNext"]:
            nxt = str(row.iloc[0][nxt_col]).strip()
            if nxt and nxt not in visited:
                stack.append(nxt)
    orphan_nodes = sorted(list(all_ids - visited)) if start_rule_id in all_ids else sorted(list(all_ids))

    return IntegrityReport(
        missing_required_columns=missing_cols,
        missing_on_true_false=missing_on_true_false,
        missing_outcome_for_actions=missing_outcome_for_actions,
        invalid_references=invalid_refs,
        orphan_nodes=orphan_nodes,
        start_node=start_rule_id if start_rule_id in all_ids else None,
    )