#!/usr/bin/env python3
"""Build the Project 5 audit programme, audit plan, audit report, corrective action plan and management review documents."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch, Rectangle
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p5_data as D

P5 = T.ROOT / "05-internal-audit-management-review"
FIG, OUT = P5 / "figures", P5 / "deliverables"
WORKBOOK = OUT / "Orvanta-Internal-Audit-Workbook.xlsx"
MASTER = json.loads((T.ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
TITLE = {r["id"]: r["title"] for r in MASTER["roles"]}
SHORT = {"R-CEO": "CEO", "R-CTO": "CTO", "R-CFO": "CFO", "R-COO": "COO", "R-CISO": "CISO", "R-HCOMP": "Head of Compliance", "R-RISK": "Risk Manager", "R-DPO": "DPO", "R-HPEOPLE": "Head of People"}
TEAL, INK, MUTED, WARN = "#0F5C6E", "#16242C", "#52616B", "#B4541A"
RESULT_COLOR = {"Conforms": "#6FB39A", "Major nonconformity": "#D9623B", "Minor nonconformity": "#F2AE72", "Observation": "#FBE3A8", "Opportunity for improvement": "#BFD9E2", "Not yet due": "#B8C4CA"}
FILLS = {"Major nonconformity": "F3B9A3", "Minor nonconformity": "FAD9B8", "Observation": "FCF3D2", "Opportunity for improvement": "DCEAF0", "Conforms": "E1F0E7", "Not yet due": "E3E8EA",
         "On target": "E1F0E7", "On track": "FCF3D2", "Off target": "FAD9B8", "F": "8FCBB0", "S": "DCEFE5", "High": "FAD9B8"}
NOTE = "Audit evidence, samples and the audit team are simulated for this portfolio sample. " + D.INDEPENDENCE

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"


def load():
    wb = load_workbook(WORKBOOK, data_only=True)
    results = {}
    for r in wb["Checklist"].iter_rows(min_row=5, values_only=True):
        if r[0]:
            results[r[8]] = results.get(r[8], 0) + 1
    kpis = [dict(id=r[0], name=r[1], unit=r[2], better=r[3], target=r[4], series=list(r[5:12]), latest=r[12], status=r[13], trend=r[14], owner=r[16])
            for r in wb["KPI Dashboard"].iter_rows(min_row=5, values_only=True) if r[0]]
    actions = [dict(id=r[0], finding=r[1], action=r[2], owner=r[4], due=r[5], status=r[6], schedule=r[8]) for r in wb["CAPA"].iter_rows(min_row=5, values_only=True) if r[0]]
    return results, kpis, actions


def doc(title, subtitle, label, doc_id, date, reviewer, approver, toc, history):
    return T.BrandDoc(title=title, subtitle=subtitle, label=label, doc_id=doc_id, version="1.0", date=date, author="Jahangir Shukurov", reviewer=reviewer, approver=approver,
                      classification="Confidential (sample)", client="Orvanta Payments UAB", history=history, toc_pages=toc)


def fmt(value):
    return value.strftime("%d %b %Y").lstrip("0")


KPI_SHORT = {"OBJ-07": "OBJ-07  Log sources in SIEM, %", "OBJ-08": "OBJ-08  Tier 1 suppliers assessed", "OBJ-05": "OBJ-05  Leaver suspension, hours",
             "OBJ-09": "OBJ-09  Reviewed deployments, %", "KRI-01": "KRI-01  High or Critical risks", "KRI-03": "KRI-03  Alerts triaged in a day, %"}


# --- Figures ---------------------------------------------------------------------------------

def fig_coverage(path):
    audits = [a[0] for a in D.PROGRAMME]
    fig = plt.figure(figsize=(7.0, 3.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 3.5)
    ax.axis("off")
    x0, cw, rh, top = 2.25, 0.585, 0.215, 2.85
    for year, start, count in ((2027, 0, 2), (2028, 2, 3), (2029, 5, 3)):
        ax.text(x0 + (start + count / 2) * cw, 3.36, str(year), ha="center", va="center", fontsize=8.5, fontweight="bold", color=TEAL)
    for i, a in enumerate(D.PROGRAMME):
        ax.text(x0 + (i + 0.5) * cw, 3.08, f"{a[2]}\n{a[4]}", ha="center", va="center", fontsize=6.6, color=INK, linespacing=1.15)
    for r, (area, rating, marks) in enumerate(D.COVERAGE):
        y = top - (r + 1) * rh
        ax.text(0.02, y + rh / 2, area, va="center", fontsize=7.4, color=INK)
        ax.text(2.02, y + rh / 2, rating, va="center", ha="center", fontsize=6.8, color=WARN if rating == "High" else MUTED, fontweight="bold" if rating == "High" else "normal")
        for i, mark in enumerate(marks):
            color = {"F": "#0F5C6E", "S": "#9CCBD4", "-": "#EEF2F4"}[mark]
            ax.add_patch(Rectangle((x0 + i * cw + 0.02, y + 0.02), cw - 0.04, rh - 0.04, fc=color, ec="none"))
    ax.legend(handles=[Patch(fc="#0F5C6E", label="Full audit of the area"), Patch(fc="#9CCBD4", label="Sample"), Patch(fc="#EEF2F4", label="Not in this audit")],
              loc="lower center", ncol=3, frameon=False, fontsize=7.4, bbox_to_anchor=(0.6, -0.01), handlelength=1.1)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_results(path, results):
    order = [k for k in RESULT_COLOR if results.get(k)]
    fig, ax = plt.subplots(figsize=(7.0, 1.4))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.96, bottom=0.52)
    left = 0
    for key in order:
        n = results[key]
        ax.barh(0, n, left=left, color=RESULT_COLOR[key], edgecolor="white", linewidth=1.5, height=0.6)
        ax.text(left + n / 2, 0, str(n), ha="center", va="center", fontsize=9, fontweight="bold", color=INK)
        left += n
    ax.set_xlim(0, left)
    ax.axis("off")
    ax.legend(handles=[Patch(fc=RESULT_COLOR[k], label=k) for k in order], loc="lower center", ncol=3, frameon=False, fontsize=7.4, bbox_to_anchor=(0.5, -0.98), handlelength=1.1)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_fishbone(path):
    fig = plt.figure(figsize=(7.0, 3.3))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 3.3)
    ax.axis("off")
    spine_y = 1.65
    ax.plot([0.35, 5.5], [spine_y, spine_y], color=INK, lw=2)
    ax.add_patch(plt.Polygon([(5.5, spine_y + 0.42), (6.98, spine_y + 0.42), (6.98, spine_y - 0.42), (5.5, spine_y - 0.42)], fc=TEAL, ec="none"))
    ax.text(6.24, spine_y, "Critical suppliers\nnot under control\n(NC-01)", ha="center", va="center", fontsize=7.8, fontweight="bold", color="white", linespacing=1.2)
    cats = list(D.FISHBONE.items())
    for i, (name, causes) in enumerate(cats):
        upper = i % 2 == 0
        x = 1.5 + (i // 2) * 1.42
        y_end = spine_y + (1.2 if upper else -1.2)
        ax.plot([x + 0.55, x], [spine_y, y_end], color=MUTED, lw=1.2)
        ax.text(x - 0.02, y_end + (0.12 if upper else -0.12), name, ha="center", va="center", fontsize=8.2, fontweight="bold", color=TEAL)
        for k, cause in enumerate(causes):
            frac = 0.38 + k * 0.34
            cx, cy = x + 0.55 * (1 - frac), spine_y + (y_end - spine_y) * frac
            ax.text(cx - 0.06, cy, cause, ha="right", va="center", fontsize=7.6, color=INK)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_kpis(path, kpis):
    picks = ["OBJ-07", "OBJ-08", "OBJ-05", "OBJ-09", "KRI-01", "KRI-03"]
    by_id = {k["id"]: k for k in kpis}
    fig, axes = plt.subplots(2, 3, figsize=(7.0, 3.5))
    fig.subplots_adjust(left=0.06, right=0.985, top=0.9, bottom=0.08, wspace=0.28, hspace=0.62)
    for ax, pick in zip(axes.flat, picks):
        k = by_id[pick]
        color = TEAL if k["status"] != "Off target" else WARN
        ax.plot(range(7), k["series"], color=color, lw=1.8, marker="o", ms=3)
        ax.axhline(k["target"], color=MUTED, lw=0.9, ls="--")
        ax.text(6.05, k["target"], " target", va="bottom", ha="right", fontsize=6.2, color=MUTED)
        ax.set_title(KPI_SHORT[k["id"]], fontsize=7.4, color=INK, loc="left", pad=4)
        ax.set_xticks(range(7))
        ax.set_xticklabels([m[0] for m in D.MONTHS], fontsize=6.6, color=MUTED)
        ax.tick_params(axis="y", labelsize=6.6, colors=MUTED, length=0)
        ax.tick_params(axis="x", length=0)
        low, high = min(k["series"] + [k["target"]]), max(k["series"] + [k["target"]])
        pad = (high - low) * 0.15 or 1
        ax.set_ylim(low - pad, high + pad)
        ax.grid(axis="y", color="#E3EAED", lw=0.7)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


# --- Documents -------------------------------------------------------------------------------

def build_programme(toc):
    d = doc("Internal Audit Programme 2027 to 2029", "A three-year, risk-based plan for auditing the ISMS", "Project 5  |  Audit programme", "ORV-AUD-001", "21 May 2027",
            f"{WHO['R-HCOMP']}, Head of Compliance", f"{WHO['R-CEO']}, CEO", toc,
            [["0.1", "10 May 2027", "Jahangir Shukurov", "Draft for Head of Compliance review"], ["1.0", "21 May 2027", "Jahangir Shukurov", "Approved by the CEO"]])
    d.h1("Summary", new_page=True)
    d.p("This programme sets out which parts of the ISMS are audited, when and by whom, from 2027 to 2029. It meets ISO/IEC 27001:2022 clause 9.2 and follows the guidance of ISO 19011:2018 and ISO/IEC 27007.")
    d.stat_row([(str(len(D.PROGRAMME)), "Audits in three years"), ("2", "Full ISMS audits"), ("Yearly", "All High-risk areas"), ("3 years", "Every area at least once")])
    d.bullets([
        ("Risk decides frequency.", "Areas behind High risks are audited every year. Lower-risk areas are audited at least once in the cycle."),
        ("Timed for certification.", "A full audit comes before Stage 1, a follow-up before Stage 2, and themed audits before each surveillance visit."),
        ("Independent.", f"Audits are carried out by {D.FIRM}, which has no part in running the controls it tests."),
    ])
    d.callout(NOTE, lead="Reading note.")
    d.h1("Objectives and criteria")
    d.bullets(["Confirm that the ISMS conforms to ISO/IEC 27001:2022 and to Orvanta's own policies and procedures.",
               "Confirm that controls work in practice, with priority on those that treat High risks.",
               "Find weaknesses before the certification body does, and before an attacker does.",
               "Give the management review reliable input."])
    d.p("Audit criteria are ISO/IEC 27001:2022 clauses 4 to 10, the applicable Annex A controls in the Statement of Applicability, Orvanta's policies and procedures, and its legal and contractual requirements.")
    d.h1("Risk-based approach")
    d.table(["Area risk rating", "Basis", "Audit frequency"], [
        ["High", "Area treats a High or Critical risk, had a major gap in the gap assessment, or supports a critical service", "Every year"],
        ["Medium", "Area treats Medium risks or had moderate gaps", "At least twice in three years"],
        ["Low", "Area has stable controls and low inherent risk", "At least once in three years"],
    ], [0.2, 0.55, 0.25], first_bold=True)
    d.p("Ratings are reviewed each year against the risk register, incidents and earlier audit results. A serious incident or a major change can add an unplanned audit.")
    d.h1("Three-year schedule", new_page=True)
    d.table(["ID", "When", "Audit", "Type", "Focus"], [[a[0], f"{a[2]} {a[1]}", a[3], a[4], a[5]] for a in D.PROGRAMME], [0.14, 0.11, 0.24, 0.11, 0.4], size=8.5, first_bold=True)
    d.figure(FIG / "coverage.png", "Coverage of each area across the eight audits.")
    d.h1("Auditors")
    d.bullets([
        ("Independence.", "Auditors do not audit their own work. Nobody who designed or operates a control audits it. The audit firm reports to the Head of Compliance and has direct access to the Management Board Chair."),
        ("Competence.", "The lead auditor holds an ISO/IEC 27001 lead auditor qualification and has audited payment or financial services firms. Technical areas use an auditor with cloud and identity experience."),
        ("Evaluation.", "The Head of Compliance reviews auditor performance after each audit, using auditee feedback and report quality."),
    ])
    d.h1("Methods and reporting")
    d.bullets([
        ("Methods.", "Interviews, document review, observation and sample testing of records. Baku is audited by video, with screen sharing for system evidence."),
        ("Sampling.", "Sample sizes follow risk: larger for High-risk areas and for populations with past failures. The plan for each audit records the sizes used."),
        ("Findings.", "Each nonconformity states the requirement, the evidence and the failure. Findings are graded major, minor, observation or opportunity for improvement."),
        ("Reporting.", "A report is issued within five working days of the closing meeting. Owners propose corrective actions within ten working days."),
        ("Follow-up.", "Corrective actions are tracked to closure, and their effectiveness is tested at the next audit."),
    ])
    d.h1("Monitoring the programme")
    d.table(["Measure", "Target"], [["Audits completed as scheduled", "100%"], ["Reports issued within five working days", "100%"], ["Corrective actions closed by their due date", "At least 90%"],
                                    ["Repeat findings", "None"]], [0.7, 0.3], first_bold=True, keep=True)
    d.save(OUT / "ORV-AUD-001-Internal-Audit-Programme.docx")
    return d


def build_plan(toc):
    d = doc(f"Audit Plan {D.AUDIT_ID}", f"Full ISMS audit, {D.AUDIT_DATES}", "Project 5  |  Audit plan", "ORV-AUD-002", "28 June 2027",
            f"{D.LEAD}, Lead Auditor, {D.FIRM}", f"{WHO['R-HCOMP']}, Head of Compliance", toc,
            [["0.1", "21 June 2027", "Jahangir Shukurov", "Draft shared with auditees"], ["1.0", "28 June 2027", "Jahangir Shukurov", "Agreed with the Head of Compliance"]])
    d.h1("Audit overview", new_page=True)
    d.table(["Item", "Detail"], [
        ["Audit", f"{D.AUDIT_ID}, the first audit in the 2027 to 2029 programme"], ["Dates", D.AUDIT_DATES],
        ["Objectives", "Determine whether the ISMS conforms to ISO/IEC 27001:2022 and Orvanta's own requirements, whether it is effectively implemented, and whether Orvanta is ready for the Stage 1 certification audit"],
        ["Criteria", "ISO/IEC 27001:2022 clauses 4 to 10, applicable Annex A controls in the Statement of Applicability version 1.1, Orvanta policies ORV-POL-01 to 12, procedures ORV-PRC-01 and 02, and the Risk Management Methodology"],
        ["Scope", "The full ISMS scope: all products, AWS production, Vilnius, Baku and remote working. The sampling period is 1 February to 30 June 2027"],
        ["Audit team", f"{D.LEAD}, lead auditor. {D.AUDITOR}, auditor for technical areas. Both from {D.FIRM}"],
        ["Audit client", f"{WHO['R-HCOMP']}, Head of Compliance"], ["Language and location", "English. On site in Vilnius, by video with Baku"],
    ], [0.22, 0.78], first_bold=True)
    d.callout(NOTE, lead="Reading note.")
    d.h1("Schedule")
    d.table(["Day", "Time", "Activity", "Auditor", "Auditees"], [list(s) for s in D.SCHEDULE], [0.12, 0.08, 0.42, 0.15, 0.23], size=8)
    d.h1("Sampling approach", new_page=True)
    d.p("Samples are chosen by the auditors, not by the auditees. Sizes reflect the risk of the area and the size of the population.", keep_next=True)
    d.table(["Area", "Population", "Sample", "Why this size"], [
        ["Leavers", "14 leavers, April to June", "10", "Slow offboarding was a baseline weakness"],
        ["Joiners", "22 joiners, February to June", "15", "Induction gates production access"],
        ["Laptops", "131 laptops", "20", "Unmanaged devices drove two attack scenarios"],
        ["Privileged access requests", "About 180 requests, May to June", "15, plus every break-glass use", "Privileged access treats the highest risk"],
        ["Tier 1 suppliers", "8 suppliers", "All 8", "Small population, critical services"],
        ["Production deployments", "About 400 in June", "30", "14% bypassed review in 2026"],
        ["Vulnerabilities", "Critical and high findings, April to June", "20", "Deadlines are new this year"],
        ["Risks", "30 risks", "8, including both Critical risks", "Tests the method end to end"],
        ["Statement of Applicability", "93 controls", "15 key controls", "Statuses must match evidence"],
    ], [0.22, 0.26, 0.2, 0.32], size=8.5, first_bold=True)
    d.h1("Arrangements")
    d.bullets([
        ("Access.", "Auditors receive read-only access to Confluence and Jira for the week. System evidence is shown on screen by the auditee and is not exported."),
        ("Confidentiality.", "Auditors work under the non-disclosure agreement in the audit contract. Notes are kept in Orvanta's audit workspace and contain no customer personal data."),
        ("Safety of production.", "No testing is done on production systems. Any technical check is run by the auditee and agreed with the Head of Platform and SRE first."),
        ("Communication.", "A short meeting at the end of each day shares emerging findings, so that nothing in the closing meeting is a surprise."),
        ("Reporting.", f"The report is issued by {D.REPORT_DATE}."),
    ])
    d.save(OUT / "ORV-AUD-002-Audit-Plan-IA-2027-01.docx")
    return d


def report_factory(results):
    ncs = [f for f in D.FINDINGS if "nonconformity" in f["type"]]
    obs = [f for f in D.FINDINGS if f["type"] == "Observation"]
    ofis = [f for f in D.FINDINGS if f["type"].startswith("Opportunity")]
    total = sum(results.values())

    def build(toc):
        d = doc(f"Internal Audit Report {D.AUDIT_ID}", f"Full ISMS audit, {D.AUDIT_DATES}", "Project 5  |  Audit report", "ORV-AUD-003", D.REPORT_DATE,
                f"{D.LEAD}, Lead Auditor, {D.FIRM}", f"{WHO['R-HCOMP']}, Head of Compliance", toc,
                [["0.1", "19 July 2027", "Jahangir Shukurov", "Draft findings confirmed with owners"], ["1.0", D.REPORT_DATE, "Jahangir Shukurov", "Issued to the CEO and the Head of Compliance"]])
        d.h1("Executive summary", new_page=True)
        d.p(f"This was the first full internal audit of Orvanta's ISMS, eight months after the gap assessment and two months before the Stage 1 certification audit. "
            f"Two auditors tested {total} questions across clauses 4 to 10 and the highest-risk Annex A controls.", bold_lead="Situation.")
        d.stat_row([("1", "Major nonconformity"), ("5", "Minor nonconformities"), ("3", "Observations"), (f"{results['Conforms']} of {total}", "Questions fully conforming")])
        d.p("The ISMS is established and largely effective. The controls that treat the highest risks work, and they were tested hardest. One area does not work: supplier control. "
            "Orvanta is ready for Stage 1 once the major nonconformity is closed.", bold_lead="Overall conclusion.")
        d.p("", bold_lead="Key findings.", after=2, keep_next=True)
        d.bullets([
            ("Critical suppliers are not under control (major).", "Three of eight Tier 1 suppliers are unassessed, and a critical contract was renewed without the required assessment."),
            ("Three controls depend on memory, not on systems.", "Leaver checks outside single sign-on, induction before production access, and tracking of risk acceptance conditions each failed in a sample."),
            ("Detection relies on one person.", "Alerts went untriaged for four days during a period of leave."),
            ("The strongest results are where the risk is highest.", "Device control, privileged access, backups and change control passed every sample."),
        ])
        d.p("A certification auditor who finds unassessed critical suppliers would raise the same major finding, which would delay certification and the EUR 2.4M of revenue that depends on it.", bold_lead="Risk in business terms.")
        d.p("", bold_lead="Decisions needed.", after=3, keep_next=True)
        d.table(["#", "Decision", "Owner", "By"], [
            ["1", "Approve the corrective action plan", WHO["R-CEO"], "6 Aug 2027"],
            ["2", "Give the supplier assessments priority over other August work", WHO["R-CEO"], "30 Jul 2027"],
            ["3", "Schedule the follow-up audit before Stage 2", WHO["R-HCOMP"], "15 Oct 2027"],
        ], [0.05, 0.6, 0.2, 0.15], after=0)

        d.h1("Scope, criteria and method", new_page=True)
        d.p(f"The audit covered the full ISMS scope from {D.AUDIT_DATES}, on site in Vilnius and by video with Baku. Criteria were ISO/IEC 27001:2022 clauses 4 to 10, the applicable Annex A controls, and Orvanta's policies, procedures and risk methodology. "
            "The audit followed the plan ORV-AUD-002 without change. It used interviews, document review, observation and sample testing over the period 1 February to 30 June 2027.")
        d.callout(NOTE, lead="Reading note.")
        d.h2("How findings are graded")
        d.table(["Grade", "Meaning"], [
            ["Major nonconformity", "A required process is missing or has broken down, or a failure puts the ISMS's ability to achieve its results in doubt."],
            ["Minor nonconformity", "A requirement was not met in a specific case, without a breakdown of the system."],
            ["Observation", "Not a failure today, but likely to become one if nothing changes."],
            ["Opportunity for improvement", "A suggestion that would make a conforming control work better."],
        ], [0.28, 0.72], first_bold=True, fills=FILLS)
        d.p("An audit tests samples. It cannot prove that no other problems exist, and conformity in a sample does not guarantee conformity everywhere.")
        d.h1("Results")
        d.figure(FIG / "results.png", f"Results of the {total} audit questions. Two questions led to the same major finding.")
        d.h2("Strengths")
        d.bullets(D.STRENGTHS)
        d.h2("Summary of findings")
        d.table(["ID", "Grade", "Finding", "Criteria", "Owner"], [[f["id"], f["type"], f["title"], f["criteria"], WHO[f["owner"]]] for f in D.FINDINGS],
                [0.09, 0.2, 0.33, 0.24, 0.14], size=8, fills=FILLS, zebra=False, keep=True)

        d.h1("Nonconformities", new_page=True)
        d.p("Each nonconformity states what is required, what the auditors found, and the failure that follows from comparing the two.")
        for f in ncs:
            d.h3(f"{f['id']}  {f['title']}")
            d.table(["Element", "Detail"], [["Grade", f["type"]], ["Criteria", f["criteria"]], ["Requirement", f["requirement"]], ["Evidence", f["evidence"]],
                                           ["Statement of nonconformity", f["statement"]], ["Reason for the grade", f["reason"]], ["Owner", WHO[f["owner"]]], ["Linked risks", f["risks"]]],
                    [0.22, 0.78], size=8.5, first_bold=True, fills=FILLS, zebra=False, keep=True)
        d.h1("Observations and opportunities")
        d.h2("Observations")
        d.table(["ID", "Observation", "Evidence", "Why it matters", "Owner"], [[f["id"], f["title"], f["evidence"], f["statement"], WHO[f["owner"]]] for f in obs],
                [0.09, 0.2, 0.3, 0.27, 0.14], size=8.5, first_bold=True)
        d.h2("Opportunities for improvement")
        d.table(["ID", "Opportunity", "Evidence", "Benefit", "Owner"], [[f["id"], f["title"], f["evidence"], f["statement"], WHO[f["owner"]]] for f in ofis],
                [0.09, 0.2, 0.3, 0.27, 0.14], size=8.5, first_bold=True)
        d.h1("Conclusion and next steps")
        d.p("Orvanta has built a working ISMS in eight months. Its policies are specific, its high-risk controls are evidenced and its reporting is candid. The findings share a pattern: where a requirement was built into a system, it held, "
            "and where it relied on a person remembering, it failed. That pattern should guide the corrective actions.")
        d.bullets([
            ("By 6 August 2027.", "Owners submit root causes and corrective actions for all six nonconformities."),
            ("By 31 August 2027.", "The major nonconformity is closed, with evidence."),
            ("26 August 2027.", "The management review considers this report."),
            ("October 2027.", "Follow-up audit IA-2027-02 tests closure and effectiveness before Stage 2."),
        ])
        d.table(["Role", "Name", "Date", "Signature"], [["Lead auditor", f"{D.LEAD}, {D.FIRM}", D.REPORT_DATE, "Signed (sample)"], ["Auditor", f"{D.AUDITOR}, {D.FIRM}", D.REPORT_DATE, "Signed (sample)"],
                                                         ["Audit client", f"{WHO['R-HCOMP']}, Head of Compliance", D.REPORT_DATE, "Received (sample)"]], [0.18, 0.44, 0.18, 0.2], first_bold=True, keep=True)
        d.section(landscape=True)
        d.h1("Appendix: checklist results")
        d.p("The workbook holds the evidence sought and what the auditor saw for each question.", keep_next=True)
        d.table(["ID", "Area", "Criteria", "Audit question", "Sampling", "Result", "Finding"], [[q[0], q[1], q[2], q[3], q[5], D.RESULT[q[7]], q[9]] for q in D.CHECKLIST],
                [0.05, 0.12, 0.17, 0.3, 0.17, 0.13, 0.06], size=7.5, fills=FILLS, zebra=False)
        d.save(OUT / "ORV-AUD-003-Internal-Audit-Report-IA-2027-01.docx")
        return d

    return build


def cap_factory(actions):
    by_finding = {f["id"]: f for f in D.FINDINGS}

    def build(toc):
        d = doc("Corrective Action Plan", f"Root causes and actions for the nonconformities of {D.AUDIT_ID}", "Project 5  |  Corrective action plan", "ORV-AUD-004", D.CAP_DATE,
                f"{WHO['R-CISO']}, CISO", f"{WHO['R-CEO']}, CEO", toc,
                [["0.1", "30 July 2027", "Jahangir Shukurov", "Root cause workshops completed"], ["1.0", D.CAP_DATE, "Jahangir Shukurov", "Submitted for approval at the management review"]])
        d.h1("Summary", new_page=True)
        d.p(f"The internal audit {D.AUDIT_ID} raised one major and five minor nonconformities. This plan gives, for each one, the immediate correction, the root cause found through a five-whys analysis, the corrective actions and the way effectiveness will be checked.")
        d.stat_row([("6", "Nonconformities"), (str(len(actions)), "Corrective actions"), (str(sum(1 for a in actions if a["schedule"] == "Overdue")), "Overdue"), ("31 Aug 2027", "Major NC closure date")])
        d.callout("Two findings share one root cause. NC-01 and NC-04 both happened because a policy requirement was published but never built into the workflow or system that enforces it. "
                  "Fixing the policy rollout process addresses both, and protects the other ten policies from the same failure.", lead="The pattern.")
        d.table(["Action", "Finding", "Root cause in brief", "Owner", "Last due date"],
                [[c["id"], c["finding"], c["root"].split(". ")[0] + ".", WHO[by_finding[c["finding"]]["owner"]], max(c["actions"], key=lambda a: T.datetime.strptime(a[2], "%d %b %Y"))[2]] for c in D.CAPA],
                [0.09, 0.09, 0.52, 0.16, 0.14], size=8.5, first_bold=True)
        d.p("A correction fixes the instance that was found. A corrective action removes the cause, so that it does not happen again. Both are recorded, because an auditor will ask for both.")
        for n, c in enumerate(D.CAPA):
            f = by_finding[c["finding"]]
            d.h1(f"{c['id']}: {f['title']}", new_page=True)
            d.p(f["statement"], bold_lead=f"{f['id']}, {f['type'].lower()}.")
            d.p(c["correction"], bold_lead="Correction.")
            d.h2("Five whys")
            d.table(["#", "Question and answer"], [[i, why] for i, why in enumerate(c["whys"], start=1)], [0.06, 0.94], size=9, first_bold=True, keep=True)
            if n == 0:
                d.figure(FIG / "fishbone.png", "Cause-and-effect diagram for NC-01. The five whys follow the Process branch.", 0.6)
            d.callout(c["root"], lead="Root cause.")
            d.h2("Corrective actions")
            d.table(["ID", "Action", "Owner", "Due", "Status"], [[a["id"], a["action"], a["owner"], fmt(a["due"]), a["status"]] for a in actions if a["finding"] == c["finding"]],
                    [0.1, 0.5, 0.16, 0.12, 0.12], size=8.5, first_bold=True, keep=True)
            d.p(c["check"], bold_lead="Effectiveness check.")
        d.save(OUT / "ORV-AUD-004-Corrective-Action-Plan.docx")
        return d

    return build


def pack_factory(kpis, results):
    def build(toc):
        d = doc("Management Review Pack", f"Inputs for the ISMS management review of {D.REVIEW_DATE}", "Project 5  |  Management review", "ORV-MR-001", "19 August 2027",
                f"{WHO['R-CISO']}, CISO", f"{WHO['R-CEO']}, CEO", toc,
                [["0.1", "12 August 2027", "Jahangir Shukurov", "Draft for CISO review"], ["1.0", "19 August 2027", "Jahangir Shukurov", "Issued to attendees one week before the review"]])
        on = sum(1 for k in kpis if k["status"] == "On target")
        off = [k for k in kpis if k["status"] == "Off target"]
        rs = D.RISK_STATUS
        d.h1("Summary", new_page=True)
        d.p("This pack gives top management what it needs to judge whether the ISMS is suitable, adequate and effective, as ISO/IEC 27001:2022 clause 9.3 requires. "
            f"It is the first full review. Figures are as of {D.KPI_DATE}.", bold_lead="Purpose.")
        d.stat_row([(f"{on} of {len(kpis)}", "Measures on target"), (str(rs["high"]), "Risks still High"), ("1 + 5", "Major and minor NCs"), ("20 Sep 2027", "Stage 1 audit")])
        d.p("", bold_lead="What management should know.", after=2, keep_next=True)
        d.bullets([
            ("The program is working.", f"Risks rated High or Critical fell from 26 to {rs['high']} in seven months, and none is Critical."),
            ("One area failed.", "Supplier control produced a major nonconformity. Its corrective actions are due before Stage 1."),
            (f"{len(off)} measures are off target.", "SIEM coverage, supplier assessments and alert triage. All three trace to capacity in a small security team."),
            ("The ISMS held in a real incident.", "A phishing attack in May was contained in 40 minutes with no data loss."),
        ])
        d.p("", bold_lead="Decisions requested.", after=3, keep_next=True)
        d.table(["#", "Decision requested", "Proposed by"], [
            ["1", "Confirm that the ISMS is suitable, adequate and effective, with the exception of supplier control", "CISO"],
            ["2", "Approve the corrective action plan ORV-AUD-004", "CISO"],
            ["3", "Reconfirm or withdraw risk acceptance RA-01", "Risk Manager"],
            ["4", "Reset the dates for objectives OBJ-07 and OBJ-08", "CISO"],
            ["5", "Approve a managed detection service for out-of-hours cover", "CISO"],
            ["6", "Confirm that Stage 1 goes ahead on 20 and 21 September 2027", "Head of Compliance"],
        ], [0.05, 0.75, 0.2], after=0)
        d.h1("Review inputs", new_page=True)
        d.p("The table covers each input that clause 9.3.2 asks top management to consider.", keep_next=True)
        d.table(["Input", "Summary for this review"], [list(x) for x in D.REVIEW_INPUTS], [0.27, 0.73], size=9, first_bold=True)
        d.h1("Performance", new_page=True)
        d.h2("Trends")
        d.p("Dashed lines show targets. Orange marks a measure that is off target and past its date.", keep_next=True)
        d.figure(FIG / "kpis.png", f"Six measures from January to July 2027.")
        d.h2("All objectives and key risk indicators")
        d.table(["ID", "Measure", "Target", "Latest", "Status", "Trend", "Owner"], [[k["id"], k["name"], k["target"], k["latest"], k["status"], k["trend"], k["owner"]] for k in kpis],
                [0.08, 0.39, 0.07, 0.07, 0.11, 0.11, 0.17], size=8, first_bold=True, fills=FILLS, zebra=False)
        d.h1("Audit and risk", new_page=True)
        d.h2("Internal audit results")
        d.p(f"{results['Conforms']} of {sum(results.values())} audit questions showed full conformity. The six nonconformities are below, with their corrective action references.", keep_next=True)
        d.table(["ID", "Grade", "Finding", "Owner", "Action"], [[f["id"], f["type"], f["title"], WHO[f["owner"]], c["id"]] for f, c in zip([x for x in D.FINDINGS if "nonconformity" in x["type"]], D.CAPA)],
                [0.09, 0.22, 0.43, 0.16, 0.1], size=8.5, fills=FILLS, zebra=False)
        d.h2("Risk status")
        d.table(["Level", "January 2027", "July 2027"], [["Critical", 2, rs["critical"]], ["High", 24, rs["high"]], ["Medium", 4, rs["medium"]], ["Low", 0, rs["low"]]], [0.4, 0.3, 0.3], first_bold=True, keep=True)
        d.p(rs["note"] + " Twenty-one of 26 treatment actions are complete.")
        d.h2("Resources")
        d.p("The security team grew from two to three in March. Even so, three of the audit findings and all three off-target measures point to the same constraint: tasks that depend on one person. "
            "The proposals in this pack favor automation and shared rotas over further hiring, with a managed detection service for out-of-hours cover.")
        d.save(OUT / "ORV-MR-001-Management-Review-Pack.docx")
        return d

    return build


def build_minutes(toc):
    d = doc("Management Review Minutes", f"ISMS management review held on {D.REVIEW_DATE}", "Project 5  |  Management review", "ORV-MR-002", D.REVIEW_DATE,
            f"{WHO['R-CISO']}, CISO", f"{WHO['R-CEO']}, CEO", toc, [["1.0", D.REVIEW_DATE, "Jahangir Shukurov", "Minutes approved by the chair"]])
    d.h1("Meeting details", new_page=True)
    d.table(["Item", "Detail"], [["Meeting", "ISMS management review, first full review"], ["Date and place", f"{D.REVIEW_DATE}, 10:00 to 12:00, Vilnius office and video"], ["Chair", f"{WHO['R-CEO']}, CEO"],
                                 ["Minutes", "Jahangir Shukurov"], ["Input", "Management Review Pack ORV-MR-001, issued 19 August 2027"],
                                 ["Guest", f"{D.LEAD}, Lead Auditor, {D.FIRM}, for the audit item only"]], [0.22, 0.78], first_bold=True)
    d.h2("Attendees")
    d.table(["Name", "Role"], [[WHO[r], TITLE[r]] for r in D.ATTENDEES], [0.4, 0.6], first_bold=True)
    d.callout("The meeting and its attendees are fictional. " + D.INDEPENDENCE.split(". ", 1)[0] + ".", lead="Reading note.")
    d.h1("Discussion")
    d.table(["Item", "Discussion"], [
        ["1. Earlier actions", "All seven actions from the February and May checkpoints were confirmed closed."],
        ["2. Audit results", "The lead auditor presented the report. The CEO asked why supplier control failed when other controls held. The auditor's answer: the requirement was never built into the contract workflow. The General Counsel was not present, so the Head of Compliance took the action to confirm the workflow change."],
        ["3. Performance", "The CISO presented the dashboard. The CFO challenged the missed SIEM date. The CISO explained that the last sources are supplier portals that need custom connectors. The Board accepted a new date."],
        ["4. Risk", "The Risk Manager confirmed no Critical risks remain. The CTO asked that the single-region risk be studied properly in 2028, not only re-accepted each year."],
        ["5. Resources", "The CISO proposed a managed detection service. The CFO asked for a firm cost before final approval. Approval in principle was given."],
        ["6. Stage 1 readiness", "The Head of Compliance confirmed the certification body's dates. All agreed Stage 1 should go ahead only if NC-01 is closed and verified."],
    ], [0.2, 0.8], size=9, first_bold=True)
    d.h1("Decisions", new_page=True)
    d.p("These are the outputs of the review: decisions on improvement and on changes to the ISMS.", keep_next=True)
    d.table(["ID", "Decision"], [list(x) for x in D.DECISIONS], [0.1, 0.9], size=9, first_bold=True)
    d.h1("Actions")
    d.table(["ID", "Action", "Owner", "Due"], [[a[0], a[1], WHO[a[2]], a[3]] for a in D.REVIEW_ACTIONS], [0.1, 0.56, 0.2, 0.14], size=9, first_bold=True, keep=True)
    d.p("The next checkpoint is on 25 November 2027. The next full management review is planned for February 2028.")
    d.table(["Role", "Name", "Date", "Signature"], [["Chair", f"{WHO['R-CEO']}, CEO", D.REVIEW_DATE, "Signed (sample)"], ["Minutes", "Jahangir Shukurov", D.REVIEW_DATE, "Signed (sample)"]],
            [0.18, 0.44, 0.18, 0.2], first_bold=True, keep=True)
    d.save(OUT / "ORV-MR-002-Management-Review-Minutes.docx")
    return d


def main():
    results, kpis, actions = load()
    FIG.mkdir(parents=True, exist_ok=True)
    fig_coverage(FIG / "coverage.png")
    fig_results(FIG / "results.png", results)
    fig_fishbone(FIG / "fishbone.png")
    fig_kpis(FIG / "kpis.png", kpis)
    for name, fn in (("ORV-AUD-001-Internal-Audit-Programme", build_programme), ("ORV-AUD-002-Audit-Plan-IA-2027-01", build_plan),
                     ("ORV-AUD-003-Internal-Audit-Report-IA-2027-01", report_factory(results)), ("ORV-AUD-004-Corrective-Action-Plan", cap_factory(actions)),
                     ("ORV-MR-001-Management-Review-Pack", pack_factory(kpis, results)), ("ORV-MR-002-Management-Review-Minutes", build_minutes)):
        T.build_two_pass(fn, OUT / f"{name}.docx")
        print("Built", name)
    for keep in (OUT / ".gitkeep", P5 / "previews/.gitkeep"):
        keep.unlink(missing_ok=True)
    T.make_cover_image(P5 / "cover.png", "Project 5: Internal audit", "Internal Audit and Management Review",
                       "Audit programme, risk-based checklist, graded findings, root cause analysis and a management review",
                       [(str(sum(results.values())), "audit questions"), ("1 + 5", "major and minor NCs"), (str(len(actions)), "corrective actions"), (str(len(kpis)), "KPIs and KRIs")])
    (P5 / "data").mkdir(exist_ok=True)
    (P5 / "data/audit_results.json").write_text(json.dumps(dict(audit=D.AUDIT_ID, results=results, findings=D.FINDINGS, kpis=kpis, decisions=D.DECISIONS), indent=1, ensure_ascii=False, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
