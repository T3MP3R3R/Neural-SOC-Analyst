import io
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

def _parse(raw):
    """Safely parse analysis whether it's a dict or a JSON string."""
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(str(raw).replace("```json","").replace("```","").strip())
    except Exception:
        return {
            "risk_level":    "Unknown",
            "risk_score":    50,
            "explanation":   str(raw),
            "recommendation":"Manual review required."
        }


def generate_pdf(history):
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=18*mm, bottomMargin=18*mm
    )

    # ── Styles ──────────────────────────────────────
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title", fontName="Helvetica-Bold", fontSize=16,
        textColor=colors.HexColor("#00ccff"), spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "Sub", fontName="Helvetica", fontSize=8,
        textColor=colors.HexColor("#5e8fa8"), spaceAfter=12
    )
    section_style = ParagraphStyle(
        "Section", fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.HexColor("#00ccff"), spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=8,
        textColor=colors.HexColor("#b8ddf0"), leading=13
    )

    # ── Color map ────────────────────────────────────
    risk_colors = {
        "high":    colors.HexColor("#ff1f3d"),
        "medium":  colors.HexColor("#ff9300"),
        "low":     colors.HexColor("#00ff88"),
        "unknown": colors.HexColor("#5e8fa8"),
    }

    # ── Build story ──────────────────────────────────
    story = []

    story.append(Paragraph("N.S.A // NEURAL SOC ANALYST", title_style))
    story.append(Paragraph(
        f"SOC INCIDENT REPORT  ·  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  ·  Incidents: {len(history)}",
        sub_style
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#112030")))
    story.append(Spacer(1, 8))

    if not history:
        story.append(Paragraph("No incidents recorded.", body_style))
    else:
        # Summary table
        high = sum(1 for i in history if _parse(i["analysis"]).get("risk_level","").lower()=="high")
        med  = sum(1 for i in history if _parse(i["analysis"]).get("risk_level","").lower()=="medium")
        low  = sum(1 for i in history if _parse(i["analysis"]).get("risk_level","").lower()=="low")

        story.append(Paragraph("EXECUTIVE SUMMARY", section_style))

        summary_data = [
            ["TOTAL INCIDENTS", "HIGH RISK", "MEDIUM RISK", "LOW RISK"],
            [str(len(history)), str(high), str(med), str(low)]
        ]
        summary_table = Table(summary_data, colWidths=[42*mm]*4)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND",   (0,0),(-1,0), colors.HexColor("#070e18")),
            ("TEXTCOLOR",    (0,0),(-1,0), colors.HexColor("#00ccff")),
            ("BACKGROUND",   (0,1),(-1,-1),colors.HexColor("#02040a")),
            ("TEXTCOLOR",    (1,1),(1,1),  colors.HexColor("#ff1f3d")),
            ("TEXTCOLOR",    (2,1),(2,1),  colors.HexColor("#ff9300")),
            ("TEXTCOLOR",    (3,1),(3,1),  colors.HexColor("#00ff88")),
            ("TEXTCOLOR",    (0,1),(0,1),  colors.HexColor("#b8ddf0")),
            ("FONTNAME",     (0,0),(-1,-1),"Helvetica-Bold"),
            ("FONTSIZE",     (0,0),(-1,0), 8),
            ("FONTSIZE",     (0,1),(-1,-1),14),
            ("ALIGN",        (0,0),(-1,-1),"CENTER"),
            ("VALIGN",       (0,0),(-1,-1),"MIDDLE"),
            ("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#070e18"),colors.HexColor("#050a12")]),
            ("BOX",          (0,0),(-1,-1),0.5,colors.HexColor("#112030")),
            ("INNERGRID",    (0,0),(-1,-1),0.5,colors.HexColor("#112030")),
            ("TOPPADDING",   (0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))

        # Individual incidents
        story.append(Paragraph("INCIDENT DETAILS", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#112030")))

        for idx, item in enumerate(history, 1):
            a = _parse(item["analysis"])
            lvl   = (a.get("risk_level","unknown")).lower()
            score = a.get("risk_score", 0)
            color = risk_colors.get(lvl, risk_colors["unknown"])

            story.append(Spacer(1, 8))

            # Incident header row
            hdr_data = [[
                f"#{idx:03d}  RISK: {lvl.upper()}",
                f"SCORE: {score}/100"
            ]]
            hdr_table = Table(hdr_data, colWidths=[130*mm, 40*mm])
            hdr_table.setStyle(TableStyle([
                ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#070e18")),
                ("TEXTCOLOR",   (0,0),(0,0),   color),
                ("TEXTCOLOR",   (1,0),(1,0),   color),
                ("FONTNAME",    (0,0),(-1,-1), "Helvetica-Bold"),
                ("FONTSIZE",    (0,0),(-1,-1), 9),
                ("ALIGN",       (1,0),(1,0),   "RIGHT"),
                ("BOX",         (0,0),(-1,-1), 0.5, colors.HexColor("#112030")),
                ("LEFTPADDING", (0,0),(0,0),   6),
                ("RIGHTPADDING",(1,0),(1,0),   6),
                ("TOPPADDING",  (0,0),(-1,-1), 5),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ]))
            story.append(hdr_table)

            # Input artifact
            raw_input = str(item.get("input",""))[:300]
            if len(str(item.get("input",""))) > 300:
                raw_input += "..."

            detail_data = [
                ["INPUT ARTIFACT", raw_input],
                ["EXPLANATION",   a.get("explanation","N/A")],
                ["RECOMMENDATION",a.get("recommendation","N/A")],
            ]
            detail_table = Table(detail_data, colWidths=[38*mm, 132*mm])
            detail_table.setStyle(TableStyle([
                ("BACKGROUND",   (0,0),(0,-1), colors.HexColor("#050a12")),
                ("BACKGROUND",   (1,0),(1,-1), colors.HexColor("#02040a")),
                ("TEXTCOLOR",    (0,0),(0,-1), colors.HexColor("#5e8fa8")),
                ("TEXTCOLOR",    (1,0),(1,-1), colors.HexColor("#b8ddf0")),
                ("FONTNAME",     (0,0),(0,-1), "Helvetica-Bold"),
                ("FONTNAME",     (1,0),(1,-1), "Helvetica"),
                ("FONTSIZE",     (0,0),(-1,-1),8),
                ("VALIGN",       (0,0),(-1,-1),"TOP"),
                ("BOX",          (0,0),(-1,-1),0.5, colors.HexColor("#112030")),
                ("INNERGRID",    (0,0),(-1,-1),0.5, colors.HexColor("#0a1422")),
                ("LEFTPADDING",  (0,0),(-1,-1),5),
                ("RIGHTPADDING", (0,0),(-1,-1),5),
                ("TOPPADDING",   (0,0),(-1,-1),5),
                ("BOTTOMPADDING",(0,0),(-1,-1),5),
                ("WORDWRAP",     (1,0),(1,-1), True),
            ]))
            story.append(detail_table)

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#112030")))
    story.append(Paragraph(
        f"END OF REPORT  ·  NSA v2.0.0  ·  GROQ / LLAMA-3.1  ·  {datetime.now().strftime('%Y-%m-%d')}",
        ParagraphStyle("Footer", fontName="Helvetica", fontSize=7, textColor=colors.HexColor("#112030"), spaceBefore=6, alignment=1)
    ))

    doc.build(story)
    buf.seek(0)
    return buf