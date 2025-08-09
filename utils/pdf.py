from typing import Dict, List
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


def build_pdf_summary(branding: Dict[str, str], outcome: str, audit_trail: List[Dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph(branding.get("hospital_name", "Hospital"), styles["Title"]))
    story.append(Paragraph("Cervical Screening Decision Summary", styles["h2"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Outcome: <b>{outcome or 'Not determined'}</b>", styles["h3"]))
    story.append(Spacer(1, 12))

    # Audit trail table
    data = [["RuleID", "Question", "Answer"]]
    for row in audit_trail:
        data.append([row.get("RuleID", ""), row.get("QuestionText", ""), str(row.get("Answer", ""))])
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ])
    )
    story.append(table)

    doc.build(story)
    return buffer.getvalue()