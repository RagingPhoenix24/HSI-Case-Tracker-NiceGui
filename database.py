import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any
from models import CaseDetail, Client, Person, Task, CourtDate, DiscoveryLink, CaseFile
from config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cases table (simple list view data)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            client TEXT,
            subject_target TEXT,
            case_type TEXT,
            status TEXT,
            priority TEXT,
            assignee TEXT,
            date_opened TEXT,
            due_date TEXT,
            notes TEXT,
            case_number TEXT
        )
    """)
    
    # Case details stored as JSON for simplicity (full fidelity to your original structure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS case_details (
            case_id TEXT PRIMARY KEY,
            details_json TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_case(case_data: Dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO cases 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_data["Case_ID"],
        case_data["Client"],
        case_data["Subject_Target"],
        case_data["Case_Type"],
        case_data["Status"],
        case_data["Priority"],
        case_data["Assignee"],
        case_data["Date_Opened"],
        case_data["Due_Date"],
        case_data["Notes"],
        case_data["Case_Number"]
    ))
    conn.commit()
    conn.close()

def save_case_details(case_id: str, details: Dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO case_details (case_id, details_json)
        VALUES (?, ?)
    """, (case_id, json.dumps(details)))
    conn.commit()
    conn.close()

def get_all_cases() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY date_opened DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_case_details(case_id: str) -> Dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT details_json FROM case_details WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["details_json"])
    return None

def delete_case(case_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM case_details WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()

# Initialize on import
init_db()
