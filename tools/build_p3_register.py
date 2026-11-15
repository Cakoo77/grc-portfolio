#!/usr/bin/env python3
"""Build the Project 3 ISMS register workbook: documents, requirements, control map and objectives."""
import json
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, DataBarRule
from openpyxl.styles import Alignment, PatternFill

sys.path.insert(0, str(Path(__file__).parent))
import p1_data as P1
import p2_data as P2
import p3_data as D
from build_p1_workbook import BOX, CENTER, F, INPUT, TINTED, WRAP, header, title
from build_p2_workbook import ROLE_LOOKUP, list_validation, write_rows
from build_p3_docs import policy_id, requirements
from doc_template import ACCENT, DISCLAIMER, MUTED, ROOT

MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
OUT = ROOT / "03-isms-documentation/deliverables/ORV-ISMS-002-ISMS-Register.xlsx"
GREEN, AMBER, RED = "CFE6D8", "FBE9B0", "F3B9A3"
day = lambda text: datetime.strptime(text, "%d %B %Y").date()


def build():
    wb = Workbook()
    readme = wb.active
    readme.title = "README"
    title(readme, "ISMS Register")
    readme.column_dimensions["A"].width = 24
    readme.column_dimensions["B"].width = 100
    notes = [("Client", "Orvanta Payments UAB (fictional)"), ("Document ID", f"ORV-ISMS-002, version 1.0, {D.KPI_DATE}"), ("Prepared by", "Jahangir Shukurov"),
             ("Classification", "Internal (sample)"),
             ("Purpose", "One place to see which documents exist, what each requires, which Annex A controls each requirement supports and how the security objectives are progressing."),
             ("Copyright", "Annex A controls are cited by ID and short name only. All requirement wording is original."),
             ("", ""), ("How to use", ""),
             ("1. Dashboard", "Live totals: documents, requirements, control coverage by theme and objective status."),
             ("2. Documents", "Register of the 15 controlled documents. Next review and review status are calculated from the as-of date on the Dashboard."),
             ("3. Requirements", "All numbered policy requirements with the Annex A controls each one supports."),
             ("4. Control Map", "All 93 Annex A controls. Requirement counts and the primary document are looked up from the Requirements sheet."),
             ("5. Objectives", "Ten security objectives. Enter the latest reading and progress recalculates."),
             ("6. Interested Parties", "Who has a stake in the ISMS and how their needs are met."),
             ("7. Roles", "Named role-holders from the Company Fact Sheet."),
             ("", ""), ("Editing", "Yellow cells are inputs. Counts, lookups, dates and statuses are formulas."),
             ("Link to other work", "The Control Map feeds the Statement of Applicability in Project 4. The risk-treatment column comes from the risk register (ORV-RISK-002).")]
    for i, (a, b) in enumerate(notes, start=4):
        readme.cell(row=i, column=1, value=a).font = F(bold=True, size=10)
        cell = readme.cell(row=i, column=2, value=b)
        cell.font, cell.alignment = F(size=10), WRAP

    ro = wb.create_sheet("Roles")
    title(ro, "Role-holders (from Company Fact Sheet)")
    header(ro, 4, ["Role ID", "Name", "Title", "Location"], [12, 24, 48, 10])
    write_rows(ro, [[r["id"], r["name"], r["title"], r["location"]] for r in MASTER["roles"]], [12, 24, 48, 10])

    # Requirements --------------------------------------------------------------------------
    rq = wb.create_sheet("Requirements")
    title(rq, "Policy requirements")
    rq["A3"] = "Each requirement lists the Annex A controls it supports. Control IDs end with a semicolon so that lookups match exactly."
    rq["A3"].font = F(color=MUTED)
    widths = [9, 13, 30, 96, 24]
    header(rq, 4, ["ID", "Document ID", "Section", "Requirement", "Annex A controls"], widths)
    rows = [[rid, policy_id(p), sec, text, " ".join(f"A.{c};" for c in ctl.split(", "))] for p in D.POLICIES for rid, sec, text, ctl in requirements(p)]
    rq_last = write_rows(rq, rows, widths, center=(1, 2))
    rq.freeze_panes = "D5"
    rq.auto_filter.ref = f"A4:E{rq_last}"
    req = lambda col: f"Requirements!${col}$5:${col}${rq_last}"

    # Documents -----------------------------------------------------------------------------
    dc = wb.create_sheet("Documents")
    title(dc, "Document register")
    dc["A3"] = "Next review and review status are formulas. Review status uses the as-of date on the Dashboard."
    dc["A3"].font = F(color=MUTED)
    widths = [14, 46, 11, 11, 20, 11, 20, 8, 13, 9, 13, 12, 11, 12]
    header(dc, 4, ["ID", "Document", "Type", "Owner ID", "Owner", "Approver ID", "Approver", "Version", "Approved", "Review cycle (months)", "Next review", "Review status", "Requirements", "Status"], widths)
    docs = [("ORV-ISMS-001", "ISMS Manual", "Manual", "R-CISO", "R-CEO", "19 February 2027")]
    docs += [(policy_id(p), p["title"], "Policy", p["owner"], p["approver"], p["date"]) for p in D.POLICIES]
    docs += [(f"ORV-PRC-{pr['num']:02d}", pr["title"], "Procedure", pr["owner"], pr["approver"], pr["date"]) for pr in D.PROCEDURES]
    rows = []
    for i, (did, name, kind, owner, approver, date) in enumerate(docs, start=5):
        rows.append([did, name, kind, owner, "=" + ROLE_LOOKUP.format(cell=f"D{i}"), approver, "=" + ROLE_LOOKUP.format(cell=f"F{i}"), "1.0", day(date), 12, f"=EDATE(I{i},J{i})",
                     f'=IF(K{i}<Dashboard!$B$4,"Overdue",IF(K{i}-Dashboard!$B$4<=60,"Due soon","Current"))', f"=COUNTIF({req('B')},A{i})", "Approved"])
    dc_last = write_rows(dc, rows, widths, center=(1, 3, 4, 6, 8, 9, 10, 11, 12, 13, 14), inputs=(4, 6, 9, 10, 14))
    for i in range(5, dc_last + 1):
        dc.cell(row=i, column=9).number_format = dc.cell(row=i, column=11).number_format = "DD MMM YYYY"
    list_validation(dc, f"N5:N{dc_last}", '"Draft,Approved,Under review,Retired"')
    for col in "DF":
        list_validation(dc, f"{col}5:{col}{dc_last}", "=Roles!$A$5:$A$28")
    for label, color in (("Overdue", RED), ("Due soon", AMBER), ("Current", GREEN)):
        dc.conditional_formatting.add(f"L5:L{dc_last}", CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))
    dc.freeze_panes = "C5"
    dc.auto_filter.ref = f"A4:N{dc_last}"

    # Control map ---------------------------------------------------------------------------
    cm = wb.create_sheet("Control Map")
    title(cm, "Annex A control map")
    cm["A3"] = "Requirement counts and the primary document are looked up from the Requirements sheet. The last two columns come from the risk register (ORV-RISK-002)."
    cm["A3"].font = F(color=MUTED)
    widths = [9, 54, 16, 13, 16, 10, 14, 12]
    header(cm, 4, ["Control", "Control name", "Theme", "Requirements", "Primary document", "Covered", "Selected in risk treatment", "Linked risks"], widths)
    linked = {}
    for r in P2.RISKS:
        for c in r["controls"].split(", "):
            linked[c] = linked.get(c, 0) + 1
    rows = []
    for i, c in enumerate(P1.CONTROLS, start=5):
        cid = "A." + c[0]
        rows.append([cid, c[1], P1.THEMES[c[0].split(".")[0]], f'=COUNTIF({req("E")},"*"&A{i}&";*")',
                     f'=IFERROR(INDEX({req("B")},MATCH("*"&A{i}&";*",{req("E")},0)),"Not covered")', f'=IF(D{i}>0,"Yes","No")',
                     "Yes" if cid in linked else "No", linked.get(cid, 0)])
    cm_last = write_rows(cm, rows, widths, center=(1, 4, 5, 6, 7, 8), inputs=(7, 8))
    cm.conditional_formatting.add(f"F5:F{cm_last}", CellIsRule(operator="equal", formula=['"No"'], fill=PatternFill("solid", bgColor=RED)))
    cm.conditional_formatting.add(f"F5:F{cm_last}", CellIsRule(operator="equal", formula=['"Yes"'], fill=PatternFill("solid", bgColor=GREEN)))
    cm.freeze_panes = "C5"
    cm.auto_filter.ref = f"A4:H{cm_last}"
    ctl = lambda col: f"'Control Map'!${col}$5:${col}${cm_last}"

    # Objectives ----------------------------------------------------------------------------
    ob = wb.create_sheet("Objectives")
    title(ob, "Information security objectives")
    ob["A3"] = f"Baselines are from November 2026. Latest readings are as of {D.KPI_DATE}. Enter a new reading and progress recalculates."
    ob["A3"].font = F(color=MUTED)
    widths = [9, 40, 46, 8, 10, 9, 9, 10, 13, 13, 11, 20, 28]
    header(ob, 4, ["ID", "Objective", "KPI", "Unit", "Baseline", "Target", "Latest", "Progress", "Status", "Due", "Owner ID", "Owner", "Data source"], widths)
    rows = []
    for i, o in enumerate(D.OBJECTIVES, start=5):
        rows.append([o[0], o[1], o[2], o[3], o[4], o[5], o[6], f"=IF(F{i}=E{i},1,MAX(0,MIN(1,(G{i}-E{i})/(F{i}-E{i}))))", f'=IF(H{i}>=1,"Met","In progress")',
                     datetime.strptime(o[7], "%d %b %Y").date(), o[8], "=" + ROLE_LOOKUP.format(cell=f"K{i}"), o[9]])
    ob_last = write_rows(ob, rows, widths, center=(1, 4, 5, 6, 7, 8, 9, 10, 11), inputs=(7,))
    for i in range(5, ob_last + 1):
        ob.cell(row=i, column=8).number_format = "0%"
        ob.cell(row=i, column=10).number_format = "DD MMM YYYY"
    ob.conditional_formatting.add(f"H5:H{ob_last}", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color="6FB39A"))
    ob.conditional_formatting.add(f"I5:I{ob_last}", CellIsRule(operator="equal", formula=['"Met"'], fill=PatternFill("solid", bgColor=GREEN)))
    ob.freeze_panes = "C5"

    ip = wb.create_sheet("Interested Parties")
    title(ip, "Interested parties")
    widths = [34, 60, 60]
    header(ip, 4, ["Interested party", "What they need", "How Orvanta meets it"], widths)
    write_rows(ip, [list(x) for x in D.PARTIES], widths)

    # Dashboard -----------------------------------------------------------------------------
    ds = wb.create_sheet("Dashboard")
    title(ds, "Dashboard")
    for col, width in zip("ABCDEF", (60, 16, 14, 14, 14, 14)):
        ds.column_dimensions[col].width = width
    facts = [("As-of date (input)", day(D.KPI_DATE)), ("Controlled documents", f"=COUNTA(Documents!$A$5:$A${dc_last})"), ("Numbered requirements", f"=COUNTA({req('A')})"),
             ("Annex A controls covered, of 93", f'=COUNTIF({ctl("F")},"Yes")'),
             ("Risk-treatment controls covered", f'=COUNTIFS({ctl("G")},"Yes",{ctl("F")},"Yes")&" of "&COUNTIF({ctl("G")},"Yes")'),
             ("Objectives met", f'=COUNTIF(Objectives!$I$5:$I${ob_last},"Met")&" of "&COUNTA(Objectives!$A$5:$A${ob_last})'),
             ("Documents overdue for review", f'=COUNTIF(Documents!$L$5:$L${dc_last},"Overdue")')]
    for i, (label, value) in enumerate(facts, start=4):
        ds.cell(row=i, column=1, value=label).font = F(bold=True)
        cell = ds.cell(row=i, column=2, value=value)
        cell.font, cell.fill, cell.alignment = F(bold=True, size=11, color=ACCENT), TINTED, Alignment(horizontal="right")
    ds["B4"].number_format, ds["B4"].fill = "DD MMM YYYY", INPUT
    header(ds, 12, ["Annex A theme", "Controls", "Covered", "Requirement links", "% covered"])
    for i, theme in enumerate(P1.THEMES.values(), start=13):
        values = [theme, f"=COUNTIF({ctl('C')},A{i})", f'=COUNTIFS({ctl("C")},A{i},{ctl("F")},"Yes")', f"=SUMIF({ctl('C')},A{i},{ctl('D')})", f"=C{i}/B{i}"]
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
        ds.cell(row=i, column=5).number_format = "0%"
    header(ds, 19, ["Document", "Requirements"])
    first = 20
    for i, p in enumerate(D.POLICIES, start=first):
        for c, v in enumerate((f"{policy_id(p)} {p['title']}", f'=COUNTIF({req("B")},"{policy_id(p)}")'), start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
    last = first + len(D.POLICIES) - 1
    ds.cell(row=last + 2, column=1, value="Totals check").font = F(bold=True, color=MUTED)
    ds.cell(row=last + 2, column=2, value=f'=IF(AND(SUM(B13:B16)=93,SUM(B{first}:B{last})=B6),"OK","CHECK")').font = F(bold=True, color=MUTED)
    chart = BarChart()
    chart.type, chart.style, chart.title, chart.legend = "bar", 10, "Requirements per policy", None
    chart.add_data(Reference(ds, min_col=2, min_row=first, max_row=last), titles_from_data=False)
    chart.set_categories(Reference(ds, min_col=1, min_row=first, max_row=last))
    chart.y_axis.delete = chart.x_axis.delete = False
    chart.x_axis.scaling.orientation = "maxMin"
    chart.series[0].graphicalProperties.solidFill = ACCENT
    chart.series[0].graphicalProperties.line.solidFill = ACCENT
    chart.height, chart.width = 9.5, 19
    ds.add_chart(chart, "H3")
    ds.freeze_panes = "A4"

    wb["Dashboard"].sheet_properties.tabColor = ACCENT
    wb._sheets = [wb[n] for n in ["README", "Dashboard", "Documents", "Requirements", "Control Map", "Objectives", "Interested Parties", "Roles"]]
    for ws in wb.worksheets:
        ws.oddFooter.left.text = DISCLAIMER
        ws.oddFooter.right.text = "Page &P of &N"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb["Dashboard"].page_setup.fitToHeight = 1
    props = wb.properties
    props.creator, props.title, props.subject = "Jahangir Shukurov", "ISMS Register", DISCLAIMER
    wb.save(OUT)
    print("Saved", OUT.name)


if __name__ == "__main__":
    build()
