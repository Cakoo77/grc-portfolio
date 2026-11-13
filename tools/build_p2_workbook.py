#!/usr/bin/env python3
"""Build the Project 2 risk assessment workbook with live formulas."""
import json
import sys
from datetime import date
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

sys.path.insert(0, str(Path(__file__).parent))
import p2_data as D
from build_p1_workbook import BOX, CENTER, F, INPUT, TINTED, WRAP, est_height, header, title
from doc_template import ACCENT, DISCLAIMER, MUTED, ROOT

MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
OUT = ROOT / "02-risk-assessment/deliverables/Orvanta-Risk-Assessment-Workbook.xlsx"
LEVEL_FILL = {"Critical": "E9805F", "High": "F6C08F", "Medium": "FBE9B0", "Low": "CFE6D8"}
FIRST = 5
ROLE_LOOKUP = "INDEX(Roles!$B$5:$B$28,MATCH({cell},Roles!$A$5:$A$28,0))"


def level_formula(cell):
    return f'=IF({cell}>=Criteria!$B$21,"Critical",IF({cell}>=Criteria!$B$22,"High",IF({cell}>=Criteria!$B$23,"Medium","Low")))'


def level_rules(ws, rng):
    for label, color in LEVEL_FILL.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))


def write_rows(ws, rows, widths, first=FIRST, center=(), inputs=()):
    for i, values in enumerate(rows, start=first):
        for c, value in enumerate(values, start=1):
            cell = ws.cell(row=i, column=c, value=value)
            cell.font, cell.border = F(), BOX
            cell.alignment = CENTER if c in center else WRAP
            if c in inputs:
                cell.fill = INPUT
        ws.row_dimensions[i].height = est_height(values, widths)
    return first + len(rows) - 1


def list_validation(ws, rng, formula):
    dv = DataValidation(type="list", formula1=formula, allow_blank=False, showErrorMessage=True, errorTitle="Invalid value", error="Choose from the list.")
    dv.add(rng)
    ws.add_data_validation(dv)


def assets():
    systems = {s["id"]: s for s in MASTER["systems"]}
    classes = {d["id"]: d for d in MASTER["data_classes"]}
    rank = {"Restricted": 3, "Confidential": 2, "Internal": 1}
    rows = []
    for sid, (kind, c, i, a) in D.SYSTEM_ASSETS.items():
        s = systems[sid]
        top = max((classes[d]["classification"] for d in s["data"]), key=rank.get)
        rows.append([s["name"], kind, sid, s["owner"], c, i, a, top, s["hosting"]])
    for did, (owner, c, i, a) in D.DATA_ASSETS.items():
        rows.append([classes[did]["name"], "Information", did, owner, c, i, a, classes[did]["classification"], "AWS eu-central-1 and SaaS tools"])
    rows += [list(x) for x in D.OTHER_ASSETS]
    return [[f"AST-{n:02d}"] + r for n, r in enumerate(rows, start=1)]


