# pdf_utils/paths.py
from __future__ import annotations
from pathlib import Path
import os

def get_assets_root() -> Path:
    """
    يكتشف مجلد assets بجانب ملف الحزمة، مع دعم override عبر:
    PDF_UTILS_ASSETS=/path/to/assets
    """
    env = os.getenv("PDF_UTILS_ASSETS")
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p

    here = Path(__file__).resolve().parent
    cand = here / "assets"
    return cand if cand.exists() else here  # آخر الحلول: مجلد الحزمة نفسه

ASSETS = get_assets_root()
ICONS_DIR = ASSETS / "icons"
