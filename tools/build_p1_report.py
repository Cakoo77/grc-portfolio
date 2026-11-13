#!/usr/bin/env python3
"""Build the Project 1 report, figures, previews and cover from the recalculated workbook."""
import json
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Patch, Rectangle
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p1_data as D

ROOT = T.ROOT
P1 = ROOT / "01-gap-assessment"
FIG = P1 / "figures"
WORKBOOK = P1 / "deliverables/Orvanta-ISO27001-Gap-Assessment-Workbook.xlsx"
OUT = P1 / "deliverables/Orvanta-ISO27001-Gap-Assessment-Report.docx"
MASTER = json.loads((ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
SCORE_COLORS = ["#B4541A", "#E08A5B", "#F3C98B", "#BFDCCB", "#6FB39A", "#2F8573"]
SCORE_TEXT = ["white", "#16242C", "#16242C", "#16242C", "#16242C", "white"]
PHASE_COLORS = {"1 Foundation": "#0F5C6E", "2 Build": "#3D8A9B", "3 Operate": "#79B4C1", "4 Certify": "#B4541A"}

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"


def load_results():
    wb = load_workbook(WORKBOOK, data_only=True)

    def rows(sheet):
        ws = wb[sheet]
        out = []
        for r in ws.iter_rows(min_row=5, values_only=True):
            if not r[0]:
                continue
            out.append({"id": r[0], "name": r[1], "area": r[2], "score": r[5], "gap": r[7], "pscore": r[11], "priority": r[12], "effort": r[13], "owner": r[15], "pgap": r[16]})
        return out

    clauses, controls = rows("Clauses"), rows("Annex A")
    pg = []
    for r in wb["Priority Gaps"].iter_rows(min_row=5, max_row=14, values_only=True):
        pg.append(dict(id=r[0], title=r[1], why=r[2], what=r[3], owner=r[5], target=r[6], items=r[7], p1=r[8], avg=r[9], pscore=r[10], rank=r[11]))
    pg.sort(key=lambda x: x["rank"])
    ds = wb["Dashboard"]
    summary = dict(avg=ds["B4"].value, met=ds["B5"].value, total=ds["B6"].value, pct=ds["B7"].value)
    groups = []
    for r in ds.iter_rows(min_row=10, values_only=True):
        if r[0] and isinstance(r[1], (int, float)) and r[0][0] not in "SML" and r[0] != "Totals check":
            groups.append(dict(name=r[0], count=r[1], avg=r[2], met=r[3], p1=r[4], p2=r[5], p3=r[6], pct=r[7]))
    all_rows = clauses + controls
    counts = {p: sum(1 for x in all_rows if x["priority"] == p) for p in ("P1", "P2", "P3", "Met")}
    return clauses, controls, pg, summary, groups, counts


def heat_map(path, title_rows, per_row):
    """title_rows: list of (label, [(id, score), ...]); cells wrap at per_row and carry their score as text."""
    rows_needed = sum(max(1, -(-len(cells) // per_row)) for _, cells in title_rows)
    height = 0.42 * rows_needed + 0.14 * len(title_rows) + 0.52
    fig, ax = plt.subplots(figsize=(7.0, height))
    fig.subplots_adjust(0, 0, 1, 1)
    label_w, cw, ch = 1.15, (7.0 - 1.15) / per_row, 0.42
    y = height
    for label, cells in title_rows:
        count = max(1, -(-len(cells) // per_row))
        ax.text(0.02, y - 0.1, label, fontsize=7.8, fontweight="bold", color="#16242C", va="top")
        for i, (cid, score) in enumerate(cells):
            r, c = divmod(i, per_row)
            x, yy = label_w + c * cw, y - (r + 1) * ch
            ax.add_patch(Rectangle((x + 0.015, yy + 0.015), cw - 0.03, ch - 0.03, fc=SCORE_COLORS[score], ec="white", lw=0.5))
            ax.text(x + cw / 2, yy + ch * 0.64, cid, ha="center", va="center", fontsize=6.3, color=SCORE_TEXT[score])
            ax.text(x + cw / 2, yy + ch * 0.28, str(score), ha="center", va="center", fontsize=7.2, fontweight="bold", color=SCORE_TEXT[score])
        y -= count * ch + 0.14
    handles = [Patch(fc=SCORE_COLORS[i], ec="none", label=f"{s[0]} {s[1]}") for i, s in enumerate(D.SCALE)]
    ax.legend(handles=handles, loc="lower center", ncol=6, frameon=False, fontsize=7.3, bbox_to_anchor=(0.5, -0.005), columnspacing=1.1, handlelength=1.1, handletextpad=0.4)
    ax.set_xlim(0, 7)
    ax.set_ylim(0, height)
    ax.axis("off")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def gantt(path):
    rows = D.ROADMAP
    fig, ax = plt.subplots(figsize=(11, 5.4))
    fig.subplots_adjust(left=0.36, right=0.995, top=0.945, bottom=0.085)
    n = len(rows)
    for i, (rid, phase, activity, _gap, _owner, start, end) in enumerate(rows):
        y = n - i - 1
        ax.barh(y, end - start + 1, left=start - 1, height=0.62, color=PHASE_COLORS[phase], zorder=3)
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{r[0]}  {r[2]}" for r in reversed(rows)], fontsize=7.5, color="#16242C")
    ax.set_xticks(range(13), minor=False)
    ax.set_xticklabels([""] * 13)
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.6, n - 0.4)
    for i, m in enumerate(D.MONTHS):
        ax.text(i + 0.5, n - 0.1, m, ha="center", va="bottom", fontsize=7.5, color="#52616B")
    ax.grid(axis="x", color="#E3EAED", lw=0.8, zorder=0)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.legend(handles=[Patch(fc=c, label=k.split(" ", 1)[1]) for k, c in PHASE_COLORS.items()], loc="lower left", ncol=4, frameon=False, fontsize=8, bbox_to_anchor=(-0.02, -0.095), handlelength=1.2)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def attack_figure(path):
    fig = plt.figure(figsize=(7.0, 4.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    cw, ch, gx, gy = 2.14, 2.0, 0.29, 0.38
    teal, warn, ink, muted = "#0F5C6E", "#B4541A", "#16242C", "#52616B"
    pos = []
    for i, s in enumerate(D.ATTACK_PATH):
        r, c = divmod(i, 3)
        x, y = c * (cw + gx) + 0.01, 4.5 - (r + 1) * ch - r * gy - 0.03
        pos.append((x, y))
        color = warn if s[1] == "Detection gap" else teal
        ax.add_patch(FancyBboxPatch((x, y), cw - 0.02, ch, boxstyle="round,pad=0,rounding_size=0.07", fc="#F4F9FA", ec=color, lw=1.0))
        ax.add_patch(Circle((x + 0.25, y + ch - 0.27), 0.15, fc=color, ec="none"))
        ax.text(x + 0.25, y + ch - 0.275, str(s[0]), ha="center", va="center", fontsize=9, fontweight="bold", color="white")
        ax.text(x + 0.5, y + ch - 0.27, s[3], va="center", fontsize=9.2, fontweight="bold", color=ink)
        ax.text(x + 0.12, y + ch - 0.6, s[1].upper(), va="center", fontsize=6.6, fontweight="bold", color=color)
        ax.text(x + 0.12, y + ch - 0.76, s[2], va="center", fontsize=6.8, color=muted)
        ax.text(x + 0.12, y + ch - 0.93, textwrap.fill(s[4], 38), va="top", fontsize=7.2, color=ink, linespacing=1.25)
        ax.text(x + 0.12, y + 0.13, f"Open door: {s[5]}  |  {s[6]}", va="center", fontsize=6.8, fontweight="bold", color=color)
    arrow = dict(arrowstyle="-|>", mutation_scale=9, lw=1.1, color=muted, shrinkA=0, shrinkB=0)
    for i in (0, 1, 3, 4):
        x, y = pos[i]
        ax.add_patch(FancyArrowPatch((x + cw + 0.01, y + ch / 2), (x + cw + gx - 0.03, y + ch / 2), **arrow))
    (x3, y3), (x4, y4) = pos[2], pos[3]
    mid = y3 - gy / 2
    ax.plot([x3 + cw / 2, x3 + cw / 2, x4 + cw / 2], [y3, mid, mid], color=muted, lw=1.1)
    ax.add_patch(FancyArrowPatch((x4 + cw / 2, mid), (x4 + cw / 2, y4 + ch + 0.01), **arrow))
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def make_figures(clauses, controls):
    FIG.mkdir(parents=True, exist_ok=True)
    attack_figure(FIG / "attack-path.png")
    clause_rows = []
    for key, name in D.CLAUSE_NAMES.items():
        clause_rows.append((f"{key} {name}".replace(" evaluation", "\nevaluation"), [(c["id"], c["score"]) for c in clauses if c["id"].split(".")[0] == key]))
    heat_map(FIG / "heatmap-clauses.png", clause_rows, 7)
    theme_rows = []
    for key, name in D.THEMES.items():
        theme_rows.append((f"{name}", [(c["id"][2:], c["score"]) for c in controls if c["id"][2:].split(".")[0] == key]))
    heat_map(FIG / "heatmap-annex-a.png", theme_rows, 13)
    gantt(FIG / "roadmap-gantt.png")


def build_factory(clauses, controls, pg, summary, groups, counts):
    def build(toc_pages):
        d = T.BrandDoc(
            title="ISO/IEC 27001:2022 Gap Assessment", subtitle="Findings, priorities and a 12-month roadmap to certification",
            label="Project 1  |  Assessment report", doc_id="ORV-GAP-001", version="1.0", date="27 November 2026",
            author="Jahangir Shukurov", reviewer=f"{WHO['R-CISO']}, CISO-designate", approver=f"{WHO['R-CEO']}, CEO",
            classification="Confidential (sample)", client="Orvanta Payments UAB",
            history=[["0.1", "23 November 2026", "Jahangir Shukurov", "Draft for CISO-designate review"],
                     ["1.0", "27 November 2026", "Jahangir Shukurov", "Issued to the CEO and Management Board"]], toc_pages=toc_pages)

        d.h1("Executive summary", new_page=True)
        d.p("Three enterprise merchants worth EUR 2.4M a year require ISO/IEC 27001:2022 certification, and the target date is 30 November 2027. "
            "We assessed Orvanta against all 30 requirements of clauses 4 to 10 and all 93 Annex A controls. The goal is achievable, but only if the program starts in December 2026.", bold_lead="Situation.")
        d.stat_row([(f"{summary['avg']:.1f} / 5", "Average maturity"), (f"{summary['pct']:.0%}", f"At target ({summary['met']} of {summary['total']})"),
                    (str(counts["P1"]), "P1 gaps, first 90 days"), ("12 months", "To certificate decision")])
        d.p("", bold_lead="Key findings.", after=2, keep_next=True)
        d.bullets([
            ("The management system is missing.", "No clause area averages above 1.2. No scope, risk treatment, audit or management review exists, and an auditor needs all of them."),
            ("The technology is ahead of the governance.", "Encryption, Multi-AZ and infrastructure as code are real strengths, and 8 of 34 technological controls already meet target."),
            ("The most likely attack path is identity.", "Shared admin accounts, five tools without enforced MFA and 43 unmanaged laptops make a stolen credential the biggest concern."),
            ("Detection and recovery are unproven.", "There is no SIEM and no exercised incident plan, and no full restore is on record."),
        ])
        d.p("Delay puts EUR 2.4M of annual revenue, about 11% of FY2025 net revenue, at risk. Separately, the same gaps leave payment continuity, customer funds records and regulatory reporting exposed under DORA.", bold_lead="Risk in business terms.")
        d.p("", bold_lead="Decisions needed.", after=3, keep_next=True)
        d.table(["#", "Decision", "Owner", "By"], [
            ["1", "Sponsor the ISMS program as a board-level priority", WHO["R-CEO"], "30 Nov 2026"],
            ["2", "Fund the roadmap, including a third security hire and a SIEM", WHO["R-CEO"], "15 Dec 2026"],
            ["3", "Move the CISO reporting line from the CTO to the CEO", WHO["R-CEO"], "31 Dec 2026"],
            ["4", "Include the Baku subsidiary in the ISMS scope", WHO["R-CTO"], "15 Jan 2027"],
            ["5", "Commission a QSA review of PCI DSS scope and validation level", WHO["R-CISO"], "31 Jan 2027"],
        ], [0.05, 0.6, 0.2, 0.15], after=0)

        d.h1("Scope and method", new_page=True)
        d.p("This assessment covers Orvanta Payments UAB and Orvanta Engineering LLC: all products, AWS production, Vilnius, Baku and remote work. Fieldwork ran from 9 to 20 November 2026.")
        d.callout("Interviews and document reviews are simulated for this portfolio sample. They comprise 13 interviews and 22 documents, listed in the workbook's Evidence sheet.", lead="Evidence basis.")
        d.h2("Maturity scale")
        d.table(["Score", "Label", "What it means"], [[s[0], s[1], s[2]] for s in D.SCALE], [0.1, 0.2, 0.7], first_bold=True)
        d.p("The target is level 3 for every item. Certification tests whether a control is defined, working and evidenced; chasing level 5 everywhere would cost money without helping the audit.")
        d.h2("How priorities are set")
        d.p("Each open gap receives a score from a transparent formula. Weights sit in the workbook, so leadership can challenge and change them.", keep_next=True)
        d.table(["Factor", "Points", "Why it counts"], [
            ["Gap size", "2 per level below target", "Larger gaps take longer and carry more exposure"],
            ["Certification blocker", "2 if yes", "Some gaps would likely stop the audit outright"],
            ["Attack relevance", "High 3, Medium 2, Low 1, None 0", "Reflects how directly an attacker could exploit the gap"],
        ], [0.25, 0.3, 0.45], first_bold=True)
        d.p("A score of 9 or more is P1 (start in the first 90 days), 6 to 8 is P2 (complete by mid-2027), and lower scores are P3.")

        d.h1("Results")
        d.h2("Maturity by clause", )
        d.p(f"All {sum(1 for c in clauses if c['score'] < 3)} clause requirements are below target. Performance evaluation is the weakest area, because the ISMS has never been measured, audited or reviewed.", keep_next=True)
        d.figure(FIG / "heatmap-clauses.png", "Maturity heat map for clauses 4 to 10. Each cell shows the requirement and its score.")
        d.p("The table summarizes clauses and Annex A themes together. Workbook formulas produce every figure.", keep_next=True)
        d.table(["Area", "Items", "Average", "At target", "P1", "P2", "P3"],
                [[g["name"], g["count"], f"{g['avg']:.1f}", g["met"], g["p1"], g["p2"], g["p3"]] for g in groups], [0.4, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], first_bold=True)
        d.h2("Climate change consideration")
        d.p("Amendment 1:2024 asks organizations to decide whether climate change is a relevant issue, and notes that interested parties may have related requirements. Orvanta has not yet considered this. "
            "We expect limited direct relevance, but the decision must be recorded. Points to weigh include regional disruption affecting cloud or office services and sustainability questions from enterprise merchants.").paragraph_format.keep_together = True
        d.h2("Maturity by Annex A theme")
        theme = [g for g in groups if g["name"] in D.THEMES.values()]
        d.p("Physical and people controls score best, because offices are simple and HR practice is sound. Organizational controls score lowest because they depend on governance that does not exist yet.", keep_next=True)
        d.figure(FIG / "heatmap-annex-a.png", "Maturity heat map for all 93 Annex A controls, by theme.")
        d.h2("What already works")
        d.p(f"{counts['Met']} items already meet target. They matter for two reasons: the roadmap must not break them, and they show the engineering culture can run disciplined controls.", keep_next=True)
        d.bullets([
            ("Resilient, encrypted platform.", "Multi-AZ databases, KMS encryption at rest, TLS 1.2+ and synchronized clocks (A.8.14, A.8.24, A.8.17)."),
            ("Separated environments.", "Production, staging and development run in separate AWS accounts, defined in Terraform (A.8.31)."),
            ("Sound hiring basics.", "Screening, employment terms and NDAs are consistently applied (A.6.1, A.6.2, A.6.6)."),
            ("Regulatory discipline.", "Compliance keeps working contacts with the supervisor and retains ledger and AML records well (A.5.5, A.5.33)."),
        ])
        d.h2("How this compares with the intake view")
        d.p(f"The Company Fact Sheet recorded an indicative {sum(m['score'] for m in MASTER['maturity']) / len(MASTER['maturity']):.1f}, based on 12 broad domains. This assessment finds {summary['avg']:.1f}. "
            "The lower score is expected: it adds the clause requirements, where almost nothing is formally in place, and it credits only what evidence supports.")
        d.h1("How an attacker would use these gaps")
        d.p("A control gap matters most when it joins others into a path. The scenario below chains six gaps found in this assessment, from a phishing email to destroyed backups. "
            "Every step uses a weakness we observed, and none needs advanced skill.", keep_next=True)
        d.figure(FIG / "attack-path.png", "Illustrative attack path through current gaps. Technique IDs refer to MITRE ATT&CK.")
        d.callout("This is a scenario, not evidence that an attack has happened. Project 2 develops it into full attack-scenario analysis with likelihood and impact.", lead="Reading note.")
        d.p("Breaking the path at any step stops it. The table shows which planned actions close each door. Steps 3, 4 and 6 each have a quick win that starts closing them within 30 days.", keep_next=True)
        d.table(["Step", "Attacker's move", "Controls leaving the door open", "Priority gap", "Closed by"],
                [[s[0], s[3], s[5], s[6], s[7]] for s in D.ATTACK_PATH], [0.08, 0.27, 0.3, 0.15, 0.2], first_bold=True)
        d.p("This is why identity, logging and backup actions sit early in the roadmap even where their paperwork gap looks small: they sit on the shortest route to customer data and the ledger.")

        d.h1("Top 10 priority gaps", new_page=True)
        d.p("Rows in the workbook group into ten gaps, ranked by average priority score. Each is written for leadership: what could happen, and what fixes it. The average favors tightly focused gaps, so read it with the P1 count: GAP-03 and GAP-04 have the most P1 items.", keep_next=True)
        for rank, g in enumerate(pg, start=1):
            d.h3(f"{rank}. {g['title']} ({g['id']})")
            p = d.p(g["why"], after=2, keep_next=True)
            d.p(g["what"], bold_lead="Fix:", after=2, keep_next=True)
            d.p(f"Owner: {g['owner']}  |  Target: {g['target']}  |  {g['items']} linked items, {g['p1']} P1  |  Average maturity {g['avg']:.1f}", size=8.5, color=T.MUTED, after=6)

        d.h1("Quick wins")
        d.p("These eight actions need little budget and cut real risk within 30 days. They also build momentum and give the auditor early evidence.", keep_next=True)
        d.table(["ID", "Action", "Why it pays off", "Owner", "Days"], [[q[0], q[1], q[2], WHO[q[4]], q[5]] for q in D.QUICK_WINS], [0.08, 0.4, 0.3, 0.16, 0.06], size=8)

        d.section(landscape=True)
        d.h1("12-month roadmap")
        d.figure(FIG / "roadmap-gantt.png", "Roadmap from December 2026 to the certificate decision by 30 November 2027.", 0.97)
        d.section(landscape=False)
        d.h2("Why the sequence works")
        d.bullets([
            ("Foundation first.", "Scope and risk results decide which controls apply, so they cannot wait."),
            ("Attack paths next.", "Identity, endpoints, change control and backups are fixed early because they reduce real exposure now."),
            ("Records need time.", "Controls must operate before auditors can sample them, so monitoring runs from April 2027."),
            ("Buffer before the deadline.", "Stage 2 in October leaves time to close findings before 30 November 2027."),
        ])
        d.h2("Main risks to the plan")
        d.table(["Risk", "Effect", "Response"], [
            ["Security team stays at two people", "SIEM and evidence work slip", "Decide on the third hire by 15 December 2026"],
            ["Feature pressure beats remediation", "Roadmap items lose engineering time", "Reserve capacity in each CTO team's plan"],
            ["Certification body availability", "Stage audit dates move", "Book the auditor by March 2027"],
            ["Vendors respond slowly", "Tier 1 assessments run late", "Start early and use existing assurance reports"],
        ], [0.33, 0.3, 0.37], first_bold=True)
        d.h2("Limits of this assessment")
        d.p("This is a point-in-time view based on interviews and sampled evidence, not a certification audit, and it does not guarantee a certification result. Applicability is settled in the Statement of Applicability, so some scored controls may change. Costs are outside its scope. Regulatory matters are not legal advice.")
        d.h1("Appendix: all P1 items", new_page=True)
        p1_rows = sorted([r for r in clauses + controls if r["priority"] == "P1"], key=lambda r: -r["pscore"])
        d.p(f"The {len(p1_rows)} requirements and controls rated P1, highest priority score first. The workbook holds evidence and recommendations for each.", keep_next=True)
        d.table(["ID", "Requirement or control", "Score", "Priority", "Effort", "Owner", "Gap"],
                [[r["id"], r["name"], r["score"], r["pscore"], r["effort"], r["owner"], r["pgap"]] for r in p1_rows],
                [0.08, 0.42, 0.07, 0.09, 0.07, 0.18, 0.09], size=7.5)
        d.save(OUT)
        return d

    return build


def main():
    clauses, controls, pg, summary, groups, counts = load_results()
    make_figures(clauses, controls)
    pdf = T.build_two_pass(build_factory(clauses, controls, pg, summary, groups, counts), OUT)
    prev = P1 / "previews"
    (prev / ".gitkeep").unlink(missing_ok=True)
    (P1 / "deliverables/.gitkeep").unlink(missing_ok=True)
    T.make_cover_image(P1 / "cover.png", "Project 1: Gap assessment", "ISO/IEC 27001:2022 Gap Assessment",
                       "Maturity heat maps, an attack path view, top 10 gaps and a 12-month roadmap",
                       [("123", "requirements assessed"), (f"{summary['avg']:.1f}/5", "average maturity"), (str(counts["P1"]), "P1 gaps"), ("12", "month roadmap")])
    data = dict(summary=summary, counts=counts, groups=groups, priority_gaps=pg, clauses=clauses, controls=controls)
    (P1 / "data").mkdir(exist_ok=True)
    (P1 / "data/gap_assessment_results.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print("PDF", pdf, summary, counts)


if __name__ == "__main__":
    main()
