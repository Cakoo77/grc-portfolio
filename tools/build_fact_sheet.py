#!/usr/bin/env python3
"""Build the Orvanta Company Fact Sheet (docx and PDF), its diagrams, previews and cover image."""
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

ROOT = T.ROOT
PROFILE = ROOT / "00-company-profile"
M = json.loads((PROFILE / "data" / "orvanta_master.json").read_text(encoding="utf-8"))
FIG = PROFILE / "figures"
ROLES = {r["id"]: r for r in M["roles"]}
SYSTEMS = {s["id"]: s for s in M["systems"]}
OUT = PROFILE / "deliverables" / "Orvanta-Company-Fact-Sheet.docx"

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"

A, INK, MUTED, TINT, RULE, WARN = "#0F5C6E", "#16242C", "#52616B", "#E8F1F3", "#C9D6DB", "#B4541A"


def who(role_id):
    return ROLES[role_id]["name"]


def title_of(role_id):
    return ROLES[role_id]["title"]


# --- Diagrams --------------------------------------------------------------------------------

def _box(ax, x, y, w, h, text, fill="white", edge=A, color=INK, size=7.4, bold=False, dashed=False, lw=1.0, va="center"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05", fc=fill, ec=edge, lw=lw,
                                ls="--" if dashed else "-", zorder=2))
    ty = y + h / 2 if va == "center" else y + h - 0.09
    ax.text(x + w / 2, ty, text, ha="center", va="center" if va == "center" else "top", fontsize=size, color=color,
            fontweight="bold" if bold else "normal", zorder=3, linespacing=1.18)


def _line(ax, xs, ys, color="#7E929C", lw=0.9, ls="-"):
    ax.plot(xs, ys, color=color, lw=lw, ls=ls, zorder=1, solid_capstyle="round")


def _canvas(width, height):
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.04, width + 0.04)
    ax.set_ylim(-0.04, height + 0.04)
    ax.axis("off")
    return fig, ax


