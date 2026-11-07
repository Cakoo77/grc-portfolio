"""Shared brand identity and Word document builder for every portfolio deliverable.

Word's automatic table of contents only fills in when a user updates fields, so documents are
built twice: the first pass measures heading pages from the PDF, the second writes them in. The
TOC stays a real Word field, so it can still be refreshed in Word.
"""
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pymupdf as fitz
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Emu, Pt, RGBColor, Twips
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
MONOGRAM = ASSETS / "js-monogram.png"

DISCLAIMER = "Sample engagement — fictional company, prepared for portfolio purposes."
FONT = "Arial"
ACCENT = "0F5C6E"
INK = "16242C"
MUTED = "52616B"
TINT = "E8F1F3"
RULE = "C9D6DB"
ZEBRA = "F6F9FA"
FILL_CRITICAL = "F9E3DA"
FILL_HIGH = "FCF0D6"

ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

PAGE_LONG, PAGE_SHORT, MARGIN = 16838, 11906, 1134


def rgb(hex_value: str) -> RGBColor:
    return RGBColor.from_string(hex_value)


# --- Brand images -----------------------------------------------------------------------------

def make_monogram(path: Path = MONOGRAM, size: int = 512) -> None:
    big = size * 4
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, big - 1, big - 1), radius=big // 7, fill=f"#{ACCENT}")
    font = ImageFont.truetype(ARIAL_BOLD, int(big * 0.5))
    draw.text((big / 2, big / 2), "JS", font=font, fill="white", anchor="mm")
    img = img.resize((size, size), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    path.with_suffix(".svg").write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><rect width="512" height="512" '
        f'rx="73" fill="#{ACCENT}"/><text x="256" y="256" dy=".35em" text-anchor="middle" '
        'font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="256" fill="#fff">JS</text></svg>\n',
        encoding="utf-8",
    )


def make_cover_image(path: Path, label: str, title: str, subtitle: str, stats: list[tuple[str, str]]) -> None:
    """Write the 1600x1200 portfolio cover used on GitHub and Upwork."""
    W, H, pad = 1600, 1200, 110
    img = Image.new("RGB", (W, H), f"#{ACCENT}")
    draw = ImageDraw.Draw(img)
    font = lambda face, size: ImageFont.truetype(face, size)
    plate = Image.new("RGBA", (448, 448), (0, 0, 0, 0))
    plate_draw = ImageDraw.Draw(plate)
    plate_draw.rounded_rectangle((0, 0, 447, 447), radius=72, fill="white")
    plate_draw.text((224, 224), "JS", font=font(ARIAL_BOLD, 216), fill=f"#{ACCENT}", anchor="mm")
    plate = plate.resize((112, 112), Image.LANCZOS)
    img.paste(plate, (pad, pad), plate)
    draw.text((pad + 140, pad + 18), "Jahangir Shukurov", font=font(ARIAL_BOLD, 36), fill="white")
    draw.text((pad + 140, pad + 64), "GRC Portfolio", font=font(ARIAL, 30), fill="#CFE3E8")
    y = 350
    draw.text((pad, y), label.upper(), font=font(ARIAL_BOLD, 30), fill="#9CD3DF")
    y += 62
    for line in _wrap(draw, title, font(ARIAL_BOLD, 84), W - 2 * pad):
        draw.text((pad, y), line, font=font(ARIAL_BOLD, 84), fill="white")
        y += 100
    y += 12
    for line in _wrap(draw, subtitle, font(ARIAL, 36), W - 2 * pad):
        draw.text((pad, y), line, font=font(ARIAL, 36), fill="#DCEBEE")
        y += 50
    col = (W - 2 * pad) / max(len(stats), 1)
    for i, (value, name) in enumerate(stats):
        x = pad + i * col
        draw.text((x, 860), value, font=font(ARIAL_BOLD, 66), fill="white")
        draw.text((x, 942), name, font=font(ARIAL, 28), fill="#CFE3E8")
    draw.line((pad, 1040, W - pad, 1040), fill="#4F8A98", width=2)
    draw.text((pad, 1066), DISCLAIMER, font=font(ARIAL, 28), fill="#DCEBEE")
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def _wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line]


# --- Word helpers -----------------------------------------------------------------------------

def _set_style_font(style, size, bold=None, color=INK):
    style.font.name = FONT
    style.font.size = Pt(size)
    if bold is not None:
        style.font.bold = bold
    style.font.italic = False
    style.font.color.rgb = rgb(color)
    fonts = style.element.get_or_add_rPr().get_or_add_rFonts()
    for attr in list(fonts.attrib):
        if "Theme" in attr:
            del fonts.attrib[attr]
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), FONT)


