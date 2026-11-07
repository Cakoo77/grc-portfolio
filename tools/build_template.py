#!/usr/bin/env python3
"""Build the reusable Word template in assets/ from the same code that builds every deliverable."""
import doc_template as T

OUT = T.ASSETS / "js-grc-document-template.docx"


def build(toc_pages):
    d = T.BrandDoc(
        title="Document Title", subtitle="One line on what this document does for the reader",
        label="Project number  |  Document type", doc_id="ORV-XXX-001", version="1.0", date="Date of issue",
        author="Jahangir Shukurov", reviewer="Reviewer name and role", approver="Approver name and role",
        classification="Confidential (sample)", client="Orvanta Payments UAB",
        history=[["1.0", "Date of issue", "Jahangir Shukurov", "Describe the change"]], toc_pages=toc_pages)
    d.h1("Executive summary", new_page=True)
    d.p("Open every report with one page a CEO can read in two minutes: situation, key findings, risk in business terms, decisions needed.")
    d.h1("Section heading")
    d.h2("Subsection heading")
    d.p("Body text is Arial 10 pt. Headings number themselves. In Word, refresh the contents with Update Field after editing.")
    d.bullets(["Keep bullets short.", "Start each one with the point."])
    d.table(["Column", "Column", "Column"], [["Value", "Value", "Value"], ["Value", "Value", "Value"]], [0.3, 0.3, 0.4])
    d.callout("Use a callout for one point the reader must not miss.", lead="Note.")
    d.save(OUT)
    return d


if __name__ == "__main__":
    T.make_monogram()
    pdf = T.build_two_pass(build, OUT)
    pdf.unlink()
    print("Template:", OUT)
