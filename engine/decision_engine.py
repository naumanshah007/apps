from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

import pandas as pd


@dataclass
class DecisionState:
    current_rule_id: Optional[str]
    answers: List[Dict]
    outcome: Optional[str]


def _eval_numeric_condition(value: float, expr: str) -> Optional[bool]:
    if not expr:
        return None
    e = expr.replace(" ", "")
    try:
        if e.startswith(">="):
            return float(value) >= float(e[2:])
        if e.startswith("<="):
            return float(value) <= float(e[2:])
        if e.startswith(">"):
            return float(value) > float(e[1:])
        if e.startswith("<"):
            return float(value) < float(e[1:])
        if e.startswith("=="):
            return float(value) == float(e[2:])
    except Exception:
        return None
    return None


class DecisionEngine:
    def __init__(self, rules_df: pd.DataFrame, start_rule_id: str) -> None:
        self.rules = rules_df.set_index("RuleID", drop=False)
        self.start_rule_id = start_rule_id
        self.state = DecisionState(current_rule_id=start_rule_id, answers=[], outcome=None)

    def get_current_rule(self) -> Optional[pd.Series]:
        if self.state.current_rule_id is None:
            return None
        if self.state.current_rule_id not in self.rules.index:
            return None
        return self.rules.loc[self.state.current_rule_id]

    def is_action(self, rule: pd.Series) -> bool:
        return str(rule.get("AnswerType", "")).strip().lower() == "action"

    def answer_current(self, value: any) -> None:
        rule = self.get_current_rule()
        if rule is None:
            return
        if self.is_action(rule):
            # Action terminates
            self.state.outcome = str(rule.get("Outcome", "")).strip() or None
            self.state.current_rule_id = None
            return

        # Record answer with timestamp
        self.state.answers.append(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "RuleID": rule["RuleID"],
                "Variable": rule.get("Variable", ""),
                "QuestionText": rule.get("QuestionText", ""),
                "Answer": value,
            }
        )

        # Determine routing for boolean/yes-no/numeric/multi
        yn = None
        if isinstance(value, bool):
            yn = value
        elif isinstance(value, (int, float)):
            cond = _eval_numeric_condition(float(value), str(rule.get("Notes", "")))
            yn = cond if cond is not None else None
        elif isinstance(value, str):
            low = value.strip().lower()
            if low in {"yes", "true"}:
                yn = True
            elif low in {"no", "false"}:
                yn = False

        next_id: Optional[str] = None
        if yn is not None:
            next_id = str(rule.get("OnTrueNext" if yn else "OnFalseNext", "")).strip() or None
        else:
            # For non-boolean answers, default to OnTrueNext
            next_id = str(rule.get("OnTrueNext", "")).strip() or None

        if next_id is None:
            # Terminal without explicit action
            self.state.current_rule_id = None
            self.state.outcome = None
            return

        next_rule = self.rules.loc[next_id] if next_id in self.rules.index else None
        if next_rule is not None and self.is_action(next_rule):
            self.state.outcome = str(next_rule.get("Outcome", "")).strip() or None
            self.state.current_rule_id = None
        else:
            self.state.current_rule_id = next_id