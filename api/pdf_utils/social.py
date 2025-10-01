# api/pdf_utils/social.py
import re

def extract_social_handle(kind: str, value: str):
    """
    يقبل هاندل صافي أو رابط كامل (مع/بدون https أو www).
    يعيد (display_handle, full_url) أو None.
    """
    v = (value or "").strip()
    if not v:
        return None

    # نظّف البادئات العامة
    v = re.sub(r'^(https?:\/\/)?(www\.)?', '', v, flags=re.I).strip()
    v = re.sub(r'^\s*(GitHub|LinkedIn)\s*:\s*', '', v, flags=re.I)  # لو المستخدم كتب "GitHub: TamerOnLine"
    v = v.strip()

    def clean_handle(h: str) -> str:
        h = h.strip()
        h = re.sub(r'^@', '', h)  # شيل @ لو موجودة
        return h

    if kind == "GitHub":
        # github.com/<handle> أو هاندل مباشرة
        m = re.search(r'^github\.com/([^/?#]+)', v, re.I)
        handle = clean_handle(m.group(1)) if m else clean_handle(v)
        if '/' in handle:
            handle = handle.split('/')[0]
        if handle:
            return handle, f"https://github.com/{handle}"
        return None

    if kind == "LinkedIn":
        # linkedin.com/in/<handle> أو /pub/
        m = re.search(r'^linkedin\.com/(?:in|pub)/([^/?#]+)', v, re.I)
        handle = clean_handle(m.group(1)) if m else clean_handle(v)
        if '/' in handle:
            handle = handle.split('/')[0]
        if handle:
            return handle, f"https://www.linkedin.com/in/{handle}"
        return None

    return None
