# pdf_utils/fonts.py
from __future__ import annotations
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path
import platform

from .paths import ASSETS

# RTL اختياري
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    AR_OK = True
except Exception:
    AR_OK = False

def rtl(txt: str) -> str:
    if not txt:
        return ""
    if AR_OK:
        return get_display(arabic_reshaper.reshape(txt))
    return txt

def register_font_safe(path: Path, name: str, fallback: str = "Helvetica") -> str:
    try:
        if path and path.is_file():
            pdfmetrics.registerFont(TTFont(name, str(path)))
            return name
    except Exception:
        pass
    return fallback

def find_arabic_font() -> tuple[str, Path|None]:
    """
    يحاول العثور على خط عربي مناسب:
    1) assets/NotoNaskhArabic-Regular.ttf
    2) مسارات نظام شائعة
    """
    # 1) من الأصول
    cand = ASSETS / "NotoNaskhArabic-Regular.ttf"
    if cand.exists():
        return "NotoNaskh", cand

    # 2) مسارات نظام
    sys = platform.system().lower()
    candidates: list[Path] = []
    if "windows" in sys:
        candidates += [Path(r"C:\Windows\Fonts\NotoNaskhArabic-Regular.ttf"),
                       Path(r"C:\Windows\Fonts\arial.ttf")]  # أقل جودة للعربي، مجرد طوق نجاة
    elif "linux" in sys:
        candidates += [
            Path("/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf"),
            Path("/usr/share/fonts/truetype/noto/NotoNaskhArabicUI-Regular.ttf"),
        ]
    elif "darwin" in sys:  # macOS
        candidates += [
            Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
            Path("/Library/Fonts/NotoNaskhArabic-Regular.ttf"),
        ]

    for p in candidates:
        if p.exists():
            return "NotoNaskh", p

    return "Helvetica", None  # fallback

def find_symbol_font() -> tuple[str, Path|None]:
    """
    خط للرموز/الإيموجي:
    - Windows: Segoe UI Symbols
    - Linux: Noto Sans Symbols2
    - macOS: Apple Symbols
    """
    sys = platform.system().lower()
    if "windows" in sys:
        p = Path(r"C:\Windows\Fonts\seguisym.ttf")
        return ("SegoeUISymbol", p if p.exists() else None)
    elif "linux" in sys:
        p = Path("/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf")
        return ("NotoSansSymbols2", p if p.exists() else None)
    elif "darwin" in sys:
        p = Path("/System/Library/Fonts/Supplemental/Apple Symbols.ttf")
        return ("AppleSymbols", p if p.exists() else None)
    return ("Helvetica", None)

# تسجيل الخط العربي
_AR_NAME, _AR_PATH = find_arabic_font()
AR_FONT = register_font_safe(_AR_PATH, _AR_NAME, fallback="Helvetica")

# تسجيل خط الرموز
_UI_NAME, _UI_PATH = find_symbol_font()
UI_FONT = register_font_safe(_UI_PATH, _UI_NAME, fallback="Helvetica")