def org_chart(path):
    fig, ax = _canvas(12.6, 6.2)
    w, h, step, size = 1.2, 0.62, 1.24, 8.4

    def role(x, y, label, rid, **kw):
        _box(ax, x, y, w, h, f"{label}\n{who(rid)}", size=size, **kw)

    top = dict(fill=A, color="white", edge=A)
    ceo_x = 6.0
    role(ceo_x, 5.56, "Board Chair", "R-CHAIR", **top)
    role(ceo_x, 4.74, "CEO", "R-CEO", **top)
    _line(ax, [ceo_x + w / 2] * 2, [5.56, 5.36])
    _box(ax, 8.1, 5.56, 2.2, h, "Internal audit (co-sourced)\nRivenmark Assurance UAB", edge=MUTED, dashed=True, size=size)
    _line(ax, [ceo_x + w, 8.1], [5.87, 5.87], ls="--")

    y2 = 3.8
    cols = [("CFO", "R-CFO"), ("COO", "R-COO"), ("CPO", "R-CPO"), ("CCO", "R-CCO"),
            ("Head of Compliance\nand MLRO", "R-HCOMP"), ("DPO", "R-DPO"), ("General Counsel", "R-GC"), ("Head of People", "R-HPEOPLE")]
    col_a, col_b, trunk_gap = 0.0, 1.38, 0.18
    cto_x = (col_a + col_b) / 2
    xs = [2.72 + i * step for i in range(len(cols))]
    centers = [cto_x + w / 2] + [x + w / 2 for x in xs]
    bus = 4.58
    _line(ax, [ceo_x + w / 2] * 2, [4.74, bus])
    _line(ax, [min(centers), max(centers)], [bus, bus])
    for cx in centers:
        _line(ax, [cx, cx], [bus, y2 + h])
    role(cto_x, y2, "CTO", "R-CTO", fill=TINT)
    for x, (label, rid) in zip(xs, cols):
        role(x, y2, label, rid, fill=TINT)

    below = {"R-CFO": [("Treasury and\nSafeguarding", "R-TREAS")],
             "R-COO": [("Payment Operations", "R-PAYOPS"), ("Customer Support", "R-SUPMGR")],
             "R-HCOMP": [("Risk Manager", "R-RISK")]}
    row = 0.74
    for x, (_, rid) in zip(xs, cols):
        for i, (label, child) in enumerate(below.get(rid, [])):
            y = y2 - row * (i + 1)
            role(x, y, label, child)
            _line(ax, [x + w / 2] * 2, [y + h, y + h + row - h])

    trunk = cto_x + w / 2
    rows_y = [y2 - row * (i + 1) for i in range(5)]
    _line(ax, [trunk, trunk], [y2, rows_y[4] + h / 2])
    for y, (label, rid) in zip(rows_y, [("Platform and SRE", "R-HSRE"), ("Payments Engineering", "R-HPAY"),
                                        ("Cards and Accounts", "R-HCARD"), ("Merchant Experience", "R-HMX")]):
        role(col_b, y, label, rid)
        _line(ax, [trunk, col_b], [y + h / 2] * 2)
    # The highlighted line is observation OBS-12.
    role(col_a, rows_y[0], "CISO-designate", "R-CISO", edge=WARN, lw=1.9)
    _line(ax, [col_a + w, trunk], [rows_y[0] + h / 2] * 2, color=WARN, lw=1.5)
    role(col_a, rows_y[1], "Security Engineer", "R-SECENG")
    _line(ax, [col_a + w / 2] * 2, [rows_y[1] + h, rows_y[0]])
    for y, (label, rid) in zip(rows_y[2:], [("IT Operations", "R-ITOPS"), ("QA", "R-QA"), ("Data and Analytics", "R-DATA")]):
        role(col_a, y, label, rid)
        _line(ax, [col_a + w, trunk], [y + h / 2] * 2)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def architecture(path):
    fig = plt.figure(figsize=(11, 6.05))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 110)
    ax.set_ylim(0, 60.5)
    ax.axis("off")

    def zone(x, y, w, h, label, edge=RULE, fill="#FAFCFC", color=MUTED, dashed=False, inset=1.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.8", fc=fill, ec=edge, lw=1.0,
                                    ls="--" if dashed else "-", zorder=1))
        ax.text(x + inset, y + h - 1.0, label, fontsize=7.8, color=color, fontweight="bold", va="top", zorder=3)

    def node(x, y, w, h, text, fill="white", edge=A, size=7.4, dashed=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.5", fc=fill, ec=edge, lw=0.9,
                                    ls="--" if dashed else "-", zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=INK, zorder=3, linespacing=1.15)

    def tag(x, y, label, color=A):
        ax.text(x, y, label, fontsize=7.2, fontweight="bold", color=color, ha="center", va="center", zorder=4,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))

    def arrow(a, b, color=A):
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=7, lw=0.9, color=color, zorder=2.5, shrinkA=0, shrinkB=0))

    zone(0, 13, 15, 47.5, "Users")
    node(1.5, 49, 12, 6, "Merchant\nsystems")
    node(1.5, 40, 12, 6, "Customers\n(web portal)")
    node(1.5, 31, 12, 6, "Vilnius and\nremote staff")
    node(1.5, 22, 12, 6, "Baku engineers\n(Orvanta Eng. LLC)", edge=WARN, size=7)
    node(1.5, 14.2, 12, 5.8, "Helvora agents\n(Riga)")
    node(18, 42, 9, 10, "Cloudflare\nCDN, WAF,\nDDoS")

    zone(30, 13, 58, 47.5, "AWS eu-central-1  |  five accounts: prod, staging, dev, shared-services, legacy", edge=A, fill="#F4F9FA", color=A)
    zone(32, 31, 54, 25.5, "Production EKS cluster (SYS-07), private subnets", edge=A, fill="white", color=A)
    col = [34, 51.3, 68.6]
    for x, text in zip(col, ["Merchant Payment API\nSYS-01", "Merchant and Customer\nPortal  SYS-05", "Orbit Back-Office\nSYS-06"]):
        node(x, 44.5, 15.6, 7.5, text, fill=TINT)
    for x, text in zip(col, ["Payment Core and\nLedger  SYS-02", "Business Accounts\nSYS-03", "Card Program Service\nSYS-04"]):
        node(x, 33, 15.6, 7.5, text, fill=TINT)
    arrow((41.8, 44.5), (41.8, 40.5))
    arrow((59.1, 44.5), (59.1, 40.5))

    row_y, row_h = 14.5, 12.5
    zone(31.5, row_y, 22, row_h, "Legacy: no MFA, CloudTrail off", edge=WARN, fill="#FDF6F1", color=WARN, dashed=True)
    for x, text in zip((32.6, 39.6, 46.6), ("OpenVPN\nSYS-26", "Jenkins\nSYS-25", "Metabase\nSYS-24")):
        node(x, 15.6, 6.2, 7.2, text, edge=WARN, size=6.6)
    zone(54.5, row_y, 14.5, row_h, "Data stores")
    for x, text in zip((55.4, 62.2), ("RDS\nSYS-08", "S3\nSYS-09")):
        node(x, 15.6, 5.9, 7.2, text, size=6.6)
    zone(70, row_y, 16.5, row_h, "Shared services")
    for x, text in zip((70.8, 76, 81.2), ("Logging\nSYS-21", "Backup\nSYS-22", "IAM\nSYS-10")):
        node(x, 15.6, 4.9, 7.2, text, size=6)
    arrow((61.8, 31), (61.8, 27))
    arrow((75, 31), (75, 27))
    tag(79.3, 29, "DF-08")

    zone(91, 13, 19, 47.5, "Critical providers")
    node(92.5, 46, 16, 8, "Tessarin card platform\nSYS-20")
    node(92.5, 35, 16, 8, "Vaskora Bank SEPA\nSYS-23")
    node(92.5, 24, 16, 8, "Kyrovia KYC and AML\nSYS-18")
    node(92.5, 14.5, 16, 6.5, "Twilio SMS")

    zone(0, 0, 110, 11, "Workforce and delivery tools, behind Okta SSO (SYS-13) except where noted", inset=15)
    labels = ["Zendesk (agents local)\nSYS-19", "Okta\nSYS-13", "GitHub + Actions\nSYS-11", "Terraform\nSYS-12",
              "Google Workspace\nSYS-14", "Slack\nSYS-15", "Jira / Confluence\nSYS-16", "Jamf\nSYS-17"]
    for i, text in enumerate(labels):
        node(1.5 + i * 13.5, 1, 12.6, 6.2, text, size=6.6)

    arrow((13.5, 52), (18, 49))
    tag(15.9, 53.3, "DF-01")
    arrow((13.5, 43), (18, 45))
    arrow((27, 48.2), (34, 48.2))
    arrow((86, 50), (92.5, 50))
    tag(89.3, 51.8, "DF-03")
    arrow((86, 39), (92.5, 39))
    tag(89.3, 40.8, "DF-02")
    arrow((86, 33), (92.5, 28))
    tag(89.3, 33.6, "DF-04/05")
    arrow((13.5, 25), (32.6, 19.5), WARN)
    tag(22.5, 25, "DF-07", WARN)
    arrow((7.5, 14.2), (7.5, 7.2))
    tag(11, 12.1, "DF-06")
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def maturity_chart(path):
    rows = sorted(M["maturity"], key=lambda r: r["score"])
    fig, ax = plt.subplots(figsize=(7.0, 3.55))
    names = [r["domain"] for r in rows]
    scores = [r["score"] for r in rows]
    ax.barh(names, scores, color=A, height=0.56)
    for i, s in enumerate(scores):
        ax.text(s + 0.06, i, f"{s:.1f}", va="center", fontsize=8.5, color=INK)
    ax.set_xlim(0, 5)
    ax.set_xticks(range(6))
    ax.tick_params(axis="x", labelsize=8, colors=MUTED, length=0)
    ax.tick_params(axis="y", labelsize=8.5, colors=INK, length=0)
    ax.grid(axis="x", color="#E3EAED", lw=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel("Indicative maturity (0 = absent, 5 = optimized)", fontsize=8, color=MUTED)
    fig.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)


