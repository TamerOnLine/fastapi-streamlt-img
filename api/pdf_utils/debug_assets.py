# pdf_utils/debug_assets.py
from .paths import ASSETS, ICONS_DIR
from .fonts import _AR_NAME, _AR_PATH, _UI_NAME, _UI_PATH

def print_assets_info():
    print("ASSETS:", ASSETS)
    print("ICONS_DIR:", ICONS_DIR)
    print("Arabic font:", _AR_NAME, _AR_PATH)
    print("Symbols font:", _UI_NAME, _UI_PATH)
