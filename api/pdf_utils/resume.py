from io import BytesIO
from typing import List, Tuple, Optional, Dict, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader

from .config import *
from .shapes import draw_round_rect
from .sections_left import draw_left_column, draw_left_extra_sections
from .sections_right import draw_right_extra_sections, draw_projects, draw_education

def build_resume_pdf(
    *, name: str = "", location: str = "", phone: str = "", email: str = "",
    github: str = "", linkedin: str = "", birthdate: str = "",
    skills: List[str] = (), languages: List[str] = (),
    projects: List[Tuple[str, str, Optional[str]]] = (),
    education_items: List[str] = (),
    photo_bytes: Optional[bytes] = None,
    rtl_mode: bool = False,
    sections_left: List[Dict[str, Any]] | None = None,
    sections_right: List[Dict[str, Any]] | None = None,
) -> bytes:
    sections_left = sections_left or []
    sections_right = sections_right or []

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    W, H = A4

    margin = 16 * mm
    gutter = 8 * mm
    left_w = 0.40 * (W - 2 * margin - gutter)
    right_w = 0.60 * (W - 2 * margin - gutter)
    left_x = margin
    right_x = margin + left_w + gutter
    y_top = H - margin

    # بطاقة العمود الأيسر
    CARD_TOP, CARD_W, CARD_H, CARD_X, CARD_Y = y_top, left_w, H - 2*margin, left_x, margin
    draw_round_rect(c, CARD_X, CARD_Y, CARD_W, CARD_H)
    inner_x = CARD_X + CARD_PAD
    inner_w = CARD_W - 2*CARD_PAD
    cursor  = CARD_TOP - CARD_PAD

    # صورة دائرية (إن وُجدت)
    if photo_bytes:
        try:
            img = ImageReader(BytesIO(photo_bytes))
            max_d = 42*mm; d = min(inner_w, max_d); r = d/2.0
            cx = inner_x + inner_w/2.0; cy = cursor - r
            ix = cx - r; iy = cy - r
            c.saveState(); p = c.beginPath(); p.circle(cx, cy, r); c.clipPath(p, stroke=0, fill=0)
            c.drawImage(img, ix, iy, width=d, height=d, preserveAspectRatio=True, mask="auto")
            c.restoreState()
            c.setStrokeColor(LEFT_BORDER); c.setLineWidth(1); c.circle(cx, cy, r)
            cursor = iy - 6*mm
        except Exception:
            pass

    # محتوى العمود الأيسر الأساسي
    cursor = draw_left_column(
        c, name=name, location=location, phone=phone, email=email,
        github=github, linkedin=linkedin, birthdate=birthdate,
        skills=list(skills), languages=list(languages),
        inner_x=inner_x, inner_w=inner_w, cursor=cursor,
    )

    # أقسام إضافية يسار
    cursor = draw_left_extra_sections(c, inner_x, inner_w, cursor, sections_left)

    # العمود الأيمن
    yR = y_top - GAP_AFTER_HEADING
    yR = draw_right_extra_sections(c, right_x, right_w, yR, sections_right)
    yR = draw_projects(c, right_x, right_w, yR, list(projects), rtl_mode)
    yR = draw_education(c, right_x, right_w, yR, list(education_items))

    c.showPage(); c.save()
    out = buffer.getvalue(); buffer.close()
    return out
