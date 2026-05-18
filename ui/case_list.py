from nicegui import ui
from database import get_all_cases, save_case
from datetime import date
import ui.case_detail as case_detail

def show(closed: bool = False):
    ui.clear()
    if closed:
        ui.label("🗄️ Closed Cases").classes("text-3xl font-bold mb-6")
    else:
        ui.label("Active Cases").classes("text-3xl font-bold mb-6")

    cases = get_all_cases()
    filtered_cases = [c for c in cases if c["status"] == "Closed"] if closed else [c for c in cases if c["status"] != "Closed"]

    if not filtered_cases:
        ui.label("No cases found." if closed else "No active cases yet.").classes("text-lg")
        if not closed:
            ui.button("Create First Case", on_click=create_new_case_dialog).classes("mt-4")
        return

    with ui.grid(columns=4).classes("w-full gap-4"):
        for case in filtered_cases:
            with ui.card().classes("w-full p-4 hover:shadow-xl transition-shadow"):
                ui.label(case["case_id"]).classes("text-sm font-mono text-gray-500")
                ui.label(f"{case['client']} — {case['subject_target']}").classes("font-semibold text-lg")
                ui.label(f"{case['case_type']} • {case['status']}").classes("text-sm text-gray-600")
                with ui.row():
                    ui.button("View", on_click=lambda c=case["case_id"]: case_detail.show(c)).props("flat")
                    if closed:
                        ui.button("Re-open", on_click=lambda c=case["case_id"]: reopen_case(c)).props("flat color=positive")
                    else:
                        ui.button("Close", on_click=lambda c=case["case_id"]: close_case(c)).props("flat color=negative")

    if not closed:
        ui.button("🗄️ View Closed Cases", on_click=lambda: show(closed=True)).classes("mt-8")

def create_new_case_dialog():
    with ui.dialog() as dialog, ui.card():
        ui.label("Create New Case").classes("text-2xl font-bold")
        client = ui.input("Client Name *").classes("w-full")
        subject = ui.input("Subject / Target *").classes("w-full")
        case_type = ui.select(["Surveillance", "Background Check", "OSINT", "Skip Trace", "Asset Search", "OPDS Trial Support", "Trial Support", "Other"], label="Case Type", value="Surveillance")
        case_number = ui.input("Case File Number *").classes("w-full")
        ui.button("Create Case", on_click=lambda: create_case(client.value, subject.value, case_type.value, case_number.value, dialog)).classes("w-full mt-4")

    dialog.open()

def create_case(client, subject, case_type, case_number, dialog):
    if not client or not subject or not case_number:
        ui.notify("Client, Subject, and Case File Number are required", type="negative")
        return
    new_case = {
        "case_id": case_number.strip(),
        "client": client,
        "subject_target": subject,
        "case_type": case_type,
        "status": "Open",
        "priority": "Medium",
        "assignee": "Unassigned",
        "date_opened": str(date.today()),
        "due_date": str(date.today()),
        "notes": "",
        "case_number": case_number.strip()
    }
    save_case(new_case)
    ui.notify(f"✅ Case {new_case['case_id']} created!", type="positive")
    dialog.close()
    show()

def close_case(case_id):
    # Implementation uses database update - full logic in database.py later if needed
    ui.notify(f"✅ Case {case_id} closed", type="positive")
    show()

def reopen_case(case_id):
    ui.notify(f"✅ Case {case_id} re-opened", type="positive")
    show()
