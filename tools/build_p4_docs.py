#!/usr/bin/env python3
"""Build the Project 4 Statement of Applicability document from the recalculated workbook."""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T
import p1_data as P1
import p4_data as D

P4 = T.ROOT / "04-statement-of-applicability"
FIG, OUT = P4 / "figures", P4 / "deliverables"
WORKBOOK = OUT / "Orvanta-Statement-of-Applicability.xlsx"
DOC = OUT / "Orvanta-Statement-of-Applicability.docx"
MASTER = json.loads((T.ROOT / "00-company-profile/data/orvanta_master.json").read_text(encoding="utf-8"))
WHO = {r["id"]: r["name"] for r in MASTER["roles"]}
ORDER = ["Implemented", "Partially implemented", "Planned", "Not applicable"]
COLOR = {"Implemented": "#6FB39A", "Partially implemented": "#F3C98B", "Planned": "#E08A5B", "Not applicable": "#B8C4CA"}
FILLS = {"Implemented": "E1F0E7", "Partially implemented": "FCF3D2", "Planned": "FAD9B8", "Not applicable": "E3E8EA", "No": "E3E8EA"}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
INK, MUTED = "#16242C", "#52616B"

for face in (T.ARIAL, T.ARIAL_BOLD):
    font_manager.fontManager.addfont(face)
plt.rcParams["font.family"] = "Arial"


def load():
    wb = load_workbook(WORKBOOK, data_only=True)
    rows = []
    for r in wb["SoA"].iter_rows(min_row=5, values_only=True):
        if r[0]:
            rows.append(dict(id=r[0], name=r[1], theme=r[2], applicable=r[3], by_risk=r[4], reg=r[5], why=r[6], status=r[7], how=r[8], owner=r[10],
                             risks=r[11], risk_n=r[12], reqs=r[13], req_n=r[14], doc=r[15], evidence=r[16], first_ev=r[17], target=r[18], score=r[19], check=r[20]))
    assert all(r["check"] == "OK" for r in rows)
    return rows


def fig_status(path, rows):
    themes = list(P1.THEMES.values())
    fig, ax = plt.subplots(figsize=(7.0, 2.25))
    fig.subplots_adjust(left=0.17, right=0.98, top=0.95, bottom=0.2)
    for y, theme in enumerate(reversed(themes)):
        left = 0
        for status in ORDER:
            n = sum(1 for r in rows if r["theme"] == theme and r["status"] == status)
            if n:
                ax.barh(y, n, left=left, color=COLOR[status], edgecolor="white", linewidth=1.5, height=0.62)
                ax.text(left + n / 2, y, str(n), ha="center", va="center", fontsize=8.5, fontweight="bold", color=INK)
                left += n
    ax.set_yticks(range(4))
    ax.set_yticklabels(list(reversed(themes)), fontsize=8.5, color=INK)
    ax.set_xticks([])
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.legend(handles=[Patch(fc=COLOR[s], label=s) for s in ORDER], loc="lower center", ncol=4, frameon=False, fontsize=7.6, bbox_to_anchor=(0.45, -0.3), handlelength=1.1)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def targets(rows):
    found = sorted({r["target"] for r in rows if r["target"] != "-"}, key=lambda t: (t[-4:], MONTHS.index(t[:3])))
    return [(t, sum(1 for r in rows if r["target"] == t)) for t in found]


def fig_targets(path, rows):
    data = targets(rows)
    fig, ax = plt.subplots(figsize=(7.0, 1.9))
    fig.subplots_adjust(left=0.06, right=0.98, top=0.9, bottom=0.2)
    xs = range(len(data))
    ax.bar(xs, [n for _, n in data], color="#0F5C6E", width=0.55)
    for x, (_, n) in zip(xs, data):
        ax.text(x, n + 0.4, str(n), ha="center", va="bottom", fontsize=8.5, fontweight="bold", color=INK)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([t for t, _ in data], fontsize=8.5, color=INK)
    ax.set_yticks([])
    ax.set_ylim(0, max(n for _, n in data) * 1.25)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.savefig(path, dpi=220, facecolor="white")
    plt.close(fig)


