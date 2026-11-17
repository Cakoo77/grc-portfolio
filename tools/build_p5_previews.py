#!/usr/bin/env python3
"""Render preview images for Project 5 from the built deliverables. Pages are found by their text."""
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

P5 = T.ROOT / "05-internal-audit-management-review"
DELIVER, PREVIEWS = P5 / "deliverables", P5 / "previews"


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
    report = DELIVER / "ORV-AUD-003-Internal-Audit-Report-IA-2027-01.pdf"
    save_page(report, "Overall conclusion.", "report-summary.png", 110)
    save_page(report, "Each nonconformity states what is required", "report-nonconformity.png", 110)
    save_page(DELIVER / "ORV-AUD-004-Corrective-Action-Plan.pdf", "Cause-and-effect diagram", "capa-root-cause.png", 110)
    save_page(DELIVER / "ORV-AUD-001-Internal-Audit-Programme.pdf", "Coverage of each area", "programme-coverage.png", 110)
    save_page(DELIVER / "ORV-MR-001-Management-Review-Pack.pdf", "Dashed lines show targets", "review-kpis.png", 110)
    save_page(DELIVER / "ORV-MR-002-Management-Review-Minutes.pdf", "These are the outputs of the review", "review-decisions.png", 110)
    workbook = T.to_pdf(DELIVER / "Orvanta-Internal-Audit-Workbook.xlsx", Path(tempfile.mkdtemp()))
    save_page(workbook, "Questions with full conformity", "workbook-dashboard.png", 110)
    save_page(workbook, "Audit checklist:", "workbook-checklist.png", 130)
    print("Previews:", sorted(p.name for p in PREVIEWS.glob("*.png")))


if __name__ == "__main__":
    main()
