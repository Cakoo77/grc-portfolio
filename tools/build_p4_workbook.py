#!/usr/bin/env python3
"""Build the Project 4 Statement of Applicability workbook with live formulas."""
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(Path(__file__).parent))
import p1_data as P1
import p2_data as P2
import p3_data as P3
import p4_data as D
from build_p1_workbook import BOX, F, INPUT, TINTED, WRAP, header, title
from build_p2_workbook import ROLE_LOOKUP, list_validation, write_rows
from build_p3_docs import policy_id, requirements
from doc_template import ACCENT, DISCLAIMER, MUTED, ROOT

MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
OUT = ROOT / "04-statement-of-applicability/deliverables/Orvanta-Statement-of-Applicability.xlsx"
FILL = {"Implemented": "CFE6D8", "Partially implemented": "FBE9B0", "Planned": "F6C08F", "Not applicable": "E3E8EA"}
FIRST = 5


def links():
    """Return {control: (risk ids, requirement ids, primary document)} derived from Projects 2 and 3."""
    risks, reqs, primary = {}, {}, {}
    for r in P2.RISKS:
        for c in r["controls"].split(", "):
            risks.setdefault(c[2:], []).append(r["id"])
    for p in P3.POLICIES:
        for rid, _, _, controls in requirements(p):
            for c in controls.split(", "):
                reqs.setdefault(c, []).append(rid)
                primary.setdefault(c, policy_id(p))
    return risks, reqs, primary


