import os
import json
from typing import Dict, List

import pandas as pd
from PIL import Image

try:
    import pytesseract
except Exception:
    pytesseract = None

try:
    import easyocr
except Exception:
    easyocr = None

RULES_XLSX = os.path.abspath("./data/screening_rules_master_integrated.xlsx")
IMAGES_DIR = os.path.abspath("./images")

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


def ensure_rules_workbook() -> None:
    os.makedirs(os.path.dirname(RULES_XLSX), exist_ok=True)
    if not os.path.exists(RULES_XLSX):
        df = pd.DataFrame(columns=COLUMNS)
        with pd.ExcelWriter(RULES_XLSX, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Rules", index=False)
        print(f"Initialized empty workbook at {RULES_XLSX}")


def run_tesseract(image_path: str) -> str:
    if pytesseract is None:
        return ""
    img = Image.open(image_path)
    custom_oem_psm_config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(img, config=custom_oem_psm_config)
    return text


def run_easyocr(image_path: str, reader=None) -> str:
    if easyocr is None:
        return ""
    if reader is None:
        reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)


def ocr_all() -> Dict[str, str]:
    files = [
        "1.jpg","2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.jpg","8.jpg","9.jpg","10.jpg","table.jpg"
    ]
    out: Dict[str, str] = {}
    reader = None
    if easyocr is not None:
        reader = easyocr.Reader(["en"], gpu=False)
    for fname in files:
        path = os.path.join(IMAGES_DIR, fname)
        if not os.path.exists(path):
            print(f"Missing: {path}")
            continue
        t1 = run_tesseract(path)
        t2 = run_easyocr(path, reader=reader)
        merged = "\n".join([s for s in [t1, t2] if s])
        out[fname] = merged
    return out


def main():
    ensure_rules_workbook()
    os.makedirs(IMAGES_DIR, exist_ok=True)
    texts = ocr_all()
    out_json = os.path.abspath("./data/ocr_output.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    print(f"Saved OCR text to {out_json}")
    print("Next: Parse OCR into atomic rules and populate the Excel (manual review may be needed).")


if __name__ == "__main__":
    main()