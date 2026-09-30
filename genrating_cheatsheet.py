from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os
import textwrap

from doc_loader import load_document, cleaning
from llm import genrate_ques, evaluate_ans, generate_cheatsheet
# Top-level code moved to if __name__ == '__main__' below



"""
pdf_builder.py
--------------
Plug-and-play PDF builder for interview cheat sheet.

Usage:
    from pdf_builder import build_cheatsheet_pdf

    raw_text = generate_cheatsheet(resume_context)   # your LangChain function
    build_cheatsheet_pdf(raw_text, "cheatsheet.pdf")
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER


# ─── COLORS ──────────────────────────────────────────────────────────────────
DARK_BG    = colors.HexColor("#1a1a2e")
ACCENT     = colors.HexColor("#e94560")
TECH_BLUE  = colors.HexColor("#0f3460")
TEXT_DARK  = colors.HexColor("#1a1a2e")
TEXT_GRAY  = colors.HexColor("#6c757d")
HR_COLOR   = colors.HexColor("#dee2e6")
WARN_BG    = colors.HexColor("#fff3cd")
WARN_TEXT  = colors.HexColor("#842029")
INTRO_BG   = colors.HexColor("#eef6ff")
DSA_BG     = colors.HexColor("#fff8f0")
HR_ANS_BG  = colors.HexColor("#f0fff4")


# ─── STYLES ──────────────────────────────────────────────────────────────────
def _styles():
    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "title": s("title", fontName="Helvetica-Bold", fontSize=22,
                   textColor=colors.white, alignment=TA_CENTER,
                   leading=26, spaceAfter=0, spaceBefore=0),
        "section": s("section", fontName="Helvetica-Bold", fontSize=11,
                     textColor=ACCENT, spaceBefore=12, spaceAfter=5),
        "item_key": s("item_key", fontName="Helvetica-Bold", fontSize=9.5,
                      textColor=TEXT_DARK, spaceAfter=2),
        "item_val": s("item_val", fontName="Helvetica", fontSize=9,
                      textColor=TEXT_GRAY, spaceAfter=5, leftIndent=10),
        "bullet":   s("bullet",   fontName="Helvetica", fontSize=9.5,
                      textColor=TEXT_DARK, spaceAfter=4, leftIndent=10),
        "tech_key": s("tech_key", fontName="Helvetica-Bold", fontSize=9,
                      textColor=colors.white),
        "tech_val": s("tech_val", fontName="Helvetica", fontSize=9,
                      textColor=TEXT_DARK),
        "hr_q":     s("hr_q",     fontName="Helvetica-Bold", fontSize=9.5,
                      textColor=TECH_BLUE, spaceAfter=2),
        "hr_a":     s("hr_a",     fontName="Helvetica", fontSize=9,
                      textColor=TEXT_DARK, spaceAfter=6, leftIndent=10),
        "warn":     s("warn",     fontName="Helvetica", fontSize=9.5,
                      textColor=WARN_TEXT),
        "footer":   s("footer",   fontName="Helvetica", fontSize=8,
                      textColor=TEXT_GRAY, alignment=TA_CENTER, spaceBefore=6),
        "intro_val":s("intro_val",fontName="Helvetica", fontSize=9.5,
                      textColor=TEXT_DARK, spaceAfter=0, leftIndent=10,
                      leading=14),
    }


# ─── SANITIZER ───────────────────────────────────────────────────────────────
def _sanitize(text: str) -> str:
    """Replace any character Helvetica cannot render with a safe ASCII equivalent."""
    replacements = {
        # dashes & hyphens
        "\u2011": "-",   # non-breaking hyphen
        "\u2012": "-",   # figure dash
        "\u2013": "-",   # en dash
        "\u2014": "-",   # em dash
        "\u2015": "-",   # horizontal bar
        # quotes
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        # spaces
        "\u00a0": " ",   # non-breaking space
        "\u202f": " ",   # narrow no-break space
        # bullets & symbols
        "\u2022": "-",   # bullet
        "\u2023": "-",   # triangular bullet
        "\u25cf": "-",   # black circle
        "\u2192": "->",  # right arrow
        "\u2713": "OK",  # check mark
        "\u2718": "X",   # cross mark
        # fractions / math
        "\u00bd": "1/2",
        "\u00bc": "1/4",
        "\u00be": "3/4",
        # other common problem chars
        "\u00ae": "(R)",
        "\u00a9": "(C)",
        "\u2026": "...", # ellipsis
        "\u00b7": ".",   # middle dot
        # TF-IDF special: non-ascii hyphen variants seen in LLM output
        "\uff0d": "-",   # fullwidth hyphen
    }
    for char, safe in replacements.items():
        text = text.replace(char, safe)

    # Final pass: drop anything still outside latin-1 printable range
    result = []
    for ch in text:
        if ord(ch) < 256:
            result.append(ch)
        else:
            result.append("?")
    return "".join(result)


# ─── PARSER ──────────────────────────────────────────────────────────────────
def _parse(text: str) -> dict:
    """Parse raw LLM output into a section → items dict."""
    SECTIONS = [
        "SELF INTRODUCTION",
        "PROJECT PITCHES",
        "KEY TECHNOLOGIES",
        "DSA TOPICS TO REVISE",
        "HR ANSWERS",
        "WEAK AREAS TO COVER",
    ]
    data = {s: [] for s in SECTIONS}
    current = None

    for line in text.strip().splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        matched = next((s for s in SECTIONS if stripped.upper().startswith(s)), None)
        if matched:
            current = matched
        elif current and stripped.startswith("- "):
            clean = _sanitize(stripped[2:].strip())
            data[current].append(clean)

    return data


# ─── HELPERS ─────────────────────────────────────────────────────────────────
def _section_header(story, title, W, st):
    story.append(Paragraph(f"[ {title} ]", st["section"]))
    story.append(HRFlowable(width=W, thickness=1, color=HR_COLOR, spaceAfter=5))


def _kv_items(story, items, st, key_style="item_key", val_style="item_val"):
    for item in items:
        if ":" in item:
            k, v = item.split(":", 1)
            story.append(Paragraph(f"->  {k.strip()}", st[key_style]))
            story.append(Paragraph(v.strip(), st[val_style]))
        else:
            story.append(Paragraph(f"->  {item}", st[key_style]))


def _two_col_bullets(story, items, W, st):
    half = (len(items) + 1) // 2
    col1, col2 = items[:half], items[half:]
    rows = []
    for i in range(max(len(col1), len(col2))):
        c1 = Paragraph(f"• {col1[i]}" if i < len(col1) else "", st["bullet"])
        c2 = Paragraph(f"• {col2[i]}" if i < len(col2) else "", st["bullet"])
        rows.append([c1, c2])
    t = Table(rows, colWidths=[W / 2, W / 2])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DSA_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 4))


# ─── MAIN BUILDER ─────────────────────────────────────────────────────────────
def build_cheatsheet_pdf(raw_text: str, output_path: str = "interview_cheatsheet.pdf") -> str:
    """
    Parse raw LLM cheat-sheet text and render a styled PDF.

    Args:
        raw_text    : The string returned by generate_cheatsheet()
        output_path : Where to save the PDF

    Returns:
        output_path (str)
    """
    W = A4[0] - 36 * mm  # usable page width

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=14*mm,  bottomMargin=14*mm,
    )
    st = _styles()
    data = _parse(raw_text)
    story = []

    # ── HEADER BANNER ────────────────────────────────────────────────────────
    header = Table([[Paragraph("INTERVIEW CHEAT SHEET", st["title"])]],
                   colWidths=[W])
    header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DARK_BG),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))

    # ── SELF INTRODUCTION ────────────────────────────────────────────────────
    items = data["SELF INTRODUCTION"]
    if items:
        _section_header(story, "SELF INTRODUCTION", W, st)
        intro_text = items[0].split(":", 1)[-1].strip() if ":" in items[0] else items[0]
        intro_table = Table([[Paragraph(intro_text, st["intro_val"])]], colWidths=[W])
        intro_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), INTRO_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("LINEAFTER",     (0, 0), (0, -1), 3, ACCENT),
        ]))
        story.append(intro_table)
        story.append(Spacer(1, 4))

    # ── PROJECT PITCHES ──────────────────────────────────────────────────────
    items = data["PROJECT PITCHES"]
    if items:
        _section_header(story, "PROJECT PITCHES", W, st)
        _kv_items(story, items, st)

    # ── KEY TECHNOLOGIES ─────────────────────────────────────────────────────
    items = data["KEY TECHNOLOGIES"]
    if items:
        _section_header(story, "KEY TECHNOLOGIES", W, st)
        rows = []
        for item in items:
            if ":" in item:
                k, v = item.split(":", 1)
                rows.append([
                    Paragraph(k.strip(), st["tech_key"]),
                    Paragraph(v.strip(), st["tech_val"]),
                ])
            else:
                rows.append([Paragraph(item, st["tech_key"]), Paragraph("", st["tech_val"])])

        tech_table = Table(rows, colWidths=[W * 0.28, W * 0.72])
        tech_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, -1), TECH_BLUE),
            ("ROWBACKGROUNDS",(1, 0), (1, -1),
             [colors.HexColor("#eef2ff"), colors.HexColor("#dde5ff")]),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.5, colors.white),
        ]))
        story.append(tech_table)
        story.append(Spacer(1, 4))

    # ── DSA TOPICS TO REVISE ─────────────────────────────────────────────────
    items = data["DSA TOPICS TO REVISE"]
    if items:
        _section_header(story, "DSA TOPICS TO REVISE", W, st)
        # Show topic : definition in two-column key-val style
        rows = []
        for item in items:
            if ":" in item:
                k, v = item.split(":", 1)
                rows.append([
                    Paragraph(f"• {k.strip()}", ParagraphStyle(
                        "dsa_k", fontName="Helvetica-Bold", fontSize=9,
                        textColor=TECH_BLUE
                    )),
                    Paragraph(v.strip(), ParagraphStyle(
                        "dsa_v", fontName="Helvetica", fontSize=9,
                        textColor=TEXT_DARK
                    )),
                ])
            else:
                rows.append([
                    Paragraph(f"• {item}", ParagraphStyle(
                        "dsa_b", fontName="Helvetica", fontSize=9.5,
                        textColor=TEXT_DARK
                    )),
                    Paragraph("", st["bullet"]),
                ])

        dsa_table = Table(rows, colWidths=[W * 0.35, W * 0.65])
        dsa_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), DSA_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.4, HR_COLOR),
        ]))
        story.append(dsa_table)
        story.append(Spacer(1, 4))

    # ── HR ANSWERS ───────────────────────────────────────────────────────────
    items = data["HR ANSWERS"]
    if items:
        _section_header(story, "HR ANSWERS", W, st)
        hr_rows = []
        for item in items:
            if ":" in item:
                k, v = item.split(":", 1)
                hr_rows.append([
                    Paragraph(f"Q: {k.strip()}", st["hr_q"]),
                    Paragraph(v.strip(), st["hr_a"]),
                ])
            else:
                hr_rows.append([Paragraph(item, st["hr_q"]), Paragraph("", st["hr_a"])])

        hr_table = Table(hr_rows, colWidths=[W * 0.32, W * 0.68])
        hr_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), HR_ANS_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.4, HR_COLOR),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(hr_table)
        story.append(Spacer(1, 4))

    # ── WEAK AREAS TO COVER ──────────────────────────────────────────────────
    items = data["WEAK AREAS TO COVER"]
    if items:
        _section_header(story, "WEAK AREAS TO COVER", W, st)
        warn_rows = [[Paragraph(f">>  {item}", st["warn"])] for item in items]
        warn_table = Table(warn_rows, colWidths=[W])
        warn_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), WARN_BG),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.5, colors.HexColor("#ffc107")),
        ]))
        story.append(warn_table)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width=W, thickness=1, color=HR_COLOR))
    story.append(Paragraph("Interview Cheat Sheet  |  Good luck!", st["footer"]))

    doc.build(story)
    print(f"✅ PDF saved → {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    sample_resume = r"C:\Users\hp\Downloads\Resume_in_pdf.pdf"
    if os.path.exists(sample_resume):
        p, t = load_document(sample_resume)
        text = cleaning(t)
        data = generate_cheatsheet(text)
        build_cheatsheet_pdf(data, "documents/My_cheatsheet.pdf")
    else:
        print("Run via application or provide a valid resume file path.")