# frontend/app.py — نسخة كاملة مع حفظ الصورة Base64 داخل JSON + إرسالها إلى FastAPI عند التوليد
from __future__ import annotations

import base64
import json
import mimetypes
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
import streamlit as st

# ─────────────────────────────
# إعداد عام
# ─────────────────────────────
st.set_page_config(page_title="Resume PDF Builder", page_icon="🧾", layout="centered")
st.title("🧾 Resume PDF Builder (FastAPI + Streamlit)")
st.caption(
    "كل الحقول اختيارية. ارفع JSON (Browse files) → Load uploaded لتعبئة الحقول، أو عدّل واحفظ بـ Save.\n"
    "تستطيع أيضًا رفع صورة شخصية وسيتم حفظها داخل JSON كـ Base64."
)

# ─────────────────────────────
# مسارات المشروع
# ─────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[1]
PROFILES_DIR = BASE_DIR / "profiles"
OUTPUTS_DIR = BASE_DIR / "outputs"
PROFILES_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# ─────────────────────────────
# مفاتيح حالة الجلسة
# ─────────────────────────────
K = {
    "name": "f_name",
    "location": "f_location",
    "phone": "f_phone",
    "email": "f_email",
    "birthdate": "f_birthdate",
    "github": "f_github",
    "linkedin": "f_linkedin",
    "skills": "f_skills",
    "languages": "f_languages",
    "projects_text": "f_projects_text",
    "education_text": "f_education_text",
    "sections_left_text": "f_sections_left_text",
    "sections_right_text": "f_sections_right_text",
    "rtl_mode": "f_rtl_mode",
    "api_base": "f_api_base",
}

for key in K.values():
    if key not in st.session_state:
        st.session_state[key] = "" if key != K["rtl_mode"] else False

# حالة حفظ/عرض PDF
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "pdf_filename" not in st.session_state:
    st.session_state.pdf_filename = "resume.pdf"

# مفاتيح خاصة بالصورة
PHOTO_BYTES_KEY = "photo_bytes"
PHOTO_MIME_KEY = "photo_mime"
PHOTO_NAME_KEY = "photo_name"
if PHOTO_BYTES_KEY not in st.session_state:
    st.session_state[PHOTO_BYTES_KEY] = None
if PHOTO_MIME_KEY not in st.session_state:
    st.session_state[PHOTO_MIME_KEY] = None
if PHOTO_NAME_KEY not in st.session_state:
    st.session_state[PHOTO_NAME_KEY] = None

# ─────────────────────────────
# أدوات مساعدة
# ─────────────────────────────
def persist_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def guess_mime_from_name(name: Optional[str]) -> str:
    if not name:
        return "image/png"
    mt, _ = mimetypes.guess_type(name)
    return mt or "image/png"


def encode_photo_to_b64() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    b = st.session_state.get(PHOTO_BYTES_KEY)
    if not b:
        return None, None, None
    mime = st.session_state.get(PHOTO_MIME_KEY) or "image/png"
    name = st.session_state.get(PHOTO_NAME_KEY) or "photo.png"
    return base64.b64encode(b).decode("utf-8"), mime, name


def decode_photo_from_b64(photo_b64: str, photo_mime: Optional[str], photo_name: Optional[str]) -> None:
    try:
        raw = base64.b64decode(photo_b64)
        st.session_state[PHOTO_BYTES_KEY] = raw
        st.session_state[PHOTO_MIME_KEY] = photo_mime or "image/png"
        st.session_state[PHOTO_NAME_KEY] = photo_name or "photo.png"
    except Exception:
        st.session_state[PHOTO_BYTES_KEY] = None
        st.session_state[PHOTO_MIME_KEY] = None
        st.session_state[PHOTO_NAME_KEY] = None


def payload_from_form() -> Dict[str, Any]:
    """يبني Payload كامل لحفظه في JSON أو لإرساله للـ API (نصوص + الصورة Base64)."""
    p = {
        "name": st.session_state.get(K["name"], ""),
        "location": st.session_state.get(K["location"], ""),
        "phone": st.session_state.get(K["phone"], ""),
        "email": st.session_state.get(K["email"], ""),
        "github": st.session_state.get(K["github"], ""),
        "linkedin": st.session_state.get(K["linkedin"], ""),
        "birthdate": st.session_state.get(K["birthdate"], ""),
        "skills": [s.strip() for s in st.session_state.get(K["skills"], "").split(",") if s.strip()],
        "languages": [s.strip() for s in st.session_state.get(K["languages"], "").split(",") if s.strip()],
        "projects_text": st.session_state.get(K["projects_text"], ""),
        "education_text": st.session_state.get(K["education_text"], ""),
        "sections_left_text": st.session_state.get(K["sections_left_text"], ""),
        "sections_right_text": st.session_state.get(K["sections_right_text"], ""),
        "rtl_mode": bool(st.session_state.get(K["rtl_mode"], False)),
    }

    photo_b64, photo_mime, photo_name = encode_photo_to_b64()
    p["photo_b64"] = photo_b64
    p["photo_mime"] = photo_mime
    p["photo_name"] = photo_name
    return p


