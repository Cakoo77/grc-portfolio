#!/usr/bin/env python3
"""Render preview images for Project 2 from the built deliverables. Pages are found by their text."""
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

P2 = T.ROOT / "02-risk-assessment"
DELIVER, PREVIEWS = P2 / "deliverables", P2 / "previews"


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
    report = DELIVER / "Orvanta-Risk-Assessment-Report.pdf"
    for marker, name in (("Executive summary", "report-summary.png"), ("Top 10 risks today", "report-heatmaps.png"),
                         ("Cloud credential compromise (SCN-A)", "report-scenario.png"), ("Risk treatment plan", "report-treatment-plan.png")):
        save_page(report, marker, name, 110)
    save_page(DELIVER / "Orvanta-Risk-Management-Methodology.pdf", "Risk levels and appetite", "methodology-criteria.png", 110)
    workbook = T.to_pdf(DELIVER / "Orvanta-Risk-Assessment-Workbook.xlsx", Path(tempfile.mkdtemp()))
    save_page(workbook, "Critical or High today", "workbook-dashboard.png", 110)
    save_page(workbook, "Risk heat maps", "workbook-heat-maps.png", 110)
    print("Previews:", sorted(p.name for p in PREVIEWS.glob("*.png")))


if __name__ == "__main__":
    main()
