import os
import json
import pandas as pd
from engine.rules_loader import load_rules_excel, normalize_rules, integrity_checks

RULES_XLSX = os.path.abspath("./data/screening_rules_master_integrated.xlsx")
START_RULE_ID = "F1-01"


def main():
    if not os.path.exists(RULES_XLSX):
        raise SystemExit(f"Rules file missing: {RULES_XLSX}")
    df = normalize_rules(load_rules_excel(RULES_XLSX))
    report = integrity_checks(df, START_RULE_ID)

    issues = {
        "missing_required_columns": report.missing_required_columns,
        "missing_on_true_false": report.missing_on_true_false,
        "missing_outcome_for_actions": report.missing_outcome_for_actions,
        "invalid_references": report.invalid_references,
        "orphan_nodes": report.orphan_nodes,
        "start_node": report.start_node,
    }

    out_json = os.path.abspath("./data/rules_validation.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2)
    print(f"Saved validation JSON to {out_json}")

    # Flat CSV of unresolved refs + orphans
    rows = []
    for r in report.invalid_references:
        rows.append({"issue": "invalid_reference", "id": r})
    for r in report.orphan_nodes:
        rows.append({"issue": "orphan_node", "id": r})
    out_csv = os.path.abspath("./data/rules_validation.csv")
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"Saved validation CSV to {out_csv}")


if __name__ == "__main__":
    main()