def build():
    wb = Workbook()
    readme = wb.active
    readme.title = "README"
    title(readme, "Threat-Informed Risk Assessment Workbook")
    readme.column_dimensions["A"].width = 24
    readme.column_dimensions["B"].width = 100
    notes = [("Client", "Orvanta Payments UAB (fictional)"), ("Document ID", "ORV-RISK-002, version 1.0, 12 February 2027"), ("Prepared by", "Jahangir Shukurov"),
             ("Classification", "Confidential (sample)"), ("Risk position as of", f"{D.AS_OF}. Quick wins QW-01 to QW-08 were complete by then and count as existing controls."),
             ("Evidence basis", "Simulated workshops and document review. No real organization was assessed."),
             ("References", "Method aligned with ISO/IEC 27005:2022 and ISO/IEC 27001:2022 clause 6.1.2. Controls are cited by Annex A ID only. Techniques are cited by MITRE ATT&CK ID and name."),
             ("", ""), ("How to use", ""),
             ("1. Dashboard", "Live counts by level and stage, top 10 risks, and risks by owner."),
             ("2. Risk Register", "30 risks. Each is scored three times: inherent, current (with existing controls) and target (after treatment)."),
             ("3. Heat Maps", "5x5 grids for the three stages. Each cell counts the risks at that likelihood and impact."),
             ("4. Treatment Plan", "26 actions with owners, due dates and roadmap references. Linked-risk figures are calculated."),
             ("5. Scenarios", "Three attack scenarios, step by step, with prevent, detect and respond coverage today and after treatment."),
             ("6. Assets", "40 assets with owners and confidentiality, integrity and availability ratings."),
             ("7. Threats", "21 threats. Adversarial threats are mapped to MITRE ATT&CK."),
             ("8. Criteria", "Likelihood and impact scales, level thresholds and risk appetite. Change a threshold and every sheet recalculates."),
             ("9. Roles", "Named role-holders from the Company Fact Sheet."),
             ("", ""), ("Editing", "Yellow cells are inputs. Scores, levels, lookups and counts are formulas."),
             ("Scoring", "Score = likelihood x impact. Inherent impact is the highest of the four impact dimensions.")]
    for i, (a, b) in enumerate(notes, start=4):
        readme.cell(row=i, column=1, value=a).font = F(bold=True, size=10)
        cell = readme.cell(row=i, column=2, value=b)
        cell.font, cell.alignment = F(size=10), WRAP

    # Criteria ------------------------------------------------------------------------------
    cr = wb.create_sheet("Criteria")
    title(cr, "Risk criteria")
    widths = [22, 16, 30, 34, 44, 40]
    header(cr, 4, ["Likelihood", "Label", "Expected frequency", "Threat-informed test"], widths)
    write_rows(cr, [list(x) for x in D.LIKELIHOOD], widths, 5, center=(1,))
    cr["A11"] = "Impact (the highest dimension sets the impact score)"
    cr["A11"].font = F(bold=True, color=ACCENT, size=10)
    header(cr, 12, ["Impact", "Label", "Financial", "Regulatory", "Customer", "Operational"])
    write_rows(cr, [list(x) for x in D.IMPACT], widths, 13, center=(1,))
    cr["A19"] = "Risk levels and acceptance authority"
    cr["A19"].font = F(bold=True, color=ACCENT, size=10)
    header(cr, 20, ["Level", "Minimum score", "Required response", "Who may accept"])
    write_rows(cr, [list(x) for x in D.LEVELS], widths, 21, center=(2,), inputs=(2,))
    for r in range(21, 25):
        cr.cell(row=r, column=1).fill = PatternFill("solid", fgColor=LEVEL_FILL[cr.cell(row=r, column=1).value])
    cr["A26"] = "Risk appetite: highest score acceptable without formal acceptance"
    cr["A26"].font = F(bold=True)
    cr["B26"] = D.APPETITE_MAX
    cr["B26"].font, cr["B26"].fill, cr["B26"].border = F(bold=True), INPUT, BOX
    cr["C26"] = "Scores above this need treatment or a signed acceptance."
    cr["C26"].font = F(color=MUTED)

    # Roles ---------------------------------------------------------------------------------
    ro = wb.create_sheet("Roles")
    title(ro, "Role-holders (from Company Fact Sheet)")
    header(ro, 4, ["Role ID", "Name", "Title", "Location"], [12, 24, 48, 10])
    write_rows(ro, [[r["id"], r["name"], r["title"], r["location"]] for r in MASTER["roles"]], [12, 24, 48, 10])
    assert len(MASTER["roles"]) == 24

    # Threats -------------------------------------------------------------------------------
    n_risks = len(D.RISKS)
    last = FIRST + n_risks - 1
    rr = lambda col: f"'Risk Register'!${col}${FIRST}:${col}${last}"
    th = wb.create_sheet("Threats")
    title(th, "Threat catalog")
    th["A3"] = "Technique IDs and names refer to MITRE ATT&CK, checked against attack.mitre.org in November 2026."
    th["A3"].font = F(color=MUTED)
    widths = [9, 36, 22, 26, 50, 46, 9]
    header(th, 4, ["ID", "Threat", "Source", "ATT&CK tactic", "ATT&CK technique", "Why it is relevant to Orvanta", "Risks linked"], widths)
    th_last = write_rows(th, [list(t) + [f"=COUNTIF({rr('E')},A{i})"] for i, t in enumerate(D.THREATS, start=5)], widths, center=(1, 7))
    th.freeze_panes = "C5"
    th.auto_filter.ref = f"A4:G{th_last}"

    # Assets --------------------------------------------------------------------------------
    asset_rows = assets()
    a = wb.create_sheet("Assets")
    title(a, "Asset register")
    a["A3"] = "Ratings: 3 high, 2 medium, 1 low. Criticality is the highest of the three ratings."
    a["A3"].font = F(color=MUTED)
    widths = [9, 34, 16, 10, 11, 20, 6, 6, 6, 11, 14, 30, 9]
    header(a, 4, ["ID", "Asset", "Type", "Source ref", "Owner ID", "Owner", "C", "I", "A", "Criticality", "Classification", "Location or hosting", "Risks linked"], widths)
    rows = []
    for i, r in enumerate(asset_rows, start=5):
        rows.append([r[0], r[1], r[2], r[3], r[4], "=" + ROLE_LOOKUP.format(cell=f"E{i}"), r[5], r[6], r[7],
                     f'=INDEX({{"Low","Medium","High"}},MAX(G{i}:I{i}))', r[8], r[9], f'=COUNTIF({rr("D")},"*"&A{i}&"*")'])
    a_last = write_rows(a, rows, widths, center=(1, 4, 5, 7, 8, 9, 10, 13), inputs=(5, 7, 8, 9))
    for col in "GHI":
        list_validation(a, f"{col}5:{col}{a_last}", '"1,2,3"')
    list_validation(a, f"E5:E{a_last}", "=Roles!$A$5:$A$28")
    a.freeze_panes = "C5"
    a.auto_filter.ref = f"A4:M{a_last}"

    # Risk register -------------------------------------------------------------------------
    rg = wb.create_sheet("Risk Register")
    title(rg, "Risk register")
    rg["A3"] = f"Position as of {D.AS_OF}. Yellow cells are inputs. Scores, levels and lookups are formulas."
    rg["A3"].font = F(color=MUTED)
    cols = ["ID", "Risk", "Risk statement", "Assets", "Threat ID", "ATT&CK technique", "Priority gap", "Baseline observation", "Owner ID", "Owner",
            "Inherent likelihood", "Financial", "Regulatory", "Customer", "Operational", "Inherent impact", "Inherent score", "Inherent level",
            "Existing controls", "Current likelihood", "Current impact", "Current score", "Current level",
            "Treatment option", "Annex A controls", "Treatment actions", "Target likelihood", "Target impact", "Target score", "Target level",
            "Due date", "Within appetite after treatment", "Acceptance ref", "Sort key"]
    widths = [8, 26, 52, 14, 9, 34, 9, 11, 11, 18, 10, 9, 10, 9, 10, 9, 9, 10, 40, 10, 9, 9, 10, 11, 22, 16, 10, 9, 9, 10, 12, 12, 11, 9]
    header(rg, 4, cols, widths)
    due = {t[0]: date.fromisoformat(t[3]) for t in D.TREATMENTS}
    rows = []
    for n, r in enumerate(D.RISKS, start=FIRST):
        actions = [x for x in r["actions"].split(", ") if x != "-"]
        rows.append([
            r["id"], r["title"], r["statement"], r["assets"], r["threat"],
            f"=INDEX(Threats!$E$5:$E${th_last},MATCH(E{n},Threats!$A$5:$A${th_last},0))", r["gap"], r["obs"], r["owner"], "=" + ROLE_LOOKUP.format(cell=f"I{n}"),
            r["li"], *r["impacts"], f"=MAX(L{n}:O{n})", f"=K{n}*P{n}", level_formula(f"Q{n}"),
            r["existing"], r["lc"], r["ic"], f"=T{n}*U{n}", level_formula(f"V{n}"),
            r["option"], r["controls"], r["actions"], r["lt"], r["it"], f"=AA{n}*AB{n}", level_formula(f"AC{n}"),
            max(due[x] for x in actions) if actions else date(2027, 8, 31),
            f'=IF(AC{n}<=Criteria!$B$26,"Yes","Needs acceptance")', r["acceptance"], f"=V{n}*10000+Q{n}*100+(100-ROW())"])
    center = (1, 5, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 27, 28, 29, 30, 31, 32, 33, 34)
    write_rows(rg, rows, widths, center=center, inputs=(9, 11, 12, 13, 14, 15, 20, 21, 24, 27, 28, 31))
    for n in range(FIRST, last + 1):
        rg.cell(row=n, column=31).number_format = "DD MMM YYYY"
    for col in ("K", "L", "M", "N", "O", "T", "U", "AA", "AB"):
        list_validation(rg, f"{col}{FIRST}:{col}{last}", '"1,2,3,4,5"')
    list_validation(rg, f"X{FIRST}:X{last}", '"Mitigate,Avoid,Transfer,Accept"')
    list_validation(rg, f"I{FIRST}:I{last}", "=Roles!$A$5:$A$28")
    list_validation(rg, f"E{FIRST}:E{last}", f"=Threats!$A$5:$A${th_last}")
    for col in ("R", "W", "AD"):
        level_rules(rg, f"{col}{FIRST}:{col}{last}")
    rg.conditional_formatting.add(f"AF{FIRST}:AF{last}", CellIsRule(operator="equal", formula=['"Needs acceptance"'], font=Font(bold=True, color="B4541A")))
    rg.column_dimensions["AH"].hidden = True
    rg.freeze_panes = rg.cell(row=FIRST, column=3)
    rg.auto_filter.ref = f"A4:AG{last}"

    # Treatment plan ------------------------------------------------------------------------
    tp = wb.create_sheet("Treatment Plan")
    title(tp, "Risk treatment plan")
    tp["A3"] = "Status as of 12 February 2027. Linked-risk figures are calculated from the Risk Register."
    tp["A3"].font = F(color=MUTED)
    widths = [9, 62, 11, 20, 13, 10, 8, 13, 9, 12]
    header(tp, 4, ["ID", "Action", "Owner ID", "Owner", "Due date", "Roadmap ref", "Effort", "Status", "Risks addressed", "Highest linked current score"], widths)
    rows = []
    for i, t in enumerate(D.TREATMENTS, start=5):
        rows.append([t[0], t[1], t[2], "=" + ROLE_LOOKUP.format(cell=f"C{i}"), date.fromisoformat(t[3]), t[4], t[5], t[6],
                     f'=COUNTIF({rr("Z")},"*"&A{i}&"*")', f'=SUMPRODUCT(MAX(ISNUMBER(SEARCH(A{i},{rr("Z")}))*{rr("V")}))'])
    tp_last = write_rows(tp, rows, widths, center=(1, 3, 5, 6, 7, 8, 9, 10), inputs=(3, 5, 8))
    for i in range(5, tp_last + 1):
        tp.cell(row=i, column=5).number_format = "DD MMM YYYY"
    list_validation(tp, f"H5:H{tp_last}", '"Planned,In progress,Done"')
    list_validation(tp, f"C5:C{tp_last}", "=Roles!$A$5:$A$28")
    tp.conditional_formatting.add(f"H5:H{tp_last}", CellIsRule(operator="equal", formula=['"Done"'], fill=PatternFill("solid", bgColor=LEVEL_FILL["Low"])))
    tp.conditional_formatting.add(f"H5:H{tp_last}", CellIsRule(operator="equal", formula=['"In progress"'], fill=PatternFill("solid", bgColor=LEVEL_FILL["Medium"])))
    tp.freeze_panes = "C5"
    tp.auto_filter.ref = f"A4:J{tp_last}"

    # Heat maps -----------------------------------------------------------------------------
    hm = wb.create_sheet("Heat Maps")
    title(hm, "Risk heat maps")
    hm["A3"] = "Each cell counts the risks at that likelihood (across) and impact (down). Colors follow the level thresholds in use when the workbook was built."
    hm["A3"].font = F(color=MUTED)
    band = lambda score: next(label for label, minimum, *_ in D.LEVELS if score >= minimum)
    for g, (name, lcol, icol) in enumerate((("Inherent", "K", "P"), ("Current, with existing controls", "T", "U"), ("Target, after treatment", "AA", "AB"))):
        c0 = 1 + g * 7
        hm.cell(row=5, column=c0, value=name).font = F(bold=True, color=ACCENT, size=10)
        hm.cell(row=6, column=c0, value="Impact").font = F(bold=True, color=MUTED)
        for k, impact in enumerate(range(5, 0, -1)):
            row = 7 + k
            hm.cell(row=row, column=c0, value=impact).font = F(bold=True)
            hm.cell(row=row, column=c0).alignment = Alignment(horizontal="center", vertical="center")
            for likelihood in range(1, 6):
                cell = hm.cell(row=row, column=c0 + likelihood, value=f"=COUNTIFS({rr(lcol)},{likelihood},{rr(icol)},{impact})")
                cell.fill = PatternFill("solid", fgColor=LEVEL_FILL[band(likelihood * impact)])
                cell.font, cell.border, cell.number_format = F(bold=True, size=12), BOX, "0;;"
                cell.alignment = Alignment(horizontal="center", vertical="center")
            hm.row_dimensions[row].height = 34
        for likelihood in range(1, 6):
            cell = hm.cell(row=12, column=c0 + likelihood, value=likelihood)
            cell.font, cell.alignment = F(bold=True), Alignment(horizontal="center")
        hm.cell(row=13, column=c0 + 1, value="Likelihood").font = F(bold=True, color=MUTED)
        hm.cell(row=14, column=c0, value="Total").font = F(color=MUTED)
        hm.cell(row=14, column=c0 + 1, value=f"=SUM({L(c0 + 1)}7:{L(c0 + 5)}11)").font = F(bold=True)
        hm.column_dimensions[L(c0)].width = 9
        for likelihood in range(1, 6):
            hm.column_dimensions[L(c0 + likelihood)].width = 8
        hm.column_dimensions[L(c0 + 6)].width = 4

    # Scenarios -----------------------------------------------------------------------------
    sc = wb.create_sheet("Scenarios")
    title(sc, "Attack scenarios: control coverage along the kill chain")
    sc["A3"] = "Status: Missing, Partial or Effective (by design, to be confirmed by testing). Technique IDs refer to MITRE ATT&CK."
    sc["A3"].font = F(color=MUTED)
    widths = [9, 6, 20, 36, 46, 16, 10, 10, 12, 10, 10, 12, 10, 10]
    header(sc, 4, ["Scenario", "Step", "Tactic", "Technique", "What happens at Orvanta", "Prevent controls", "Prevent today", "Prevent target",
                   "Detect controls", "Detect today", "Detect target", "Respond controls", "Respond today", "Respond target"], widths)
    rows = []
    for s in D.SCENARIOS:
        for n, st in enumerate(s["steps"], start=1):
            row = [s["id"], n, st[0], st[1], st[2]]
            for controls, today, target in st[3:]:
                row += [controls, D.STATUS[today], D.STATUS[target]]
            rows.append(row)
    sc_last = write_rows(sc, rows, widths, center=(1, 2, 7, 8, 10, 11, 13, 14), inputs=(7, 8, 10, 11, 13, 14))
    for col in "GHJKMN":
        rng = f"{col}5:{col}{sc_last}"
        list_validation(sc, rng, '"Missing,Partial,Effective"')
        for label, color in (("Missing", LEVEL_FILL["Critical"]), ("Partial", LEVEL_FILL["Medium"]), ("Effective", LEVEL_FILL["Low"])):
            sc.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{label}"'], fill=PatternFill("solid", bgColor=color)))
    sc.freeze_panes = "F5"
    sc.auto_filter.ref = f"A4:N{sc_last}"

    # Dashboard -----------------------------------------------------------------------------
    ds = wb.create_sheet("Dashboard")
    title(ds, "Dashboard")
    for col, width in zip("ABCDEFG", (34, 50, 20, 14, 14, 16, 16)):
        ds.column_dimensions[col].width = width
    facts = [("Risks assessed", f"=COUNTA({rr('A')})"),
             ("Critical or High today", f'=COUNTIF({rr("W")},"Critical")+COUNTIF({rr("W")},"High")'),
             ("Critical or High after treatment", f'=COUNTIF({rr("AD")},"Critical")+COUNTIF({rr("AD")},"High")'),
             ("Formally accepted above appetite", f'=COUNTIF({rr("AG")},"RA-*")'),
             ("Average score today", f"=AVERAGE({rr('V')})"),
             ("Average score after treatment", f"=AVERAGE({rr('AC')})")]
    for i, (label, formula) in enumerate(facts, start=4):
        ds.cell(row=i, column=1, value=label).font = F(bold=True)
        cell = ds.cell(row=i, column=2, value=formula)
        cell.font, cell.fill, cell.alignment = F(bold=True, size=11, color=ACCENT), TINTED, Alignment(horizontal="right")
        cell.number_format = "0.0" if "Average" in label else "0"
    header(ds, 10, ["Level", "Inherent", "Current", "After treatment"])
    for i, (label, *_rest) in enumerate(D.LEVELS, start=11):
        values = [label] + [f'=COUNTIF({rr(col)},A{i})' for col in ("R", "W", "AD")]
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
        ds.cell(row=i, column=1).fill = PatternFill("solid", fgColor=LEVEL_FILL[label])
    header(ds, 17, ["Treatment option", "Risks"])
    for i, option in enumerate(("Mitigate", "Avoid", "Transfer", "Accept"), start=18):
        for c, v in enumerate((option, f'=COUNTIF({rr("X")},A{i})'), start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c > 1 else Alignment()
    header(ds, 24, ["Top 10 risks today", "Risk", "Owner", "Current score", "Current level", "Target score", "Target level"])
    for n in range(1, 11):
        i = 24 + n
        match = f"MATCH(LARGE({rr('AH')},{n}),{rr('AH')},0)"
        values = [f"=INDEX({rr('A')},{match})"] + [f"=INDEX({rr(col)},{match})" for col in ("B", "J", "V", "W", "AC", "AD")]
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c in (1, 4, 5, 6, 7) else Alignment()
    level_rules(ds, "E25:E34")
    level_rules(ds, "G25:G34")
    owners = sorted({r["owner"] for r in D.RISKS})
    header(ds, 37, ["Risk owner ID", "Owner", "Risks", "Critical or High today", "Highest current score"])
    for i, owner in enumerate(owners, start=38):
        values = [owner, "=" + ROLE_LOOKUP.format(cell=f"A{i}"), f"=COUNTIF({rr('I')},A{i})",
                  f'=COUNTIFS({rr("I")},A{i},{rr("W")},"Critical")+COUNTIFS({rr("I")},A{i},{rr("W")},"High")',
                  f"=SUMPRODUCT(MAX(({rr('I')}=A{i})*{rr('V')}))"]
        for c, v in enumerate(values, start=1):
            cell = ds.cell(row=i, column=c, value=v)
            cell.font, cell.border = F(), BOX
            cell.alignment = Alignment(horizontal="center") if c in (1, 3, 4, 5) else Alignment()
    check = 38 + len(owners) + 1
    ds.cell(row=check, column=1, value="Totals check").font = F(bold=True, color=MUTED)
    ds.cell(row=check, column=2, value=f'=IF(AND(SUM(B11:B14)=B4,SUM(C11:C14)=B4,SUM(D11:D14)=B4,SUM(C38:C{check - 2})=B4,SUM(B18:B21)=B4),"OK","CHECK")').font = F(bold=True, color=MUTED)
    chart = BarChart()
    chart.type, chart.style, chart.title = "col", 10, "Risks by level at each stage"
    chart.add_data(Reference(ds, min_col=2, max_col=4, min_row=10, max_row=14), titles_from_data=True)
    chart.set_categories(Reference(ds, min_col=1, min_row=11, max_row=14))
    chart.y_axis.delete = chart.x_axis.delete = False
    chart.y_axis.majorUnit = 5
    for series, color in zip(chart.series, ("7F8C92", "B4541A", ACCENT)):
        series.graphicalProperties.solidFill = color
        series.graphicalProperties.line.solidFill = color
    chart.height, chart.width = 8.5, 15.5
    ds.add_chart(chart, "I3")
    ds.freeze_panes = "A4"

    wb["Dashboard"].sheet_properties.tabColor = ACCENT
    order = ["README", "Dashboard", "Risk Register", "Heat Maps", "Treatment Plan", "Scenarios", "Assets", "Threats", "Criteria", "Roles"]
    wb._sheets = [wb[n] for n in order]
    for ws in wb.worksheets:
        ws.oddFooter.left.text = DISCLAIMER
        ws.oddFooter.right.text = "Page &P of &N"
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    for name in ("Dashboard", "Heat Maps"):
        wb[name].page_setup.fitToHeight = 1
    props = wb.properties
    props.creator, props.title, props.subject = "Jahangir Shukurov", "Threat-Informed Risk Assessment Workbook", DISCLAIMER
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print("Saved", OUT.name)


if __name__ == "__main__":
    build()