def _field(paragraph, instruction, size=None, color=None):
    def run_with(element):
        run = paragraph.add_run()
        if size:
            run.font.size = Pt(size)
        if color:
            run.font.color.rgb = rgb(color)
        run._r.append(element)
        return run

    for kind in ("begin", None, "separate", "text", "end"):
        if kind is None:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = f" {instruction} "
        elif kind == "text":
            el = OxmlElement("w:t")
            el.text = "1"
        else:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        run_with(el)


def _para_border(paragraph, side, color=RULE, size=6, space=6):
    pPr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    el = OxmlElement(f"w:{side}")
    for key, val in (("val", "single"), ("sz", str(size)), ("space", str(space)), ("color", color)):
        el.set(qn(f"w:{key}"), val)
    borders.append(el)
    pPr.append(borders)


def _shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:shd")):
        tcPr.remove(old)
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>'))


def _cell_borders(cell, **sides):
    tcPr = cell._tc.get_or_add_tcPr()
    xml = f'<w:tcBorders {nsdecls("w")}>'
    for side in ("top", "left", "bottom", "right"):
        spec = sides.get(side)
        if spec:
            xml += f'<w:{side} w:val="single" w:sz="{spec[0]}" w:space="0" w:color="{spec[1]}"/>'
        else:
            xml += f'<w:{side} w:val="nil"/>'
    tcPr.append(parse_xml(xml + "</w:tcBorders>"))


def _fix_table(table, widths):
    tbl = table._tbl
    pr = tbl.tblPr
    for tag in ("w:tblW", "w:tblLayout", "w:tblCellMar", "w:tblStyle", "w:tblLook"):
        for old in pr.findall(qn(tag)):
            pr.remove(old)
    pr.append(parse_xml(f'<w:tblW {nsdecls("w")} w:w="{sum(widths)}" w:type="dxa"/>'))
    pr.append(parse_xml(f'<w:tblLayout {nsdecls("w")} w:type="fixed"/>'))
    pr.append(parse_xml(
        f'<w:tblCellMar {nsdecls("w")}><w:top w:w="55" w:type="dxa"/><w:left w:w="85" w:type="dxa"/>'
        '<w:bottom w:w="55" w:type="dxa"/><w:right w:w="85" w:type="dxa"/></w:tblCellMar>'))
    for col, width in zip(tbl.tblGrid.findall(qn("w:gridCol")), widths):
        col.set(qn("w:w"), str(width))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = Twips(width)
        row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


# Word enforces child order inside these elements; helpers above append in convenient order.
_ORDER = {
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers",
            "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
            "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
            "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
            "rPr", "sectPr", "pPrChange"],
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection",
             "tcFitText", "vAlign", "hideMark"],
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc",
              "tblCellSpacing", "tblInd", "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"],
    "trPr": ["cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit", "trHeight", "tblHeader",
             "tblCellSpacing", "jc", "hidden"],
}


def _normalize(root):
    for name, order in _ORDER.items():
        rank = {qn(f"w:{tag}"): i for i, tag in enumerate(order)}
        for element in root.iter(qn(f"w:{name}")):
            children = sorted(element, key=lambda child: rank.get(child.tag, len(order)))
            for child in list(element):
                element.remove(child)
            element.extend(children)