def apply_payload_to_form(p: Dict[str, Any]) -> None:
    st.session_state[K["name"]] = p.get("name", "")
    st.session_state[K["location"]] = p.get("location", "")
    st.session_state[K["phone"]] = p.get("phone", "")
    st.session_state[K["email"]] = p.get("email", "")
    st.session_state[K["birthdate"]] = p.get("birthdate", "")
    st.session_state[K["github"]] = p.get("github", "")
    st.session_state[K["linkedin"]] = p.get("linkedin", "")

    st.session_state[K["skills"]] = (
        ", ".join(p.get("skills", [])) if isinstance(p.get("skills"), list) else (p.get("skills", "") or "")
    )
    st.session_state[K["languages"]] = (
        ", ".join(p.get("languages", [])) if isinstance(p.get("languages"), list) else (p.get("languages", "") or "")
    )

    st.session_state[K["projects_text"]] = p.get("projects_text", "")
    st.session_state[K["education_text"]] = p.get("education_text", "")
    st.session_state[K["sections_left_text"]] = p.get("sections_left_text", "")
    st.session_state[K["sections_right_text"]] = p.get("sections_right_text", "")
    st.session_state[K["rtl_mode"]] = bool(p.get("rtl_mode", False))

    # أعد الصورة من Base64 إن وُجدت
    if p.get("photo_b64"):
        decode_photo_from_b64(p.get("photo_b64", ""), p.get("photo_mime"), p.get("photo_name"))
    else:
        st.session_state[PHOTO_BYTES_KEY] = None
        st.session_state[PHOTO_MIME_KEY] = None
        st.session_state[PHOTO_NAME_KEY] = None


# ─────────────────────────────
# الشريط الجانبي: Save / Load
# ─────────────────────────────
st.sidebar.header("💾 Save / Load (مع الصورة)")
preset_name = st.sidebar.text_input("Preset name", value="", placeholder="my-profile")

uploaded_json = st.sidebar.file_uploader("Browse JSON (Load)", type=["json"], key="json_loader")
btn_load_json = st.sidebar.button("Load uploaded")
if btn_load_json and uploaded_json is not None:
    try:
        content = json.loads(uploaded_json.read().decode("utf-8"))
        apply_payload_to_form(content)
        st.sidebar.success("تم التحميل بنجاح ✅")
    except Exception as e:
        st.sidebar.error(f"فشل التحميل: {e}")

btn_save = st.sidebar.button("Save current")
if btn_save:
    if not preset_name.strip():
        st.sidebar.warning("اكتب اسم Preset.")
    else:
        out = PROFILES_DIR / f"{preset_name.strip()}.json"
        payload = payload_from_form()
        persist_json_atomic(out, payload)
        st.sidebar.success(f"تم الحفظ: {out.name}")

# ─────────────────────────────
# نموذج الإدخال
# ─────────────────────────────
st.subheader("🧾 البيانات الأساسية")
colA, colB = st.columns(2)
with colA:
    st.text_input("الاسم", key=K["name"], placeholder="Tamer Hamad Faour")
    st.text_input("الهاتف", key=K["phone"], placeholder="+49 …")
    st.text_input("GitHub", key=K["github"], placeholder="TamerOnLine أو https://github.com/TamerOnLine")
    st.text_input("LinkedIn", key=K["linkedin"], placeholder="linkedin.com/in/…")
with colB:
    st.text_input("الموقع", key=K["location"], placeholder="Wuppertal, Deutschland")
    st.text_input("البريد الإلكتروني", key=K["email"], placeholder="you@example.com")
    st.text_input("تاريخ الميلاد", key=K["birthdate"], placeholder="01.01.1990")

st.text_input("المهارات (comma separated)", key=K["skills"], placeholder="FastAPI, PostgreSQL, Alembic, Docker")
st.text_input("اللغات (comma separated)", key=K["languages"], placeholder="العربية (لغة أم), Deutsch (B1), English (B2)")

st.subheader("📚 نصوص الأقسام (يمين/يسار)")
st.text_area("Projects (نص خام بصيغة البلوكات)", key=K["projects_text"], height=140, placeholder=(
    "NeuroServe\nFastAPI GPU-ready inference server…\nhttps://github.com/…\n\n"
    "RepoSmith\nBootstraps Python projects…\nhttps://github.com/…"
))
st.text_area("Education (بلوكات بسطر فارغ بين كل واحد)", key=K["education_text"], height=120, placeholder=(
    "AI (KI) Development – Mystro GmbH (Wuppertal)\n18.06.2024–30.12.2024 — 1000 UE\n\n"
    "Praktikum – Yolo GmbH (Wuppertal)\n17.02.2025–14.03.2025"
))

