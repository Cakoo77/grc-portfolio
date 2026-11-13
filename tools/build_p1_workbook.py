#!/usr/bin/env python3
"""Build the Project 1 gap assessment workbook with live formulas."""
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.comments import Comment
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).parent))
import p1_data as D
from doc_template import ACCENT, DISCLAIMER, INK, MUTED, RULE, TINT, ROOT

MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
OUT = ROOT / "01-gap-assessment/deliverables/Orvanta-ISO27001-Gap-Assessment-Workbook.xlsx"
HEAD = PatternFill("solid", fgColor=ACCENT)
TINTED = PatternFill("solid", fgColor=TINT)
INPUT = PatternFill("solid", fgColor="FFF8DC")
THIN = Side(style="thin", color=RULE)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
F = lambda **k: Font(name="Arial", size=k.pop("size", 9), color=k.pop("color", INK), **k)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="top", wrap_text=True)


def title(ws, text, sub=None, width=8):
    ws["A1"] = text
    ws["A1"].font = F(size=15, bold=True, color=ACCENT)
    ws["A2"] = sub or DISCLAIMER
    ws["A2"].font = F(color=MUTED)
    ws.sheet_view.showGridLines = False


def header(ws, row, columns, widths=None):
    for c, name in enumerate(columns, start=1):
        cell = ws.cell(row=row, column=c, value=name)
        cell.font = F(bold=True, color="FFFFFF")
        cell.fill = HEAD
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BOX
        if widths:
            ws.column_dimensions[L(c)].width = widths[c - 1]
    ws.row_dimensions[row].height = 40


def est_height(values, widths, line=12.5):
    lines = 1
    for value, width in zip(values, widths):
        if isinstance(value, str) and not value.startswith("="):
            lines = max(lines, int(len(value) / max(width * 1.12, 1)) + 1)
    return min(lines * line + 3, 200)


def add_priority_rules(ws, col, first, last):
    rng = f"{col}{first}:{col}{last}"
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"P1"'], fill=PatternFill("solid", bgColor="F4B6A0"), font=Font(bold=True)))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"P2"'], fill=PatternFill("solid", bgColor="FBE3A8")))
    ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=['"P3"'], fill=PatternFill("solid", bgColor="DCEAF0")))


def score_rule(rng):
    return ColorScaleRule(start_type="num", start_value=0, start_color="E9805F", mid_type="num", mid_value=2, mid_color="FBE3A8", end_type="num", end_value=4, end_color="9CCFB5")


COLUMNS = ["ID", "Requirement or control", "Area", "Current state", "Evidence observed", "Maturity score (0-5)", "Target", "Gap (points)",
           "Recommendation", "Certification blocker", "Attack relevance", "Priority score", "Priority", "Effort", "Owner ID", "Owner",
           "Priority gap", "Attacker's view", "Baseline observation"]
WIDTHS = [8, 28, 14, 42, 13, 9, 7, 7, 42, 12, 10, 8, 8, 7, 11, 18, 9, 38, 12]
F_SCORE, F_TARGET, F_GAP, F_BLOCK, F_ATTACK, F_PSCORE, F_PRI, F_EFFORT, F_OWNERID, F_OWNER, F_PGAP = "F", "G", "H", "J", "K", "L", "M", "N", "O", "P", "Q"
FIRST = 5


