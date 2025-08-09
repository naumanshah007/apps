import pandas as pd
from engine.decision_engine import DecisionEngine


def minimal_rules() -> pd.DataFrame:
    data = [
        {"RuleID": "F1-01", "Variable": "age_ge_25", "QuestionText": "Age >= 25?", "AnswerType": "Yes/No", "Options": "", "OnTrueNext": "F1-02", "OnFalseNext": "F1-ACT1", "Outcome": "", "Notes": "", "SourceFigure": "Fig1"},
        {"RuleID": "F1-02", "Variable": "hpv_detected", "QuestionText": "HPV detected?", "AnswerType": "Yes/No", "Options": "", "OnTrueNext": "F1-ACT2", "OnFalseNext": "F1-ACT3", "Outcome": "", "Notes": "", "SourceFigure": "Fig3"},
        {"RuleID": "F1-ACT1", "Variable": "", "QuestionText": "", "AnswerType": "Action", "Options": "", "OnTrueNext": "", "OnFalseNext": "", "Outcome": "Invite at next scheduled visit", "Notes": "", "SourceFigure": "Fig1"},
        {"RuleID": "F1-ACT2", "Variable": "", "QuestionText": "", "AnswerType": "Action", "Options": "", "OnTrueNext": "", "OnFalseNext": "", "Outcome": "Colposcopy", "Notes": "", "SourceFigure": "Fig3"},
        {"RuleID": "F1-ACT3", "Variable": "", "QuestionText": "", "AnswerType": "Action", "Options": "", "OnTrueNext": "", "OnFalseNext": "", "Outcome": "Return for screening in 5 years", "Notes": "", "SourceFigure": "Fig3"},
    ]
    return pd.DataFrame(data)


def test_path_yes_hpv():
    df = minimal_rules()
    engine = DecisionEngine(df, "F1-01")
    engine.answer_current(True)   # age >=25 -> F1-02
    engine.answer_current(True)   # hpv detected -> F1-ACT2 (Colposcopy)
    assert engine.state.outcome == "Colposcopy"


def test_path_no_hpv():
    df = minimal_rules()
    engine = DecisionEngine(df, "F1-01")
    engine.answer_current(True)
    engine.answer_current(False)
    assert engine.state.outcome == "Return for screening in 5 years"


if __name__ == "__main__":
    test_path_yes_hpv()
    test_path_no_hpv()
    print("Sample scenarios passed")