st.text_area("Left sections [Title] + - items", key=K["sections_left_text"], height=120, placeholder=(
    "[Zertifikate]\n- AWS Cloud Practitioner\n- Scrum Basics\n\n[Hobbys]\n- Laufen\n- Lesen"
))
st.text_area("Right sections [Title] + - items / paragraphs", key=K["sections_right_text"], height=120, placeholder=(
    "[Profil]\n- Backend-Entwickler mit Fokus auf FastAPI…\n- Erfahrung mit LLMs (RAG/Agenten)…"
))

st.checkbox("تفعيل RTL للنصوص اليمنى (العربية)", key=K["rtl_mode"])  # true/false

# ─────────────────────────────
# صورة شخصية (اختياري)
# ─────────────────────────────
st.subheader("📷 صورة شخصية (اختياري)")
up = st.file_uploader("ارفع صورة (PNG/JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=False, key="photo_uploader")

col1, col2 = st.columns([1, 3])
with col1:
    if up is not None:
        st.session_state[PHOTO_BYTES_KEY] = up.read()
        st.session_state[PHOTO_NAME_KEY] = up.name
        st.session_state[PHOTO_MIME_KEY] = up.type or guess_mime_from_name(up.name)
    if st.session_state.get(PHOTO_BYTES_KEY):
        st.image(st.session_state[PHOTO_BYTES_KEY], caption=st.session_state.get(PHOTO_NAME_KEY) or "photo", width=128)
    else:
        st.caption("لا توجد صورة حالياً.")

with col2:
    if st.session_state.get(PHOTO_BYTES_KEY):
        if st.button("🧹 إزالة الصورة"):
            st.session_state[PHOTO_BYTES_KEY] = None
            st.session_state[PHOTO_MIME_KEY] = None
            st.session_state[PHOTO_NAME_KEY] = None
            st.rerun()

# ─────────────────────────────
# استدعاء FastAPI (multipart)
# ─────────────────────────────
def call_generate_form(api_base: str, form_state: Dict[str, Any]) -> bytes:
    url = api_base.rstrip("/") + "/generate-form"

    # API يتوقع skills_text / languages_text كنصوص
    skills_text = ", ".join(form_state.get("skills", []))
    languages_text = ", ".join(form_state.get("languages", []))

    data = {
        "name": form_state.get("name", ""),
        "location": form_state.get("location", ""),
        "phone": form_state.get("phone", ""),
        "email": form_state.get("email", ""),
        "github": form_state.get("github", ""),
        "linkedin": form_state.get("linkedin", ""),
        "birthdate": form_state.get("birthdate", ""),
        "projects_text": form_state.get("projects_text", ""),
        "education_text": form_state.get("education_text", ""),
        "sections_left_text": form_state.get("sections_left_text", ""),
        "sections_right_text": form_state.get("sections_right_text", ""),
        "skills_text": skills_text,
        "languages_text": languages_text,
        "rtl_mode": "true" if form_state.get("rtl_mode") else "false",
    }

    files = None
    if st.session_state.get(PHOTO_BYTES_KEY):
        files = {
            "photo": (
                st.session_state.get(PHOTO_NAME_KEY) or "photo.png",
                st.session_state.get(PHOTO_BYTES_KEY),
                st.session_state.get(PHOTO_MIME_KEY) or "image/png",
            )
        }

    resp = requests.post(url, data=data, files=files, timeout=60)
    resp.raise_for_status()
    return resp.content

# ─────────────────────────────
# API base + أزرار التوليد/التحميل
# ─────────────────────────────
api_base = st.text_input("API Base", value=st.session_state.get(K["api_base"], "http://127.0.0.1:8000"))
st.session_state[K["api_base"]] = api_base

colG1, colG2 = st.columns([1, 1])
with colG1:
    if st.button("🧾 Generate PDF"):
        form_payload = payload_from_form()
        try:
            pdf_bytes = call_generate_form(api_base, form_payload)
            st.session_state.pdf_bytes = pdf_bytes
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.pdf_filename = f"resume_{ts}.pdf"
            st.success("تم إنشاء الـ PDF ✅")
        except Exception as e:
            st.error(f"فشل طلب التوليد: {e}")

with colG2:
    if st.session_state.get("pdf_bytes"):
        st.download_button(
            "⬇️ Download PDF",
            data=st.session_state.pdf_bytes,
            file_name=st.session_state.pdf_filename,
            mime="application/pdf",
        )

# زر تنزيل دائم أسفل الصفحة عند توافر PDF
if st.session_state.get("pdf_bytes"):
    st.download_button(
        "⬇️ Download PDF",
        data=st.session_state.pdf_bytes,
        file_name=st.session_state.pdf_filename,
        mime="application/pdf",
        key="download_bottom",
    )
