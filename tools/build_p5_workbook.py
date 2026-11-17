#!/usr/bin/env python3
"""Build the Project 5 internal audit workbook: programme, checklist, findings, corrective actions and KPI dashboard."""
import json
import sys
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, PatternFill
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, str(Path(__file__).parent))
import p5_data as D
from build_p1_workbook import BOX, F, INPUT, TINTED, WRAP, header, title
from build_p2_workbook import ROLE_LOOKUP, list_validation, write_rows
from doc_template import ACCENT, DISCLAIMER, MUTED, ROOT

MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
OUT = ROOT / "05-internal-audit-management-review/deliverables/Orvanta-Internal-Audit-Workbook.xlsx"
GREEN, AMBER, ORANGE, RED, GREY = "CFE6D8", "FBE9B0", "F6C08F", "F3B9A3", "E3E8EA"
RESULT_FILL = {"Conforms": GREEN, "Major nonconformity": RED, "Minor nonconformity": ORANGE, "Observation": AMBER, "Opportunity for improvement": "DCEAF0", "Not yet due": GREY}
day = lambda text: datetime.strptime(text, "%d %b %Y").date()


def fills(ws, rng, mapping):
    for label, color in mapping.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))


def build():
    wb = Workbook()
    readme = wb.active
    readme.title = "README"
    title(readme, "Internal Audit Workbook")
    readme.column_dimensions["A"].width = 24
    readme.column_dimensions["B"].width = 100
    notes = [("Client", "Orvanta Payments UAB (fictional)"), ("Document ID", f"ORV-AUD-005, version 1.0, {D.CAP_DATE}"), ("Audit", f"{D.AUDIT_ID}, full ISMS audit, {D.AUDIT_DATES}"),
             ("Audit team", f"{D.LEAD} (lead auditor) and {D.AUDITOR} (auditor), {D.FIRM}. Fictional people and firm."), ("Prepared by", "Jahangir Shukurov"),
             ("Classification", "Confidential (sample)"), ("Evidence basis", "Audit evidence, samples and results are simulated. No real organization was audited."),
             ("Independence", D.INDEPENDENCE), ("", ""), ("How to use", ""),
             ("1. Dashboard", "Live counts of audit results, findings and corrective actions."),
             ("2. Programme", "Three-year audit programme and the coverage of each area."),
             ("3. Checklist", "46 risk-based audit questions with criteria, evidence sought, sampling, result and what the auditor saw."),
             ("4. Findings", "Twelve findings with statement, owner, linked risks and root cause."),
             ("5. Evidence Notes", "Fifteen records of what was examined, when and with whom."),
             ("6. CAPA", "Corrective actions with owners and due dates. Days to due and overdue status are calculated from the as-of date on the Dashboard."),
             ("7. KPI Dashboard", "Ten objectives and five key risk indicators, monthly from January to July 2027, with status and trend."),
             ("8. Roles", "Named role-holders from the Company Fact Sheet."),
             ("", ""), ("Editing", "Yellow cells are inputs. Names, counts, statuses and dates to due are formulas.")]
    for i, (a, b) in enumerate(notes, start=4):
        readme.cell(row=i, column=1, value=a).font = F(bold=True, size=10)
        cell = readme.cell(row=i, column=2, value=b)
        cell.font, cell.alignment = F(size=10), WRAP

    ro = wb.create_sheet("Roles")
    title(ro, "Role-holders (from Company Fact Sheet)")
    header(ro, 4, ["Role ID", "Name", "Title", "Location"], [12, 24, 48, 10])
    write_rows(ro, [[r["id"], r["name"], r["title"], r["location"]] for r in MASTER["roles"]], [12, 24, 48, 10])

    # Programme -----------------------------------------------------------------------------
    pr = wb.create_sheet("Programme")
    title(pr, "Internal audit programme 2027 to 2029")
    widths = [34, 10] + [13] * len(D.PROGRAMME) + [10]
    header(pr, 4, ["ID", "Year", "Month", "Audit", "Type", "Focus"], [13, 8, 8, 30, 12, 70])
    write_rows(pr, [list(a) for a in D.PROGRAMME], [13, 8, 8, 30, 12, 70], center=(1, 2, 3, 5))
    top = 5 + len(D.PROGRAMME) + 2
    pr.cell(row=top - 1, column=1, value="Coverage by area: F is a full audit of the area, S is a sample").font = F(bold=True, color=ACCENT, size=10)
    cols = ["Area", "Risk rating"] + [a[0] for a in D.PROGRAMME] + ["Times audited"]
    for c, name in enumerate(cols, start=1):
        cell = pr.cell(row=top, column=c, value=name)
        cell.font, cell.fill, cell.border, cell.alignment = F(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=ACCENT), BOX, Alignment(wrap_text=True, vertical="center", horizontal="center" if c > 1 else None)
    pr.row_dimensions[top].height = 30
    for i, (area, rating, marks) in enumerate(D.COVERAGE, start=top + 1):
        last_col = L(2 + len(marks))
        values = [area, rating] + marks + [f'=COUNTIF(C{i}:{last_col}{i},"F")+COUNTIF(C{i}:{last_col}{i},"S")']
        for c, v in enumerate(values, start=1):
            cell = pr.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
            if 2 < c < len(values):
                cell.fill = INPUT
    end = top + len(D.COVERAGE)
    grid = f"C{top + 1}:{L(2 + len(D.PROGRAMME))}{end}"
    fills(pr, grid, {"F": "8FCBB0", "S": "DCEFE5"})
    list_validation(pr, grid, '"F,S,-"')

    # Evidence notes ------------------------------------------------------------------------
    en = wb.create_sheet("Evidence Notes")
    title(en, "Audit evidence notes (simulated)")
    widths = [8, 12, 26, 11, 20, 74, 60]
    header(en, 4, ["ID", "Date", "Method", "Auditee ID", "Auditee", "What was examined", "Result"], widths)
    rows = [[e[0], day(e[1]), e[2], e[3], "=" + ROLE_LOOKUP.format(cell=f"D{i}"), e[4], e[5]] for i, e in enumerate(D.EVIDENCE_NOTES, start=5)]
    en_last = write_rows(en, rows, widths, center=(1, 2, 4))
    for i in range(5, en_last + 1):
        en.cell(row=i, column=2).number_format = "DD MMM YYYY"
    en.freeze_panes = "C5"

    # Checklist -----------------------------------------------------------------------------
    ck = wb.create_sheet("Checklist")
    title(ck, f"Audit checklist: {D.AUDIT_ID}")
    ck["A3"] = "Questions are risk-based: areas behind High risks are tested with larger samples. Yellow cells are inputs."
    ck["A3"].font = F(color=MUTED)
    widths = [7, 20, 26, 46, 36, 28, 11, 20, 22, 58, 10]
    header(ck, 4, ["ID", "Area", "Criteria", "Audit question", "Evidence sought", "Sampling", "Auditee ID", "Auditee", "Result", "What the auditor saw", "Finding"], widths)
    rows = [[q[0], q[1], q[2], q[3], q[4], q[5], q[6], "=" + ROLE_LOOKUP.format(cell=f"G{i}"), D.RESULT[q[7]], q[8], q[9]] for i, q in enumerate(D.CHECKLIST, start=5)]
    ck_last = write_rows(ck, rows, widths, center=(1, 7, 9, 11), inputs=(9,))
    list_validation(ck, f"I5:I{ck_last}", '"' + ",".join(D.RESULT.values()) + '"')
    fills(ck, f"I5:I{ck_last}", RESULT_FILL)
    ck.freeze_panes = "D5"
    ck.auto_filter.ref = f"A4:K{ck_last}"
    chk = lambda col: f"Checklist!${col}$5:${col}${ck_last}"

    # CAPA ----------------------------------------------------------------------------------
    ca = wb.create_sheet("CAPA")
    title(ca, "Corrective action tracker")
    ca["A3"] = f"Status as of the date on the Dashboard ({D.CAP_DATE}). Days to due and schedule status are formulas."
    ca["A3"].font = F(color=MUTED)
    widths = [9, 9, 74, 11, 20, 13, 13, 10, 12]
    header(ca, 4, ["Action ID", "Finding", "Corrective action", "Owner ID", "Owner", "Due date", "Status", "Days to due", "Schedule"], widths)
    rows, i = [], 5
    as_of = datetime.strptime(D.CAP_DATE, "%d %B %Y").date()
    for c in D.CAPA:
        for n, (action, owner, due) in enumerate(c["actions"], start=1):
            status = "Done" if day(due) <= as_of else "In progress"
            rows.append([f"{c['id']}.{n}", c["finding"], action, owner, "=" + ROLE_LOOKUP.format(cell=f"D{i}"), day(due), status,
                         f'=IF(G{i}="Done","",F{i}-Dashboard!$B$4)', f'=IF(G{i}="Done","Done",IF(F{i}<Dashboard!$B$4,"Overdue","On time"))'])
            i += 1
    ca_last = write_rows(ca, rows, widths, center=(1, 2, 4, 6, 7, 8, 9), inputs=(4, 6, 7))
    for r in range(5, ca_last + 1):
        ca.cell(row=r, column=6).number_format = "DD MMM YYYY"
    list_validation(ca, f"G5:G{ca_last}", '"Open,In progress,Done"')
    fills(ca, f"I5:I{ca_last}", {"Overdue": RED, "On time": AMBER, "Done": GREEN})
    ca.freeze_panes = "C5"
    ca.auto_filter.ref = f"A4:I{ca_last}"
    cap = lambda col: f"CAPA!${col}$5:${col}${ca_last}"

    # Findings ------------------------------------------------------------------------------
    fd = wb.create_sheet("Findings")
    title(fd, "Findings register")
    widths = [9, 24, 34, 30, 62, 11, 20, 22, 9, 10, 10, 62]
    header(fd, 4, ["ID", "Type", "Title", "Criteria", "Statement", "Owner ID", "Owner", "Linked risks", "Checklist items", "Actions", "Actions done", "Root cause"], widths)
    roots = {c["finding"]: c["root"] for c in D.CAPA}
    rows = [[f["id"], f["type"], f["title"], f["criteria"], f["statement"], f["owner"], "=" + ROLE_LOOKUP.format(cell=f"F{i}"), f["risks"], f"=COUNTIF({chk('K')},A{i})",
             f"=COUNTIF({cap('B')},A{i})", f'=COUNTIFS({cap("B")},A{i},{cap("G")},"Done")', roots.get(f["id"], "-")] for i, f in enumerate(D.FINDINGS, start=5)]
    fd_last = write_rows(fd, rows, widths, center=(1, 2, 6, 9, 10, 11))
    fills(fd, f"B5:B{fd_last}", RESULT_FILL)
    fd.freeze_panes = "D5"
    fd.auto_filter.ref = f"A4:L{fd_last}"

    # KPI dashboard -------------------------------------------------------------------------
    kp = wb.create_sheet("KPI Dashboard")
    title(kp, "ISMS KPI and KRI dashboard, January to July 2027")
    kp["A3"] = "Monthly readings are inputs. Latest value, status and trend are formulas."
    kp["A3"].font = F(color=MUTED)
    widths = [9, 50, 8, 10, 8] + [7] * 7 + [8, 12, 12, 11, 20, 13]
    header(kp, 4, ["ID", "Measure", "Unit", "Better when", "Target"] + D.MONTHS + ["Latest", "Status", "Trend", "Owner ID", "Owner", "Due date"], widths)
    rows = []
    for i, k in enumerate(D.KPIS, start=5):
        higher = k[3] == "up"
        rows.append([k[0], k[1], k[2], "Higher" if higher else "Lower", k[4], *k[5], f"=L{i}",
                     f'=IF(IF(D{i}="Higher",M{i}>=E{i},M{i}<=E{i}),"On target",IF(AND(R{i}<>"-",R{i}>Dashboard!$B$4),"On track","Off target"))',
                     f'=IF(L{i}=K{i},"Steady",IF((L{i}>K{i})=(D{i}="Higher"),"Improving","Worsening"))', k[6], "=" + ROLE_LOOKUP.format(cell=f"P{i}"), day(D.KPI_DUE[k[0]]) if k[0] in D.KPI_DUE else "-"])
    kp_last = write_rows(kp, rows, widths, center=tuple(range(3, 17)) + (18,), inputs=tuple(range(6, 13)))
    for r in range(5, kp_last + 1):
        kp.cell(row=r, column=18).number_format = "DD MMM YYYY"
    fills(kp, f"N5:N{kp_last}", {"On target": GREEN, "On track": AMBER, "Off target": ORANGE})
    fills(kp, f"O5:O{kp_last}", {"Worsening": RED})
    kp.freeze_panes = "C5"
    for anchor, heading, picks in (("A22", "Coverage measures, %", ("OBJ-04", "OBJ-07", "OBJ-09", "OBJ-10", "KRI-03")), ("J22", "Risks rated High or Critical", ("KRI-01",))):
        chart = LineChart()
        chart.title, chart.style, chart.height, chart.width = heading, 12, 8.5, 15.5
        chart.y_axis.delete = chart.x_axis.delete = False
        for pick in picks:
            row = 5 + [k[0] for k in D.KPIS].index(pick)
            chart.add_data(Reference(kp, min_col=2, max_col=12, min_row=row, max_row=row), from_rows=True, titles_from_data=True)
        chart.set_categories(Reference(kp, min_col=6, max_col=12, min_row=4, max_row=4))
        for series in chart.series:
            series.smooth = False
        kp.add_chart(chart, anchor)

    # Dashboard -----------------------------------------------------------------------------
    ds = wb.create_sheet("Dashboard")
    title(ds, "Dashboard")
    for col, width in zip("ABCD", (44, 16, 16, 16)):
        ds.column_dimensions[col].width = width
    ds["A4"], ds["B4"] = "As-of date (input)", as_of
    ds["A4"].font = F(bold=True)
    ds["B4"].font, ds["B4"].fill, ds["B4"].number_format, ds["B4"].alignment = F(bold=True, size=11, color=ACCENT), INPUT, "DD MMM YYYY", Alignment(horizontal="right")
    facts = [("Audit questions", f"=COUNTA({chk('A')})"), ("Questions with full conformity", f'=COUNTIF({chk("I")},"Conforms")'),
             ("Nonconformities raised", f'=COUNTIF(Findings!$B$5:$B${fd_last},"*nonconformity")'), ("Corrective actions", f"=COUNTA({cap('A')})"),
             ("Corrective actions done", f'=COUNTIF({cap("G")},"Done")'), ("Corrective actions overdue", f'=COUNTIF({cap("I")},"Overdue")'),
             ("KPIs and KRIs on target", f"=COUNTIF('KPI Dashboard'!$N$5:$N${kp_last},\"On target\")"), ("KPIs and KRIs off target", f"=COUNTIF('KPI Dashboard'!$N$5:$N${kp_last},\"Off target\")")]
    for i, (label, formula) in enumerate(facts, start=5):
        ds.cell(row=i, column=1, value=label).font = F(bold=True)
        cell = ds.cell(row=i, column=2, value=formula)
        cell.font, cell.fill, cell.alignment = F(bold=True, size=11, color=ACCENT), TINTED, Alignment(horizontal="right")
    header(ds, 15, ["Checklist result", "Questions"])
    for i, label in enumerate(D.RESULT.values(), start=16):
        for c, v in enumerate((label, f"=COUNTIF({chk('I')},A{i})"), start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
        ds.cell(row=i, column=1).fill = PatternFill("solid", fgColor=RESULT_FILL[label])
    header(ds, 24, ["Finding type", "Findings"])
    types = ["Major nonconformity", "Minor nonconformity", "Observation", "Opportunity for improvement"]
    for i, label in enumerate(types, start=25):
        for c, v in enumerate((label, f"=COUNTIF(Findings!$B$5:$B${fd_last},A{i})"), start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
        ds.cell(row=i, column=1).fill = PatternFill("solid", fgColor=RESULT_FILL[label])
    owners = sorted({f["owner"] for f in D.FINDINGS})
    header(ds, 31, ["Finding owner ID", "Owner", "Findings", "Open actions"])
    for i, owner in enumerate(owners, start=32):
        values = [owner, "=" + ROLE_LOOKUP.format(cell=f"A{i}"), f"=COUNTIF(Findings!$F$5:$F${fd_last},A{i})", f'=COUNTIFS({cap("D")},A{i},{cap("G")},"<>Done")']
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c in (1, 3, 4) else Alignment()
    end = 32 + len(owners)
    ds.cell(row=end + 1, column=1, value="Totals check").font = F(bold=True, color=MUTED)
    ds.cell(row=end + 1, column=2, value=f'=IF(AND(SUM(B16:B21)=B5,SUM(B25:B28)=COUNTA(Findings!$A$5:$A${fd_last}),SUM(C32:C{end - 1})=SUM(B25:B28)),"OK","CHECK")').font = F(bold=True, color=MUTED)
    ds.freeze_panes = "A4"

    wb["Dashboard"].sheet_properties.tabColor = ACCENT
    wb._sheets = [wb[n] for n in ["README", "Dashboard", "Programme", "Checklist", "Findings", "Evidence Notes", "CAPA", "KPI Dashboard", "Roles"]]
    for ws in wb.worksheets:
        ws.oddFooter.left.text = DISCLAIMER
        ws.oddFooter.right.text = "Page &P of &N"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    for name in ("Dashboard", "KPI Dashboard", "Programme"):
        wb[name].page_setup.fitToHeight = 1
    props = wb.properties
    props.creator, props.title, props.subject = "Jahangir Shukurov", "Internal Audit Workbook", DISCLAIMER
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("Saved", OUT.name)


if __name__ == "__main__":
    build()