# --- Document --------------------------------------------------------------------------------

FILLS = {"Critical": T.FILL_CRITICAL, "High": T.FILL_HIGH, "Tier 1": T.FILL_CRITICAL, "Tier 2": T.FILL_HIGH}


def build(toc_pages):
    c = M["company"]
    fy = c["metrics_fy2025"]
    pipeline = c["certification_driver"]["enterprise_pipeline_eur_m"]
    pipeline_pct = pipeline / fy["net_revenue_eur_m"] * 100
    avg = sum(x["score"] for x in M["maturity"]) / len(M["maturity"])
    headcount = sum(d["vilnius"] + d["baku"] + d["remote"] for d in M["departments"])

    d = T.BrandDoc(
        title="Company Fact Sheet", subtitle="Single source of truth for the Orvanta GRC engagement",
        label="Phase 0  |  Client baseline", doc_id="ORV-PROFILE-001", version="1.0", date="7 November 2026",
        author="Jahangir Shukurov", reviewer=f"{who('R-CISO')}, CISO-designate", approver=f"{who('R-CEO')}, CEO",
        classification="Confidential (sample)", client=c["legal_name"],
        history=[["0.1", "2 November 2026", "Jahangir Shukurov", "Working draft from client intake"],
                 ["1.0", "7 November 2026", "Jahangir Shukurov", "Baseline issued for the engagement"]],
        toc_pages=toc_pages)

    # 1 -----------------------------------------------------------------------------------
    d.h1("Executive summary", new_page=True)
    d.p(f"Orvanta Payments UAB is a Vilnius-based payment institution with {headcount} people, most of its engineers in Baku, "
        f"and EUR {fy['total_payment_volume_eur_bn']} billion in annual payment volume. It grew faster than its security "
        "governance. Three enterprise merchant prospects now require ISO/IEC 27001:2022 certification, and DORA already applies.",
        bold_lead="Situation.")
    d.stat_row([(f"EUR {fy['net_revenue_eur_m']}M", "FY2025 net revenue"), (f"EUR {fy['avg_safeguarded_funds_eur_m']}M", "Average safeguarded funds"),
                (f"{fy['active_merchants']}", "Active merchants"), (f"{avg:.1f} / 5", "Indicative security maturity")])
    d.p("", bold_lead="Key findings from intake.", after=2, keep_next=True)
    d.bullets([
        ("Strong build, weak governance.", "Terraform, encryption and Multi-AZ are in place, but there is no ISMS and no current risk register."),
        ("Identity is the easiest way in.", "Shared admin accounts, five tools without enforced MFA and a 9-day median offboarding time."),
        ("Attacks would go unnoticed.", "There is no SIEM, no scheduled log review and no exercised incident plan."),
        ("Recovery is unproven.", "No full restore is on record, and backups share an account with production."),
        ("Suppliers are unassessed.", "None of the 20 vendors has a documented assessment, including all eight preliminary Tier 1 providers."),
    ])
    d.p(f"EUR {pipeline}M of annual enterprise revenue, equal to {pipeline_pct:.0f}% of FY2025 net revenue, depends on certification "
        "by 30 November 2027. A serious credential compromise could also disrupt payments, delay regulatory reporting and put "
        "customer trust and the licence relationship under strain.", bold_lead="Risk in business terms.")
    d.p("", bold_lead="Decisions needed from the CEO and Management Board.", after=3, keep_next=True)
    d.table(["#", "Decision", "Owner", "By"], [
        ["1", "Sponsor the ISMS program and name it a board-level priority", who("R-CEO"), "30 Nov 2026"],
        ["2", "Move the CISO reporting line from the CTO to the CEO (OBS-12)", who("R-CEO"), "31 Dec 2026"],
        ["3", "Include the Baku subsidiary in the ISMS scope", who("R-CTO"), "15 Jan 2027"],
        ["4", "Commission a QSA review of PCI DSS scope and validation level", who("R-CISO"), "31 Jan 2027"],
    ], [0.05, 0.6, 0.2, 0.15], after=0)

    # 2 -----------------------------------------------------------------------------------
    d.h1("How to use this document", new_page=True)
    d.p("This fact sheet records what the engagement team knows about Orvanta on 7 November 2026. Every later project draws its "
        "names, systems, vendors and baseline facts from here. If a fact changes, it changes here first, in the machine-readable "
        "master file (data/orvanta_master.json), and the documents are rebuilt.")
    d.table(["Prefix", "Meaning", "Example", "Used by"], [
        ["R-", "Role and named holder", "R-CISO", "All projects (owners, RACI, sign-off)"],
        ["BP-", "Business process", "BP-05", "Projects 2 and 7 (risk, BIA)"],
        ["SYS-", "System", "SYS-08", "Projects 1, 2, 4 and 7"],
        ["D-", "Data class", "D-CHD", "Projects 2 and 3"],
        ["DF-", "Data flow", "DF-07", "Projects 2 and 6"],
        ["VEN-", "Vendor", "VEN-02", "Projects 2, 6 and 8"],
        ["REG-", "Regulatory or contractual driver", "REG-01", "Projects 1, 7 and 8"],
        ["OBS-", "Baseline observation from intake", "OBS-05", "Projects 1, 2 and 5"],
    ], [0.1, 0.36, 0.14, 0.4], first_bold=True)
    d.callout("Orvanta and its named people, fictional suppliers, figures and observations are invented. Real vendors appear only "
              "as tools Orvanta uses. Nothing here describes the security of those vendors or of any real company.", lead="Reading note.")

    # 3 -----------------------------------------------------------------------------------
    d.h1("Company profile")
    d.h2("Overview")
    d.table(["Attribute", "Detail"], [
        ["Legal entity", f"{c['legal_name']}, founded {c['founded']}, payment institution licence since {c['licensed']}"],
        ["Headquarters", c["hq"]],
        ["Engineering hub", c["engineering_hub"]],
        ["Supervisor", c["supervisor"]],
        ["Production hosting", f"{c['cloud_region']}, with no production workload outside the EU"],
        ["Scale, FY2025", f"EUR {fy['total_payment_volume_eur_bn']}bn payment volume, {fy['active_merchants']} merchants, {fy['business_accounts']:,} business accounts, {fy['active_cards']:,} active cards, {headcount} employees"],
    ], [0.25, 0.75], first_bold=True)
    d.h2("Products")
    d.bullets([
        ("Merchant Payment API.", "SEPA Credit Transfer and SEPA Instant pay-ins and payouts, plus card acceptance through a hosted payment page."),
        ("Business accounts.", "IBAN accounts, statements and a web portal for small and mid-sized companies."),
        ("Card issuing.", "Debit cards for account holders. Tessarin handles issuer processing and stores full card numbers."),
    ])
    d.h2("Why the engagement is happening")
    d.bullets([
        ("Revenue.", f"{c['certification_driver']['enterprise_prospects']} enterprise prospects worth EUR {pipeline}M a year made certification a contract condition."),
        ("Regulation.", "DORA has applied to Orvanta since 17 January 2025, and the ICT risk framework is not yet complete."),
        ("Scale.", "Headcount doubled in three years, and informal controls no longer keep pace with engineering output."),
    ])

    # 4 -----------------------------------------------------------------------------------
    d.section(landscape=True)
    d.h1("Organization")
    d.h2("Organization chart")
    d.figure(FIG / "org-chart.png", "Orvanta reporting lines. The highlighted CISO-designate line is observation OBS-12.", 0.92)
    d.section(landscape=False)
    d.h2("Named role-holders")
    d.table(["Role ID", "Role", "Holder", "Location", "Reports to"],
            [[r["id"], r["title"], r["name"], r["location"], r["reports_to"] or "Shareholders"] for r in M["roles"]],
            [0.13, 0.42, 0.2, 0.1, 0.15], size=8)
    d.h2("Headcount by function and location")
    rows = [[x["name"], who(x["lead"]), x["vilnius"], x["baku"], x["remote"], x["vilnius"] + x["baku"] + x["remote"]] for x in M["departments"]]
    totals = [sum(r[i] for r in rows) for i in range(2, 6)]
    rows.append(["Total", ""] + totals)
    d.table(["Function", "Lead", "Vilnius", "Baku", "Remote", "Total"], rows, [0.33, 0.25, 0.105, 0.105, 0.105, 0.105], last_bold=True)

    # 5 -----------------------------------------------------------------------------------
    d.h1("Business processes")
    d.p("Twelve processes run the business. Criticality here is a working view, which the Business Impact Analysis in Project 7 tests and replaces with measured recovery objectives.")
    d.table(["ID", "Process", "What it does", "Owner", "Key systems", "Criticality"],
            [[p["id"], p["name"], p["description"], who(p["owner"]), ", ".join(p["systems"]), p["criticality"]] for p in M["processes"]],
            [0.07, 0.2, 0.3, 0.16, 0.16, 0.11], size=8, fills=FILLS)

    # 6 -----------------------------------------------------------------------------------
    d.section(landscape=True)
    d.h1("Technology")
    d.h2("Network and cloud architecture")
    d.figure(FIG / "architecture.png", "High-level architecture and data flows. Dashed orange marks legacy components outside Okta and the cross-border engineering path.", 0.9)
    d.h2("System inventory")
    d.table(["ID", "System", "Purpose", "Hosting", "Owner", "Criticality", "Data", "Access reality"],
            [[s["id"], s["name"], s["purpose"], s["hosting"], who(s["owner"]), s["criticality"], ", ".join(s["data"]), s["access"]] for s in M["systems"]],
            [0.06, 0.15, 0.17, 0.12, 0.11, 0.07, 0.1, 0.22], size=7.5, fills=FILLS)
    d.h2("Data classes")
    d.table(["ID", "Data class", "Classification", "ID", "Data class", "Classification"],
            _two_up(M["data_classes"]), [0.08, 0.28, 0.14, 0.08, 0.28, 0.14], size=7.5, after=2)
    d.h2("High-level data flows")
    d.table(["ID", "From", "To", "Data", "Protection today", "Cross-border"],
            [[f["id"], f["from"], f["to"], f["data"], f["protection"], f["cross_border"]] for f in M["data_flows"]],
            [0.05, 0.19, 0.17, 0.22, 0.18, 0.19], size=7.5, after=0)

    # 7 -----------------------------------------------------------------------------------
    d.section(landscape=False)
    d.h1("Vendors")
    d.p("Tiers are preliminary, based on data access and business criticality. Project 6 formalizes the criteria. \"CIF\" marks a vendor that "
        "appears to support a critical or important function under DORA, pending legal confirmation.")
    d.table(["ID", "Vendor", "Service", "Data access", "Tier", "CIF"],
            [[v["id"], v["name"], v["service"], v["data_access"], v["tier_prelim"], v["cif"]] for v in M["vendors"]],
            [0.08, 0.24, 0.28, 0.26, 0.08, 0.06], size=8, fills=FILLS)

    # 8 -----------------------------------------------------------------------------------
    d.h1("Regulatory landscape")
    d.p("The table sets out what applies and why. It deliberately omits reporting deadlines and detailed requirements, which Projects 7 and 8 cover and verify. "
        "It is a working view, not legal advice.")
    d.table(["ID", "Driver", "Why it matters to Orvanta", "Regulator or authority", "Owner", "Status"],
            [[r["id"], r["name"], r["why"], r["regulator"], who(r["owner"]), r["status"]] for r in M["regulations"]],
            [0.085, 0.22, 0.3, 0.15, 0.125, 0.12], size=8)
    d.h2("Verification status")
    d.p("Checked on 7 November 2026. Items marked [verify against official source] could not be confirmed on an official page and need checking before anyone relies on them.", keep_next=True)
    d.table(["ID", "What was checked and the result"], [[r["id"], r["verification"]] for r in M["regulations"]], [0.085, 0.915], size=8)

    # 9 -----------------------------------------------------------------------------------
    d.h1("Current security maturity")
    d.p(f"The average indicative score is {avg:.1f} out of 5. This is an intake view from interviews and a light document review, not a formal assessment. "
        "Project 1 replaces it with a control-by-control score against clauses 4 to 10 and all 93 Annex A controls.", keep_next=True)
    d.figure(FIG / "maturity.png", "Indicative maturity by security domain, highest at the top.", 0.88)
    d.h2("Baseline observations and the attacker's view")
    d.p("Each observation is paired with how an attacker would use it, because a gap matters most when it opens a real attack path.", keep_next=True)
    d.table(["ID", "Area", "What we observed", "How an attacker would use it", "Owner"],
            [[o["id"], o["area"], o["fact"], o["attacker_view"], who(o["owner"])] for o in M["observations"]],
            [0.08, 0.15, 0.34, 0.3, 0.13], size=8)
    d.save(OUT)
    return d


