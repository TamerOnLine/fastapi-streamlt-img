# demo_make_pdf.py
from api.pdf_utils import build_resume_pdf
from pathlib import Path

pdf = build_resume_pdf(
    name="Tamer Hamad Faour",
    location="Wuppertal, Deutschland",
    phone="+49 176 000000",
    email="tamer@example.com",
    github="TamerOnLine",                   # يتحول لرابط clickable
    linkedin="linkedin.com/in/tameronline", # يتحول لرابط clickable
    birthdate="01.01.1990",
    skills=[
        "FastAPI, PostgreSQL, Alembic",
        "LLMs (RAG/Agents), Docker, CI/CD"
    ],
    languages=["العربية (لغة أم)", "Deutsch (B1)", "English (B2)"],
    projects=[
        ("NeuroServe",
         "خادم استدلال FastAPI جاهز لـ GPU يدعم Whisper وBART وCLIP…",
         "https://github.com/..."),
    ],
    education_items=[
        "AI (KI) Development – Mystro GmbH (Wuppertal)\n18.06.2024–30.12.2024 — 1000 UE",
    ],
    rtl_mode=True,  # يفعّل اتجاه RTL في النصوص اليمنى عند الحاجة
)

out = Path("outputs/test_assets_ok.pdf")
out.parent.mkdir(exist_ok=True)
out.write_bytes(pdf)
print("OK ->", out)
