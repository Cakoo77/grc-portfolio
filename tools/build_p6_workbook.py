#!/usr/bin/env python3
"""Build the Project 6 third-party risk workbook: inventory, tiering, questionnaire, scored assessments, findings, contracts and register."""
import json
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, PatternFill
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, str(Path(__file__).parent))
import p6_data as D
from build_p1_workbook import BOX, F, INPUT, TINTED, WRAP, header, title
from build_p2_workbook import ROLE_LOOKUP, list_validation, write_rows
from doc_template import ACCENT, DISCLAIMER, MUTED, ROOT

MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
VEN = {v["id"]: v for v in MASTER["vendors"]}
OUT = ROOT / "06-third-party-risk/deliverables/Orvanta-Third-Party-Risk-Workbook.xlsx"
GREEN, AMBER, ORANGE, RED, GREY = "CFE6D8", "FBE9B0", "F6C08F", "F3B9A3", "E3E8EA"
RATING_FILL = {"Low": GREEN, "Medium": AMBER, "High": ORANGE, "Critical": RED}
day = lambda text: datetime.strptime(text, "%d %b %Y").date()
SHORT = {"VEN-02": "Tessarin", "VEN-04": "Vaskora Bank", "VEN-05": "Helvora"}


def fills(ws, rng, mapping):
    for label, color in mapping.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))