class BrandDoc:
    def __init__(self, title, subtitle, label, doc_id, version, date, author, reviewer, approver,
                 classification, client, history, toc_pages=None):
        self.title, self.subtitle, self.label = title, subtitle, label
        self.doc_id, self.version, self.date = doc_id, version, date
        self.author, self.reviewer, self.approver = author, reviewer, approver
        self.classification, self.client, self.history = classification, client, history
        self.toc_pages = toc_pages or {}
        self.headings, self.counters, self.fig = [], [0, 0], 0
        self.doc = Document()
        self._setup_styles()
        self._setup_numbering()
        self._bm = 100
        props = self.doc.core_properties
        props.title, props.author, props.subject = title, author, DISCLAIMER
        props.language, props.keywords, props.comments = "en-US", "GRC; sample engagement", DISCLAIMER
        props.last_modified_by = author
        props.created = props.modified = datetime.now(timezone.utc).replace(tzinfo=None)
        section = self.doc.sections[0]
        self._page(section, landscape=False)
        section.different_first_page_header_footer = True
        self._header_footer(section)
        self._cover(section)

    # Setup ---------------------------------------------------------------------------------
    def _setup_styles(self):
        styles = self.doc.styles
        _set_style_font(styles["Normal"], 10)
        fmt = styles["Normal"].paragraph_format
        fmt.space_after, fmt.space_before, fmt.line_spacing = Pt(6), Pt(0), 1.12
        defaults = styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
        for old in defaults.findall(qn("w:lang")):
            defaults.remove(old)
        defaults.append(parse_xml(f'<w:lang {nsdecls("w")} w:val="en-US" w:eastAsia="en-US" w:bidi="ar-SA"/>'))
        for name, size, before, after in (("Heading 1", 16, 18, 8), ("Heading 2", 12, 13, 5), ("Heading 3", 10.5, 9, 3)):
            style = styles[name]
            _set_style_font(style, size, True, ACCENT)
            pf = style.paragraph_format
            pf.space_before, pf.space_after, pf.keep_with_next, pf.keep_together = Pt(before), Pt(after), True, True
        for name in ("List Bullet", "List Number"):
            _set_style_font(styles[name], 10)
            styles[name].paragraph_format.space_after = Pt(3)
        front = styles.add_style("Front Heading", 1)
        front.base_style = styles["Normal"]
        _set_style_font(front, 13, True, ACCENT)
        front.paragraph_format.space_before, front.paragraph_format.space_after = Pt(12), Pt(6)
        front.paragraph_format.keep_with_next = True
        caption = styles["Caption"]
        _set_style_font(caption, 8.5, False, MUTED)
        caption.paragraph_format.space_before, caption.paragraph_format.space_after = Pt(4), Pt(10)
        for name, left in (("TOC 1", 0), ("TOC 2", 280)):
            style = styles.add_style(name, 1)
            style.base_style = styles["Normal"]
            _set_style_font(style, 10 if name == "TOC 1" else 9.5, name == "TOC 1", INK)
            style.paragraph_format.left_indent = Twips(left)
            style.paragraph_format.space_after = Pt(3)
            style.paragraph_format.space_before = Pt(5 if name == "TOC 1" else 0)

    def _setup_numbering(self):
        numbering = self.doc.part.numbering_part.element
        abstract_id, num_id = 90, 90
        xml = f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{abstract_id}"><w:multiLevelType w:val="multilevel"/>'
        for lvl, (fmt, style) in enumerate((("%1", "Heading1"), ("%1.%2", "Heading2"))):
            xml += (f'<w:lvl w:ilvl="{lvl}"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:pStyle w:val="{style}"/>'
                    f'<w:lvlText w:val="{fmt}"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="624"/></w:tabs>'
                    '<w:ind w:left="624" w:hanging="624"/></w:pPr></w:lvl>')
        xml += "</w:abstractNum>"
        first_num = numbering.find(qn("w:num"))
        abstract = parse_xml(xml)
        if first_num is not None:
            first_num.addprevious(abstract)
        else:
            numbering.append(abstract)
        numbering.append(parse_xml(
            f'<w:num {nsdecls("w")} w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/></w:num>'))
        for lvl, name in enumerate(("Heading 1", "Heading 2")):
            pPr = self.doc.styles[name].element.get_or_add_pPr()
            pPr.append(parse_xml(
                f'<w:numPr {nsdecls("w")}><w:ilvl w:val="{lvl}"/><w:numId w:val="{num_id}"/></w:numPr>'))

    def _page(self, section, landscape):
        if landscape:
            section.orientation = WD_ORIENT.LANDSCAPE
            section.page_width, section.page_height = Twips(PAGE_LONG), Twips(PAGE_SHORT)
        else:
            section.orientation = WD_ORIENT.PORTRAIT
            section.page_width, section.page_height = Twips(PAGE_SHORT), Twips(PAGE_LONG)
        section.left_margin = section.right_margin = Twips(MARGIN)
        section.top_margin, section.bottom_margin = Twips(1304), Twips(1190)
        section.header_distance, section.footer_distance = Twips(510), Twips(454)

    @property
    def width(self):
        section = self.doc.sections[-1]
        return int(section.page_width.twips) - 2 * MARGIN

    def _header_footer(self, section):
        width = int(section.page_width.twips) - 2 * MARGIN
        section.header.is_linked_to_previous = False
        section.footer.is_linked_to_previous = False
        header = section.header.paragraphs[0]
        header.style = self.doc.styles["Normal"]
        header.text = ""
        header.paragraph_format.tab_stops.clear_all()
        header.paragraph_format.tab_stops.add_tab_stop(Twips(width), WD_TAB_ALIGNMENT.RIGHT)
        header.add_run().add_picture(str(MONOGRAM), height=Cm(0.45))
        run = header.add_run(f"  {self.client}  |  {self.title}")
        run.font.size, run.font.color.rgb = Pt(8), rgb(MUTED)
        run = header.add_run(f"\t{self.classification}")
        run.font.size, run.font.bold, run.font.color.rgb = Pt(8), True, rgb(ACCENT)
        _para_border(header, "bottom")

        footer = section.footer.paragraphs[0]
        footer.style = self.doc.styles["Normal"]
        footer.text = ""
        footer.paragraph_format.tab_stops.clear_all()
        footer.paragraph_format.tab_stops.add_tab_stop(Twips(width), WD_TAB_ALIGNMENT.RIGHT)
        _para_border(footer, "top")
        run = footer.add_run(DISCLAIMER)
        run.font.size, run.font.color.rgb = Pt(8), rgb(MUTED)
        run = footer.add_run("\tPage ")
        run.font.size, run.font.color.rgb = Pt(8), rgb(MUTED)
        _field(footer, "PAGE", 8, MUTED)
        run = footer.add_run(" of ")
        run.font.size, run.font.color.rgb = Pt(8), rgb(MUTED)
        _field(footer, "NUMPAGES", 8, MUTED)

    # Front matter --------------------------------------------------------------------------
    def _cover(self, section):
        first = section.first_page_footer.paragraphs[0]
        run = first.add_run(DISCLAIMER)
        run.font.size, run.font.color.rgb = Pt(8), rgb(MUTED)
        _para_border(first, "top")

        p = self.doc.paragraphs[0] if self.doc.paragraphs else self.doc.add_paragraph()
        p.add_run().add_picture(str(MONOGRAM), height=Cm(1.5))
        p.paragraph_format.space_after = Pt(4)
        p = self.doc.add_paragraph()
        run = p.add_run("Jahangir Shukurov")
        run.font.bold, run.font.size = True, Pt(11)
        run = p.add_run("  |  GRC Portfolio")
        run.font.size, run.font.color.rgb = Pt(11), rgb(MUTED)
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(120)
        run = p.add_run(self.label.upper())
        run.font.bold, run.font.size, run.font.color.rgb = True, Pt(10.5), rgb(ACCENT)
        p = self.doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(self.title)
        run.font.bold, run.font.size, run.font.color.rgb = True, Pt(30), rgb(INK)
        p = self.doc.add_paragraph()
        run = p.add_run(self.subtitle)
        run.font.size, run.font.color.rgb = Pt(13), rgb(MUTED)
        p.paragraph_format.space_after = Pt(14)
        _para_border(p, "bottom", ACCENT, 18, 12)
        for key, value in (("Client", self.client), ("Document ID", self.doc_id), ("Version", self.version),
                           ("Date", self.date), ("Classification", self.classification)):
            p = self.doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.tab_stops.add_tab_stop(Twips(1800))
            run = p.add_run(f"{key}\t")
            run.font.color.rgb = rgb(MUTED)
            p.add_run(value).font.bold = True
        self.doc.paragraphs[-5].paragraph_format.space_before = Pt(14)
        p = self.callout(DISCLAIMER, space_before=70)
        self.page_break()
        self._front_heading("Document control")
        self.table(["Field", "Value"], [
            ["Document ID", self.doc_id], ["Title", self.title], ["Version", self.version], ["Date", self.date],
            ["Author", self.author], ["Reviewer", self.reviewer], ["Approver", self.approver],
            ["Classification", self.classification]], [0.25, 0.75], first_bold=True)
        self._front_heading("Version history")
        self.table(["Version", "Date", "Author", "Change"], self.history, [0.12, 0.2, 0.22, 0.46])
        self._front_heading("Contents")
        self.toc_anchor = self.doc.add_paragraph()

    def _front_heading(self, text):
        self.doc.add_paragraph(text, style="Front Heading")

    def page_break(self):
        p = self.doc.paragraphs[-1] if self.doc.element.body[-2].tag == qn("w:p") else self.doc.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)

    def write_toc(self):
        width = self.doc.sections[0].page_width.twips - 2 * MARGIN
        anchor = self.toc_anchor._p
        entries = self.headings
        for i, (level, number, text, bookmark) in enumerate(entries):
            p = self.doc.add_paragraph(style=f"TOC {level}")
            p.paragraph_format.tab_stops.add_tab_stop(Twips(int(width)), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            if i == 0:
                for kind, value in (("begin", None), ("instr", ' TOC \\o "1-2" \\h \\z \\u '), ("separate", None)):
                    run = p.add_run()
                    if kind == "instr":
                        el = OxmlElement("w:instrText")
                        el.set(qn("xml:space"), "preserve")
                        el.text = value
                    else:
                        el = OxmlElement("w:fldChar")
                        el.set(qn("w:fldCharType"), kind)
                    run._r.append(el)
            link = OxmlElement("w:hyperlink")
            link.set(qn("w:anchor"), bookmark)
            link.set(qn("w:history"), "1")
            run = p.add_run(f"{number}  {text}\t{self.toc_pages.get(bookmark, 0)}")
            link.append(run._r)
            p._p.append(link)
            if i == len(entries) - 1:
                run = p.add_run()
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), "end")
                run._r.append(el)
            anchor.addprevious(p._p)
        anchor.getparent().remove(anchor)

    # Content -------------------------------------------------------------------------------
    def section(self, landscape=False):
        section = self.doc.add_section(WD_SECTION.NEW_PAGE)
        self._page(section, landscape)
        section.different_first_page_header_footer = False
        self._header_footer(section)
        return section

    def h1(self, text, new_page=False):
        self.counters[0] += 1
        self.counters[1] = 0
        return self._heading(text, 1, str(self.counters[0]), new_page)

    def h2(self, text):
        self.counters[1] += 1
        return self._heading(text, 2, f"{self.counters[0]}.{self.counters[1]}", False)

    def _heading(self, text, level, number, new_page):
        p = self.doc.add_paragraph(text, style=f"Heading {level}")
        p.paragraph_format.page_break_before = new_page
        self._bm += 1
        name = f"_Toc{self._bm:06d}"
        start = OxmlElement("w:bookmarkStart")
        start.set(qn("w:id"), str(self._bm))
        start.set(qn("w:name"), name)
        end = OxmlElement("w:bookmarkEnd")
        end.set(qn("w:id"), str(self._bm))
        p._p.insert(1 if p._p.pPr is not None else 0, start)
        p._p.append(end)
        self.headings.append((level, number, text, name))
        return p

    def p(self, text, bold_lead=None, size=None, color=None, after=None, keep_next=False):
        p = self.doc.add_paragraph()
        if bold_lead:
            run = p.add_run(bold_lead + " ")
            run.font.bold = True
            if size:
                run.font.size = Pt(size)
        run = p.add_run(text)
        if size:
            run.font.size = Pt(size)
        if color:
            run.font.color.rgb = rgb(color)
        if after is not None:
            p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.keep_with_next = keep_next
        return p

    def h3(self, text):
        return self.doc.add_paragraph(text, style="Heading 3")

    def bullets(self, items):
        for item in items:
            p = self.doc.add_paragraph(style="List Bullet")
            if isinstance(item, tuple):
                p.add_run(item[0] + " ").font.bold = True
                p.add_run(item[1])
            else:
                p.add_run(item)

    def table(self, headers, rows, fractions, size=8.5, first_bold=False, fills=None, zebra=True, after=8, last_bold=False):
        widths = [int(self.width * f) for f in fractions]
        widths[-1] += self.width - sum(widths)
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        _fix_table(table, widths)
        table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
        fills = fills or {}
        for c, text in enumerate(headers):
            cell = table.cell(0, c)
            _shade(cell, ACCENT)
            _cell_borders(cell, bottom=(4, ACCENT))
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(0)
            para.paragraph_format.keep_with_next = True
            run = para.add_run(text)
            run.font.size, run.font.bold, run.font.color.rgb = Pt(size), True, rgb("FFFFFF")
        for r, row in enumerate(rows, start=1):
            for c, text in enumerate(row):
                cell = table.cell(r, c)
                _cell_borders(cell, bottom=(4, RULE))
                if str(text) in fills:
                    _shade(cell, fills[str(text)])
                elif zebra and r % 2 == 0:
                    _shade(cell, ZEBRA)
                para = cell.paragraphs[0]
                para.paragraph_format.space_after = Pt(0)
                para.paragraph_format.line_spacing = 1.05
                run = para.add_run(str(text))
                run.font.size = Pt(size)
                if (first_bold and c == 0) or (last_bold and r == len(rows)):
                    run.font.bold = True
        self._spacer(after)
        return table

    def stat_row(self, stats):
        share = 1 / len(stats)
        widths = [int(self.width * share)] * len(stats)
        widths[-1] += self.width - sum(widths)
        table = self.doc.add_table(rows=1, cols=len(stats))
        _fix_table(table, widths)
        for cell, (value, name) in zip(table.rows[0].cells, stats):
            _shade(cell, TINT)
            _cell_borders(cell, left=(18, "FFFFFF"), right=(18, "FFFFFF"))
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(0)
            run = para.add_run(value)
            run.font.size, run.font.bold, run.font.color.rgb = Pt(15), True, rgb(ACCENT)
            para = cell.add_paragraph()
            para.paragraph_format.space_after = Pt(0)
            run = para.add_run(name)
            run.font.size, run.font.color.rgb = Pt(8), rgb(MUTED)
        self._spacer(8)

    def callout(self, text, lead=None, space_before=0):
        if space_before:
            self._spacer(space_before)
        table = self.doc.add_table(rows=1, cols=1)
        _fix_table(table, [self.width])
        cell = table.cell(0, 0)
        _shade(cell, TINT)
        _cell_borders(cell, left=(24, ACCENT))
        para = cell.paragraphs[0]
        para.paragraph_format.space_after = Pt(0)
        if lead:
            run = para.add_run(lead + " ")
            run.font.bold, run.font.size = True, Pt(9.5)
        run = para.add_run(text)
        run.font.size = Pt(9.5)
        self._spacer(6)

    def figure(self, path, caption, width_fraction=1.0):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_after = Pt(0)
        p.add_run().add_picture(str(path), width=Emu(int(self.width * width_fraction * 635)))
        self.fig += 1
        self.doc.add_paragraph(f"Figure {self.fig}: {caption}", style="Caption").alignment = WD_ALIGN_PARAGRAPH.CENTER

    def _spacer(self, points):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(max(points, 1))
        p.paragraph_format.line_spacing_rule = 4  # exact height
        run = p.add_run()
        run.font.size = Pt(1)
        return p

    def save(self, path):
        self.write_toc()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        for zoom in self.doc.settings.element.findall(qn("w:zoom")):
            zoom.set(qn("w:percent"), "100")
        _normalize(self.doc.element)
        _normalize(self.doc.styles.element)
        for section in self.doc.sections:
            for part in (section.header, section.footer, section.first_page_footer):
                _normalize(part._element)
        self.doc.save(path)
        return path


