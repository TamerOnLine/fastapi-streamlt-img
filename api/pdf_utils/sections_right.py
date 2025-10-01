from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from .config import *
from .shapes import draw_rule
from .text import draw_par
from .fonts import AR_FONT

def draw_right_extra_sections(c: canvas.Canvas, right_x: float, right_w: float, yR: float, sections_right: list[dict]) -> float:
    for sec in (sections_right or []):
        title = (sec.get("title") or "").strip()
        lines = [str(x).strip() for x in (sec.get("lines") or []) if str(x).strip()]
        if not title or not lines:
            continue
        c.setFont("Helvetica-Bold", RIGHT_SEC_HEADING_SIZE); c.setFillColor(colors.black)
        c.drawString(right_x, yR, title); yR -= RIGHT_SEC_TITLE_TO_RULE_GAP
        c.setStrokeColor(RIGHT_SEC_RULE_COLOR); c.setLineWidth(RIGHT_SEC_RULE_WIDTH)
        c.line(right_x, yR, right_x + right_w, yR); yR -= RIGHT_SEC_RULE_TO_TEXT_GAP
        c.setFont("Helvetica", RIGHT_SEC_TEXT_SIZE); c.setFillColor(colors.black)
        yR = draw_par(c, right_x, yR, lines, "Helvetica", RIGHT_SEC_TEXT_SIZE, right_w, "left", False, RIGHT_SEC_LINE_GAP, RIGHT_SEC_PARA_GAP)
        yR -= RIGHT_SEC_SECTION_GAP
    return yR

def draw_projects(
    c: canvas.Canvas, right_x: float, right_w: float, yR: float,
    projects: list[tuple[str, str, str | None]], rtl_mode: bool = False
) -> float:
    # فلترة العناصر الفارغة
    clean_projects: list[tuple[str, str, str | None]] = []
    for title, desc, link in (projects or []):
        t = (title or "").strip()
        d = (desc or "").strip()
        l = (link or "").strip() if link else None
        if t or d or l:   # مشروع فعلي لو فيه أي شيء
            clean_projects.append((t, d, l))

    if not clean_projects:
        return yR  # لا نرسم القسم إطلاقًا

    # العنوان والخط
    c.setFont("Helvetica-Bold", HEADING_SIZE); c.setFillColor(HEADING_COLOR)
    c.drawString(right_x, yR, "Ausgewählte Projekte"); yR -= GAP_AFTER_HEADING
    draw_rule(c, right_x, yR, right_w); yR -= RIGHT_SEC_RULE_TO_TEXT_GAP

    # المحتوى
    for title, desc, link in clean_projects:
        c.setFont("Helvetica-Bold", PROJECT_TITLE_SIZE); c.setFillColor(SUBHEAD_COLOR)
        c.drawString(right_x, yR, title); yR -= PROJECT_TITLE_GAP_BELOW

        c.setFillColor(colors.black)
        yR = draw_par(
            c=c, x=right_x, y=yR,
            lines=(desc or "").split("\n"),
            font=(AR_FONT if rtl_mode else "Helvetica"),
            size=TEXT_SIZE, max_w=right_w,
            align=("right" if rtl_mode else "left"),
            rtl_mode=rtl_mode, leading=PROJECT_DESC_LEADING,
        )

        yR -= PROJECT_LINK_GAP_ABOVE
        if link:
            font_name = "Helvetica-Oblique"
            c.setFont(font_name, PROJECT_LINK_TEXT_SIZE); c.setFillColor(HEADING_COLOR)
            link_text = f"Repo: {link}"
            c.drawString(right_x, yR, link_text)
            tw  = pdfmetrics.stringWidth(link_text, font_name, PROJECT_LINK_TEXT_SIZE)
            asc = pdfmetrics.getAscent(font_name)  / 1000.0 * PROJECT_LINK_TEXT_SIZE
            dsc = abs(pdfmetrics.getDescent(font_name)) / 1000.0 * PROJECT_LINK_TEXT_SIZE
            c.linkURL(link, (right_x, yR - dsc, right_x + tw, yR + asc * 0.2), relative=0, thickness=0)
        yR -= PROJECT_BLOCK_GAP

    return yR


def draw_education(c: canvas.Canvas, right_x: float, right_w: float, yR: float, education_items: list[str]) -> float:
    # فلترة البلوكات الفارغة
    items = [str(b).strip() for b in (education_items or []) if str(b).strip()]
    if not items:
        return yR  # لا ترسم القسم

    # العنوان والخط
    c.setFont("Helvetica-Bold", HEADING_SIZE); c.setFillColor(HEADING_COLOR)
    c.drawString(right_x, yR, "Berufliche Weiterbildung"); yR -= GAP_AFTER_HEADING
    draw_rule(c, right_x, yR, right_w); yR -= RIGHT_SEC_RULE_TO_TEXT_GAP

    for block in items:
        parts = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not parts:
            continue

        # العنوان
        c.setFont("Helvetica-Bold", TEXT_SIZE); c.setFillColor(EDU_TITLE_COLOR)
        c.drawString(right_x, yR, parts[0]); yR -= RIGHT_SEC_LINE_GAP

        # باقي النص
        rest = parts[1:]
        if rest:
            c.setFillColor(colors.black)
            yR = draw_par(c, right_x, yR, rest, "Helvetica", RIGHT_SEC_TEXT_SIZE,
                          right_w, "left", False, EDU_TEXT_LEADING, 2)
        yR -= RIGHT_SEC_SECTION_GAP

    return yR