def assessment_sheet(wb, name, heading, rows, is_clause):
    ws = wb.create_sheet(name)
    title(ws, heading)
    ws["A3"] = "Yellow cells are inputs. Gap, priority score, priority and owner name are formulas."
    ws["A3"].font = F(color=MUTED)
    header(ws, FIRST - 1, COLUMNS, WIDTHS)
    for i, r in enumerate(rows):
        n = FIRST + i
        values = [r["id"], r["name"], r["area"], r["state"], r["evidence"], r["score"], 3,
                  f"=MAX(G{n}-F{n},0)", r["rec"], r["blocker"], r["attack"],
                  f"=IF(H{n}=0,0,H{n}*Scale!$B$20+IF(J{n}=\"Y\",Scale!$B$21,0)+INDEX(Scale!$B$14:$B$17,MATCH(K{n},Scale!$A$14:$A$17,0)))",
                  f"=IF(H{n}=0,\"Met\",IF(L{n}>=Scale!$B$22,\"P1\",IF(L{n}>=Scale!$B$23,\"P2\",\"P3\")))",
                  r["effort"], r["owner"], f"=INDEX(Roles!$B$5:$B$28,MATCH(O{n},Roles!$A$5:$A$28,0))", r["gap"] or "-", r["view"] or "-", r["obs"] or "-"]
        for c, value in enumerate(values, start=1):
            cell = ws.cell(row=n, column=c, value=value)
            cell.font = F()
            cell.alignment = CENTER if c in (6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 19) else WRAP
            cell.border = BOX
        for col in (F_SCORE, F_TARGET, F_BLOCK, F_ATTACK, F_EFFORT, F_OWNERID):
            ws[f"{col}{n}"].fill = INPUT
        ws.row_dimensions[n].height = est_height(values, WIDTHS)
    last = FIRST + len(rows) - 1
    dvs = [(F_SCORE, '"0,1,2,3,4,5"'), (F_TARGET, '"0,1,2,3,4,5"'), (F_BLOCK, '"Y,N"'), (F_ATTACK, '"High,Medium,Low,None"'),
           (F_EFFORT, '"S,M,L"'), (F_OWNERID, "=Roles!$A$5:$A$28")]
    for col, formula in dvs:
        dv = DataValidation(type="list", formula1=formula, allow_blank=False, showErrorMessage=True, errorTitle="Invalid value", error="Choose from the list.")
        dv.add(f"{col}{FIRST}:{col}{last}")
        ws.add_data_validation(dv)
    ws.conditional_formatting.add(f"F{FIRST}:F{last}", score_rule(None))
    add_priority_rules(ws, F_PRI, FIRST, last)
    ws.freeze_panes = ws.cell(row=FIRST, column=3)
    ws.auto_filter.ref = f"A{FIRST - 1}:S{last}"
    return ws, last