def build():
    wb = Workbook()
    readme = wb.active
    readme.title = "README"
    title(readme, "Third-Party Risk Workbook")
    readme.column_dimensions["A"].width = 24
    readme.column_dimensions["B"].width = 100
    notes = [("Client", "Orvanta Payments UAB (fictional)"), ("Document ID", f"ORV-TPRM-004, version 1.0, {D.AS_OF}"), ("Prepared by", "Jahangir Shukurov"),
             ("Classification", "Confidential (sample)"),
             ("Evidence basis", "Supplier answers, findings and contract terms are simulated. Real vendors appear only as tools Orvanta uses, and nothing here describes their actual security."),
             ("Originality", "The 60 questions are written for this engagement. They are not copied from any published questionnaire."),
             ("", ""), ("How to use", ""),
             ("1. Dashboard", "Live counts: suppliers by tier, assessment coverage, ratings, open findings and contract gaps."),
             ("2. Inventory", "All 20 suppliers. Enter the three ratings and the tier is calculated. Review dates follow from the tier."),
             ("3. Questionnaire", "60 questions in 10 domains, with the evidence asked for and the weight of each."),
             ("4. Assessments", "Answers from three suppliers. Scores, domain results and ratings are calculated on the Scores sheet."),
             ("5. Scores", "Score by domain and overall rating for each assessed supplier."),
             ("6. Findings", "Findings with required remediation, due dates and interim controls."),
             ("7. Contracts", "Fifteen contract clauses checked for each assessed supplier."),
             ("8. Register", "A simplified register of ICT services that support critical or important functions."),
             ("9. Criteria", "Tiering rules, rating bands and answer scores. Change a band and ratings recalculate."),
             ("10. Roles", "Named role-holders from the Company Fact Sheet."),
             ("", ""), ("Editing", "Yellow cells are inputs. Tiers, scores, ratings, dates and counts are formulas."),
             ("Register note", "The Register sheet is a working view. The official register of information under DORA uses the templates in Commission Implementing Regulation (EU) 2024/2956.")]
    for i, (a, b) in enumerate(notes, start=4):
        readme.cell(row=i, column=1, value=a).font = F(bold=True, size=10)
        cell = readme.cell(row=i, column=2, value=b)
        cell.font, cell.alignment = F(size=10), WRAP

    ro = wb.create_sheet("Roles")
    title(ro, "Role-holders (from Company Fact Sheet)")
    header(ro, 4, ["Role ID", "Name", "Title", "Location"], [12, 24, 48, 10])
    write_rows(ro, [[r["id"], r["name"], r["title"], r["location"]] for r in MASTER["roles"]], [12, 24, 48, 10])

    # Criteria ------------------------------------------------------------------------------
    cr = wb.create_sheet("Criteria")
    title(cr, "Tiering, scoring and rating criteria")
    widths = [26, 16, 70]
    header(cr, 4, ["Rating input", "Score", "Meaning"], widths)
    rows = [["Data sensitivity", 0, "No Orvanta data"], ["Data sensitivity", 1, "Internal data or metadata only"], ["Data sensitivity", 2, "Confidential data, including personal data"],
            ["Data sensitivity", 3, "Restricted data: identity documents, cardholder data or credentials"],
            ["Business criticality", 1, "Service can stop for a week without customer impact"], ["Business criticality", 2, "Service supports a High-criticality process, with a workaround"],
            ["Business criticality", 3, "Service supports a critical process, with no quick workaround"],
            ["System access", 0, "No access to Orvanta systems"], ["System access", 1, "Named, limited access"], ["System access", 2, "Administrative access or many users"]]
    write_rows(cr, rows, widths, 5, center=(2,))
    cr["A17"] = "Tier rule"
    cr["A17"].font = F(bold=True, color=ACCENT, size=10)
    for i, line in enumerate(["Tier 1: data sensitivity is 3, or business criticality is 3.", "Tier 2: data sensitivity is 2, or business criticality is 2, or system access is 1 or more.", "Tier 3: everything else."], start=18):
        cr.cell(row=i, column=1, value=line).font = F()
    cr["A23"] = "Rating bands (minimum share of points)"
    cr["A23"].font = F(bold=True, color=ACCENT, size=10)
    header(cr, 24, ["Rating", "Minimum score", "Meaning"])
    write_rows(cr, [list(b) for b in D.RATING_BANDS], widths, 25, center=(2,), inputs=(2,))
    for r in range(25, 29):
        cr.cell(row=r, column=2).number_format = "0%"
        cr.cell(row=r, column=1).fill = PatternFill("solid", fgColor=RATING_FILL[cr.cell(row=r, column=1).value])
    cr["A30"] = "Key-question rule: a No on any key question means the rating cannot be better than High."
    cr["A30"].font = F(color=MUTED)
    cr["A32"] = "Answer scores"
    cr["A32"].font = F(bold=True, color=ACCENT, size=10)
    header(cr, 33, ["Answer", "Share of points", "Meaning"])
    write_rows(cr, [["Yes", 1, "In place, with evidence"], ["Partial", 0.5, "In place in part, or without full evidence"], ["No", 0, "Not in place"], ["N/A", "-", "Does not apply to the service. Excluded from the score"]], widths, 34, center=(2,))

    # Questionnaire and assessments ---------------------------------------------------------
    qs = wb.create_sheet("Questionnaire")
    title(qs, "Supplier security questionnaire")
    widths = [7, 34, 84, 46, 8, 8]
    header(qs, 4, ["ID", "Domain", "Question", "Evidence we ask for", "Key", "Weight"], widths)
    rows = [[f"Q{n:02d}", D.DOMAINS[(n - 1) // 6], q[0], q[1], "Yes" if q[2] else "No", f'=IF(E{n + 4}="Yes",2,1)'] for n, q in enumerate(D.QUESTIONS, start=1)]
    q_last = write_rows(qs, rows, widths, center=(1, 5, 6), inputs=(5,))
    list_validation(qs, f"E5:E{q_last}", '"Yes,No"')
    qs.freeze_panes = "C5"
    qs.auto_filter.ref = f"A4:F{q_last}"

    asx = wb.create_sheet("Assessments")
    title(asx, "Assessment answers and scores")
    asx["A3"] = "Answers are inputs. Points and maximum points are formulas. N/A answers are left out of the score."
    asx["A3"].font = F(color=MUTED)
    cols = ["ID", "Domain", "Question", "Key", "Weight"]
    for v in D.ASSESSED:
        cols += [f"{SHORT[v]} answer", f"{SHORT[v]} points", f"{SHORT[v]} maximum"]
    widths = [7, 30, 70, 7, 8] + [12, 9, 10] * 3
    header(asx, 4, cols, widths)
    rows = []
    for n, q in enumerate(D.QUESTIONS, start=1):
        r = n + 4
        row = [f"Q{n:02d}", D.DOMAINS[(n - 1) // 6], q[0], f"=Questionnaire!E{r}", f"=Questionnaire!F{r}"]
        for k, v in enumerate(D.ASSESSED):
            ans, pts, mx = L(6 + k * 3), L(7 + k * 3), L(8 + k * 3)
            letter = D.ANSWERS[v].replace(" ", "")[n - 1]
            row += [D.ANSWER[letter], f'=IF({ans}{r}="N/A",0,$E{r}*IF({ans}{r}="Yes",1,IF({ans}{r}="Partial",0.5,0)))', f'=IF({ans}{r}="N/A",0,$E{r})']
        rows.append(row)
    a_last = write_rows(asx, rows, widths, center=(1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), inputs=(6, 9, 12))
    for k in range(3):
        col = L(6 + k * 3)
        list_validation(asx, f"{col}5:{col}{a_last}", '"Yes,Partial,No,N/A"')
        fills(asx, f"{col}5:{col}{a_last}", {"Yes": GREEN, "Partial": AMBER, "No": RED, "N/A": GREY})
    asx.freeze_panes = "D5"
    asx.auto_filter.ref = f"A4:{L(len(cols))}{a_last}"
    rng = lambda col: f"Assessments!${col}$5:${col}${a_last}"

    sc = wb.create_sheet("Scores")
    title(sc, "Assessment scores by domain")
    widths = [38, 16, 16, 16]
    header(sc, 4, ["Domain"] + [SHORT[v] for v in D.ASSESSED], widths)
    for i, dom in enumerate(D.DOMAINS, start=5):
        values = [dom] + [f"=SUMIF({rng('B')},$A{i},{rng(L(7 + k * 3))})/SUMIF({rng('B')},$A{i},{rng(L(8 + k * 3))})" for k in range(3)]
        for c, v in enumerate(values, start=1):
            cell = sc.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            if c > 1:
                cell.number_format, cell.alignment = "0%", Alignment(horizontal="center")
    labels = [("Overall score", lambda k: f"=SUM({rng(L(7 + k * 3))})/SUM({rng(L(8 + k * 3))})"),
              ("Key questions answered No", lambda k: f'=COUNTIFS({rng("D")},"Yes",{rng(L(6 + k * 3))},"No")'),
              ("Rating", lambda k: f'=IF({L(2 + k)}16<Criteria!$B$27,"Critical",IF(OR({L(2 + k)}16<Criteria!$B$26,{L(2 + k)}17>0),"High",IF({L(2 + k)}16<Criteria!$B$25,"Medium","Low")))'),
              ("Findings raised", lambda k: f"=COUNTIF(Findings!$C$5:$C$40,{L(2 + k)}$4)")]
    for i, (label, make) in enumerate(labels, start=16):
        sc.cell(row=i, column=1, value=label).font = F(bold=True)
        sc.cell(row=i, column=1).border = BOX
        for k in range(3):
            cell = sc.cell(row=i, column=2 + k, value=make(k))
            cell.font, cell.border, cell.alignment = F(bold=True), BOX, Alignment(horizontal="center")
            if i == 16:
                cell.number_format = "0%"
    fills(sc, "B18:D18", RATING_FILL)
    from openpyxl.formatting.rule import ColorScaleRule
    sc.conditional_formatting.add("B5:D14", ColorScaleRule(start_type="num", start_value=0.2, start_color="E9805F", mid_type="num", mid_value=0.7, mid_color="FBE3A8", end_type="num", end_value=1, end_color="9CCFB5"))
    chart = BarChart()
    chart.type, chart.style, chart.title = "bar", 10, "Score by domain"
    chart.add_data(Reference(sc, min_col=2, max_col=4, min_row=4, max_row=14), titles_from_data=True)
    chart.set_categories(Reference(sc, min_col=1, min_row=5, max_row=14))
    chart.y_axis.delete = chart.x_axis.delete = False
    chart.x_axis.scaling.orientation = "maxMin"
    chart.y_axis.scaling.min, chart.y_axis.scaling.max, chart.y_axis.number_format = 0, 1, "0%"
    for series, color in zip(chart.series, (ACCENT, "79B4C1", "B4541A")):
        series.graphicalProperties.solidFill = color
        series.graphicalProperties.line.solidFill = color
    chart.height, chart.width = 11, 17
    sc.add_chart(chart, "F4")

    # Findings ------------------------------------------------------------------------------
    fd = wb.create_sheet("Findings")
    title(fd, "Supplier findings and remediation")
    fd["A3"] = f"Status as of {D.AS_OF}. Days to due and schedule are formulas, using the as-of date on the Dashboard."
    fd["A3"].font = F(color=MUTED)
    widths = [8, 9, 14, 9, 58, 14, 50, 13, 11, 20, 50, 12, 10, 11]
    header(fd, 4, ["ID", "Supplier ID", "Supplier", "Severity", "Finding", "Questions", "What Orvanta requires", "Due date", "Owner ID", "Owner", "Interim control", "Status", "Days to due", "Schedule"], widths)
    rows = [[f[0], f[1], SHORT[f[1]], f[2], f[3], f[4], f[5], day(f[6]), D.VENDORS[f[1]][0], "=" + ROLE_LOOKUP.format(cell=f"I{i}"), f[7], "Open",
             f'=IF(L{i}="Closed","",H{i}-Dashboard!$B$4)', f'=IF(L{i}="Closed","Closed",IF(H{i}<Dashboard!$B$4,"Overdue","On time"))'] for i, f in enumerate(D.FINDINGS, start=5)]
    f_last = write_rows(fd, rows, widths, center=(1, 2, 4, 6, 8, 9, 12, 13, 14), inputs=(8, 12))
    for r in range(5, f_last + 1):
        fd.cell(row=r, column=8).number_format = "DD MMM YYYY"
    list_validation(fd, f"L5:L{f_last}", '"Open,In progress,Closed"')
    fills(fd, f"D5:D{f_last}", RATING_FILL)
    fills(fd, f"N5:N{f_last}", {"Overdue": RED, "On time": AMBER, "Closed": GREEN})
    fd.freeze_panes = "E5"
    fd.auto_filter.ref = f"A4:N{f_last}"

    # Contracts -----------------------------------------------------------------------------
    ct = wb.create_sheet("Contracts")
    title(ct, "Contract security clause checklist")
    ct["A3"] = "Status before remediation, taken from the signed contracts. Counts are formulas."
    ct["A3"].font = F(color=MUTED)
    widths = [5, 30, 70, 14, 14, 14]
    header(ct, 4, ["#", "Clause", "What it must cover"] + [SHORT[v] for v in D.ASSESSED], widths)
    c_last = write_rows(ct, [[n, c[0], c[1], *c[2]] for n, c in enumerate(D.CLAUSES, start=1)], widths, center=(1, 4, 5, 6), inputs=(4, 5, 6))
    list_validation(ct, f"D5:F{c_last}", '"Present,Partial,Missing,N/A"')
    fills(ct, f"D5:F{c_last}", {"Present": GREEN, "Partial": AMBER, "Missing": RED})
    for i, label in enumerate(("Present", "Partial", "Missing"), start=c_last + 2):
        ct.cell(row=i, column=3, value=f"Clauses {label.lower()}").font = F(bold=True)
        for col in "DEF":
            cell = ct.cell(row=i, column="ABCDEF".index(col) + 1, value=f'=COUNTIF({col}5:{col}{c_last},"{label}")')
            cell.font, cell.alignment, cell.border = F(bold=True), Alignment(horizontal="center"), BOX
    ct.freeze_panes = "D5"

    # Inventory -----------------------------------------------------------------------------
    inv = wb.create_sheet("Inventory")
    title(inv, "Supplier inventory and tiering")
    inv["A3"] = "Enter the three ratings and the tier is calculated. Rating of the three suppliers assessed in this project comes from the Scores sheet."
    inv["A3"].font = F(color=MUTED)
    cols = ["ID", "Supplier", "Service", "Owner ID", "Owner", "Data sensitivity", "Business criticality", "System access", "Tier", "Preliminary tier", "Supports a critical function",
            "Last assessed", "Rating", "Review cycle (months)", "Next review", "Review status", "Contract renewal", "Contract checklist", "Open findings"]
    widths = [9, 28, 38, 11, 20, 10, 10, 9, 8, 10, 10, 13, 10, 9, 13, 13, 13, 13, 9]
    header(inv, 4, cols, widths)
    rows = []
    for i, (vid, v) in enumerate(D.VENDORS.items(), start=5):
        owner, data, crit, access, assessed, rating, renewal, checklist = v
        if vid in D.ASSESSED:
            rating_cell = f"=INDEX(Scores!$B$18:$D$18,{D.ASSESSED.index(vid) + 1})"
        else:
            rating_cell = rating or "-"
        rows.append([vid, VEN[vid]["name"], VEN[vid]["service"], owner, "=" + ROLE_LOOKUP.format(cell=f"D{i}"), data, crit, access,
                     f'=IF(OR(F{i}=3,G{i}=3),"Tier 1",IF(OR(F{i}=2,G{i}=2,H{i}>=1),"Tier 2","Tier 3"))', VEN[vid]["tier_prelim"], VEN[vid]["cif"],
                     day(assessed) if assessed else "-", rating_cell, f'=IF(I{i}="Tier 1",12,IF(I{i}="Tier 2",24,"-"))',
                     f'=IF(OR(L{i}="-",N{i}="-"),"-",EDATE(L{i},N{i}))',
                     f'=IF(I{i}="Tier 3","Not required",IF(L{i}="-","Not yet assessed",IF(O{i}<Dashboard!$B$4,"Overdue","Current")))',
                     day(renewal), checklist, f'=COUNTIFS(Findings!$B$5:$B${f_last},A{i},Findings!$L$5:$L${f_last},"<>Closed")'])
    i_last = write_rows(inv, rows, widths, center=tuple(range(4, 20)), inputs=(4, 6, 7, 8, 12, 17, 18))
    for r in range(5, i_last + 1):
        for c in (12, 15, 17):
            inv.cell(row=r, column=c).number_format = "DD MMM YYYY"
    list_validation(inv, f"F5:G{i_last}", '"0,1,2,3"')
    list_validation(inv, f"H5:H{i_last}", '"0,1,2"')
    fills(inv, f"I5:I{i_last}", {"Tier 1": RED, "Tier 2": AMBER, "Tier 3": GREEN})
    fills(inv, f"M5:M{i_last}", RATING_FILL)
    fills(inv, f"P5:P{i_last}", {"Overdue": RED, "Not yet assessed": AMBER, "Current": GREEN})
    inv.freeze_panes = "C5"
    inv.auto_filter.ref = f"A4:S{i_last}"
    iv = lambda col: f"Inventory!${col}$5:${col}${i_last}"

    # Register ------------------------------------------------------------------------------
    rg = wb.create_sheet("Register")
    title(rg, "ICT services supporting critical or important functions")
    rg["A3"] = "A simplified working view. The official register of information uses the templates in Commission Implementing Regulation (EU) 2024/2956."
    rg["A3"].font = F(color=MUTED)
    widths = [9, 28, 36, 44, 34, 34, 13, 44, 13, 10, 13]
    header(rg, 4, ["Supplier ID", "Supplier", "ICT service", "Function supported", "Data location", "Subcontractors", "Substitutability", "Exit arrangements", "Contract renewal", "Rating", "Last assessed"], widths)
    rows = []
    for i, (vid, r) in enumerate(D.REGISTER.items(), start=5):
        look = lambda col: f"=INDEX({iv(col)},MATCH(A{i},{iv('A')},0))"
        rows.append([vid, look("B"), look("C"), r[0], r[1], r[2], r[3], r[4], look("Q"), look("M"), look("L")])
    r_last = write_rows(rg, rows, widths, center=(1, 7, 9, 10, 11), inputs=(7,))
    for r in range(5, r_last + 1):
        rg.cell(row=r, column=9).number_format = rg.cell(row=r, column=11).number_format = "DD MMM YYYY"
    list_validation(rg, f"G5:G{r_last}", '"Easy,Medium,Hard"')
    fills(rg, f"G5:G{r_last}", {"Hard": ORANGE, "Medium": AMBER, "Easy": GREEN})
    fills(rg, f"J5:J{r_last}", RATING_FILL)
    rg.freeze_panes = "C5"

    # Dashboard -----------------------------------------------------------------------------
    ds = wb.create_sheet("Dashboard")
    title(ds, "Dashboard")
    for col, width in zip("ABCDE", (44, 16, 16, 16, 16)):
        ds.column_dimensions[col].width = width
    ds["A4"], ds["B4"] = "As-of date (input)", datetime.strptime(D.AS_OF, "%d %B %Y").date()
    ds["A4"].font = F(bold=True)
    ds["B4"].font, ds["B4"].fill, ds["B4"].number_format, ds["B4"].alignment = F(bold=True, size=11, color=ACCENT), INPUT, "DD MMM YYYY", Alignment(horizontal="right")
    facts = [("Suppliers in the inventory", f"=COUNTA({iv('A')})"), ("Tier 1 suppliers", f'=COUNTIF({iv("I")},"Tier 1")'),
             ("Tier 1 suppliers assessed", f'=COUNTIFS({iv("I")},"Tier 1",{iv("L")},"<>-")'), ("Tier 1 suppliers rated High or Critical", f'=COUNTIFS({iv("I")},"Tier 1",{iv("M")},"High")+COUNTIFS({iv("I")},"Tier 1",{iv("M")},"Critical")'),
             ("Open findings", f'=COUNTIF(Findings!$L$5:$L${f_last},"<>Closed")'), ("Findings overdue", f'=COUNTIF(Findings!$N$5:$N${f_last},"Overdue")'),
             ("Suppliers whose tier changed from the preliminary view", f"=SUMPRODUCT(--({iv('I')}<>{iv('J')}))")]
    for i, (label, formula) in enumerate(facts, start=5):
        ds.cell(row=i, column=1, value=label).font = F(bold=True)
        cell = ds.cell(row=i, column=2, value=formula)
        cell.font, cell.fill, cell.alignment = F(bold=True, size=11, color=ACCENT), TINTED, Alignment(horizontal="right")
    header(ds, 14, ["Tier", "Suppliers", "Assessed", "Not yet assessed", "Open findings"])
    for i, tier in enumerate(("Tier 1", "Tier 2", "Tier 3"), start=15):
        values = [tier, f"=COUNTIF({iv('I')},A{i})", f'=COUNTIFS({iv("I")},A{i},{iv("L")},"<>-")', f"=B{i}-C{i}", f"=SUMIF({iv('I')},A{i},{iv('S')})"]
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
    header(ds, 20, ["Finding severity", "Open"])
    for i, sev in enumerate(("Critical", "High", "Medium", "Low"), start=21):
        for c, v in enumerate((sev, f'=COUNTIFS(Findings!$D$5:$D${f_last},A{i},Findings!$L$5:$L${f_last},"<>Closed")'), start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
        ds.cell(row=i, column=1).fill = PatternFill("solid", fgColor=RATING_FILL[sev])
    header(ds, 27, ["Assessed in this project", "Score", "Rating", "Findings", "Clauses missing"])
    for k, v in enumerate(D.ASSESSED):
        i = 28 + k
        col = L(2 + k)
        values = [SHORT[v], f"=Scores!{col}16", f"=Scores!{col}18", f"=Scores!{col}19", f"=Contracts!{L(4 + k)}{c_last + 4}"]
        for c, val in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=val)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
        ds.cell(row=i, column=2).number_format = "0%"
    fills(ds, "C28:C30", RATING_FILL)
    ds.cell(row=32, column=1, value="Totals check").font = F(bold=True, color=MUTED)
    ds.cell(row=32, column=2, value=f'=IF(AND(SUM(B15:B17)=B5,SUM(B21:B24)=B9,SUM(D28:D30)=COUNTA(Findings!$A$5:$A${f_last})),"OK","CHECK")').font = F(bold=True, color=MUTED)
    ds.freeze_panes = "A4"

    wb["Dashboard"].sheet_properties.tabColor = ACCENT
    wb._sheets = [wb[n] for n in ["README", "Dashboard", "Inventory", "Questionnaire", "Assessments", "Scores", "Findings", "Contracts", "Register", "Criteria", "Roles"]]
    for ws in wb.worksheets:
        ws.oddFooter.left.text = DISCLAIMER
        ws.oddFooter.right.text = "Page &P of &N"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    for name in ("Dashboard", "Scores", "Inventory"):
        wb[name].page_setup.fitToHeight = 1
    props = wb.properties
    props.creator, props.title, props.subject = "Jahangir Shukurov", "Third-Party Risk Workbook", DISCLAIMER
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("Saved", OUT.name)


if __name__ == "__main__":
    build()
