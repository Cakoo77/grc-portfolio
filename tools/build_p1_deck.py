#!/usr/bin/env python3
"""Build the Project 1 executive briefing deck from the calculated assessment results."""
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p1_data as D

P1 = T.ROOT / "01-gap-assessment"
RESULTS = json.loads((P1 / "data/gap_assessment_results.json").read_text(encoding="utf-8"))
OUT = P1 / "deliverables/Orvanta-ISO27001-Executive-Briefing.pptx"
MASTER = json.loads((T.ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
TEAL, INK, MUTED, TINT, WHITE, ORANGE = (RGBColor.from_string(x) for x in (T.ACCENT, T.INK, T.MUTED, T.TINT, "FFFFFF", "B4541A"))
SHORT = {
    "GAP-01": "No approved scope, policy or objectives, so an auditor cannot begin.",
    "GAP-02": "Spending follows the last customer question, not the biggest risk.",
    "GAP-03": "One stolen password could reach production, data and payments.",
    "GAP-04": "Card numbers in tickets and 43 unmanaged laptops create breach exposure.",
    "GAP-05": "An intruder could stay for weeks because no one is watching.",
    "GAP-06": "A confused first hour prolongs outages and risks late reports.",
    "GAP-07": "If backups fail, ledgers and customer funds records are at risk.",
    "GAP-08": "Critical services run through suppliers nobody has assessed.",
    "GAP-09": "14% of Q3 2026 deployments reached production without review.",
    "GAP-10": "No audit or management review means Stage 2 cannot pass.",
}


def text(slide, x, y, w, h, value, size=14, bold=False, color=INK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = anchor
    para = frame.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = value
    run.font.size, run.font.bold, run.font.name, run.font.color.rgb = Pt(size), bold, T.FONT, color
    return box


def card(slide, x, y, w, h, fill=TINT):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.adjustments[0] = 0.06
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def badge(slide, x, y, d, value, fill=TEAL, size=14):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.fill.background()
    shape.shadow.inherit = False
    frame = shape.text_frame
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    para = frame.paragraphs[0]
    para.alignment = PP_ALIGN.CENTER
    run = para.add_run()
    run.text = str(value)
    run.font.size, run.font.bold, run.font.name, run.font.color.rgb = Pt(size), True, T.FONT, WHITE


def new_slide(prs, title, number, notes):
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.6), Inches(0.42), Inches(12.1), Inches(1.0)
    t.text_frame.word_wrap = True
    t.text_frame.vertical_anchor = MSO_ANCHOR.TOP
    t.text_frame.margin_left = t.text_frame.margin_top = 0
    para = t.text_frame.paragraphs[0]
    para.alignment = PP_ALIGN.LEFT
    run = para.add_run()
    run.text = title
    run.font.size, run.font.bold, run.font.name, run.font.color.rgb = Pt(30), True, T.FONT, TEAL
    text(slide, 0.6, 7.03, 10, 0.25, T.DISCLAIMER, 10, color=MUTED)
    text(slide, 11.7, 7.03, 1.03, 0.25, str(number), 10, color=MUTED, align=PP_ALIGN.RIGHT)
    slide.notes_slide.notes_text_frame.text = notes
    return slide


def main():
    s, counts, groups, pg = RESULTS["summary"], RESULTS["counts"], RESULTS["groups"], RESULTS["priority_gaps"]
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    prs.core_properties.title = "ISO/IEC 27001:2022 Gap Assessment: Executive Briefing"
    prs.core_properties.author = "Jahangir Shukurov"
    prs.core_properties.last_modified_by = "Jahangir Shukurov"
    prs.core_properties.subject = T.DISCLAIMER

    # 1 Title
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = TEAL
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(0.8), Inches(2.25), Inches(11.5), Inches(1.8)
    t.text_frame.word_wrap = True
    t.text_frame.margin_left = 0
    para = t.text_frame.paragraphs[0]
    para.alignment = PP_ALIGN.LEFT
    run = para.add_run()
    run.text = "ISO/IEC 27001:2022 Gap Assessment"
    run.font.size, run.font.bold, run.font.name, run.font.color.rgb = Pt(46), True, T.FONT, WHITE
    plate = card(slide, 0.8, 0.75, 0.8, 0.8, WHITE)
    plate.adjustments[0] = 0.14
    text(slide, 0.8, 0.75, 0.8, 0.8, "JS", 24, True, TEAL, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(slide, 1.8, 0.86, 8, 0.6, "Jahangir Shukurov  |  GRC Portfolio", 18, color=WHITE)
    text(slide, 0.8, 4.2, 11.5, 0.6, "Executive briefing for the Management Board of Orvanta Payments UAB", 22, color=WHITE)
    text(slide, 0.8, 4.85, 11.5, 0.4, "27 November 2026  |  Confidential (sample)", 16, color=RGBColor.from_string("DCEBEE"))
    text(slide, 0.8, 6.75, 11.5, 0.3, T.DISCLAIMER, 12, color=RGBColor.from_string("DCEBEE"))
    slide.notes_slide.notes_text_frame.text = "Purpose: agree the program and take five decisions. Evidence is simulated for this portfolio sample."

    # 2 Bottom line
    slide = new_slide(prs, "Certification by November 2027 is achievable if we start in December", 2,
                      "Open with the conclusion. Orvanta builds good technology, but the management system an auditor must test does not exist yet.")
    stats = [(f"{s['avg']:.1f}/5", "average maturity", "Target is 3 on every item"), (f"{s['pct']:.0%}", "already at target", f"{s['met']} of {s['total']} requirements"),
             (str(counts["P1"]), "P1 gaps", "Start within 90 days"), ("EUR 2.4M", "annual revenue at stake", "About 11% of FY2025 net revenue")]
    for i, (value, label, sub) in enumerate(stats):
        x = 0.6 + i * 3.1
        card(slide, x, 1.75, 2.85, 2.5)
        text(slide, x + 0.22, 2.0, 2.45, 0.9, value, 38, True, TEAL)
        text(slide, x + 0.22, 2.95, 2.45, 0.35, label, 15, True)
        text(slide, x + 0.22, 3.35, 2.45, 0.7, sub, 13, color=MUTED)
    text(slide, 0.6, 4.65, 12.1, 0.4, "What this means", 20, True, TEAL)
    text(slide, 0.6, 5.15, 12.1, 1.5, "Encryption, redundancy and infrastructure as code are real strengths. The gaps sit in governance, identity, detection and recovery. "
         "They are fixable within 12 months, with clear sponsorship, funding and engineering time.", 18)

    # 3 Chart
    slide = new_slide(prs, "Governance lags technology, and no clause area is near target", 3,
                      "Scores are averages from the workbook. Level 3 is the certification target. Physical and people controls score better because they are simpler for a cloud-hosted firm.")
    data = CategoryChartData()
    ordered = list(reversed(groups))
    data.categories = [g["name"] for g in ordered]
    data.add_series("Average maturity", [round(g["avg"], 1) for g in ordered])
    frame = slide.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.6), Inches(1.5), Inches(7.9), Inches(5.35), data)
    chart = frame.chart
    chart.has_legend = False
    chart.has_title = True
    chart.chart_title.text_frame.text = "Average maturity by area (target = 3)"
    chart.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
    chart.chart_title.text_frame.paragraphs[0].runs[0].font.bold = True
    chart.font.name, chart.font.size = T.FONT, Pt(12)
    plot = chart.plots[0]
    plot.gap_width = 45
    plot.has_data_labels = True
    plot.data_labels.number_format, plot.data_labels.number_format_is_linked = "0.0", False
    plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    plot.series[0].format.fill.solid()
    plot.series[0].format.fill.fore_color.rgb = TEAL
    va = chart.value_axis
    va.minimum_scale, va.maximum_scale, va.major_unit = 0, 4, 1
    va.major_gridlines.format.line.color.rgb = RGBColor.from_string("E3EAED")
    va.format.line.fill.background()
    chart.category_axis.format.line.color.rgb = RGBColor.from_string(T.RULE)
    weakest = min(groups, key=lambda g: g["avg"])
    best = max(groups, key=lambda g: g["avg"])
    for i, (head, body) in enumerate([("Weakest", f"{weakest['name'].split(' ', 1)[1]} at {weakest['avg']:.1f}: no audit, review or measurement yet"),
                                      ("Strongest", f"{best['name']} at {best['avg']:.1f}: production runs in AWS and offices are simple"),
                                      ("Why it matters", "Certification tests the management system, not only the technology")]):
        y = 1.65 + i * 1.72
        card(slide, 8.85, y, 3.88, 1.55)
        text(slide, 9.05, y + 0.14, 3.5, 0.3, head, 15, True, TEAL)
        text(slide, 9.05, y + 0.5, 3.5, 1.0, body, 14)

    # 4 Top gaps
    slide = new_slide(prs, "Five gaps carry the highest priority scores", 4,
                      "These are the top five of ten. The ranking uses average priority score: gap size, certification blocker and attack relevance. Identity also matters: it has the most P1 items among technical gaps.")
    for i, g in enumerate(pg[:5]):
        y = 1.55 + i * 1.07
        card(slide, 0.6, y, 12.13, 0.95)
        badge(slide, 0.8, y + 0.2, 0.55, i + 1, size=16)
        text(slide, 1.55, y + 0.14, 3.9, 0.7, g["title"], 16, True, anchor=MSO_ANCHOR.TOP)
        text(slide, 5.5, y + 0.14, 5.3, 0.7, SHORT[g["id"]], 14)
        text(slide, 10.95, y + 0.14, 1.65, 0.7, f"{g['owner']}\n{g['target']}", 11, color=MUTED)

    # 5 Attack path
    slide = new_slide(prs, "One realistic attack path runs through six open gaps", 5,
                      "Illustrative scenario built from observed gaps, not evidence of an attack. Technique IDs refer to MITRE ATT&CK. Breaking any step stops the path; quick wins close steps 3, 4 and 6 first.")
    for i, s in enumerate(D.ATTACK_PATH):
        col, row = i % 3, i // 3
        x, y = 0.6 + col * 4.1, 1.5 + row * 2.32
        card(slide, x, y, 3.93, 2.15)
        badge(slide, x + 0.2, y + 0.2, 0.55, s[0], ORANGE if s[1] == "Detection gap" else TEAL, 16)
        text(slide, x + 0.95, y + 0.17, 2.85, 0.4, s[3], 17, True)
        text(slide, x + 0.95, y + 0.55, 2.85, 0.3, s[2], 11, color=MUTED)
        text(slide, x + 0.2, y + 1.05, 3.55, 1.0, s[8], 14)
    text(slide, 0.6, 6.2, 12.1, 0.6, "Breaking any one step stops the path. Quick wins start closing steps 3, 4 and 6 within 30 days.", 18, True, TEAL)

    # 6 Quick wins
    slide = new_slide(prs, "Eight quick wins cut real risk within 30 days", 6,
                      "These need little or no new budget. Each one creates evidence for the auditor. Ask owners to confirm dates in this meeting.")
    short = ["Enable CloudTrail in the legacy account", "Purge card numbers from tickets, add redaction", "Enforce MFA on Kyrovia and agent Zendesk", "Cut Okta super admins to two plus break-glass",
             "Protect all production repositories", "Remove leaver access within 24 hours", "Run and record one full database restore", "Publish incident call list and report channel"]
    for i, (q, label) in enumerate(zip(D.QUICK_WINS, short)):
        col, row = i % 2, i // 2
        x, y = 0.6 + col * 6.2, 1.55 + row * 1.32
        card(slide, x, y, 5.93, 1.15)
        badge(slide, x + 0.18, y + 0.24, 0.68, f"{q[5]}d", size=14)
        text(slide, x + 1.05, y + 0.14, 4.7, 0.65, label, 15, True)
        text(slide, x + 1.05, y + 0.78, 4.7, 0.3, WHO[q[4]], 12, color=MUTED)

    # 6 Roadmap
    slide = new_slide(prs, "A four-phase plan reaches the certificate decision by 30 November 2027", 7,
                      "Stage 2 in October leaves a buffer to close findings. The auditor should be booked by March 2027. Controls need months of operating records before the audit.")
    phases = [("Foundation", "Dec 26 to Mar 27", ["Program and budget", "Scope and policy", "Risk assessment", "Statement of Applicability"], 0.6, 3.0, RGBColor.from_string("0F5C6E")),
              ("Build", "Jan to Jun 27", ["Policies and procedures", "Identity and laptops", "Change control", "Backups, BIA, suppliers"], 3.7, 3.0, RGBColor.from_string("2F7B8D")),
              ("Operate", "Feb to Nov 27", ["SIEM and daily triage", "Incident playbooks", "KPI dashboard", "Awareness program"], 6.8, 3.0, RGBColor.from_string("4C8F9F")),
              ("Certify", "Jul to Nov 27", ["Internal audit: Jul", "Management review: Aug", "Stage 1: Sep", "Stage 2: Oct"], 9.9, 2.83, ORANGE)]
    for name, span, items, x, w, color in phases:
        arrow = slide.shapes.add_shape(MSO_SHAPE.PENTAGON, Inches(x), Inches(1.65), Inches(w), Inches(1.15))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = color
        arrow.line.fill.background()
        arrow.shadow.inherit = False
        text(slide, x + 0.2, 1.78, w - 0.55, 0.45, name, 20, True, WHITE)
        text(slide, x + 0.2, 2.26, w - 0.55, 0.35, span, 13, color=WHITE)
        card(slide, x, 3.0, w - 0.12, 3.75)
        for j, item in enumerate(items):
            text(slide, x + 0.2, 3.2 + j * 0.87, w - 0.5, 0.75, item, 15)

    # 7 Decisions
    slide = new_slide(prs, "Five decisions are needed from this Board", 8,
                      "Close by asking for each decision in turn. Decision 2 and 3 have the largest effect on whether the plan holds.")
    decisions = [("Sponsor the ISMS program as a board-level priority", "R-CEO", "30 Nov 2026"), ("Fund the roadmap, with a third security hire and a SIEM", "R-CEO", "15 Dec 2026"),
                 ("Move the CISO reporting line from the CTO to the CEO", "R-CEO", "31 Dec 2026"), ("Include the Baku subsidiary in the ISMS scope", "R-CTO", "15 Jan 2027"),
                 ("Commission a QSA review of PCI DSS scope and level", "R-CISO", "31 Jan 2027")]
    for i, (decision, owner, by) in enumerate(decisions):
        y = 1.55 + i * 1.07
        card(slide, 0.6, y, 12.13, 0.95)
        badge(slide, 0.8, y + 0.2, 0.55, i + 1, ORANGE, 16)
        text(slide, 1.55, y + 0.25, 7.4, 0.5, decision, 17, True)
        text(slide, 9.15, y + 0.28, 1.95, 0.45, WHO[owner], 13, color=MUTED)
        text(slide, 11.2, y + 0.28, 1.4, 0.45, by, 13, True, TEAL)

    prs.save(OUT)
    T.to_pdf(OUT)
    print("Saved", OUT)


if __name__ == "__main__":
    main()
