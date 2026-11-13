#!/usr/bin/env python3
"""Render preview images for Project 1 from the built deliverables. Pages are found by their text."""
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

P1 = T.ROOT / "01-gap-assessment"
DELIVER, PREVIEWS = P1 / "deliverables", P1 / "previews"


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
    report = DELIVER / "Orvanta-ISO27001-Gap-Assessment-Report.pdf"
    for marker, name in (("Executive summary", "report-summary.png"), ("Maturity by Annex A theme", "report-heatmap.png"),
                         ("How an attacker would use these gaps", "report-attack-path.png"), ("12-month roadmap", "report-roadmap.png")):
        save_page(report, marker, name, 110)
    deck = DELIVER / "Orvanta-ISO27001-Executive-Briefing.pdf"
    save_page(deck, "achievable if we start", "briefing-bottom-line.png", 80)
    save_page(deck, "One realistic attack path", "briefing-attack-path.png", 80)
    workbook = T.to_pdf(DELIVER / "Orvanta-ISO27001-Gap-Assessment-Workbook.xlsx", Path(tempfile.mkdtemp()))
    save_page(workbook, "Overall average maturity", "workbook-dashboard.png", 110)
    save_page(workbook, "Annex A: 93 controls", "workbook-annex-a.png", 130)
    print("Previews:", sorted(p.name for p in PREVIEWS.glob("*.png")))


if __name__ == "__main__":
    main()
