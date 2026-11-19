#!/usr/bin/env python3
"""Render preview images for Project 6 from the built deliverables. Pages are found by their text."""
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

P6 = T.ROOT / "06-third-party-risk"
DELIVER, PREVIEWS = P6 / "deliverables", P6 / "previews"


def save_page(pdf, marker, name, dpi):
    doc = pymupdf.open(pdf)
    hits = [page for page in doc if marker in page.get_text() and "Contents" not in page.get_text()]
    if not hits:
        raise ValueError(f"No page containing {marker!r} in {pdf}")
    hits[0].get_pixmap(dpi=dpi).save(PREVIEWS / name)


def main():
    PREVIEWS.mkdir(exist_ok=True)
    for old in PREVIEWS.glob("*.png"):
        old.unlink()
    report = DELIVER / "ORV-TPRM-003-Supplier-Assessment-Report.pdf"
    save_page(report, "Decisions needed.", "report-summary.png", 110)
    save_page(report, "Results at a glance", "report-scores.png", 110)
    save_page(report, "Helvora's people are trained", "report-high-risk-supplier.png", 110)
    procedure = DELIVER / "ORV-TPRM-001-Third-Party-Risk-Management-Procedure.pdf"
    save_page(procedure, "The five stages of a supplier relationship", "procedure-lifecycle.png", 110)
    save_page(procedure, "Tier by data sensitivity", "procedure-tiering.png", 110)
    save_page(DELIVER / "ORV-TPRM-002-Supplier-Security-Questionnaire.pdf", "Governance and assurance", "questionnaire.png", 110)
    workbook = T.to_pdf(DELIVER / "Orvanta-Third-Party-Risk-Workbook.xlsx", Path(tempfile.mkdtemp()))
    save_page(workbook, "Tier 1 suppliers assessed", "workbook-dashboard.png", 110)
    save_page(workbook, "Supplier inventory and tiering", "workbook-inventory.png", 130)
    print("Previews:", sorted(p.name for p in PREVIEWS.glob("*.png")))


if __name__ == "__main__":
    main()
