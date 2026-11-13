#!/usr/bin/env python3
"""Build the Project 2 methodology, risk assessment report and risk acceptance record from the recalculated workbook."""
import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Patch, Polygon, Rectangle
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p2_data as D

P2 = T.ROOT / "02-risk-assessment"
FIG, OUT = P2 / "figures", P2 / "deliverables"
WORKBOOK = OUT / "Orvanta-Risk-Assessment-Workbook.xlsx"
MASTER = json.loads((T.ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
BAND = {"Critical": "#D9623B", "High": "#F2AE72", "Medium": "#FBE9B0", "Low": "#CFE6D8"}
BAND_FILL = {"Critical": "F3B9A3", "High": "FAD9B8", "Medium": "FCF3D2", "Low": "E1F0E7"}
COVER = {0: "#E9805F", 1: "#FBE3A8", 2: "#8FCBB0"}
TEAL, INK, MUTED = "#0F5C6E", "#16242C", "#52616B"
ORDER = ["Critical", "High", "Medium", "Low"]

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"


def band(score):
    return next(label for label, minimum, *_ in D.LEVELS if score >= minimum)


def load():
    wb = load_workbook(WORKBOOK, data_only=True)
    risks = []
    for r in wb["Risk Register"].iter_rows(min_row=5, values_only=True):
        if not r[0]:
            continue
        risks.append(dict(id=r[0], title=r[1], statement=r[2], assets=r[3], threat=r[4], technique=r[5], gap=r[6], owner=r[9],
                          li=r[10], ii=r[15], si=r[16], bi=r[17], existing=r[18], lc=r[19], ic=r[20], sc=r[21], bc=r[22],
                          option=r[23], controls=r[24], actions=r[25], lt=r[26], it=r[27], st=r[28], bt=r[29], due=r[30], accept=r[32]))
    plan = [dict(id=r[0], action=r[1], owner=r[3], due=r[4], ref=r[5], effort=r[6], status=r[7], risks=r[8], top=r[9])
            for r in wb["Treatment Plan"].iter_rows(min_row=5, values_only=True) if r[0]]
    counts = {stage: {lvl: sum(1 for x in risks if x[key] == lvl) for lvl in ORDER} for stage, key in (("inherent", "bi"), ("current", "bc"), ("target", "bt"))}
    return risks, plan, counts


# --- Figures ---------------------------------------------------------------------------------

def canvas(w, h):
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    return fig, ax


def grid(ax, x0, y0, cell, heading, content):
    ax.text(x0 + 2.5 * cell, y0 + 5 * cell + 0.14, heading, ha="center", va="bottom", fontsize=9, fontweight="bold", color=INK)
    for i in range(1, 6):
        for l in range(1, 6):
            x, y = x0 + (l - 1) * cell, y0 + (i - 1) * cell
            ax.add_patch(Rectangle((x, y), cell, cell, fc=BAND[band(l * i)], ec="white", lw=1.2))
            text, size, weight = content(l, i)
            ax.text(x + cell / 2, y + cell / 2, text, ha="center", va="center", fontsize=size, fontweight=weight, color=INK, linespacing=1.15)
        ax.text(x0 - 0.1, y0 + (i - 0.5) * cell, str(i), ha="right", va="center", fontsize=7.5, color=MUTED)
        ax.text(x0 + (i - 0.5) * cell, y0 - 0.1, str(i), ha="center", va="top", fontsize=7.5, color=MUTED)
    ax.text(x0 + 2.5 * cell, y0 - 0.3, "Likelihood", ha="center", va="top", fontsize=7.5, color=MUTED)
    ax.text(x0 - 0.3, y0 + 2.5 * cell, "Impact", ha="center", va="center", rotation=90, fontsize=7.5, color=MUTED)


def legend(ax, x, y):
    for k, label in enumerate(ORDER):
        ax.add_patch(Rectangle((x + k * 1.05, y), 0.16, 0.12, fc=BAND[label], ec="none"))
        ax.text(x + k * 1.05 + 0.22, y + 0.06, label, va="center", fontsize=7.5, color=INK)


def fig_matrix(path):
    fig, ax = canvas(4.2, 3.9)
    grid(ax, 0.6, 0.75, 0.62, "Risk score = likelihood x impact", lambda l, i: (str(l * i), 9, "bold"))
    legend(ax, 0.35, 0.08)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_heatmaps(path, risks):
    fig, ax = canvas(7.0, 4.25)

    def cells(lk, ik):
        def content(l, i):
            ids = [r["id"][4:] for r in risks if r[lk] == l and r[ik] == i]
            return "\n".join(textwrap.wrap(" ".join(ids), 9)), 6.6, "bold"
        return content

    grid(ax, 0.48, 0.78, 0.6, f"Today, with existing controls", cells("lc", "ic"))
    grid(ax, 3.95, 0.78, 0.6, "After treatment", cells("lt", "it"))
    legend(ax, 1.5, 0.08)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_levels(path, counts):
    fig, ax = plt.subplots(figsize=(7.0, 1.75))
    fig.subplots_adjust(left=0.2, right=0.98, top=0.86, bottom=0.2)
    stages = [("After treatment", "target"), ("Today", "current"), ("Inherent", "inherent")]
    for row, (label, key) in enumerate(stages):
        left = 0
        for lvl in ORDER:
            n = counts[key][lvl]
            if n:
                ax.barh(row, n, left=left, color=BAND[lvl], edgecolor="white", linewidth=1.5, height=0.62)
                ax.text(left + n / 2, row, str(n), ha="center", va="center", fontsize=9, fontweight="bold", color=INK)
                left += n
    ax.set_yticks(range(3))
    ax.set_yticklabels([s[0] for s in stages], fontsize=8.5, color=INK)
    ax.set_xlim(0, 30)
    ax.set_xticks([])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.legend(handles=[Patch(fc=BAND[l], label=l) for l in ORDER], loc="lower center", ncol=4, frameon=False, fontsize=7.5, bbox_to_anchor=(0.45, -0.32), handlelength=1.1)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_scenario(path, scenario):
    steps = scenario["steps"]
    rh, top = 0.5, 0.62
    h = top + rh * len(steps) + 0.42
    fig, ax = canvas(7.0, h)
    label_w, cw, gap = 2.72, 0.68, 0.16
    panels = [(label_w, "Today", 1), (label_w + 3 * cw + gap, "After treatment", 2)]
    for x0, name, _ in panels:
        ax.text(x0 + 1.5 * cw, h - 0.14, name, ha="center", va="center", fontsize=8.6, fontweight="bold", color=INK)
        for k, col in enumerate(("Prevent", "Detect", "Respond")):
            ax.text(x0 + (k + 0.5) * cw, h - 0.42, col, ha="center", va="center", fontsize=7.2, color=MUTED)
    for n, st in enumerate(steps):
        y = h - top - (n + 1) * rh
        ax.add_patch(plt.Circle((0.17, y + rh / 2), 0.13, fc=TEAL, ec="none"))
        ax.text(0.17, y + rh / 2 - 0.005, str(n + 1), ha="center", va="center", fontsize=7.6, fontweight="bold", color="white")
        ax.text(0.4, y + rh * 0.66, st[1], va="center", fontsize=7.6, fontweight="bold", color=INK)
        ax.text(0.4, y + rh * 0.3, st[0], va="center", fontsize=6.8, color=MUTED)
        for x0, _, idx in panels:
            for k, cell in enumerate(st[3:]):
                ax.add_patch(Rectangle((x0 + k * cw + 0.02, y + 0.03), cw - 0.04, rh - 0.06, fc=COVER[cell[idx]], ec="none"))
                ax.text(x0 + (k + 0.5) * cw, y + rh / 2, cell[0].replace(", ", "\n"), ha="center", va="center", fontsize=6.3, color=INK, linespacing=1.1)
    for k, (status, label) in enumerate(D.STATUS.items()):
        ax.add_patch(Rectangle((label_w + k * 1.0, 0.1), 0.16, 0.12, fc=COVER[status], ec="none"))
        ax.text(label_w + k * 1.0 + 0.22, 0.16, label, va="center", fontsize=7.4, color=INK)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_process(path):
    steps = ["Set context", "Identify", "Analyze", "Evaluate", "Treat", "Accept"]
    notes = ["Scope, criteria,\nappetite", "Assets, threats,\ngaps, scenarios", "Likelihood and\nimpact, 3 stages", "Compare with\nappetite, rank", "Choose option,\nplan actions", "Owner or CEO\nsigns residual risk"]
    fig, ax = canvas(7.0, 1.95)
    w, hgt, y = 1.12, 0.55, 1.28
    for i, (s, note) in enumerate(zip(steps, notes)):
        x = 0.04 + i * 1.16
        ax.add_patch(Polygon([(x, y), (x + w - 0.14, y), (x + w, y + hgt / 2), (x + w - 0.14, y + hgt), (x, y + hgt), (x + 0.14 if i else x, y + hgt / 2)], closed=True, fc=TEAL, ec="none"))
        ax.text(x + w / 2 + (0.04 if i else 0), y + hgt / 2, s, ha="center", va="center", fontsize=8.2, fontweight="bold", color="white")
        ax.text(x + w / 2, y - 0.1, note, ha="center", va="top", fontsize=6.9, color=INK, linespacing=1.2)
    for k, label in enumerate(("Communicate and consult with risk owners and leadership throughout", "Monitor and review: quarterly, and on significant change")):
        yy = 0.36 - k * 0.3
        ax.add_patch(FancyBboxPatch((0.04, yy), 6.92, 0.24, boxstyle="round,pad=0,rounding_size=0.05", fc="#E8F1F3", ec="none"))
        ax.text(3.5, yy + 0.12, label, ha="center", va="center", fontsize=7.6, color=INK)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


# --- Documents -------------------------------------------------------------------------------

def common(**kw):
    return dict(author="Jahangir Shukurov", classification="Confidential (sample)", client="Orvanta Payments UAB", **kw)


def build_method(toc):
    d = T.BrandDoc(title="Risk Management Methodology", subtitle="How Orvanta identifies, scores, treats and accepts information security risk",
                   label="Project 2  |  Methodology", doc_id="ORV-RISK-001", version="1.0", date="18 December 2026",
                   reviewer=f"{WHO['R-RISK']}, Risk Manager", approver=f"{WHO['R-CEO']}, CEO",
                   history=[["0.1", "9 December 2026", "Jahangir Shukurov", "Draft for Risk Manager and CISO-designate review"],
                            ["1.0", "18 December 2026", "Jahangir Shukurov", "Approved by the CEO for use"]], toc_pages=toc, **common())
    d.h1("Summary", new_page=True)
    d.p("This document sets one repeatable way to assess information security risk at Orvanta. It replaces the February 2025 spreadsheet, which had no scales, owners or acceptance rules. "
        "It is aligned with ISO/IEC 27005:2022 and meets the needs of ISO/IEC 27001:2022 clauses 6.1.2, 6.1.3, 8.2 and 8.3.")
    d.bullets([
        ("Business scales.", "Likelihood and impact use five levels each. Impact is defined in euros, regulatory consequence, customer effect and payment downtime."),
        ("Threat-informed.", "Risks come from assets and from attack scenarios. Adversarial threats are mapped to MITRE ATT&CK, so likelihood reflects how attackers really work."),
        ("Three scores per risk.", "Inherent, current with existing controls, and target after treatment. The difference shows what controls are worth."),
        ("Clear appetite.", f"Scores up to {D.APPETITE_MAX} are within appetite. Higher scores need treatment or a signed acceptance by the CEO or the Management Board."),
        ("Named owners.", "Every risk has one accountable owner, and every treatment action has an owner and a date."),
    ])
    d.callout("The Management Board approves the appetite. The CEO approves this method and accepts High risks. Risk owners accept Medium and Low risks.", lead="Who decides.")

    d.h1("Purpose and scope")
    d.p("The method applies to all information and systems in the ISMS scope: Orvanta Payments UAB, Orvanta Engineering LLC, all products, AWS production, both offices, remote work and suppliers that handle Orvanta data. "
        "It covers risks to confidentiality, integrity and availability, plus related regulatory and commercial consequences. Enterprise risks without an information security cause stay in the corporate risk process run by the Risk Manager.")
    d.h1("Roles")
    d.table(["Role", "Holder", "Responsibility"], [
        ["Management Board", f"Chaired by {WHO['R-CHAIR']}", "Approves risk appetite. Accepts Critical risks as time-limited exceptions. Reviews the risk profile each quarter."],
        ["CEO", WHO["R-CEO"], "Approves this method and the treatment plan. Accepts High risks in writing."],
        ["Risk Manager", WHO["R-RISK"], "Owns the method and the register. Runs workshops and checks scoring is consistent."],
        ["CISO-designate", WHO["R-CISO"], "Provides threat and control expertise. Maintains the threat catalog and attack scenarios."],
        ["Risk owners", "Named per risk", "Accountable for one risk each: agree scores, choose treatment, accept Medium and Low residual risk."],
        ["Asset owners", "Named per asset", "Rate confidentiality, integrity and availability and keep the asset record current."],
        ["DPO and Head of Compliance", f"{WHO['R-DPO']}, {WHO['R-HCOMP']}", "Advise on privacy and regulatory impact."],
    ], [0.22, 0.24, 0.54], first_bold=True)

    d.h1("Process")
    d.figure(FIG / "process.png", "The risk process. Consultation and review run alongside every step.")
    d.table(["Step", "What happens", "Output"], [
        ["Set context", "Confirm scope, criteria and appetite. Refresh the asset register and threat catalog.", "Approved criteria"],
        ["Identify", "Find risks two ways: by asset (what could go wrong with this system or data) and by event (how an attack or failure would unfold).", "Risk statements with cause, event and consequence"],
        ["Analyze", "Score likelihood and impact at three stages. Record existing controls and their evidence.", "Scored register"],
        ["Evaluate", "Compare scores with appetite and rank the risks.", "Prioritized risk list"],
        ["Treat", "Choose mitigate, avoid, transfer or accept. Select Annex A controls and plan actions.", "Treatment plan and input to the Statement of Applicability"],
        ["Accept", "The right authority signs off residual risk.", "Acceptance records"],
    ], [0.16, 0.54, 0.3], first_bold=True)

    d.h1("Risk criteria", new_page=True)
    d.h2("Likelihood")
    d.p("Likelihood combines expected frequency with a threat-informed test: how common the technique is and how open the path is today.", keep_next=True)
    d.table(["Score", "Label", "Expected frequency", "Threat-informed test"], [list(x) for x in D.LIKELIHOOD], [0.09, 0.16, 0.3, 0.45], first_bold=True)
    d.h2("Impact")
    d.p("Impact is rated on four dimensions, and the highest one sets the score. Financial bands are tied to FY2025 net revenue of EUR 21.4M.", keep_next=True)
    d.table(["Score", "Label", "Financial", "Regulatory", "Customer", "Operational"], [list(x) for x in D.IMPACT], [0.08, 0.12, 0.16, 0.19, 0.24, 0.21], size=8, first_bold=True)
    d.h2("Risk levels and appetite")
    d.figure(FIG / "matrix.png", "Risk matrix. Score is likelihood multiplied by impact.", 0.52)
    d.table(["Level", "Score", "Required response", "Who may accept"],
            [[lvl, f"{lo} to {hi}", resp, who] for (lvl, lo, resp, who), hi in zip(D.LEVELS, (25, 16, 9, 4))], [0.14, 0.12, 0.52, 0.22], first_bold=True, fills=BAND_FILL)
    d.callout(f"Orvanta accepts risks scored {D.APPETITE_MAX} or lower when a named owner monitors them. It does not accept untreated High or Critical risks to customer funds, payment availability or customer data. "
              "Any exception is written, time-limited and reviewed.", lead="Risk appetite statement.")

    d.h1("Threat-informed analysis")
    d.p("Many risk registers score likelihood by instinct. Here, likelihood is tested against how an attack would actually proceed.")
    d.bullets([
        ("Threat catalog.", "Each adversarial threat names the MITRE ATT&CK tactic and technique it relies on. Non-adversarial threats, such as outages and errors, are listed without a technique."),
        ("Attack scenarios.", "The most serious risks are walked through step by step as a kill chain. For each step we ask which control would prevent it, detect it or respond to it."),
        ("Coverage status.", "Each control at each step is rated Missing, Partial or Effective. Effective means working by design, and it stays provisional until tested by audit or exercise."),
        ("Three scores.", "Inherent assumes no controls. Current counts controls that exist and work today. Target assumes the treatment plan is complete."),
    ])
    d.p("A step with no Effective prevent or detect control keeps likelihood at 4 or 5, whatever the paperwork says.")

    d.h1("Treatment and acceptance", new_page=True)
    d.table(["Option", "When it is used", "Example at Orvanta"], [
        ["Mitigate", "Controls can reduce likelihood or impact at reasonable cost", "Just-in-time admin access for AWS"],
        ["Avoid", "The activity or asset causing the risk can be removed", "Retiring the legacy OpenVPN bastion"],
        ["Transfer", "Part of the financial impact can be shared", "Cyber insurance for ransomware losses"],
        ["Accept", "The risk is within appetite, or treatment costs more than it saves", "Single AWS region, accepted for a fixed period"],
    ], [0.14, 0.46, 0.4], first_bold=True)
    d.p("Selected controls are compared with Annex A so that nothing necessary is missed, and the result feeds the Statement of Applicability. "
        "Acceptance above appetite needs a record stating the reason, conditions, expiry date and signatory.")
    d.h1("Monitoring and review")
    d.bullets([
        ("Quarterly.", "The Risk Manager reviews scores, action progress and expiring acceptances with each owner, and reports to the Management Board."),
        ("Yearly.", "A full reassessment, including the asset register and threat catalog."),
        ("On change.", "A new product, supplier, major architecture change, serious incident or new regulation triggers a targeted review."),
        ("Indicators.", "Key risk indicators, such as MFA coverage and restore success, give early warning between reviews."),
    ])
    d.p("The workbook is the register of record. Earlier versions are kept for three years so that changes in risk can be traced.")
    d.save(OUT / "Orvanta-Risk-Management-Methodology.docx")
    return d


def report_factory(risks, plan, counts):
    by_id = {r["id"]: r for r in risks}
    top = sorted(risks, key=lambda r: (-r["sc"], -r["si"], r["id"]))[:10]
    now_high = counts["current"]["Critical"] + counts["current"]["High"]
    after_high = counts["target"]["Critical"] + counts["target"]["High"]
    critical = [r for r in risks if r["bc"] == "Critical"]
    identity = [r for r in risks if r["gap"] == "GAP-03"]
    supplier = [r for r in risks if "TRT-16" in r["actions"]]
    avg = lambda key: sum(r[key] for r in risks) / len(risks)
    date_text = lambda value: value.strftime("%d %b %Y").lstrip("0")

    def build(toc):
        d = T.BrandDoc(title="Threat-Informed Risk Assessment", subtitle="Risk profile, attack scenarios and treatment plan",
                       label="Project 2  |  Assessment report", doc_id="ORV-RISK-003", version="1.0", date="12 February 2027",
                       reviewer=f"{WHO['R-RISK']}, Risk Manager", approver=f"{WHO['R-CEO']}, CEO",
                       history=[["0.1", "5 February 2027", "Jahangir Shukurov", "Draft for risk owner review"],
                                ["1.0", "12 February 2027", "Jahangir Shukurov", "Issued to the CEO and Management Board"]], toc_pages=toc, **common())
        d.h1("Executive summary", new_page=True)
        d.p(f"The gap assessment showed where Orvanta falls short of ISO/IEC 27001:2022. This assessment asks what could actually go wrong, how badly and how soon. "
            f"We assessed {len(risks)} risks across 40 assets and 21 threats, using the method approved on 18 December 2026. The position is as of {D.AS_OF}, after the eight quick wins.", bold_lead="Situation.")
        d.stat_row([(str(len(risks)), "Risks assessed"), (str(now_high), "High or Critical today"), (str(after_high), "High after treatment"), (str(len(plan)), "Treatment actions")])
        d.p("", bold_lead="Key findings.", after=2, keep_next=True)
        d.bullets([
            ("Most risk is still above appetite.", f"{now_high} of {len(risks)} risks are High or Critical today. Existing controls and the quick wins keep {counts['inherent']['Critical'] - counts['current']['Critical']} risks out of Critical, but not within appetite."),
            ("Two risks are Critical.", f"{critical[0]['title']} ({critical[0]['id']}) and {critical[1]['title'].lower()} ({critical[1]['id']}). Together they mean an attacker could take over production and not be noticed."),
            ("Identity is the common thread.", f"{len(identity)} risks trace back to open identity and privileged access gaps, and all three attack scenarios pass through them."),
            ("Suppliers carry unmeasured risk.", f"{len(supplier)} risks depend on vendors nobody has assessed, including the KYC provider and the card processor."),
            ("The plan works on paper.", f"{len(plan)} actions bring {len(risks) - after_high} risks within appetite by August 2027. One risk needs formal acceptance."),
        ])
        d.p("The two Critical risks combine into one outcome: production taken over with nobody noticing. That could cost more than EUR 2M and put the licence at risk. Until treatment lands, a single stolen credential is the most likely way there.", bold_lead="Risk in business terms.")
        d.p("", bold_lead="Decisions needed.", after=3, keep_next=True)
        d.table(["#", "Decision", "Owner", "By"], [
            ["1", f"Approve the risk treatment plan of {len(plan)} actions", WHO["R-CEO"], "26 Feb 2027"],
            ["2", "Accept the single-region risk (RSK-16) until 31 December 2027, with conditions", WHO["R-CEO"], "12 Feb 2027"],
            ["3", f"Confirm the risk appetite: scores up to {D.APPETITE_MAX} without formal acceptance", "Management Board", "26 Feb 2027"],
            ["4", "Receive a risk report each quarter, starting April 2027", "Management Board", "26 Feb 2027"],
        ], [0.05, 0.6, 0.2, 0.15], after=0)

        d.h1("Scope and method", new_page=True)
        d.p("The assessment covers the full ISMS scope: all products, AWS production, both offices, remote work and suppliers handling Orvanta data. "
            "It follows the Risk Management Methodology (ORV-RISK-001), aligned with ISO/IEC 27005:2022 and ISO/IEC 27001:2022 clause 6.1.2.")
        d.callout("Workshops and evidence are simulated for this portfolio sample. Risk owners named here are fictional role-holders from the Company Fact Sheet.", lead="Evidence basis.")
        d.bullets([
            ("Workshops.", "Nine sessions with risk owners between 11 and 29 January 2027, using the gap assessment results as the starting point."),
            ("Two ways in.", "Risks were identified from the asset register and from attack scenarios, then merged into one register."),
            ("Three scores.", "Inherent, current with existing controls, and target after treatment. Score is likelihood multiplied by impact, each from 1 to 5."),
            ("Threat mapping.", "Adversarial threats are mapped to MITRE ATT&CK techniques, checked against the public knowledge base."),
        ])
        d.table(["Level", "Score", "Required response", "Who may accept"],
                [[lvl, f"{lo} to {hi}", resp, who] for (lvl, lo, resp, who), hi in zip(D.LEVELS, (25, 16, 9, 4))], [0.14, 0.12, 0.52, 0.22], first_bold=True, fills=BAND_FILL)

        d.h1("Risk profile")
        d.h2("From inherent to target")
        d.p(f"Without any controls, every risk would be High or Critical. Existing controls and the quick wins bring the average score from {avg('si'):.1f} to {avg('sc'):.1f}. The treatment plan is designed to reach {avg('st'):.1f}.", keep_next=True)
        d.figure(FIG / "levels.png", "Number of risks at each level: inherent, today and after treatment.")
        d.h2("Heat maps")
        d.p("Each number is a risk ID. Today the risks cluster at high impact with likelihood 3 or 4. Treatment mostly reduces likelihood, because it closes attack paths, and reduces impact where data is masked or backups are isolated.", keep_next=True)
        d.figure(FIG / "heatmaps.png", "Risk positions today and after treatment. Numbers are risk IDs (01 is RSK-01).")
        d.h2("Top 10 risks today", )
        d.table(["ID", "Risk", "Owner", "Today", "Level", "Target"],
                [[r["id"], r["title"], r["owner"], r["sc"], r["bc"], r["st"]] for r in top], [0.1, 0.44, 0.2, 0.08, 0.1, 0.08], size=8.5, fills=BAND_FILL)

        d.h1("Attack scenarios", new_page=True)
        d.p("Three scenarios test whether controls would hold against a real attack. Each follows the attacker step by step and rates the controls that should prevent, detect or respond. "
            "Ratings after treatment are by design, and Project 5 tests them through audit.")
        for n, s in enumerate(D.SCENARIOS):
            if n:
                d.doc.add_paragraph().paragraph_format.page_break_before = True
            d.h2(f"{s['title']} ({s['id']})")
            d.p(s["summary"], after=3)
            d.p(f"Threat actor: {s['actor']}  |  Linked risks: {s['risks']}", size=8.5, color=T.MUTED, keep_next=True)
            d.figure(FIG / f"scenario-{s['id'][-1].lower()}.png", f"{s['title']}: control coverage at each step, today and after treatment. Cells show Annex A control IDs.")
            d.table(["Step", "ATT&CK technique", "What happens at Orvanta"], [[i, st[1], st[2]] for i, st in enumerate(s["steps"], start=1)], [0.08, 0.37, 0.55], size=8.5, first_bold=True)
            d.callout(s["takeaway"], lead="What this shows.")

        d.h1("Risk treatment plan", new_page=True)
        options = {o: sum(1 for r in risks if r["option"] == o) for o in ("Mitigate", "Avoid", "Accept")}
        d.p(f"{options['Mitigate']} risks are mitigated, {options['Avoid']} is avoided by retiring legacy services, and {options['Accept']} are accepted: one within appetite and one by formal record. "
            "Every action links to the certification roadmap, so there is one plan, not two.", keep_next=True)
        d.table(["ID", "Action", "Owner", "Due", "Status", "Risks"],
                [[t["id"], t["action"], t["owner"], date_text(t["due"]), t["status"], t["risks"]] for t in plan], [0.08, 0.47, 0.16, 0.11, 0.11, 0.07], size=7.5)
        d.h2("Accepted risk")
        acc = by_id[D.ACCEPTANCE["risk"]]
        d.p(f"{acc['id']} ({acc['title']}) stays at score {acc['st']} (High) after treatment. The CEO accepted it on {D.ACCEPTANCE['date']} until {D.ACCEPTANCE['valid_until']}, "
            f"under record {D.ACCEPTANCE['ref']}. {D.ACCEPTANCE['reason']}")
        d.h2("What treatment does not fix")
        d.bullets([
            ("Insider misuse.", "A person with legitimate access can still take data. Masking limits the amount and detection shortens the time, but the risk stays Medium."),
            ("Supplier breaches.", "Assessment and contracts improve assurance, but Orvanta cannot control a vendor's environment."),
            ("Design ratings.", "Target scores assume controls work as designed. They stay provisional until the internal audit in July 2027 tests them."),
        ])
        d.h2("Next steps")
        d.p("The selected controls feed the Statement of Applicability (Project 4) and the policy set (Project 3). Supplier risks drive the third-party program (Project 6), and scenarios SCN-A and SCN-B become incident playbooks (Project 7). "
            "This report is a point-in-time view, and it is not legal advice.")

        d.section(landscape=True)
        d.h1("Appendix: risk register summary")
        d.p("Scores are likelihood x impact. The workbook holds full statements, assets, existing controls and Annex A controls for each risk.", keep_next=True)
        d.table(["ID", "Risk", "Owner", "Threat and ATT&CK technique", "Inherent", "Today", "Target", "Option", "Actions"],
                [[r["id"], r["title"], r["owner"], f"{r['threat']}: {r['technique']}", r["si"], r["sc"], r["st"], r["option"], r["actions"]] for r in risks],
                [0.06, 0.22, 0.12, 0.3, 0.06, 0.05, 0.05, 0.06, 0.08], size=7.5)
        d.save(OUT / "Orvanta-Risk-Assessment-Report.docx")
        return d

    return build


def acceptance_factory(risks):
    r = next(x for x in risks if x["id"] == D.ACCEPTANCE["risk"])
    a = D.ACCEPTANCE

    def build(toc):
        d = T.BrandDoc(title="Risk Acceptance Record", subtitle=f"{a['ref']}: {r['title']} ({r['id']})",
                       label="Project 2  |  Acceptance record", doc_id="ORV-RISK-004", version="1.0", date=a["date"],
                       reviewer=f"{WHO['R-RISK']}, Risk Manager", approver=f"{WHO['R-CEO']}, CEO",
                       history=[["1.0", a["date"], "Jahangir Shukurov", "Acceptance signed by the CEO"]], toc_pages=toc, **common())
        d.h1("Risk being accepted", new_page=True)
        d.table(["Field", "Detail"], [
            ["Acceptance reference", a["ref"]], ["Risk", f"{r['id']}: {r['title']}"], ["Risk statement", r["statement"]],
            ["Risk owner", r["owner"]], ["Existing controls", r["existing"]],
            ["Score today", f"Likelihood {r['lc']} x impact {r['ic']} = {r['sc']} ({r['bc']})"],
            ["Score after planned actions", f"Likelihood {r['lt']} x impact {r['it']} = {r['st']} ({r['bt']})"],
            ["Appetite", f"Scores up to {D.APPETITE_MAX}. This risk is above appetite, so the CEO must accept it in writing."],
        ], [0.27, 0.73], first_bold=True)
        d.h1("Reason for acceptance")
        d.p(a["reason"])
        d.h1("Conditions")
        d.p("The acceptance holds only while these conditions are met.", keep_next=True)
        d.bullets(a["conditions"])
        d.h1("Decision and sign-off")
        d.p(f"The risk is accepted from {a['date']} until {a['valid_until']}. It lapses on that date unless renewed.", keep_next=True)
        d.table(["Role", "Name", "Decision", "Date", "Signature"], [
            ["Risk owner", r["owner"], "Recommends acceptance", a["date"], "Signed (sample)"],
            ["Risk Manager", WHO["R-RISK"], "Method followed", a["date"], "Signed (sample)"],
            ["CISO-designate", WHO["R-CISO"], "Consulted, agrees", a["date"], "Signed (sample)"],
            ["CEO", WHO["R-CEO"], "Accepts the risk", a["date"], "Signed (sample)"],
        ], [0.18, 0.24, 0.24, 0.17, 0.17], first_bold=True)
        d.callout("Signatories are fictional role-holders. The signatures are placeholders for this portfolio sample.", lead="Note.")
        d.save(OUT / "Orvanta-Risk-Acceptance-RA-01.docx")
        return d

    return build


def main():
    risks, plan, counts = load()
    FIG.mkdir(parents=True, exist_ok=True)
    fig_matrix(FIG / "matrix.png")
    fig_process(FIG / "process.png")
    fig_levels(FIG / "levels.png", counts)
    fig_heatmaps(FIG / "heatmaps.png", risks)
    for s in D.SCENARIOS:
        fig_scenario(FIG / f"scenario-{s['id'][-1].lower()}.png", s)
    T.build_two_pass(build_method, OUT / "Orvanta-Risk-Management-Methodology.docx")
    T.build_two_pass(report_factory(risks, plan, counts), OUT / "Orvanta-Risk-Assessment-Report.docx")
    T.build_two_pass(acceptance_factory(risks), OUT / "Orvanta-Risk-Acceptance-RA-01.docx")
    for keep in (OUT / ".gitkeep", P2 / "previews/.gitkeep"):
        keep.unlink(missing_ok=True)
    now_high = counts["current"]["Critical"] + counts["current"]["High"]
    T.make_cover_image(P2 / "cover.png", "Project 2: Risk assessment", "Threat-Informed Risk Assessment",
                       "Risk register, MITRE ATT&CK threat mapping, three attack scenarios and a treatment plan",
                       [(str(len(risks)), "risks assessed"), (str(now_high), "High or Critical today"), ("3", "attack scenarios"), (str(len(plan)), "treatment actions")])
    (P2 / "data").mkdir(exist_ok=True)
    slim = [{k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()} for r in risks]
    (P2 / "data/risk_assessment_results.json").write_text(json.dumps(dict(as_of=D.AS_OF, counts=counts, risks=slim), indent=1, ensure_ascii=False), encoding="utf-8")
    print("Built", counts)


if __name__ == "__main__":
    main()