def build():
    risks, reqs, primary = links()
    wb = Workbook()
    readme = wb.active
    readme.title = "README"
    title(readme, "Statement of Applicability")
    readme.column_dimensions["A"].width = 24
    readme.column_dimensions["B"].width = 100
    notes = [("Client", "Orvanta Payments UAB (fictional)"), ("Document ID", f"ORV-SOA-002, version 1.1, {D.AS_OF}"), ("Prepared by", "Jahangir Shukurov"),
             ("Classification", "Confidential (sample)"), ("Status as of", f"{D.AS_OF}. Evidence and status are simulated for this portfolio sample."),
             ("Copyright", "Annex A controls are cited by ID and short name only. All other wording is original."),
             ("", ""), ("How to use", ""),
             ("1. Dashboard", "Live counts: applicability, implementation status by theme, open controls by target date and by owner."),
             ("2. SoA", "All 93 Annex A controls: applicability, why the control is needed, status, how it is implemented, owner, linked risks, linked policy requirements and evidence."),
             ("3. Key Controls", "Fifteen key controls described in detail: how each works, who runs it, the tools, how it is checked and what remains."),
             ("4. Evidence", "Register of evidence referenced by the SoA, with location and owner. Usage counts are calculated."),
             ("5. Roles", "Named role-holders from the Company Fact Sheet."),
             ("", ""), ("Editing", "Yellow cells are inputs. Owner names, counts, lookups and the consistency check are formulas."),
             ("Where links come from", "Linked risks come from the risk register (ORV-RISK-002). Policy requirements come from the ISMS register (ORV-ISMS-002). The build script checks that every ID exists."),
             ("Regulatory relevance", "This column is an indicative mapping to help prioritize. It is not legal advice.")]
    for i, (a, b) in enumerate(notes, start=4):
        readme.cell(row=i, column=1, value=a).font = F(bold=True, size=10)
        cell = readme.cell(row=i, column=2, value=b)
        cell.font, cell.alignment = F(size=10), WRAP

    ro = wb.create_sheet("Roles")
    title(ro, "Role-holders (from Company Fact Sheet)")
    header(ro, 4, ["Role ID", "Name", "Title", "Location"], [12, 24, 48, 10])
    write_rows(ro, [[r["id"], r["name"], r["title"], r["location"]] for r in MASTER["roles"]], [12, 24, 48, 10])

    last = FIRST + len(P1.CONTROLS) - 1
    soa = lambda col: f"SoA!${col}${FIRST}:${col}${last}"

    ev = wb.create_sheet("Evidence")
    title(ev, "Evidence register")
    ev["A3"] = "Evidence is simulated for this portfolio sample. The last column counts the controls that cite each item."
    ev["A3"].font = F(color=MUTED)
    widths = [9, 62, 36, 11, 20, 10]
    header(ev, 4, ["ID", "Evidence", "Where it is held", "Owner ID", "Owner", "Controls using it"], widths)
    rows = [[e[0], e[1], e[2], e[3], "=" + ROLE_LOOKUP.format(cell=f"D{i}"), f'=COUNTIF({soa("Q")},"*"&A{i}&"*")'] for i, e in enumerate(D.EVIDENCE, start=5)]
    ev_last = write_rows(ev, rows, widths, center=(1, 4, 6), inputs=(4,))
    ev.freeze_panes = "C5"
    ev.auto_filter.ref = f"A4:F{ev_last}"

    s = wb.create_sheet("SoA")
    title(s, "Statement of Applicability: all 93 Annex A controls")
    s["A3"] = f"Status as of {D.AS_OF}. Yellow cells are inputs. Owner, counts, first evidence and the check column are formulas."
    s["A3"].font = F(color=MUTED)
    cols = ["Control", "Control name", "Theme", "Applicable", "Selected by risk treatment", "Regulatory relevance", "Why the control is needed, or why it is excluded", "Implementation status",
            "How it is implemented today", "Owner ID", "Owner", "Linked risks", "Risk count", "Policy requirements", "Requirement count", "Primary document", "Evidence refs",
            "First evidence item", "Target date", "Maturity in Nov 2026", "Check"]
    widths = [8, 34, 14, 10, 11, 13, 44, 16, 52, 11, 18, 24, 7, 26, 9, 13, 13, 38, 10, 9, 8]
    header(s, 4, cols, widths)
    rows = []
    for n, c in enumerate(P1.CONTROLS, start=FIRST):
        cid = c[0]
        status, reg, why, how, evidence, target = D.SOA[cid]
        rows.append(["A." + cid, c[1], P1.THEMES[cid.split(".")[0]], "No" if status == "N" else "Yes", f'=IF(M{n}>0,"Yes","No")', reg, why, D.STATUS[status], how, c[7],
                     "=" + ROLE_LOOKUP.format(cell=f"J{n}"), ", ".join(risks.get(cid, [])) or "-", f'=IF(L{n}="-",0,(LEN(L{n})-LEN(SUBSTITUTE(L{n},"RSK-","")))/4)',
                     ", ".join(reqs.get(cid, [])) or "-", f'=IF(N{n}="-",0,LEN(N{n})-LEN(SUBSTITUTE(N{n},",",""))+1)', primary.get(cid, "-"), evidence,
                     f'=IFERROR(INDEX(Evidence!$B$5:$B${ev_last},MATCH(LEFT(Q{n},5),Evidence!$A$5:$A${ev_last},0)),"-")', target, c[4],
                     f'=IF(OR(AND(D{n}="No",H{n}<>"Not applicable"),AND(D{n}="Yes",H{n}="Not applicable"),AND(D{n}="Yes",O{n}=0)),"CHECK","OK")'])
    write_rows(s, rows, widths, center=(1, 4, 5, 8, 10, 13, 15, 16, 17, 19, 20, 21), inputs=(4, 6, 8, 10, 17, 19))
    list_validation(s, f"D{FIRST}:D{last}", '"Yes,No"')
    list_validation(s, f"H{FIRST}:H{last}", '"Implemented,Partially implemented,Planned,Not applicable"')
    list_validation(s, f"J{FIRST}:J{last}", "=Roles!$A$5:$A$28")
    for label, color in FILL.items():
        s.conditional_formatting.add(f"H{FIRST}:H{last}", CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))
    s.conditional_formatting.add(f"U{FIRST}:U{last}", CellIsRule(operator="equal", formula=['"CHECK"'], font=Font(bold=True, color="B4541A")))
    s.conditional_formatting.add(f"D{FIRST}:D{last}", CellIsRule(operator="equal", formula=['"No"'], fill=PatternFill("solid", bgColor=FILL["Not applicable"])))
    s.freeze_panes = s.cell(row=FIRST, column=3)
    s.auto_filter.ref = f"A4:U{last}"

    kc = wb.create_sheet("Key Controls")
    title(kc, "Key control implementation")
    widths = [8, 30, 16, 62, 36, 30, 46, 46]
    header(kc, 4, ["Control", "Control name", "Status", "How it works at Orvanta", "Who runs it", "Tools", "How it is checked", "What remains"], widths)
    names = {c[0]: c[1] for c in P1.CONTROLS}
    rows = [["A." + cid, names[cid], f"=INDEX({soa('H')},MATCH(A{i},{soa('A')},0))", *detail] for i, (cid, detail) in enumerate(D.KEY_CONTROLS.items(), start=5)]
    kc_last = write_rows(kc, rows, widths, center=(1, 3))
    for label, color in FILL.items():
        kc.conditional_formatting.add(f"C5:C{kc_last}", CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))
    kc.freeze_panes = "C5"

    ds = wb.create_sheet("Dashboard")
    title(ds, "Dashboard")
    for col, width in zip("ABCDEFG", (40, 16, 18, 14, 16, 14, 14)):
        ds.column_dimensions[col].width = width
    facts = [("Controls in Annex A", f"=COUNTA({soa('A')})"), ("Applicable", f'=COUNTIF({soa("D")},"Yes")'), ("Excluded", f'=COUNTIF({soa("D")},"No")'),
             ("Implemented", f'=COUNTIF({soa("H")},"Implemented")'), ("Implemented, share of applicable", "=B7/B5"),
             ("Selected by risk treatment", f'=COUNTIF({soa("E")},"Yes")'), ("With regulatory relevance", f'=COUNTIF({soa("F")},"<>-")'),
             ("Consistency checks failing", f'=COUNTIF({soa("U")},"CHECK")')]
    for i, (label, formula) in enumerate(facts, start=4):
        ds.cell(row=i, column=1, value=label).font = F(bold=True)
        cell = ds.cell(row=i, column=2, value=formula)
        cell.font, cell.fill, cell.alignment = F(bold=True, size=11, color=ACCENT), TINTED, Alignment(horizontal="right")
    ds["B8"].number_format = "0%"
    statuses = list(FILL)
    header(ds, 13, ["Theme"] + statuses + ["Total"])
    for i, theme in enumerate(P1.THEMES.values(), start=14):
        values = [theme] + [f'=COUNTIFS({soa("C")},$A{i},{soa("H")},"{st}")' for st in statuses] + [f"=SUM(B{i}:E{i})"]
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
    for c in range(1, 7):
        cell = ds.cell(row=18, column=c, value="Total" if c == 1 else f"=SUM({chr(64 + c)}14:{chr(64 + c)}17)")
        cell.font, cell.border = F(bold=True), BOX
        cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
    targets = sorted({v[5] for v in D.SOA.values() if v[5] != "-"}, key=lambda t: (t[-4:], ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(t[:3])))
    header(ds, 21, ["Target date for open controls", "Controls"])
    for i, t in enumerate(targets, start=22):
        for c, v in enumerate((t, f'=COUNTIF({soa("S")},A{i})'), start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
    row = 22 + len(targets) + 1
    owners = sorted({c[7] for c in P1.CONTROLS})
    header(ds, row, ["Owner ID", "Owner", "Controls", "Not yet implemented"])
    first_owner = row + 1
    for i, owner in enumerate(owners, start=first_owner):
        values = [owner, "=" + ROLE_LOOKUP.format(cell=f"A{i}"), f"=COUNTIF({soa('J')},A{i})",
                  f'=COUNTIFS({soa("J")},A{i},{soa("H")},"Partially implemented")+COUNTIFS({soa("J")},A{i},{soa("H")},"Planned")']
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c in (1, 3, 4) else Alignment()
    end = first_owner + len(owners)
    ds.cell(row=end + 1, column=1, value="Totals check").font = F(bold=True, color=MUTED)
    ds.cell(row=end + 1, column=2, value=f'=IF(AND(F18=B4,SUM(C{first_owner}:C{end - 1})=B4,SUM(B22:B{21 + len(targets)})=C18+D18,B11=0),"OK","CHECK")').font = F(bold=True, color=MUTED)
    chart = BarChart()
    chart.type, chart.style, chart.grouping, chart.overlap, chart.title = "bar", 10, "stacked", 100, "Implementation status by theme"
    chart.add_data(Reference(ds, min_col=2, max_col=5, min_row=13, max_row=17), titles_from_data=True)
    chart.set_categories(Reference(ds, min_col=1, min_row=14, max_row=17))
    chart.y_axis.delete = chart.x_axis.delete = False
    chart.x_axis.scaling.orientation = "maxMin"
    for series, color in zip(chart.series, ("6FB39A", "F3C98B", "E08A5B", "B8C4CA")):
        series.graphicalProperties.solidFill = color
        series.graphicalProperties.line.solidFill = color
    chart.height, chart.width = 8.5, 17
    ds.add_chart(chart, "I3")
    ds.freeze_panes = "A4"

    wb["Dashboard"].sheet_properties.tabColor = ACCENT
    wb._sheets = [wb[n] for n in ["README", "Dashboard", "SoA", "Key Controls", "Evidence", "Roles"]]
    for ws in wb.worksheets:
        ws.oddFooter.left.text = DISCLAIMER
        ws.oddFooter.right.text = "Page &P of &N"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb["Dashboard"].page_setup.fitToHeight = 1
    props = wb.properties
    props.creator, props.title, props.subject = "Jahangir Shukurov", "Statement of Applicability", DISCLAIMER
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("Saved", OUT.name)


if __name__ == "__main__":
    build()
