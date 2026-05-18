import os
from datetime import datetime
from pathlib import Path
from config import UPLOAD_FOLDER

def get_case_folder(case_id: str) -> Path:
    folder = UPLOAD_FOLDER / case_id
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_uploaded_file(case_id: str, uploaded_file, category: str) -> dict:
    case_folder = get_case_folder(case_id)
    file_path = case_folder / uploaded_file.name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    
    file_info = {
        "filename": uploaded_file.name,
        "category": category,
        "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "size": f"{uploaded_file.size / (1024*1024):.2f} MB",
        "path": str(file_path)
    }
    return file_info

def delete_file(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
