import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data1 import S
from data2 import S2
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, CondPageBreak, PageBreak, KeepTogether)
from reportlab.lib.enums import TA_CENTER

OUT = sys.argv[1]
W, H = A4
M = 14 * mm
CW = W - 2 * M

def parse(txt):
    return [l.split("|") for l in txt.strip("\n").split("\n")]

def mix(c, t):  # blend colour with white, t=0 white .. 1 full
    return colors.Color(1 - (1 - c.red) * t, 1 - (1 - c.green) * t, 1 - (1 - c.blue) * t)

# (title, rows, accent hex, kind)
sections = []
pal = ["#E4572E", "#17A2B8", "#0077B6", "#00A896", "#8E5BD0", "#F28C28",
       "#C2185B", "#2E7D32", "#3F51B5", "#D4A017", "#009688", "#B8335F",
       "#5C6BC0", "#E07A1F", "#2A9D8F", "#7B4FC4", "#1976D2", "#E63946"]
order = []
for k in S:
    order.append((k, parse(S[k]), 2))
for k in S2:
    order.append((k, parse(S2[k]), 4 if k.startswith("7. ") else 2))

# regroup in logical order
def key_order(item):
    t = item[0]
    num = t.split(".")[0].replace("bis", "").replace("a", "").replace("b", "").replace("c", "")
    return 0

seq = [k for k in S] + [k for k in S2]

sty_en = ParagraphStyle("en", fontName="Helvetica-Bold", fontSize=8.6, leading=10.5)
sty_fr = ParagraphStyle("fr", fontName="Helvetica", fontSize=8.6, leading=10.5)
sty_h = ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=15, leading=18, textColor=colors.white)
sty_sub = ParagraphStyle("s", fontName="Helvetica", fontSize=9, leading=11, textColor=colors.white)
sty_th = ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8.6, leading=10.5, textColor=colors.white)

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def header(title, count, accent):
    num, _, name = title.partition(". ")
    name = name.split(" (")[0]
    left = Paragraph(esc(title if not num else title), sty_h)
    right = Paragraph("%d entrées" % count, ParagraphStyle("r", parent=sty_sub, alignment=2))
    t = Table([[left, right]], colWidths=[CW * 0.78, CW * 0.22])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), accent),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t

def pair_table(rows, accent, npairs=3):
    n = len(rows)
    per = -(-n // npairs)  # items per column-pair, reading top-down
    cells = []
    for r in range(per):
        line = []
        for p in range(npairs):
            i = p * per + r
            if i < n:
                en, fr = rows[i][0], rows[i][1]
                line += [Paragraph(esc(en), sty_en), Paragraph(esc(fr), sty_fr)]
            else:
                line += ["", ""]
        cells.append(line)
    head = []
    for p in range(npairs):
        head += [Paragraph("English", sty_th), Paragraph("Français", sty_th)]
    data = [head] + cells
    wpair = CW / npairs
    cws = []
    for p in range(npairs):
        cws += [wpair * 0.44, wpair * 0.56]
    t = Table(data, colWidths=cws, repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), mix(accent, 0.85)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.Color(1, 1, 1)),
    ]
    # alternating column colours: EN col strong tint, FR col light tint, pairs alternate hue strength
    for p in range(npairs):
        a = 2 * p
        strong = mix(accent, 0.30 if p % 2 == 0 else 0.20)
        light = mix(accent, 0.10 if p % 2 == 0 else 0.05)
        st.append(("BACKGROUND", (a, 1), (a, -1), strong))
        st.append(("BACKGROUND", (a + 1, 1), (a + 1, -1), light))
        if p > 0:
            st.append(("LINEBEFORE", (a, 0), (a, -1), 1.2, accent))
    t.setStyle(TableStyle(st))
    return t

def verb_table(rows, accent):
    head = [Paragraph(x, sty_th) for x in ["Infinitive", "Preterite", "Past participle", "Français"]]
    data = [head] + [[Paragraph(esc(r[0]), sty_en), Paragraph(esc(r[1]), sty_fr),
                      Paragraph(esc(r[2]), sty_fr), Paragraph(esc(r[3]), sty_fr)] for r in rows]
    # two blocks side by side to save space: split rows in two halves
    half = -(-len(rows) // 2)
    left, right = rows[:half], rows[half:]
    data = [head + head]
    for i in range(half):
        line = []
        for blk in (left, right):
            if i < len(blk):
                r = blk[i]
                line += [Paragraph(esc(r[0]), sty_en), Paragraph(esc(r[1]), sty_fr),
                         Paragraph(esc(r[2]), sty_fr), Paragraph(esc(r[3]), sty_fr)]
            else:
                line += ["", "", "", ""]
        data.append(line)
    f = [0.25, 0.22, 0.22, 0.31]
    cws = [CW / 2 * x for x in f] * 2
    t = Table(data, colWidths=cws, repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), mix(accent, 0.85)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.4), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("LINEBEFORE", (4, 0), (4, -1), 1.2, accent),
    ]
    tints = [0.32, 0.16, 0.26, 0.10]
    for c in range(8):
        st.append(("BACKGROUND", (c, 1), (c, -1), mix(accent, tints[c % 4])))
    t.setStyle(TableStyle(st))
    return t