def _two_up(items):
    half = (len(items) + 1) // 2
    rows = []
    for i in range(half):
        left = items[i]
        right = items[i + half] if i + half < len(items) else None
        rows.append([left["id"], left["name"], left["classification"]] + ([right["id"], right["name"], right["classification"]] if right else ["", "", ""]))
    return rows


def main():
    T.make_monogram()
    FIG.mkdir(parents=True, exist_ok=True)
    org_chart(FIG / "org-chart.png")
    architecture(FIG / "architecture.png")
    maturity_chart(FIG / "maturity.png")
    pdf = T.build_two_pass(build, OUT)
    previews = PROFILE / "previews"
    for old in previews.glob("*.png"):
        old.unlink()
    T.render_pages(pdf, previews, dpi=110, pages=[3, 5, 8, 13])
    (previews / ".gitkeep").unlink(missing_ok=True)
    (PROFILE / "deliverables" / ".gitkeep").unlink(missing_ok=True)
    T.make_cover_image(PROFILE / "cover.png", "Phase 0: client baseline", "Orvanta Payments UAB",
                       "Company Fact Sheet: the single source of truth behind eight GRC projects",
                       [("120", "employees"), (str(len(M["systems"])), "systems"), (str(len(M["vendors"])), "vendors"), (str(len(M["observations"])), "baseline gaps")])
    print("PDF:", pdf)


if __name__ == "__main__":
    main()
