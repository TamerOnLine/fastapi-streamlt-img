# pdf_utils/resources.py
from importlib import resources
from pathlib import Path
import tempfile
import shutil

def extract_resource(package: str, resource: str) -> Path:
    """
    ينسخ مورد مضمّن بالحزمة إلى ملف مؤقت ويعيد مساره.
    مثال: extract_resource("pdf_utils.assets", "NotoNaskhArabic-Regular.ttf")
    """
    with resources.files(package).joinpath(resource).open("rb") as src:
        tmpdir = Path(tempfile.mkdtemp(prefix="pdf_assets_"))
        out = tmpdir / Path(resource).name
        with out.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return out