# --- Build pipeline ---------------------------------------------------------------------------

def to_pdf(docx_path: Path) -> Path:
    docx_path = Path(docx_path)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(docx_path.parent), str(docx_path)],
                   check=True, capture_output=True, timeout=240)
    return docx_path.with_suffix(".pdf")


def measure_headings(pdf_path, headings):
    """Map each heading bookmark to its PDF page by matching large text, in document order."""
    pages = {}
    doc = fitz.open(pdf_path)
    index, start = 0, 0
    lines_by_page = []
    for page in doc:
        lines = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = line["spans"]
                text = "".join(s["text"] for s in spans).strip()
                size = max((s["size"] for s in spans), default=0)
                if size >= 11.5:
                    lines.append(re.sub(r"\s+", " ", re.sub(r"^\d+(\.\d+)?\s*", "", text)))
        lines_by_page.append(lines)
    for level, number, text, bookmark in headings:
        target = re.sub(r"\s+", " ", text)
        for i in range(start, len(lines_by_page)):
            if target in lines_by_page[i]:
                pages[bookmark] = i + 1
                start = i
                break
        else:
            raise ValueError(f"Heading not found in PDF: {number} {text}")
    doc.close()
    return pages


def build_two_pass(build_fn, docx_path):
    """build_fn(toc_pages) returns a saved BrandDoc; rebuilt once measured pages are known."""
    first = build_fn({})
    pages = measure_headings(to_pdf(docx_path), first.headings)
    second = build_fn(pages)
    pdf = to_pdf(docx_path)
    if measure_headings(pdf, second.headings) != pages:
        raise RuntimeError("TOC page numbers moved between passes")
    return pdf


def render_pages(pdf_path, out_dir, dpi=80, pages=None, prefix="page"):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    written = []
    for i, page in enumerate(doc, start=1):
        if pages and i not in pages:
            continue
        target = out_dir / f"{prefix}-{i:02d}.png"
        page.get_pixmap(dpi=dpi).save(target)
        written.append(target)
    doc.close()
    return written
