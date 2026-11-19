#!/usr/bin/env python3
"""Build the Project 6 third-party risk procedure, supplier questionnaire and supplier assessment report."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p6_data as D
from build_p3_docs import chevrons

P6 = T.ROOT / "06-third-party-risk"
FIG, OUT = P6 / "figures", P6 / "deliverables"
WORKBOOK = OUT / "Orvanta-Third-Party-Risk-Workbook.xlsx"
MASTER = json.loads((T.ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
VEN = {v["id"]: v for v in MASTER["vendors"]}
SHORT = {"VEN-02": "Tessarin", "VEN-04": "Vaskora Bank", "VEN-05": "Helvora"}
TEAL, INK, MUTED = "#0F5C6E", "#16242C", "#52616B"
FILLS = {"Low": "E1F0E7", "Medium": "FCF3D2", "High": "FAD9B8", "Critical": "F3B9A3", "Tier 1": "FAD9B8", "Tier 2": "FCF3D2", "Tier 3": "E1F0E7",
         "Present": "E1F0E7", "Partial": "FCF3D2", "Missing": "F3B9A3", "Hard": "FAD9B8"}
NOTE = "Supplier answers, findings and contract terms are simulated for this portfolio sample. Real vendors appear only as tools Orvanta uses, and nothing here describes their actual security."

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"


def load():
    wb = load_workbook(WORKBOOK, data_only=True)
    scores = {}
    rows = list(wb["Scores"].iter_rows(min_row=5, max_row=19, max_col=4, values_only=True))
    for k, v in enumerate(D.ASSESSED):
        scores[v] = dict(domains=[r[1 + k] for r in rows[:10]], overall=rows[11][1 + k], key_no=rows[12][1 + k], rating=rows[13][1 + k], findings=rows[14][1 + k])
    inventory = [dict(id=r[0], name=r[1], service=r[2], owner=r[4], tier=r[8], prelim=r[9], cif=r[10], assessed=r[11], rating=r[12], next=r[14], status=r[15], renewal=r[16], checklist=r[17], open=r[18])
                 for r in wb["Inventory"].iter_rows(min_row=5, values_only=True) if r[0]]
    return scores, inventory


def fmt(value):
    return value.strftime("%d %b %Y").lstrip("0") if hasattr(value, "strftime") else value


def doc(title, subtitle, label, doc_id, date, reviewer, approver, toc, history, classification="Confidential (sample)"):
    return T.BrandDoc(title=title, subtitle=subtitle, label=label, doc_id=doc_id, version="1.0", date=date, author="Jahangir Shukurov", reviewer=reviewer, approver=approver,
                      classification=classification, client="Orvanta Payments UAB", history=history, toc_pages=toc)


# --- Figures ---------------------------------------------------------------------------------

def fig_lifecycle(path):
    fig = plt.figure(figsize=(7.0, 1.35))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 1.35)
    ax.axis("off")
    chevrons(ax, 0.02, 0.72, [s[0] for s in D.LIFECYCLE], 6.96, h=0.56, size=9.5)
    import textwrap
    for i, (_, note) in enumerate(D.LIFECYCLE):
        ax.text(0.02 + (i + 0.5) * 6.96 / 5, 0.6, "\n".join(textwrap.wrap(note, 24)), ha="center", va="top", fontsize=7, color=INK, linespacing=1.2)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_tiers(path):
    fig = plt.figure(figsize=(4.4, 2.75))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 4.4)
    ax.set_ylim(0, 2.75)
    ax.axis("off")
    color = {"Tier 1": "#E08A5B", "Tier 2": "#F3C98B", "Tier 3": "#BFDCCB"}
    x0, y0, cw, ch = 1.25, 0.55, 0.74, 0.5
    crit = [(1, "1 Can wait a week"), (2, "2 High, workaround"), (3, "3 Critical")]
    for r, (c, label) in enumerate(crit):
        ax.text(x0 - 0.08, y0 + (r + 0.5) * ch, label, ha="right", va="center", fontsize=7, color=INK)
        for d in range(4):
            tier = "Tier 1" if d == 3 or c == 3 else "Tier 2" if d == 2 or c == 2 else "Tier 3"
            ax.add_patch(Rectangle((x0 + d * cw, y0 + r * ch), cw, ch, fc=color[tier], ec="white", lw=1.5))
            ax.text(x0 + (d + 0.5) * cw, y0 + (r + 0.5) * ch, tier, ha="center", va="center", fontsize=7.6, fontweight="bold", color=INK)
    for d, label in enumerate(("0 None", "1 Internal", "2 Confidential", "3 Restricted")):
        ax.text(x0 + (d + 0.5) * cw, y0 - 0.1, label, ha="center", va="top", fontsize=7, color=INK)
    ax.text(x0 + 2 * cw, y0 - 0.33, "Data sensitivity", ha="center", va="top", fontsize=7.6, color=MUTED)
    ax.text(x0 + 2 * cw, y0 + 3 * ch + 0.32, "Business criticality (down) against data sensitivity (across)", ha="center", va="center", fontsize=7.6, color=MUTED)
    ax.text(x0 + 2 * cw, y0 + 3 * ch + 0.12, "System access of 1 or more lifts Tier 3 to Tier 2", ha="center", va="center", fontsize=7, color=MUTED)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_scores(path, scores):
    fig = plt.figure(figsize=(7.0, 3.35))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 3.35)
    ax.axis("off")
    x0, cw, rh, top = 2.95, 1.25, 0.245, 2.95

    def shade(v):
        return "#8FCBB0" if v >= 0.85 else "#FBE3A8" if v >= 0.7 else "#F2AE72" if v >= 0.5 else "#E9805F"

    for k, v in enumerate(D.ASSESSED):
        ax.text(x0 + (k + 0.5) * cw, 3.15, SHORT[v], ha="center", va="center", fontsize=8.6, fontweight="bold", color=INK)
    for r, dom in enumerate(D.DOMAINS):
        y = top - (r + 1) * rh
        ax.text(0.02, y + rh / 2, dom, va="center", fontsize=7.8, color=INK)
        for k, v in enumerate(D.ASSESSED):
            value = scores[v]["domains"][r]
            ax.add_patch(Rectangle((x0 + k * cw + 0.02, y + 0.02), cw - 0.04, rh - 0.04, fc=shade(value), ec="none"))
            ax.text(x0 + (k + 0.5) * cw, y + rh / 2, f"{value:.0%}", ha="center", va="center", fontsize=7.8, color=INK)
    y = top - 11 * rh - 0.08
    ax.text(0.02, y + rh / 2, "Overall score and rating", va="center", fontsize=8.2, fontweight="bold", color=INK)
    for k, v in enumerate(D.ASSESSED):
        ax.add_patch(Rectangle((x0 + k * cw + 0.02, y + 0.02), cw - 0.04, rh - 0.04, fc=shade(scores[v]["overall"]), ec=INK, lw=0.8))
        ax.text(x0 + (k + 0.5) * cw, y + rh / 2, f"{scores[v]['overall']:.0%}  {scores[v]['rating']}", ha="center", va="center", fontsize=8.2, fontweight="bold", color=INK)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


# --- Documents -------------------------------------------------------------------------------

def procedure_factory(inventory):
    def build(toc):
        d = doc("Third-Party Risk Management Procedure", "How Orvanta selects, assesses, contracts, monitors and exits suppliers", "Project 6  |  Program procedure", "ORV-TPRM-001",
                D.PROCEDURE_DATE, f"{WHO['R-HCOMP']}, Head of Compliance", f"{WHO['R-CISO']}, CISO", toc,
                [["0.1", "2 August 2027", "Jahangir Shukurov", "Draft after the internal audit findings"], ["1.0", D.PROCEDURE_DATE, "Jahangir Shukurov", "Approved, with the contract workflow gate live"]],
                classification="Internal (sample)")
        tiers = {t: sum(1 for v in inventory if v["tier"] == t) for t in ("Tier 1", "Tier 2", "Tier 3")}
        d.h1("Summary", new_page=True)
        d.p("This procedure puts the Supplier Security Policy (ORV-POL-07) into practice across the whole life of a supplier relationship. It answers the major nonconformity NC-01 from internal audit IA-2027-01, "
            "which found that critical suppliers were not under control because nothing connected contract renewal to supplier assessment.")
        d.stat_row([("20", "Suppliers in scope"), (str(tiers["Tier 1"]), "Tier 1 suppliers"), ("60", "Questions for Tier 1"), ("5", "Lifecycle stages")])
        d.bullets([
            ("Tier decides effort.", "Three ratings set the tier, and the tier sets how deep the assessment goes and how often it repeats."),
            ("One hard gate.", "The contract workflow now blocks signature of any Tier 1 or Tier 2 contract without third-party risk sign-off. This is the fix for the root cause of NC-01."),
            ("Findings are managed, not filed.", "Every finding gets a requirement, a date and an interim control. Missed dates escalate to the CISO."),
            ("DORA is built in.", "Services that support critical or important functions are flagged at onboarding and kept in a register."),
        ])
        d.callout(NOTE, lead="Reading note.")
        d.h1("Roles")
        d.table(["Role", "Holder", "Responsibility"], [
            ["Head of Compliance", WHO["R-HCOMP"], "Owns this procedure, the inventory and the register. Gives third-party risk sign-off."],
            ["CISO", WHO["R-CISO"], "Sets security requirements. Decides on suppliers rated High or Critical."],
            ["Security assessor", "Security team, two trained assessors", "Scores questionnaires, verifies evidence and writes findings."],
            ["General Counsel", WHO["R-GC"], "Applies the clause checklist and runs the contract workflow."],
            ["Supplier owner", "Named per supplier", "Manages the relationship, follows up findings and reports changes."],
            ["CEO", WHO["R-CEO"], "Decides on Tier 1 suppliers rated High, and accepts any resulting risk."],
        ], [0.2, 0.26, 0.54], first_bold=True, keep=True)
        d.p("The Head of Compliance reviews this procedure every year and after any supplier incident. The next review is due in August 2028.")
        d.h1("Lifecycle")
        d.figure(FIG / "lifecycle.png", "The five stages of a supplier relationship.")
        for stage, _ in D.LIFECYCLE:
            d.h2(stage)
            d.table(["Step", "Action", "Who", "Record"], [[s[1], s[2], s[3], s[4]] for s in D.STEPS if s[0] == stage], [0.07, 0.53, 0.22, 0.18], size=8.5, first_bold=True, keep=True)
        d.h1("Tiering", new_page=True)
        d.p("Each supplier is rated on data sensitivity, business criticality and system access. The workbook calculates the tier, so two people rating the same supplier get the same answer.", keep_next=True)
        d.figure(FIG / "tiers.png", "Tier by data sensitivity and business criticality.", 0.62)
        d.p(f"Applying the rule to the 20 suppliers gives {tiers['Tier 1']} in Tier 1, {tiers['Tier 2']} in Tier 2 and {tiers['Tier 3']} in Tier 3. One supplier moved from the preliminary view in the Company Fact Sheet: "
            "the accounting system rose from Tier 3 to Tier 2, because it holds confidential financial data.")
        d.h2("Assessment depth")
        d.table(["Tier", "Assessment", "When"], [list(x) for x in D.DEPTH], [0.12, 0.6, 0.28], first_bold=True, fills=FILLS, keep=True)
        d.h1("Scoring and decisions")
        d.p("Each answer earns a share of the question's points: all for Yes, half for Partial and none for No. Fifteen key questions carry double weight. Questions that do not apply are left out.", keep_next=True)
        d.table(["Rating", "Score", "Meaning", "Decision"], [
            ["Low", "85% or more", D.RATING_BANDS[0][2], "Approve"], ["Medium", "70% to 84%", D.RATING_BANDS[1][2], "Approve with a remediation plan"],
            ["High", "50% to 69%", D.RATING_BANDS[2][2], "CISO decides. CEO decides for Tier 1"], ["Critical", "Under 50%", D.RATING_BANDS[3][2], "Reject, or plan an exit"],
        ], [0.12, 0.16, 0.44, 0.28], size=8.5, first_bold=True, fills=FILLS, keep=True)
        d.p("A No on any key question caps the rating at High, whatever the total. A supplier cannot make up for missing multi-factor authentication with good paperwork elsewhere.")
        d.h1("Contract clauses")
        d.p("The General Counsel checks every Tier 1 and Tier 2 contract against these fifteen clauses. A missing clause is either added or recorded as a finding with a date.", keep_next=True)
        d.table(["#", "Clause", "What it must cover"], [[n, c[0], c[1]] for n, c in enumerate(D.CLAUSES, start=1)], [0.06, 0.3, 0.64], size=8, first_bold=True, after=2)
        d.h1("DORA considerations")
        d.p("Orvanta is a financial entity under DORA, Regulation (EU) 2022/2554, so its ICT suppliers carry extra duties. This section is a working summary, not legal advice.")
        d.table(["Topic", "What Orvanta does", "Basis and verification"], [
            ["Register of information", "Keeps a register of all contractual arrangements for ICT services, and marks those that support critical or important functions. The workbook holds a simplified view of the eight that do.",
             "Article 28(3), confirmed through European Supervisory Authority material. Official templates: Commission Implementing Regulation (EU) 2024/2956, verified."],
            ["Reporting", "Prepares the yearly report to the Bank of Lithuania on new ICT arrangements.", "Article 28(3), confirmed as above. Format and dates: [verify against official source]."],
            ["Exit strategies", "Records exit arrangements for each ICT service that supports a critical or important function.", "Article 28(8), confirmed as above."],
            ["Concentration and subcontracting", "Rates substitutability for each such service and records known subcontractors.", "Article 29: [verify against official source]."],
            ["Contract terms", "Uses the clause checklist above for all ICT contracts.", "Article 30 sets key contractual provisions: [verify against official source] before relying on the checklist as complete."],
        ], [0.2, 0.44, 0.36], size=8, first_bold=True, after=2)
        d.h1("Measures")
        d.table(["Measure", "Target"], [["Tier 1 suppliers with a current assessment", "100%"], ["Tier 1 and Tier 2 contracts signed without sign-off", "0"], ["Findings past their due date", "0"],
                                        ["Critical-function services with documented exit arrangements", "100%"]], [0.7, 0.3], size=8, first_bold=True, keep=True, after=2)
        d.save(OUT / "ORV-TPRM-001-Third-Party-Risk-Management-Procedure.docx")
        return d

    return build


def build_questionnaire(toc):
    d = doc("Supplier Security Questionnaire", "Sixty questions in ten domains, for Tier 1 and Tier 2 suppliers", "Project 6  |  Due diligence questionnaire", "ORV-TPRM-002",
            D.PROCEDURE_DATE, f"{WHO['R-CISO']}, CISO", f"{WHO['R-HCOMP']}, Head of Compliance", toc,
            [["1.0", D.PROCEDURE_DATE, "Jahangir Shukurov", "Issued with the procedure"]], classification="Internal (sample)")
    keys = sum(1 for q in D.QUESTIONS if q[2])
    d.h1("How to complete this questionnaire", new_page=True)
    d.p("Orvanta Payments UAB is a regulated payment institution. Before we share data or rely on a service, we need to understand how the supplier protects it. This questionnaire is how we ask.")
    d.bullets([
        ("Who answers.", "The person responsible for security at the supplier. Tier 1 suppliers answer all 60 questions. Tier 2 suppliers answer the key questions and any domain we mark."),
        ("How to answer.", "Yes, Partial, No or N/A for each question, with a short explanation for anything other than Yes."),
        ("Evidence.", f"We ask for evidence on the {keys} key questions, marked Key. A current independent assurance report can stand in for most of it."),
        ("What happens next.", "We score the answers, discuss any gaps and agree a plan. A gap is rarely a reason to stop. An unanswered question usually is."),
        ("Confidentiality.", "Answers are covered by the non-disclosure agreement and are seen only by Orvanta's compliance and security teams."),
    ])
    d.callout("These questions were written for this engagement, in plain language, around the risks that matter to a payment institution. They are not copied from any published questionnaire.", lead="Originality.")
    d.h1("Questions")
    for n, dom in enumerate(D.DOMAINS):
        d.h2(dom)
        rows = [[f"Q{i + 1:02d}", q[0], q[1], "Key" if q[2] else ""] for i, q in enumerate(D.QUESTIONS) if i // 6 == n]
        d.table(["ID", "Question", "Evidence we ask for", "Key"], rows, [0.08, 0.5, 0.34, 0.08], size=8.5, first_bold=True, keep=True)
    d.save(OUT / "ORV-TPRM-002-Supplier-Security-Questionnaire.docx")
    return d


def report_factory(scores, inventory):
    by_vendor = {v: [f for f in D.FINDINGS if f[1] == v] for v in D.ASSESSED}
    tier1 = [v for v in inventory if v["tier"] == "Tier 1"]
    profile = {
        "VEN-02": ("Runs issuer processing and holds the card vault for Orvanta's card program. It sees cardholder data and every card transaction.",
                   "A mature processor with independent assurance over the service. All key questions were answered Yes or Partial, with evidence. The two findings are contract points for the next renewal.",
                   "Approve. Address the two findings at renewal in June 2028."),
        "VEN-04": ("Provides SEPA access and holds safeguarded client funds. A failure would stop payouts and settlement.",
                   "A regulated bank with strong controls across every domain. The gaps are in what the contract commits the bank to tell Orvanta, not in how the bank protects the service.",
                   "Approve. Agree a contract addendum on incident notification by December 2027."),
        "VEN-05": ("Supplies the customer support agents in Riga who work in Orvanta's Zendesk and Orbit console. Agents see customer personal data and can change account details.",
                   "Helvora's people are trained and its premises are controlled, but its own systems fall well short. Six key questions were answered No. "
                   "Because agents work inside Orvanta's tools, Orvanta's own controls limit the exposure today, which is why the service can continue while Helvora remediates.",
                   "Approve with conditions, by decision of the CEO on 9 August 2027. Helvora must close the four High findings by 30 November 2027. Orvanta reassesses on site in December. "
                   "If SF-01 and SF-02 are not closed by then, Orvanta moves agents to Orvanta-provided virtual desktops at Helvora's cost, or starts an exit."),
    }

    def build(toc):
        d = doc("Supplier Assessment Report", "Security assessments of Tessarin, Vaskora Bank and Helvora", "Project 6  |  Assessment report", "ORV-TPRM-003", D.REPORT_DATE,
                f"{WHO['R-CISO']}, CISO", f"{WHO['R-HCOMP']}, Head of Compliance", toc,
                [["0.1", "23 August 2027", "Jahangir Shukurov", "Draft findings shared with supplier owners"], ["1.0", D.REPORT_DATE, "Jahangir Shukurov", "Issued. Closes corrective action CA-01.2"]])
        d.h1("Executive summary", new_page=True)
        d.p("The internal audit of July 2027 found three of Orvanta's eight critical suppliers unassessed, and graded it a major nonconformity. "
            "This report covers those three assessments, completed between 30 July and 27 August 2027. All eight Tier 1 suppliers are now assessed.", bold_lead="Situation.")
        d.stat_row([(f"{len(tier1)} of {len(tier1)}", "Tier 1 suppliers assessed"), ("1", "Rated High"), (str(len(D.FINDINGS)), "Findings raised"), ("4", "High findings, all at Helvora")])
        d.p("", bold_lead="Key findings.", after=2, keep_next=True)
        d.bullets([
            ("Tessarin and Vaskora Bank are sound.", f"They scored {scores['VEN-02']['overall']:.0%} and {scores['VEN-04']['overall']:.0%}. Their four findings are contract points, not control failures."),
            ("Helvora is a High risk.", f"It scored {scores['VEN-05']['overall']:.0%}, with six key questions answered No: no multi-factor authentication on its own systems, unmanaged shared desktops, and no incident or continuity plan."),
            ("Orvanta's own controls contain the exposure.", "Agents work inside Orvanta's tools, where access is named, logged, restricted to Helvora's office network and monitored."),
            ("The contract is the weakest part.", "Seven of fifteen clauses are missing from the Helvora contract renewed on 1 June 2027."),
        ])
        d.p("Helvora's agents can see and change customer records. A compromised agent desktop is a realistic way to reach that data, and under GDPR and DORA Orvanta remains accountable for it.", bold_lead="Risk in business terms.")
        d.p("", bold_lead="Decisions needed.", after=3, keep_next=True)
        d.table(["#", "Decision", "Owner", "By"], [
            ["1", "Confirm that Helvora continues with conditions, and accept risk RSK-14 at High until December 2027", WHO["R-CEO"], "3 Sep 2027"],
            ["2", "Sign the Helvora contract addendum with the seven missing clauses", WHO["R-GC"], "30 Sep 2027"],
            ["3", "Record corrective action CA-01.2 as complete for the follow-up audit", WHO["R-HCOMP"], "3 Sep 2027"],
        ], [0.05, 0.6, 0.2, 0.15], after=0)

        d.h1("Method", new_page=True)
        d.p("Each supplier completed the 60-question Supplier Security Questionnaire (ORV-TPRM-002). The security assessor checked the evidence for every key question, held a call with each supplier and visited Helvora's site in Riga. "
            "Scoring and rating follow the procedure ORV-TPRM-001.")
        d.callout(NOTE, lead="Reading note.")
        d.h1("Results at a glance")
        d.figure(FIG / "scores.png", "Score by domain for the three suppliers. Green is 85% or more, yellow 70% to 84%, orange 50% to 69% and red under 50%.")
        d.table(["Supplier", "Tier", "Score", "Key questions answered No", "Rating", "Findings", "Decision"],
                [[SHORT[v], "Tier 1", f"{scores[v]['overall']:.0%}", scores[v]["key_no"], scores[v]["rating"], scores[v]["findings"], profile[v][2].split(".")[0]] for v in D.ASSESSED],
                [0.16, 0.09, 0.09, 0.18, 0.1, 0.1, 0.28], size=8.5, first_bold=True, fills=FILLS, keep=True)

        for v in D.ASSESSED:
            d.h1(f"{VEN[v]['name']}", new_page=v != "VEN-04")
            d.table(["Item", "Detail"], [["Service", VEN[v]["service"]], ["What it means for Orvanta", profile[v][0]], ["Supplier owner", WHO[D.VENDORS[v][0]]],
                                         ["Assessed", D.VENDORS[v][4]], ["Score and rating", f"{scores[v]['overall']:.0%}, {scores[v]['rating']}"], ["Decision", profile[v][2]]],
                    [0.24, 0.76], first_bold=True, keep=True)
            d.p(profile[v][1], bold_lead="Assessment.")
            d.h2("Findings and required remediation")
            d.table(["ID", "Severity", "Finding", "What Orvanta requires", "Due", "Interim control"],
                    [[f[0], f[2], f[3], f[5], f[6], f[7]] for f in by_vendor[v]], [0.07, 0.09, 0.27, 0.24, 0.1, 0.23], size=8, first_bold=True, fills=FILLS, zebra=False)

        d.h1("Contract clause check", new_page=True)
        d.p("The table shows each of the fifteen required clauses in the three signed contracts, before remediation.", keep_next=True)
        d.table(["#", "Clause"] + [SHORT[v] for v in D.ASSESSED], [[n, c[0], *c[2]] for n, c in enumerate(D.CLAUSES, start=1)], [0.06, 0.4, 0.18, 0.18, 0.18], size=8.5, fills=FILLS, zebra=False)
        d.p("The Helvora contract was renewed without the checklist, which is the failure the audit found. The contract workflow now blocks signature without third-party risk sign-off, so this cannot repeat.")
        d.h1("What this closes, and what stays open")
        d.bullets([
            ("Closed.", "Corrective action CA-01.2: all eight Tier 1 suppliers are assessed. Management review action MR-01 is met."),
            ("Open.", f"{len(D.FINDINGS)} findings, each with an owner, a date and an interim control. The follow-up audit in October tests the workflow gate and samples these."),
            ("Risk register.", "RSK-13 for the card processor can be rescored to Medium. RSK-14 for the support provider stays High until Helvora's remediation is verified. RSK-12 was assessed in June."),
            ("Next.", "Nine Tier 2 suppliers are scheduled for assessment before their next renewal, the first in November 2027."),
        ])
        d.section(landscape=True)
        d.h1("Appendix: supplier inventory")
        d.table(["ID", "Supplier", "Service", "Owner", "Tier", "Critical function", "Last assessed", "Rating", "Next review", "Open"],
                [[v["id"], v["name"], v["service"], v["owner"], v["tier"], v["cif"], fmt(v["assessed"]), v["rating"], fmt(v["next"]), v["open"]] for v in inventory],
                [0.06, 0.18, 0.21, 0.12, 0.06, 0.07, 0.09, 0.07, 0.09, 0.05], size=7.5, fills=FILLS, zebra=False)
        d.save(OUT / "ORV-TPRM-003-Supplier-Assessment-Report.docx")
        return d

    return build


def main():
    scores, inventory = load()
    FIG.mkdir(parents=True, exist_ok=True)
    fig_lifecycle(FIG / "lifecycle.png")
    fig_tiers(FIG / "tiers.png")
    fig_scores(FIG / "scores.png", scores)
    for name, fn in (("ORV-TPRM-001-Third-Party-Risk-Management-Procedure", procedure_factory(inventory)), ("ORV-TPRM-002-Supplier-Security-Questionnaire", build_questionnaire),
                     ("ORV-TPRM-003-Supplier-Assessment-Report", report_factory(scores, inventory))):
        T.build_two_pass(fn, OUT / f"{name}.docx")
        print("Built", name)
    for keep in (OUT / ".gitkeep", P6 / "previews/.gitkeep"):
        keep.unlink(missing_ok=True)
    T.make_cover_image(P6 / "cover.png", "Project 6: Third-party risk", "Third-Party Risk Management",
                       "Supplier tiering, a 60-question due diligence set, three scored assessments and a DORA register view",
                       [("20", "suppliers tiered"), ("60", "original questions"), ("3", "assessments scored"), (str(len(D.FINDINGS)), "findings with remediation")])
    (P6 / "data").mkdir(exist_ok=True)
    (P6 / "data/third_party_risk.json").write_text(json.dumps(dict(as_of=D.AS_OF, scores=scores, inventory=inventory), indent=1, ensure_ascii=False, default=str), encoding="utf-8")


if __name__ == "__main__":
    main()