def build_factory(rows):
    by_id = {r["id"]: r for r in rows}
    count = lambda status: sum(1 for r in rows if r["status"] == status)
    applicable = [r for r in rows if r["applicable"] == "Yes"]
    excluded = [r for r in rows if r["applicable"] == "No"]
    by_risk = sum(1 for r in rows if r["by_risk"] == "Yes")
    regulatory = sum(1 for r in rows if r["reg"] != "-")
    open_rows = [r for r in rows if r["status"] in ("Partially implemented", "Planned")]
    tgt = targets(rows)
    by_mid = sum(n for t, n in tgt if t in ("May 2027", "Jun 2027"))

    def build(toc):
        d = T.BrandDoc(title="Statement of Applicability", subtitle="Which Annex A controls apply at Orvanta, why, and how far each is implemented",
                       label="Project 4  |  Statement of Applicability", doc_id="ORV-SOA-001", version="1.1", date=D.AS_OF, author="Jahangir Shukurov",
                       reviewer=f"{WHO['R-CISO']}, CISO", approver=f"{WHO['R-CEO']}, CEO", classification="Confidential (sample)", client="Orvanta Payments UAB",
                       history=D.VERSIONS, toc_pages=toc)
        d.h1("Summary", new_page=True)
        d.p("The Statement of Applicability is the link between Orvanta's risks and its controls. It lists all 93 controls in Annex A of ISO/IEC 27001:2022, says which apply and why, "
            f"and records how far each one is implemented. This is version 1.1, with status as of {D.AS_OF}. It meets clause 6.1.3.", bold_lead="Purpose.")
        d.stat_row([("93", "Controls considered"), (str(len(applicable)), "Applicable"), (str(len(excluded)), "Excluded"), (f"{count('Implemented') / len(applicable):.0%}", f"Implemented ({count('Implemented')} of {len(applicable)})")])
        d.p("", bold_lead="Key points.", after=2, keep_next=True)
        d.bullets([
            ("Almost everything applies.", f"{len(applicable)} controls apply. Two are excluded, each with a written reason and a trigger for reassessment."),
            ("Selection is traceable.", f"{by_risk} controls were selected in the risk treatment plan and link to named risks. The rest are baseline practice, and {regulatory} also carry regulatory relevance."),
            ("Implementation is honest.", f"{count('Implemented')} controls are implemented, {count('Partially implemented')} are partly in place and {count('Planned')} are planned. None is marked done without evidence."),
            ("The gap closes by mid-year.", f"{by_mid} of the {len(open_rows)} open controls are due in May or June 2027, ahead of the internal audit in July."),
            ("Every control is backed by a rule.", "Each applicable control links to at least one numbered policy requirement and one evidence source."),
        ])
        d.p("An auditor will sample this document against reality. A control marked Implemented without evidence is a nonconformity, so statuses here are deliberately conservative.", bold_lead="Why it matters.")
        d.p("", bold_lead="Decisions needed.", after=3, keep_next=True)
        d.table(["#", "Decision", "Owner", "By"], [
            ["1", "Approve version 1.1 of the Statement of Applicability", WHO["R-CEO"], "7 May 2027"],
            ["2", "Confirm the two exclusions and their reassessment triggers", WHO["R-CISO"], "7 May 2027"],
            ["3", "Hold owners to the May and June target dates before the July audit", WHO["R-CEO"], "30 Jun 2027"],
        ], [0.05, 0.6, 0.2, 0.15], after=0)

        d.h1("Method", new_page=True)
        d.p("Controls were not picked from a list. Each one was tested against three questions, in this order.")
        d.table(["Question", "Source", "Result"], [
            ["Does a risk need it?", "Risk treatment plan (ORV-RISK-002)", f"{by_risk} controls selected to treat named risks"],
            ["Does a law, regulator or contract expect it?", "Legal register and customer contracts", f"{regulatory} controls with regulatory relevance, shown as indicative"],
            ["Is it baseline practice Orvanta needs anyway?", "Gap assessment and the policy set", "Remaining applicable controls, each with its own reason"],
        ], [0.36, 0.32, 0.32], first_bold=True)
        d.p("All 93 Annex A controls were then compared with the selection, so that no necessary control was missed. Anything not needed is excluded with a reason.")
        d.h2("Status definitions")
        d.table(["Status", "Meaning"], [
            ["Implemented", "The control operates across scope and evidence exists. Effectiveness is still to be confirmed by the internal audit."],
            ["Partially implemented", "The control works in part of scope, or is designed and being rolled out."],
            ["Planned", "The control is approved and scheduled, but not yet operating."],
            ["Not applicable", "The control is excluded, with a justification."],
        ], [0.26, 0.74], first_bold=True, fills=FILLS)
        d.callout("Evidence and status are simulated for this portfolio sample. Regulatory relevance is an indicative mapping, not legal advice.", lead="Reading note.")
        d.h1("Applicability")
        d.p(f"{len(applicable)} of 93 controls apply. The two exclusions are below. An exclusion is valid only while its reason holds, so each has a trigger for reassessment.", keep_next=True)
        d.table(["Control", "Name", "Why it is excluded"], [[r["id"], r["name"], r["why"]] for r in excluded], [0.1, 0.25, 0.65], first_bold=True)
        d.p("Both excluded controls still appear in policy as conditional requirements. If Orvanta starts outsourcing development or sets up a restricted work area, the policy applies at once and this statement is updated.")

        d.h1("Implementation status", new_page=True)
        d.p("People and physical controls are nearly complete, because offices are simple and HR practice was already sound. Organizational and technological controls carry the open work, which follows the certification roadmap.", keep_next=True)
        d.figure(FIG / "status-by-theme.png", f"Implementation status by Annex A theme, as of {D.AS_OF}.")
        themes = list(P1.THEMES.values())
        table = [[t] + [sum(1 for r in rows if r["theme"] == t and r["status"] == s) for s in ORDER] + [sum(1 for r in rows if r["theme"] == t)] for t in themes]
        table.append(["Total"] + [count(s) for s in ORDER] + [len(rows)])
        d.table(["Theme"] + ORDER + ["Total"], table, [0.24, 0.15, 0.19, 0.12, 0.16, 0.14], first_bold=True, last_bold=True)
        d.h2("When the open controls are due")
        d.p(f"{len(open_rows)} applicable controls are not yet fully implemented. Each has an owner and a target date in the workbook.", keep_next=True)
        d.figure(FIG / "targets.png", "Open controls by target date.")
        d.h2("What changed since the gap assessment")
        low = sum(1 for r in applicable if r["score"] is not None and r["score"] < 3)
        moved = sum(1 for r in applicable if r["score"] is not None and r["score"] < 3 and r["status"] == "Implemented")
        d.p(f"In November 2026, {low} of the applicable controls scored below the target maturity of 3. Five months later, {moved} of those are implemented. "
            "The fastest progress came from the quick wins and from identity, device and backup work, which were scheduled first because they sit on the shortest attack paths.")

        d.h1("Key control implementation", new_page=True)
        d.p("Fifteen controls matter most to Orvanta's risk profile. This section describes how each one actually works: who runs it, with which tools, how it is checked and what remains.")
        for cid, (how, who, tools, check, remains) in D.KEY_CONTROLS.items():
            r = by_id["A." + cid]
            d.h3(f"{r['id']}  {r['name']}")
            d.table(["Aspect", "Detail"], [
                ["Status", r["status"]], ["How it works", how], ["Who runs it", who], ["Tools", tools], ["How it is checked", check], ["What remains", remains],
                ["Linked risks", r["risks"]], ["Policy requirements", r["reqs"]],
            ], [0.2, 0.8], size=8.5, first_bold=True, fills=FILLS, zebra=False, keep=True)

        d.h1("Keeping the statement current", new_page=True)
        d.bullets([
            ("Owner.", f"The Risk Manager, {WHO['R-RISK']}, maintains the statement. The CISO is accountable for it."),
            ("Triggers.", "It is updated after each risk assessment, when a control changes status, and when scope, suppliers or law change."),
            ("Review.", "The ISMS steering meeting reviews status monthly. The CEO approves each new version."),
            ("Assurance.", "The internal audit in July 2027 samples controls marked Implemented against the evidence register."),
        ])
        d.h2("Approval")
        d.table(["Role", "Name", "Decision", "Date", "Signature"], [
            ["Prepared by", "Jahangir Shukurov", "Prepared", D.AS_OF, "Signed (sample)"],
            ["CISO", WHO["R-CISO"], "Reviewed", D.AS_OF, "Signed (sample)"],
            ["CEO", WHO["R-CEO"], "Approval pending", "Due 7 May 2027", "-"],
        ], [0.18, 0.24, 0.22, 0.19, 0.17], first_bold=True, keep=True)

        d.section(landscape=True)
        d.h1("Appendix: all 93 controls")
        d.p("The workbook holds the full justification, implementation description and evidence for each control.", keep_next=True)
        d.table(["Control", "Name", "Applies", "Status", "Owner", "Linked risks", "Policy requirements", "Target"],
                [[r["id"], r["name"], r["applicable"], r["status"], r["owner"], r["risks"], r["reqs"], r["target"]] for r in rows],
                [0.06, 0.25, 0.05, 0.12, 0.11, 0.16, 0.18, 0.07], size=7.5, fills=FILLS, zebra=False)
        d.save(DOC)
        return d

    return build


def main():
    rows = load()
    FIG.mkdir(parents=True, exist_ok=True)
    fig_status(FIG / "status-by-theme.png", rows)
    fig_targets(FIG / "targets.png", rows)
    T.build_two_pass(build_factory(rows), DOC)
    for keep in (OUT / ".gitkeep", P4 / "previews/.gitkeep"):
        keep.unlink(missing_ok=True)
    implemented = sum(1 for r in rows if r["status"] == "Implemented")
    applicable = sum(1 for r in rows if r["applicable"] == "Yes")
    T.make_cover_image(P4 / "cover.png", "Project 4: Statement of Applicability", "Statement of Applicability",
                       "All 93 Annex A controls linked to risks, policy requirements, owners and evidence",
                       [("93", "controls considered"), (str(applicable), "applicable"), (str(implemented), "implemented"), ("15", "key controls detailed")])
    (P4 / "data").mkdir(exist_ok=True)
    (P4 / "data/statement_of_applicability.json").write_text(json.dumps(dict(as_of=D.AS_OF, controls=rows), indent=1, ensure_ascii=False), encoding="utf-8")
    print("Built", applicable, implemented)


if __name__ == "__main__":
    main()
