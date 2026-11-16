#!/usr/bin/env python3
"""Render preview images for Project 4 from the built deliverables. Pages are found by their text."""
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

P4 = T.ROOT / "04-statement-of-applicability"
DELIVER, PREVIEWS = P4 / "deliverables", P4 / "previews"


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
    doc = DELIVER / "Orvanta-Statement-of-Applicability.pdf"
    for marker, name in (("Decisions needed.", "soa-summary.png"), ("When the open controls are due", "soa-status.png"),
                         ("Fifteen controls matter most", "soa-key-controls.png"), ("Appendix: all 93 controls", "soa-appendix.png")):
        save_page(doc, marker, name, 110)
    workbook = T.to_pdf(DELIVER / "Orvanta-Statement-of-Applicability.xlsx", Path(tempfile.mkdtemp()))
    save_page(workbook, "Implemented, share of applicable", "workbook-dashboard.png", 110)
    save_page(workbook, "Statement of Applicability: all 93", "workbook-soa.png", 130)
    print("Previews:", sorted(p.name for p in PREVIEWS.glob("*.png")))


if __name__ == "__main__":
    main()
