import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "cases.db"

# Ensure upload folder exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Professional color scheme
PRIMARY_COLOR = "#1a3c6e"
ACCENT_COLOR = "#00b4d8"
TEXT_COLOR = "#333333"
BACKGROUND_COLOR = "#f8f9fa"
