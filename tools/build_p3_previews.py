#!/usr/bin/env python3
"""Render preview images for Project 3 from the built deliverables. Pages are found by their text."""
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import doc_template as T

P3 = T.ROOT / "03-isms-documentation"
DELIVER, PREVIEWS = P3 / "deliverables", P3 / "previews"


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
    manual = DELIVER / "ORV-ISMS-001-ISMS-Manual.pdf"
    save_page(manual, "Scope statement.", "manual-scope.png", 110)
    save_page(manual, "Information security objectives", "manual-objectives.png", 110)
    policy = DELIVER / "policies/ORV-POL-02-Access-Control-Policy.pdf"
    pymupdf.open(policy)[0].get_pixmap(dpi=110).save(PREVIEWS / "policy-cover.png")
    save_page(policy, "Policy requirements", "policy-requirements.png", 110)
    save_page(DELIVER / "procedures/ORV-PRC-01-User-Access-Procedure.pdf", "Process overview", "procedure-steps.png", 110)
    workbook = T.to_pdf(DELIVER / "ORV-ISMS-002-ISMS-Register.xlsx", Path(tempfile.mkdtemp()))
    save_page(workbook, "Annex A controls covered", "register-dashboard.png", 110)
    save_page(workbook, "Annex A control map", "register-control-map.png", 120)
    save_page(workbook, "Information security objectives", "register-objectives.png", 120)
    print("Previews:", sorted(p.name for p in PREVIEWS.glob("*.png")))


if __name__ == "__main__":
    main()