def cover():
    big = ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=34, leading=38,
                         textColor=colors.white, alignment=TA_CENTER)
    mid = ParagraphStyle("mid", fontName="Helvetica", fontSize=14, leading=18,
                         textColor=colors.white, alignment=TA_CENTER)
    t = Table([[Paragraph("1000+ mots<br/>essentiels d'anglais", big)],
               [Paragraph("Niveau 3ème · liste thématique anglais - français", mid)]],
              colWidths=[CW], rowHeights=[70 * mm, 18 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0077B6")),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#00A896")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t

def toc_block(items):
    cells = []
    for i, (title, n, col) in enumerate(items):
        sw = Table([[""]], colWidths=[5 * mm], rowHeights=[5 * mm])
        sw.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), col)]))
        cells.append([sw, Paragraph(esc(title), ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=10, leading=13)),
                      Paragraph("%d" % n, ParagraphStyle("n", fontName="Helvetica", fontSize=10, leading=13, alignment=2))])
    t = Table(cells, colWidths=[8 * mm, CW - 28 * mm, 20 * mm])
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 3),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for i in range(len(cells)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (1, i), (-1, i), colors.Color(0.95, 0.96, 0.98)))
    t.setStyle(TableStyle(st))
    return t

def footer(c, doc):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.grey)
    c.drawString(M, 9 * mm, "1000+ mots essentiels d'anglais - niveau 3ème")
    c.drawRightString(W - M, 9 * mm, "Page %d" % doc.page)
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=14 * mm, bottomMargin=16 * mm,
                      title="1000+ mots essentiels d'anglais - niveau 3ème", author="")
doc.addPageTemplates([PageTemplate(id="p", frames=[Frame(M, 16 * mm, CW, H - 30 * mm, id="f",
                                                         leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                                   onPage=footer)])

story = [Spacer(1, 25 * mm), cover(), Spacer(1, 12 * mm)]
story.append(Paragraph("Comment utiliser cette liste", ParagraphStyle("hh", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.HexColor("#0077B6"))))
story.append(Spacer(1, 3 * mm))
tips = ["Apprends 20 mots par semaine, par thème.",
        "Écris une phrase personnelle avec chaque mot nouveau.",
        "Cache la colonne française et teste-toi, puis fais l'inverse.",
        "Apprends les verbes irréguliers à voix haute : be - was - been."]
for t_ in tips:
    story.append(Paragraph("• " + esc(t_), ParagraphStyle("tp", fontName="Helvetica", fontSize=10.5, leading=15, leftIndent=8)))
story.append(PageBreak())

story.append(Paragraph("Sommaire", ParagraphStyle("so", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=colors.HexColor("#0077B6"))))
story.append(Spacer(1, 4 * mm))

# build entries in order
entries = []
all_items = [(k, parse(S[k]), "p") for k in S] + [(k, parse(S2[k]), "v" if k.startswith("7. ") else "p") for k in S2]
total = 0
for i, (k, rows, kind) in enumerate(all_items):
    entries.append((k, rows, kind, colors.HexColor(pal[i % len(pal)])))
    total += len(rows) * (1)
toc = [(k, len(rows), col) for k, rows, kind, col in entries]
story.append(toc_block(toc))
story.append(Spacer(1, 5 * mm))
story.append(Paragraph("<b>Total : %d mots et expressions</b>" % total, ParagraphStyle("tt", fontName="Helvetica", fontSize=11, leading=14)))
print("TOTAL", total)

story.append(PageBreak())
for k, rows, kind, col in entries:
    story.append(CondPageBreak(45 * mm))
    story.append(header(k, len(rows), col))
    story.append(Spacer(1, 3 * mm))
    if kind == "v":
        story.append(verb_table(rows, col))
    else:
        story.append(pair_table(rows, col, 3))
    story.append(Spacer(1, 8 * mm))
doc.build(story)
