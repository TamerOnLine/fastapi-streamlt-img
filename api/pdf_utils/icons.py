# api/pdf_utils/icons.py
from __future__ import annotations
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from .text import wrap_text

from .paths import ICONS_DIR
from .fonts import UI_FONT  # لو كنت لا تستخدمه، يمكن حذفه
from .config import (
    LEFT_TEXT_FONT, LEFT_TEXT_FONT_BOLD, LEFT_TEXT_IS_BOLD,
    LEFT_TEXT_SIZE, LEFT_LINE_GAP,
    ICON_SIZE, ICON_PAD_X, ICON_TEXT_DY, ICON_VALIGN,
    HEADING_COLOR, TEXT_SIZE, LEADING_BODY,
)
from .social import extract_social_handle  # مهم لاستخدام روابط GitHub/LinkedIn


def icon_path(name: str) -> Path | None:
    p = ICONS_DIR / name
    return p if p.exists() else None

ICON_PATHS: dict[str, Path | None] = {
    "Ort":          icon_path("pin.png"),
    "Telefon":      icon_path("phone.png"),
    "E-Mail":       icon_path("mail.png"),
    "Geburtsdatum": icon_path("cake.png"),
    "GitHub":       icon_path("github.png"),
    "LinkedIn":     icon_path("linkedin.png"),
}

def draw_icon_line(
    c: canvas.Canvas,
    x: float, y: float,
    icon: Path | None,
    value: str,
    *,
    icon_w: float = ICON_SIZE,
    icon_h: float = ICON_SIZE,
    pad_x: float = ICON_PAD_X,
    size: int = LEFT_TEXT_SIZE,
    valign: str = ICON_VALIGN,
    text_dy: float = ICON_TEXT_DY,
    line_gap: int | None = None,
    max_w: float | None = None,
    halign: str = "left",
    container_w: float | None = None,
    link_url: str | None = None,
) -> float:
    value_font = LEFT_TEXT_FONT_BOLD if LEFT_TEXT_IS_BOLD else LEFT_TEXT_FONT
    asc = pdfmetrics.getAscent(value_font) / 1000.0 * size
    dsc = abs(pdfmetrics.getDescent(value_font)) / 1000.0 * size

    # أيقونة (أو نقطة احتياطية)
    if icon and icon.is_file():
        try:
            img = ImageReader(str(icon))
            c.drawImage(img, x, y - icon_h, width=icon_w, height=icon_h, mask="auto")
        except Exception:
            c.setFont(value_font, size + 2); c.drawString(x, y, "•")
    else:
        c.setFont(value_font, size + 2); c.drawString(x, y, "•")

    # حساب موضع النص
    text_x = x + icon_w + pad_x
    half_text = (asc - dsc) / 2.0
    baseline = y - (icon_h / 2.0 - half_text)  # محاذاة وسط
    text_y = baseline + text_dy

    c.setFont(value_font, size)
    c.setFillColor(colors.black)

    # لو في max_w → لف النص داخل المساحة المتاحة
    if max_w is not None:
        avail_w = max_w - (text_x - x)
        if avail_w < 20:  # حماية من عرض ضيق جدًا
            avail_w = max(20, avail_w)

        lines = wrap_text(value, value_font, size, avail_w)
        cur_y = text_y
        first_line_twidth = None

        for i, ln in enumerate(lines):
            c.drawString(text_x, cur_y, ln)
            if i == 0 and link_url:
                tw = pdfmetrics.stringWidth(ln, value_font, size)
                first_line_twidth = tw
                # اجعل منطقة الرابط على السطر الأول فقط
                c.linkURL(
                    link_url,
                    (text_x, cur_y - dsc, text_x + tw, cur_y + asc * 0.2),
                    relative=0,
                    thickness=0
                )
            cur_y -= (line_gap if line_gap is not None else LEADING_BODY)

        block_h = (text_y - cur_y) + (line_gap if line_gap is not None else LEADING_BODY)
        used_h = max(icon_h, block_h)
        # مسافة آمنة دائماً: أكبر من قيمة التباعد المطلوبة وأكبر من ارتفاع البلوك
        gap = max((line_gap or LEADING_BODY), used_h + 2)
        return y - gap

    # بدون التفاف (سطر واحد)
    c.drawString(text_x, text_y, value)
    if link_url:
        tw = pdfmetrics.stringWidth(value, value_font, size)
        c.linkURL(link_url, (text_x, text_y - dsc, text_x + tw, text_y + asc * 0.2), relative=0, thickness=0)

    used_h = max(icon_h, asc + dsc)
    gap = max((line_gap or LEADING_BODY), used_h + 2)
    return y - gap


def info_line(
    c: canvas.Canvas,
    x: float,
    y: float,
    key: str,               # "GitHub" | "LinkedIn" | "Ort" | ...
    value: str,
    max_w: float,
    align_h: str = "left",
    line_gap: int = LEFT_LINE_GAP,
    size: int = LEFT_TEXT_SIZE,
) -> float:
    """
    يرسم سطر بمعلومات وبأيقونة تلقائيًا، ويفعّل رابط GitHub/LinkedIn إن وُجد.
    يعيد y الجديد بعد السطر.
    """
    if not value:
        return y

    display = (value or "").strip()
    link = None

    # 1) محاولة الاستخراج القياسية
    if key in ("GitHub", "LinkedIn"):
        got = extract_social_handle(key, display)
        if got:
            display, link = got  # display=handle, link=full URL
        else:
            # 2) Fallback: ابنِ الرابط من الهاندل/الرابط الخام
            v = display

            # أزل بادئات شائعة لو المستخدم كتب "GitHub: TamerOnLine" أو لصق "https://www..."
            lowers = v.lower()
            for pref in ("github:", "linkedin:"):
                if lowers.startswith(pref):
                    v = v[len(pref):].strip()
                    break
            if v.startswith(("http://", "https://")):
                v = v.split("://", 1)[1]
            if v.startswith("www."):
                v = v[4:]
            v = v.lstrip("@").strip()

            # إن كان URL اختصره إلى الهاندل
            if key == "GitHub":
                # github.com/<handle>
                if v.lower().startswith("github.com/"):
                    v = v.split("/", 1)[1]
                v = v.split("/")[0]  # احذف أي مسار لاحق
                display = v
                link = f"https://github.com/{v}" if v else None

            elif key == "LinkedIn":
                # linkedin.com/in/<handle> أو /pub/
                if v.lower().startswith("linkedin.com/"):
                    parts = v.split("/", 2)
                    if len(parts) >= 3:
                        v = parts[2]
                v = v.split("/")[0]
                display = v
                link = f"https://www.linkedin.com/in/{v}" if v else None

    # أيقونة
    icon = ICON_PATHS.get(key)

    # رسم السطر (سيضيف الرابط إذا link != None)
    return draw_icon_line(
        c=c, x=x, y=y, icon=icon, value=display,
        icon_w=ICON_SIZE, icon_h=ICON_SIZE,
        pad_x=ICON_PAD_X, size=size,
        valign=ICON_VALIGN, text_dy=ICON_TEXT_DY,
        line_gap=line_gap, max_w=max_w,
        halign=align_h, container_w=max_w,
        link_url=link,
    )
