import os
import pandas as pd

OUT = os.path.abspath("./data/screening_rules_master_integrated.xlsx")
COLUMNS = [
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

os.makedirs(os.path.dirname(OUT), exist_ok=True)
df = pd.DataFrame(columns=COLUMNS)
with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Rules", index=False)
print(f"Wrote empty rules workbook to {OUT}")