#!/usr/bin/env python3
"""Build the Project 3 ISMS manual, 12 policies, 2 procedures and the combined PDF."""
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymupdf
from matplotlib import font_manager
from matplotlib.patches import Polygon

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p1_data as P1
import p2_data as P2
import p3_data as D

P3 = T.ROOT / "03-isms-documentation"
FIG, OUT = P3 / "figures", P3 / "deliverables"
MASTER = json.loads((T.ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
ROLE = {"R-CISO": "CISO", "R-CEO": "CEO", "R-ITOPS": "IT Operations Lead", "R-HSRE": "Head of Platform and SRE", "R-HPEOPLE": "Head of People",
        "R-CTO": "CTO", "R-HCOMP": "Head of Compliance", "R-RISK": "Risk Manager", "R-DPO": "DPO"}
CONTROL_NAME = {c[0]: c[1] for c in P1.CONTROLS}
TEAL, INK, MUTED = "#0F5C6E", "#16242C", "#52616B"

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"


def person(role_id):
    return f"{WHO[role_id]}, {ROLE[role_id]}"


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-")


def earlier(date_text, days):
    value = datetime.strptime(date_text, "%d %B %Y") - timedelta(days=days)
    return f"{value.day} {value:%B %Y}"


def next_review(date_text):
    return date_text.split(" ", 1)[1].replace("2027", "2028")


def policy_id(p):
    return f"ORV-POL-{p['num']:02d}"


def requirements(p):
    """Yield (requirement id, section, text, controls) with IDs numbered across the policy."""
    n = 0
    for section, items in p["sections"]:
        for text, controls in items:
            n += 1
            yield f"{p['code']}-{n:02d}", section, text, controls


def policy_controls(p):
    found = {c for _, _, _, controls in requirements(p) for c in controls.split(", ")}
    return sorted(found, key=lambda c: tuple(int(x) for x in c.split(".")))


def risks_for(controls):
    wanted = {"A." + c for c in controls}
    return [r["id"] for r in P2.RISKS if wanted & set(r["controls"].split(", "))]


def history(date, approver_role):
    return [["0.1", earlier(date, 9), "Jahangir Shukurov", "Draft for owner review"], ["1.0", date, "Jahangir Shukurov", f"Approved by the {ROLE[approver_role]}"]]


def common(doc, date, reviewer, approver, toc):
    return dict(version="1.0", date=date, author="Jahangir Shukurov", reviewer=person(reviewer), approver=person(approver), classification="Internal (sample)",
                client="Orvanta Payments UAB", history=history(date, approver), toc_pages=toc, doc_id=doc)


# --- Figures ---------------------------------------------------------------------------------

def chevrons(ax, x0, y, labels, total_w, h=0.5, size=7.6, color=TEAL):
    w = total_w / len(labels)
    for i, label in enumerate(labels):
        x = x0 + i * w
        notch = 0.13 if i else 0
        ax.add_patch(Polygon([(x, y), (x + w - 0.16, y), (x + w - 0.03, y + h / 2), (x + w - 0.16, y + h), (x, y + h), (x + notch, y + h / 2)], closed=True, fc=color, ec="none"))
        ax.text(x + w / 2 + 0.02, y + h / 2, label, ha="center", va="center", fontsize=size, color="white", fontweight="bold", linespacing=1.15)


def fig_flow(path, flows):
    rows = len(flows)
    height = 0.72 * rows + 0.1
    fig = plt.figure(figsize=(7.0, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, height)
    ax.axis("off")
    labelled = rows > 1
    for r, (name, steps) in enumerate(flows):
        y = height - 0.66 - r * 0.72
        if labelled:
            ax.text(0.02, y + 0.28, name, va="center", fontsize=8.6, fontweight="bold", color=INK)
        import textwrap
        chevrons(ax, 0.75 if labelled else 0.02, y, ["\n".join(textwrap.wrap(s, 19)) for s in steps], 6.23 if labelled else 6.96, h=0.56, size=6.9 if labelled else 8.4)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def fig_hierarchy(path):
    fig = plt.figure(figsize=(7.0, 2.9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 2.9)
    import textwrap
    ax.axis("off")
    tiers = [("Information Security Policy", "Approved by the CEO", "#0F5C6E"), ("11 topic policies", "Approved by the CISO", "#2F7B8D"),
             ("Procedures and standards", "Approved by the CISO and owned by operational leads", "#4C8F9F"), ("Records and evidence", "Kept by control owners in Jira, Okta, AWS and Confluence", "#79B4C1")]
    for i, (name, note, color) in enumerate(tiers):
        y = 2.2 - i * 0.7
        half_top, half_bottom = 0.5 + i * 0.45, 0.5 + (i + 1) * 0.45
        ax.add_patch(Polygon([(2.0 - half_top, y + 0.62), (2.0 + half_top, y + 0.62), (2.0 + half_bottom, y), (2.0 - half_bottom, y)], closed=True, fc=color, ec="white", lw=1.5))
        ax.text(2.0, y + 0.31, name if i else "Information\nSecurity Policy", ha="center", va="center", fontsize=8 if i else 7.2, fontweight="bold", color="white" if i < 3 else INK, linespacing=1.1)
        ax.text(4.55, y + 0.31, textwrap.fill(note, 34), va="center", fontsize=7.8, color=INK, linespacing=1.2)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


# --- Builders --------------------------------------------------------------------------------

def policy_factory(p, path):
    controls = policy_controls(p)

    def build(toc):
        d = T.BrandDoc(title=p["title"], subtitle=p["purpose"].split(". ")[0].rstrip(".").replace("This policy ", "A policy that ").replace("This is ", "") + ".",
                       label=f"Project 3  |  Policy {p['num']} of 12", **common(policy_id(p), p["date"], p["reviewer"], p["approver"], toc))
        d.h1("Purpose", new_page=True)
        d.p(p["purpose"])
        d.h1("Scope")
        d.p(p["scope"])
        d.h1("Roles and responsibilities")
        d.table(["Role", "Responsibility"], [list(r) for r in p["roles"]], [0.3, 0.7], first_bold=True, keep=True)
        d.h1("Policy requirements")
        d.p("Each requirement has an ID so that audits, exceptions and training can refer to it. The last column gives the Annex A controls it supports.", keep_next=True)
        rows = list(requirements(p))
        for section, _ in p["sections"]:
            d.h2(section)
            d.table(["ID", "Requirement", "Annex A"], [[rid, text, ", ".join("A." + c for c in ctl.split(", "))] for rid, sec, text, ctl in rows if sec == section], [0.1, 0.72, 0.18], size=9, first_bold=True)
        d.h1("Exceptions")
        d.p(D.EXCEPTIONS)
        d.h1("Enforcement")
        d.p(D.ENFORCEMENT)
        d.h1("Measures")
        d.p("The policy owner reports these measures to the ISMS steering meeting.", keep_next=True)
        d.table(["Measure", "Target"], [list(m) for m in p["measures"]], [0.7, 0.3], first_bold=True, keep=True)
        d.h1("Related controls, risks and documents")
        d.table(["Link", "Detail"], [
            ["Annex A controls", ", ".join("A." + c for c in controls)],
            ["Risks treated", ", ".join(risks_for(controls)) or "None directly"],
            ["Related documents", p["related"]],
        ], [0.24, 0.76], first_bold=True, keep=True)
        d.h1("Review")
        d.p(f"The {ROLE[p['owner']]} reviews this policy every year, and sooner after a serious incident or a significant change in law, technology or the business. The next review is due in {next_review(p['date'])}.")
        d.save(path)
        return d

    return build


def procedure_factory(pr, path, figure):
    def build(toc):
        d = T.BrandDoc(title=pr["title"], subtitle=pr["subtitle"], label=f"Project 3  |  Procedure {pr['num']} of 2",
                       **common(f"ORV-PRC-{pr['num']:02d}", pr["date"], pr["reviewer"], pr["approver"], toc))
        d.h1("Purpose and scope", new_page=True)
        d.p(pr["purpose"])
        d.p(pr["scope"], bold_lead="Scope.")
        d.h1("Roles")
        d.table(["Role", "Responsibility"], [list(r) for r in pr["roles"]], [0.3, 0.7], first_bold=True)
        d.h1("Process overview")
        d.figure(figure, "Process overview. Step tables below give the detail, the system used and the record kept.")
        d.h1("Procedure steps")
        for phase, steps in pr["steps"]:
            d.h2(phase)
            d.table(["Step", "Action", "Who", "System", "Record"], [list(s) for s in steps], [0.07, 0.45, 0.18, 0.14, 0.16], size=8.5, first_bold=True)
        if "sla" in pr:
            d.h1("Remediation deadlines")
            d.p("Deadlines run from the day the finding is rated. They are Orvanta's own targets, set by the CISO.", keep_next=True)
            d.table(["Severity", "Meaning", "Fix within"], [list(s) for s in pr["sla"]], [0.16, 0.6, 0.24], first_bold=True)
        d.h1("Metrics")
        d.table(["Measure", "Target"], [list(m) for m in pr["metrics"]], [0.7, 0.3], first_bold=True, keep=True)
        d.h1("Exceptions")
        d.p(D.EXCEPTIONS)
        d.h1("Related controls and documents")
        d.table(["Link", "Detail"], [["Annex A controls", ", ".join("A." + c for c in pr["controls"].split(", "))], ["Related documents", pr["related"]]], [0.24, 0.76], first_bold=True)
        d.p(f"The {ROLE[pr['owner']]} reviews this procedure every year and after any incident that shows a step did not work. The next review is due in {next_review(pr['date'])}.")
        d.save(path)
        return d

    return build


def register_rows():
    rows = [["ORV-ISMS-001", "ISMS Manual", "R-CISO", "R-CEO", "19 February 2027"]]
    rows += [[policy_id(p), p["title"], p["owner"], p["approver"], p["date"]] for p in D.POLICIES]
    rows += [[f"ORV-PRC-{pr['num']:02d}", pr["title"], pr["owner"], pr["approver"], pr["date"]] for pr in D.PROCEDURES]
    return rows


def build_manual(toc):
    date = "19 February 2027"
    d = T.BrandDoc(title="ISMS Manual", subtitle="Scope, context, interested parties, objectives and roles", label="Project 3  |  ISMS core",
                   **common("ORV-ISMS-001", date, "R-CISO", "R-CEO", toc))
    total = sum(len(list(requirements(p))) for p in D.POLICIES)
    d.h1("Summary", new_page=True)
    d.p("This manual is the entry point to Orvanta's information security management system. It says what the ISMS covers, what shapes it, who expects what from it, what it must achieve and who does what. "
        "It meets the documentation needs of ISO/IEC 27001:2022 clauses 4.1 to 4.4, 5.3 and 6.2.")
    d.stat_row([("12", "Policies"), ("2", "Procedures"), (str(total), "Numbered requirements"), ("93", "Annex A controls mapped")])
    d.bullets([
        ("Scope.", "All of Orvanta's products, people, sites and systems. Nothing Orvanta runs itself is excluded."),
        ("Objectives.", f"{len(D.OBJECTIVES)} measurable objectives, each with a baseline, target, owner and data source."),
        ("Documents.", "One top-level policy, eleven topic policies and two procedures. Every requirement has an ID and names the controls it supports."),
        ("Accountability.", "The CEO is accountable for the ISMS. The CISO runs it and reports to the CEO."),
    ])
    d.h1("Scope of the ISMS")
    d.callout(D.SCOPE["statement"], lead="Scope statement.")
    d.h2("What is included")
    d.table(["Area", "Included"], [list(x) for x in D.SCOPE["included"]], [0.22, 0.78], first_bold=True)
    d.h2("Interfaces and dependencies")
    d.p("These suppliers sit at the boundary. The table states where Orvanta's responsibility ends.", keep_next=True)
    d.table(["Supplier", "Boundary"], [list(x) for x in D.SCOPE["interfaces"]], [0.24, 0.76], first_bold=True)
    d.p(D.SCOPE["exclusions"], bold_lead="Exclusions.")

    d.h1("Context of the organization", new_page=True)
    d.p("These are the issues that most affect whether the ISMS can do its job. They were confirmed with the CEO, CTO and CISO in February 2027 and are reviewed at each management review.")
    d.h2("Internal issues")
    d.table(["Issue", "What it means for security", "How the ISMS responds"], [list(x) for x in D.CONTEXT_INTERNAL], [0.2, 0.42, 0.38], first_bold=True)
    d.h2("External issues")
    d.table(["Issue", "What it means for security", "How the ISMS responds"], [list(x) for x in D.CONTEXT_EXTERNAL], [0.2, 0.42, 0.38], first_bold=True)
    d.h2("Climate change")
    d.p(D.CLIMATE)
    d.h1("Interested parties", new_page=True)
    d.p("The table lists who has a stake in Orvanta's security and which of their needs the ISMS takes on as requirements.", keep_next=True)
    d.table(["Interested party", "What they need", "How Orvanta meets it"], [list(x) for x in D.PARTIES], [0.24, 0.4, 0.36], size=8.5, first_bold=True)

    d.section(landscape=True)
    d.h1("Information security objectives")
    d.p("Objectives are measured monthly and reported to the Management Board each quarter. Baselines are from November 2026. Latest readings are kept in the ISMS register workbook (ORV-ISMS-002).", keep_next=True)
    d.table(["ID", "Objective", "KPI", "Baseline", "Target", "Due", "Owner", "Data source"],
            [[o[0], o[1], o[2], f"{o[4]}{'%' if o[3] == '%' else ''}", f"{o[5]}{'%' if o[3] == '%' else ''}", o[7], WHO[o[8]], o[9]] for o in D.OBJECTIVES],
            [0.07, 0.22, 0.25, 0.07, 0.07, 0.09, 0.11, 0.12], size=8.5, first_bold=True)
    d.h1("Roles and responsibilities", new_page=True)
    d.p("R is responsible for doing the work, A is accountable for the result, C is consulted and I is informed. Each activity has exactly one A.", keep_next=True)
    d.table(["Activity"] + D.RACI_ROLES, [[a] + letters for a, letters in D.RACI], [0.3] + [0.07] * 10, size=8.5, first_bold=True,
            fills={"A": T.FILL_HIGH, "R": T.TINT})
    d.section(landscape=False)
    d.h1("How the ISMS runs")
    d.h2("Document hierarchy")
    d.figure(FIG / "hierarchy.png", "ISMS document hierarchy and approval levels.")
    d.bullets([
        ("Document control.", "Controlled documents live in the ISMS space in Confluence, with an owner, version, approval date and review date. Only the CISO's team can publish."),
        ("Steering.", "The CISO chairs a monthly ISMS steering meeting with the CTO, Head of Compliance, Risk Manager and operational leads."),
        ("Assurance.", "The internal audit is planned for July 2027 and the first management review for August 2027."),
        ("Improvement.", "Nonconformities, incidents and audit findings go into one corrective action register with root cause and an effectiveness check."),
    ])
    d.h2("Document register")
    d.table(["ID", "Document", "Owner", "Approved", "Next review"], [[r[0], r[1], WHO[r[2]], r[4], next_review(r[4])] for r in register_rows()], [0.14, 0.4, 0.16, 0.16, 0.14], size=8)
    d.save(OUT / "ORV-ISMS-001-ISMS-Manual.docx")
    return d


def main():
    FIG.mkdir(parents=True, exist_ok=True)
    (OUT / "policies").mkdir(parents=True, exist_ok=True)
    (OUT / "procedures").mkdir(parents=True, exist_ok=True)
    fig_hierarchy(FIG / "hierarchy.png")
    pdfs = [T.build_two_pass(build_manual, OUT / "ORV-ISMS-001-ISMS-Manual.docx")]
    for p in D.POLICIES:
        path = OUT / "policies" / f"{policy_id(p)}-{slug(p['title'])}.docx"
        pdfs.append(T.build_two_pass(policy_factory(p, path), path))
        print("Built", path.name)
    for pr in D.PROCEDURES:
        figure = FIG / f"flow-prc-{pr['num']:02d}.png"
        fig_flow(figure, pr["flows"])
        path = OUT / "procedures" / f"ORV-PRC-{pr['num']:02d}-{slug(pr['title'])}.docx"
        pdfs.append(T.build_two_pass(procedure_factory(pr, path, figure), path))
        print("Built", path.name)
    pack = pymupdf.open()
    for pdf in pdfs:
        with pymupdf.open(pdf) as part:
            pack.insert_pdf(part)
    pack.set_metadata({"title": "Orvanta ISMS Documentation Suite", "author": "Jahangir Shukurov", "subject": T.DISCLAIMER})
    pack.save(OUT / "Orvanta-ISMS-Documentation-Suite.pdf", garbage=4, deflate=True)
    for keep in (OUT / ".gitkeep", P3 / "previews/.gitkeep"):
        keep.unlink(missing_ok=True)
    reqs = [dict(id=rid, policy=policy_id(p), section=sec, text=text, controls=["A." + c for c in ctl.split(", ")]) for p in D.POLICIES for rid, sec, text, ctl in requirements(p)]
    (P3 / "data").mkdir(exist_ok=True)
    (P3 / "data/policy_requirements.json").write_text(json.dumps(reqs, indent=1, ensure_ascii=False), encoding="utf-8")
    T.make_cover_image(P3 / "cover.png", "Project 3: ISMS documentation", "ISMS Documentation Suite",
                       "ISMS manual, 12 policies and 2 procedures, with every requirement mapped to Annex A",
                       [("12", "policies"), ("2", "procedures"), (str(len(reqs)), "numbered requirements"), ("93", "controls mapped")])
    print("Pack pages:", pack.page_count, "requirements:", len(reqs))


if __name__ == "__main__":
    main()