def build():
    wb = Workbook()
    readme = wb.active
    readme.title = "README"
    title(readme, "ISO/IEC 27001:2022 Gap Assessment Workbook")
    readme.column_dimensions["A"].width = 24
    readme.column_dimensions["B"].width = 96
    rows = [("Client", "Orvanta Payments UAB (fictional)"), ("Document ID", "ORV-GAP-002, version 1.0, 27 November 2026"),
            ("Prepared by", "Jahangir Shukurov"), ("Classification", "Confidential (sample)"),
            ("Evidence basis", "Simulated interviews and document review, 9 to 20 November 2026. No real organization was assessed."),
            ("Copyright", "Clause numbers, control IDs and short names only. All other wording is original; the standard's text is not reproduced."),
            ("", ""), ("How to use", ""),
            ("1. Scale", "Holds the maturity scale, priority weights and thresholds. Change a weight and every sheet recalculates."),
            ("2. Clauses", "Clauses 4 to 10: 30 requirements, including the 2024 climate amendment under 4.1 and 4.2."),
            ("3. Annex A", "All 93 controls. Score here is an assessment input; applicability is finalized in the Project 4 Statement of Applicability."),
            ("4. Dashboard", "Live heat map and counts by clause, theme, priority and effort."),
            ("5. Priority Gaps", "The ten grouped gaps used in the report. Metrics come from the linked rows."),
            ("6. Attack Path", "Six observed gaps chained into one illustrative attack path, mapped to MITRE ATT&CK."),
            ("7. Quick Wins", "Eight actions achievable within 30 days."),
            ("8. Roadmap", "12-month Gantt view. Edit start and end months and the bars move."),
            ("9. Evidence", "Register of simulated interviews and documents cited in the assessment."),
            ("10. Roles", "Named role-holders from the Company Fact Sheet."),
            ("", ""), ("Editing", "Yellow cells are inputs with drop-downs. Everything else is calculated or descriptive."),
            ("Priority logic", "Priority score = gap points x weight + blocker points + attack points. See Scale for values.")]
    for i, (a, b) in enumerate(rows, start=4):
        readme.cell(row=i, column=1, value=a).font = F(bold=True, size=10)
        c = readme.cell(row=i, column=2, value=b)
        c.font = F(size=10)
        c.alignment = WRAP

    sc = wb.create_sheet("Scale")
    title(sc, "Maturity scale and priority logic")
    sc.column_dimensions["A"].width = 26
    sc.column_dimensions["B"].width = 14
    sc.column_dimensions["C"].width = 80
    header(sc, 4, ["Score", "Label", "Meaning"])
    for i, row in enumerate(D.SCALE, start=5):
        for c, v in enumerate(row, start=1):
            cell = sc.cell(row=i, column=c, value=v)
            cell.font, cell.border, cell.alignment = F(), BOX, WRAP
    sc["A12"] = "Attack relevance points"
    sc["A12"].font = F(bold=True, color=ACCENT, size=10)
    header(sc, 13, ["Attack relevance", "Points", "Meaning"])
    for i, row in enumerate([("High", 3, "Directly opens or widens a likely attack path"), ("Medium", 2, "Helps an attacker or slows the response"),
                             ("Low", 1, "Indirect effect"), ("None", 0, "No meaningful attack path")], start=14):
        for c, v in enumerate(row, start=1):
            cell = sc.cell(row=i, column=c, value=v)
            cell.font, cell.border, cell.alignment = F(), BOX, WRAP
        sc.cell(row=i, column=2).fill = INPUT
    sc["A19"] = "Weights and thresholds"
    sc["A19"].font = F(bold=True, color=ACCENT, size=10)
    for i, (a, b, note) in enumerate([("Gap point weight", 2, "Multiplied by gap points (0 to 3)."),
                                      ("Certification blocker points", 2, "Added when the gap would likely stop certification."),
                                      ("P1 threshold (score at or above)", 9, "P1: start in the first 90 days."),
                                      ("P2 threshold (score at or above)", 6, "P2: complete by mid-2027. Below this is P3.")], start=20):
        sc.cell(row=i, column=1, value=a).font = F()
        cell = sc.cell(row=i, column=2, value=b)
        cell.font, cell.fill, cell.border = F(), INPUT, BOX
        sc.cell(row=i, column=3, value=note).font = F(color=MUTED)
    sc["B22"].comment = Comment("Calibrated so that P1 needs a large gap plus either a blocker or high attack relevance.", "Jahangir Shukurov")

    clause_rows = [dict(id=c[0], name=c[1], area=D.CLAUSE_NAMES[c[0].split(".")[0]], state=f"Looked for: {c[2]} Found: {c[3]}", evidence=c[4], score=c[5],
                        rec=c[6], effort=c[7], owner=c[8], attack=c[9], blocker="Y", gap=c[10], view=c[11], obs=c[12]) for c in D.CLAUSES]
    control_rows = [dict(id="A." + c[0], name=c[1], area=D.THEMES[c[0].split(".")[0]], state=c[2], evidence=c[3], score=c[4], rec=c[5], effort=c[6],
                         owner=c[7], attack=c[8], blocker=c[9], gap=c[10], view=c[11], obs=c[12]) for c in D.CONTROLS]
    _, clause_last = assessment_sheet(wb, "Clauses", "Clauses 4 to 10", clause_rows, True)
    _, control_last = assessment_sheet(wb, "Annex A", "Annex A: 93 controls", control_rows, False)
    cl = lambda col: f"Clauses!${col}${FIRST}:${col}${clause_last}"
    an = lambda col: f"'Annex A'!${col}${FIRST}:${col}${control_last}"

    ds = wb.create_sheet("Dashboard")
    title(ds, "Dashboard")
    for col, w in zip("ABCDEFGH", (28, 12, 12, 12, 12, 12, 12, 12)):
        ds.column_dimensions[col].width = w
    ds["A4"], ds["A5"], ds["A6"], ds["A7"] = "Overall average maturity", "Requirements meeting target", "Total assessed", "Percent at target"
    ds["B4"] = f"=(SUM({cl('F')})+SUM({an('F')}))/B6"
    ds["B5"] = f'=COUNTIF({cl("M")},"Met")+COUNTIF({an("M")},"Met")'
    ds["B6"] = f"=COUNTA({cl('A')})+COUNTA({an('A')})"
    ds["B7"] = "=B5/B6"
    ds["B4"].number_format, ds["B7"].number_format = "0.0", "0%"
    for r in range(4, 8):
        ds[f"A{r}"].font = F(bold=True)
        ds[f"B{r}"].font = F(bold=True, size=11, color=ACCENT)
        ds[f"B{r}"].fill = TINTED
    header(ds, 9, ["Clause", "Requirements", "Average", "At target", "P1", "P2", "P3", "% at target"])
    row = 10
    for key, name in D.CLAUSE_NAMES.items():
        ds.cell(row=row, column=1, value=f"{key} {name}")
        area = f'"{name}"'
        ds.cell(row=row, column=2, value=f"=COUNTIF({cl('C')},{area})")
        ds.cell(row=row, column=3, value=f"=AVERAGEIF({cl('C')},{area},{cl('F')})")
        ds.cell(row=row, column=4, value=f'=COUNTIFS({cl("C")},{area},{cl("M")},"Met")')
        for c, p in zip((5, 6, 7), ("P1", "P2", "P3")):
            ds.cell(row=row, column=c, value=f'=COUNTIFS({cl("C")},{area},{cl("M")},"{p}")')
        ds.cell(row=row, column=8, value=f"=D{row}/B{row}")
        row += 1
    clause_end = row - 1
    row += 1
    header(ds, row, ["Annex A theme", "Controls", "Average", "At target", "P1", "P2", "P3", "% at target"])
    row += 1
    theme_start = row
    for name in D.THEMES.values():
        ds.cell(row=row, column=1, value=name)
        area = f'"{name}"'
        ds.cell(row=row, column=2, value=f"=COUNTIF({an('C')},{area})")
        ds.cell(row=row, column=3, value=f"=AVERAGEIF({an('C')},{area},{an('F')})")
        ds.cell(row=row, column=4, value=f'=COUNTIFS({an("C")},{area},{an("M")},"Met")')
        for c, p in zip((5, 6, 7), ("P1", "P2", "P3")):
            ds.cell(row=row, column=c, value=f'=COUNTIFS({an("C")},{area},{an("M")},"{p}")')
        ds.cell(row=row, column=8, value=f"=D{row}/B{row}")
        row += 1
    theme_end = row - 1
    for r in list(range(10, clause_end + 1)) + list(range(theme_start, theme_end + 1)):
        for c in range(1, 9):
            cell = ds.cell(row=r, column=c)
            cell.font, cell.border = F(), BOX
            if c > 1:
                cell.alignment = Alignment(horizontal="center")
        ds.cell(row=r, column=3).number_format = "0.0"
        ds.cell(row=r, column=8).number_format = "0%"
    for rng in (f"C10:C{clause_end}", f"C{theme_start}:C{theme_end}"):
        ds.conditional_formatting.add(rng, score_rule(None))
    row += 1
    header(ds, row, ["Effort for open gaps", "Requirements"])
    effort_start = row + 1
    for i, e in enumerate(("S", "M", "L"), start=effort_start):
        ds.cell(row=i, column=1, value={"S": "S (under 1 month)", "M": "M (1 to 3 months)", "L": "L (over 3 months)"}[e]).font = F()
        ds.cell(row=i, column=2, value=f'=COUNTIFS({cl("N")},"{e}",{cl("H")},">0")+COUNTIFS({an("N")},"{e}",{an("H")},">0")').font = F()
        ds.cell(row=i, column=2).alignment = Alignment(horizontal="center")
        for c in (1, 2):
            ds.cell(row=i, column=c).border = BOX
    row = effort_start + 4
    ds.cell(row=row, column=1, value="Totals check").font = F(bold=True, color=MUTED)
    ds.cell(row=row, column=2, value=f'=IF(AND(SUM(B10:B{clause_end})=COUNTA({cl("A")}),SUM(B{theme_start}:B{theme_end})=93),"OK","CHECK")').font = F(bold=True, color=MUTED)
    ds.freeze_panes = "A4"
    for anchor, heading, first, last in (("J4", "Average maturity by clause (target 3)", 10, clause_end), ("J21", "Average maturity by theme (target 3)", theme_start, theme_end)):
        chart = BarChart()
        chart.type, chart.style, chart.title, chart.legend = "bar", 10, heading, None
        chart.add_data(Reference(ds, min_col=3, min_row=first, max_row=last), titles_from_data=False)
        chart.set_categories(Reference(ds, min_col=1, min_row=first, max_row=last))
        chart.y_axis.scaling.min, chart.y_axis.scaling.max, chart.y_axis.majorUnit = 0, 5, 1
        chart.y_axis.delete = chart.x_axis.delete = False
        chart.x_axis.scaling.orientation = "maxMin"
        chart.series[0].graphicalProperties.solidFill = ACCENT
        chart.series[0].graphicalProperties.line.solidFill = ACCENT
        chart.height, chart.width = 8.2, 15
        ds.add_chart(chart, anchor)

    ap = wb.create_sheet("Attack Path")
    title(ap, "Illustrative attack path through current gaps")
    ap["A3"] = "A scenario built from observed gaps, not evidence of an attack. Technique IDs refer to MITRE ATT&CK."
    ap["A3"].font = F(color=MUTED)
    w = [6, 18, 30, 24, 62, 20, 11, 16]
    header(ap, 4, ["Step", "Tactic", "Technique", "Attacker's move", "What makes it possible at Orvanta", "Controls", "Priority gap", "Closed by"], w)
    for i, s in enumerate(D.ATTACK_PATH, start=5):
        vals = [s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7]]
        for c, v in enumerate(vals, start=1):
            cell = ap.cell(row=i, column=c, value=v)
            cell.font, cell.border, cell.alignment = F(), BOX, WRAP
        ap.row_dimensions[i].height = est_height(vals, w)
    ap.freeze_panes = "A5"

    pg = wb.create_sheet("Priority Gaps")
    title(pg, "Top 10 priority gaps")
    cols = ["Gap ID", "Priority gap", "Why it matters to the business", "What to do", "Owner ID", "Owner", "Target", "Linked items", "P1 items", "Average maturity", "Average priority score", "Rank"]
    widths = [8, 28, 50, 42, 11, 18, 9, 8, 7, 9, 9, 6]
    header(pg, 4, cols, widths)
    for i, g in enumerate(D.PRIORITY_GAPS, start=5):
        key = f"$A{i}"
        count = f"(COUNTIF({cl('Q')},{key})+COUNTIF({an('Q')},{key}))"
        vals = [g[0], g[1], g[2], g[3], g[4], f"=INDEX(Roles!$B$5:$B$28,MATCH(E{i},Roles!$A$5:$A$28,0))", g[5], f"={count}",
                f'=COUNTIFS({cl("Q")},{key},{cl("M")},"P1")+COUNTIFS({an("Q")},{key},{an("M")},"P1")',
                f"=(SUMIF({cl('Q')},{key},{cl('F')})+SUMIF({an('Q')},{key},{an('F')}))/H{i}",
                f"=(SUMIF({cl('Q')},{key},{cl('L')})+SUMIF({an('Q')},{key},{an('L')}))/H{i}",
                f"=RANK(K{i},$K$5:$K$14)+COUNTIF($K$5:K{i},K{i})-1"]
        for c, v in enumerate(vals, start=1):
            cell = pg.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = CENTER if c in (1, 5, 7, 8, 9, 10, 11, 12) else WRAP
        pg.cell(row=i, column=10).number_format = "0.0"
        pg.cell(row=i, column=11).number_format = "0.0"
        pg.row_dimensions[i].height = est_height(vals, widths)
    pg.freeze_panes = "C5"
    pg.conditional_formatting.add("J5:J14", score_rule(None))
    pg.auto_filter.ref = "A4:L14"

    qw = wb.create_sheet("Quick Wins")
    title(qw, "Quick wins: achievable within 30 days")
    w = [8, 56, 48, 14, 11, 18, 9, 11]
    header(qw, 4, ["ID", "Action", "Why it pays off", "Linked to", "Owner ID", "Owner", "Days", "Status"], w)
    for i, q in enumerate(D.QUICK_WINS, start=5):
        vals = [q[0], q[1], q[2], q[3], q[4], f"=INDEX(Roles!$B$5:$B$28,MATCH(E{i},Roles!$A$5:$A$28,0))", q[5], "Not started"]
        for c, v in enumerate(vals, start=1):
            cell = qw.cell(row=i, column=c, value=v)
            cell.font, cell.border, cell.alignment = F(), BOX, WRAP
        qw.cell(row=i, column=8).fill = INPUT
        qw.row_dimensions[i].height = est_height(vals, w)
    dv = DataValidation(type="list", formula1='"Not started,In progress,Done"', allow_blank=False)
    dv.add("H5:H12")
    qw.add_data_validation(dv)
    qw.freeze_panes = "A5"

    rm = wb.create_sheet("Roadmap")
    title(rm, "12-month roadmap to certification")
    base = ["ID", "Phase", "Activity", "Gap", "Owner ID", "Owner", "Start", "End"]
    w = [7, 12, 48, 8, 11, 18, 6, 6]
    header(rm, 4, base + D.MONTHS, w + [5.5] * 12)
    for i, a in enumerate(D.ROADMAP, start=6):
        vals = [a[0], a[1], a[2], a[3], a[4], f"=INDEX(Roles!$B$5:$B$28,MATCH(E{i},Roles!$A$5:$A$28,0))", a[5], a[6]]
        for c, v in enumerate(vals, start=1):
            cell = rm.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(vertical="center", wrap_text=c == 3)
        for col in "GH":
            rm[f"{col}{i}"].fill = INPUT
            rm[f"{col}{i}"].alignment = Alignment(horizontal="center", vertical="center")
        for c in range(9, 21):
            rm.cell(row=i, column=c).border = BOX
    for c in range(1, 21):
        cell = rm.cell(row=5, column=c)
        cell.fill = TINTED
        cell.font = F(color=MUTED)
        if c >= 9:
            cell.value = c - 8
            cell.alignment = Alignment(horizontal="center")
    rm.cell(row=5, column=1, value="Month index").font = F(color=MUTED)
    last = 5 + len(D.ROADMAP)
    rm.conditional_formatting.add(f"I6:T{last}", FormulaRule(formula=["AND(I$5>=$G6,I$5<=$H6)"], fill=PatternFill("solid", bgColor=ACCENT)))
    dv = DataValidation(type="whole", operator="between", formula1="1", formula2="12", showErrorMessage=True, error="Enter a month index from 1 to 12.")
    dv.add(f"G6:H{last}")
    rm.add_data_validation(dv)
    rm.freeze_panes = "D6"

    ev = wb.create_sheet("Evidence")
    title(ev, "Evidence register (simulated)")
    header(ev, 4, ["Ref", "Type", "Description", "Provided by", "Date"], [8, 11, 62, 12, 11])
    for i, e in enumerate(D.EVIDENCE, start=5):
        for c, v in enumerate(e, start=1):
            cell = ev.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
    ev.freeze_panes = "A5"
    ev.auto_filter.ref = f"A4:E{4 + len(D.EVIDENCE)}"

    ro = wb.create_sheet("Roles")
    title(ro, "Role-holders (from Company Fact Sheet)")
    header(ro, 4, ["Role ID", "Name", "Title", "Location"], [12, 24, 48, 10])
    for i, r in enumerate(MASTER["roles"], start=5):
        for c, v in enumerate((r["id"], r["name"], r["title"], r["location"]), start=1):
            cell = ro.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
    ro.freeze_panes = "A5"
    assert len(MASTER["roles"]) == 24

    wb["Dashboard"].sheet_properties.tabColor = ACCENT
    order = ["README", "Dashboard", "Clauses", "Annex A", "Priority Gaps", "Attack Path", "Quick Wins", "Roadmap", "Scale", "Evidence", "Roles"]
    wb._sheets = [wb[n] for n in order]
    for ws in wb.worksheets:
        ws.oddFooter.left.text = DISCLAIMER
        ws.oddFooter.right.text = "Page &P of &N"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb["Dashboard"].page_setup.fitToHeight = 1
    props = wb.properties
    props.creator, props.title, props.subject = "Jahangir Shukurov", "ISO/IEC 27001:2022 Gap Assessment Workbook", DISCLAIMER
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("Saved", OUT)


if __name__ == "__main__":
    build()
