"""Shared ReportLab styling for the project documents (problem statement, progress reports)."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak,
                                SimpleDocTemplate, Flowable)

FONTS = "C:/Windows/Fonts/"
pdfmetrics.registerFont(TTFont("Body", FONTS + "calibri.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", FONTS + "calibrib.ttf"))
pdfmetrics.registerFont(TTFont("Body-Italic", FONTS + "calibrii.ttf"))
pdfmetrics.registerFont(TTFont("Body-BoldItalic", FONTS + "calibriz.ttf"))
pdfmetrics.registerFont(TTFont("Head", FONTS + "cambriab.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic", boldItalic="Body-BoldItalic")

INK = colors.HexColor("#1d2733")
MUTED = colors.HexColor("#5b6773")
ACCENT = colors.HexColor("#2f6690")
ACCENT2 = colors.HexColor("#c8553d")
RULE = colors.HexColor("#d9dee3")
SHADE = colors.HexColor("#f3f6f9")
BOXFILL = colors.HexColor("#eef4fa")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm
TEXT_W = PAGE_W - 2 * MARGIN

S = {
    "title": ParagraphStyle("title", fontName="Head", fontSize=19, leading=24, textColor=INK, spaceAfter=6),
    "kicker": ParagraphStyle("kicker", fontName="Body-Bold", fontSize=9.5, leading=12, textColor=ACCENT,
                             spaceAfter=4),
    "meta": ParagraphStyle("meta", fontName="Body", fontSize=10, leading=13, textColor=MUTED, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="Head", fontSize=13.5, leading=17, textColor=INK, spaceBefore=12,
                         spaceAfter=5, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Body-Bold", fontSize=11, leading=14, textColor=ACCENT, spaceBefore=7,
                         spaceAfter=3, keepWithNext=1),
    "body": ParagraphStyle("body", fontName="Body", fontSize=10.5, leading=14.2, textColor=INK, alignment=TA_JUSTIFY,
                           spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="Body", fontSize=10.5, leading=14, textColor=INK, leftIndent=12,
                             bulletIndent=2, spaceAfter=2.5),
    "caption": ParagraphStyle("caption", fontName="Body-Italic", fontSize=9, leading=11.5, textColor=MUTED,
                              alignment=TA_LEFT, spaceBefore=3, spaceAfter=9),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=9.2, leading=11.6, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="Body-Bold", fontSize=9.2, leading=11.6, textColor=INK),
    "ref": ParagraphStyle("ref", fontName="Body", fontSize=9, leading=11.5, textColor=INK, leftIndent=14,
                          firstLineIndent=-14, spaceAfter=3),
    "box": ParagraphStyle("box", fontName="Body", fontSize=10.8, leading=15, textColor=INK, alignment=TA_JUSTIFY),
}


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items, style="bullet"):
    return [Paragraph(t, S[style], bulletText="\u2022") for t in items]


def numbered(items):
    return [Paragraph(t, S["bullet"], bulletText=f"{i}.") for i, t in enumerate(items, 1)]


def figure(path, width_mm, caption=None):
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width_mm * mm
    img.drawHeight = width_mm * mm * ratio
    parts = [img]
    if caption:
        parts.append(P(caption, "caption"))
    return KeepTogether(parts)


def table(rows, col_mm, header=True, zebra=True, font_size=None):
    data = [[c if not isinstance(c, str) else Paragraph(c, S["cellb"] if (header and i == 0) else S["cell"])
             for c in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in col_mm], repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 3.2),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2), ("LEFTPADDING", (0, 0), (-1, -1), 5),
          ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), SHADE), ("LINEBELOW", (0, 0), (-1, 0), 0.9, ACCENT)]
    if zebra:
        for r in range(2 if header else 1, len(rows), 2):
            st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#fafbfc")))
    t.setStyle(TableStyle(st))
    return t


def callout(text, title=None):
    inner = []
    if title:
        inner.append(Paragraph(f"<b>{title}</b>", ParagraphStyle("ct", parent=S["box"], textColor=ACCENT,
                                                                spaceAfter=3)))
    inner.append(Paragraph(text, S["box"]))
    t = Table([[inner]], colWidths=[TEXT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BOXFILL), ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


def make_doc(path, title, footer_text):
    def on_page(canv, doc):
        canv.saveState()
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.6)
        canv.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
        canv.setFont("Body", 8.5)
        canv.setFillColor(MUTED)
        canv.drawString(MARGIN, 9.5 * mm, footer_text)
        canv.drawRightString(PAGE_W - MARGIN, 9.5 * mm, f"{doc.page}")
        canv.restoreState()
    doc = SimpleDocTemplate(str(path), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=18 * mm,
                            bottomMargin=20 * mm, title=title, author="BTP, IIT Kharagpur")
    return doc, on_page
