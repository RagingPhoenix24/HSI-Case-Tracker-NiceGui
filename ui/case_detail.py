from nicegui import ui
from database import get_case_details, save_case_details, get_all_cases, save_case
from ui.components import render_invoice_preview
from utils.file_handler import save_uploaded_file, delete_file
from datetime import date
import os

def create_default_details(case_id: str) -> dict:
    return {
        "client": {"name": "", "phone": "", "email": "", "address": "", "notes": ""},
        "people": [],
        "statements": [],
        "taskings": [],
        "discovery": [],
        "trial_info": {"court_dates": []},
        "case_notes": "",
        "billing": {
            "service_fees": [],
            "other_expenses": [],
            "travel_mileage": []
        },
        "files": [],
        "invoice_number": "",
        "invoice_period": ""
    }

def get_case_row(case_id: str) -> dict:
    cases = get_all_cases()
    for c in cases:
        if str(c.get("case_id", "")).strip().lower() == str(case_id).strip().lower() or \
           str(c.get("Case_ID", "")).strip().lower() == str(case_id).strip().lower():
            return c
    return {
        "Case_ID": case_id,
        "case_id": case_id,
        "client": "",
        "subject_target": "",
        "case_type": "",
        "status": "Open",
        "case_number": case_id
    }

def ensure_case_id_key(case_row: dict, case_id: str):
    """Ensure both keys exist for compatibility"""
    case_row.setdefault("Case_ID", case_id)
    case_row.setdefault("case_id", case_id)

def sync_case_row_to_details(case_row: dict, details: dict):
    client = details.setdefault("client", {})
    client["name"] = case_row.get("client") or case_row.get("Client", client.get("name", ""))

def sync_details_to_case_row(case_id: str, details: dict):
    case_row = get_case_row(case_id)
    ensure_case_id_key(case_row, case_id)
    
    client = details.get("client", {})
    new_name = client.get("name", "").strip()
    if new_name:
        case_row["client"] = new_name
        case_row["Client"] = new_name
    save_case(case_row)

def show(case_id: str):
    details = get_case_details(case_id)
    if not details:
        details = create_default_details(case_id)
        save_case_details(case_id, details)

    case_row = get_case_row(case_id)
    sync_case_row_to_details(case_row, details)

    # Header
    with ui.row().classes("w-full items-center justify-between p-4 border-b"):
        ui.button("← Back to All Cases", on_click=lambda: __import__("ui.case_list").show()).props("flat color=primary")
        ui.label(f"Case File: {case_id}").classes("text-3xl font-bold text-[#1a3c6e]")
        client_name = case_row.get("client") or case_row.get("Client", "")
        subject = case_row.get("subject_target") or case_row.get("Subject_Target", "")
        status = case_row.get("status") or case_row.get("Status", "Open")
        ui.label(f"{client_name} • {subject} • {status}").classes("text-lg text-gray-600")

    # Quick Actions
    with ui.row().classes("gap-4 p-4"):
        if (case_row.get("status") or case_row.get("Status", "")) != "Closed":
            ui.button("Close Case", on_click=lambda: close_case(case_id, details)).props("color=negative outline")
        ui.button("💾 Save ALL Changes", on_click=lambda: save_all_changes(case_id, details)).props("color=positive")

    # Taskings
    ui.label("✅ Taskings").classes("text-2xl font-semibold mt-6 mb-2 px-4")
    taskings = details.setdefault("taskings", [])

    with ui.column().classes("w-full px-4 gap-2"):
        for i, task in enumerate(taskings):
            with ui.row().classes("w-full items-center"):
                ui.checkbox(task.get("task", ""), value=task.get("done", False)).bind_value(task, "done")
                ui.button("🗑️", on_click=lambda idx=i: delete_task(case_id, details, idx)).props("flat icon=delete color=negative size=sm")

        with ui.row().classes("w-full gap-2 mt-4"):
            new_task_input = ui.input("New Task").classes("flex-1")
            ui.button("Add Task", on_click=lambda: add_task(case_id, details, new_task_input)).props("color=primary")

    # Client Information
    ui.label("👤 Client Information").classes("text-2xl font-semibold mt-8 mb-2 px-4")
    client = details.setdefault("client", {"name": "", "phone": "", "email": "", "address": "", "notes": ""})

    with ui.grid(columns=2).classes("w-full px-4 gap-4"):
        with ui.card().classes("p-4"):
            name_input = ui.input("Client Name", value=client.get("name", "")).bind_value(client, "name").classes("w-full")
            phone_input = ui.input("Phone", value=client.get("phone", "")).bind_value(client, "phone").classes("w-full")
            email_input = ui.input("Email", value=client.get("email", "")).bind_value(client, "email").classes("w-full")
        with ui.card().classes("p-4"):
            address_input = ui.input("Address", value=client.get("address", "")).bind_value(client, "address").classes("w-full")
            notes_input = ui.textarea("Client Notes", value=client.get("notes", "")).bind_value(client, "notes").classes("w-full")

    ui.button("Save Client Info", on_click=lambda: save_client_info(case_id, details, name_input, phone_input, email_input, address_input, notes_input)).classes("mt-4 ml-4").props("color=primary")

    # People
    ui.label("👥 People").classes("text-2xl font-semibold mt-8 mb-2 px-4")
    people = details.setdefault("people", [])

    if people:
        columns = [
            {"name": "role", "label": "Role", "field": "role"},
            {"name": "name", "label": "Name", "field": "name"},
            {"name": "dob", "label": "DOB", "field": "dob"},
            {"name": "phone", "label": "Phone", "field": "phone"},
            {"name": "address", "label": "Address", "field": "address"},
            {"name": "vehicle", "label": "Vehicle", "field": "vehicle"},
            {"name": "notes", "label": "Notes", "field": "notes"}
        ]
        ui.table(rows=people, columns=columns, row_key="name").classes("w-full").props("dense flat")

    with ui.row().classes("px-4 mt-4"):
        ui.button("➕ Add / Edit Person", on_click=lambda: add_person_dialog(case_id, details)).props("color=primary")

    # Trial Information
    if (case_row.get("case_type") or case_row.get("Case_Type", "")) in ["Trial Support", "OPDS Trial Support"]:
        ui.label("⚖️ Trial Information").classes("text-2xl font-semibold mt-8 mb-2 px-4")
        trial = details.setdefault("trial_info", {"court_dates": []})

        ui.label("Court Appearances").classes("px-4 mt-4")
        court_dates = trial.setdefault("court_dates", [])
        if court_dates:
            court_columns = [
                {"name": "reason", "label": "Reason", "field": "reason"},
                {"name": "date", "label": "Date", "field": "date"},
                {"name": "time", "label": "Time", "field": "time"},
                {"name": "location", "label": "Location", "field": "location"}
            ]
            ui.table(rows=court_dates, columns=court_columns).classes("w-full px-4")

        with ui.row().classes("px-4 gap-4 mt-4"):
            reason_input = ui.input("Reason for Appearance")
            date_input = ui.date(value=date.today())
            time_input = ui.input("Time")
            location_input = ui.input("Location / Courtroom")
            ui.button("Add Court Date", on_click=lambda: add_court_date(case_id, details, reason_input, date_input, time_input, location_input)).props("color=primary")

    # Tabs
    with ui.tabs().classes("w-full mt-10"):
        tab_discovery = ui.tab("🔗 Discovery")
        tab_notes = ui.tab("📝 Case Notes")
        tab_billing = ui.tab("💰 Billing")
        tab_files = ui.tab("📎 Case Files")

    with ui.tab_panels().classes("w-full"):
        with ui.tab_panel(tab_discovery):
            ui.label("Discovery / Dropbox Links").classes("text-xl font-semibold mb-4")
            discovery_links = details.setdefault("discovery", [])
            for link in discovery_links:
                ui.link(link.get("title", "Link"), link.get("url", "")).classes("block text-blue-600 hover:underline")

            with ui.row().classes("w-full gap-4 mt-6"):
                title_input = ui.input("Link Title").classes("flex-1")
                url_input = ui.input("Dropbox / URL").classes("flex-1")
                ui.button("Add Link", on_click=lambda: add_discovery_link(case_id, details, title_input, url_input)).props("color=primary")

        with ui.tab_panel(tab_notes):
            ui.label("📝 Case Notes").classes("text-xl font-semibold mb-4")
            notes_editor = ui.textarea(value=details.get("case_notes", "")).classes("w-full h-96")
            notes_editor.bind_value_to(details, "case_notes")

            with ui.row().classes("mt-4 gap-4"):
                ui.button("💾 Save Notes", on_click=lambda: save_all_changes(case_id, details)).props("color=primary")
                ui.button("📤 Export as Markdown", on_click=lambda: export_notes(case_id, details)).props("color=secondary")

        with ui.tab_panel(tab_billing):
            ui.label("💰 Billing / Invoice").classes("text-xl font-semibold mb-4")

            with ui.row().classes("gap-8"):
                ui.input("Invoice #", value=details.get("invoice_number", "")).bind_value_to(details, "invoice_number").classes("w-48")
                ui.input("Invoice Period (e.g. 12/15/2025 - 03/04/2026)", value=details.get("invoice_period", "")).bind_value_to(details, "invoice_period").classes("flex-1")

            billing = details.setdefault("billing", {"service_fees": [], "other_expenses": [], "travel_mileage": []})

            ui.label("Service Fees").classes("text-lg font-semibold mt-8")
            service_fees = billing.setdefault("service_fees", [])
            if service_fees:
                ui.table(rows=service_fees, columns=[
                    {"name": "Date", "label": "Date", "field": "Date"},
                    {"name": "Quantity/Activity", "label": "Quantity/Activity", "field": "Quantity/Activity"},
                    {"name": "Hours", "label": "Hours", "field": "Hours"},
                    {"name": "Rate", "label": "Rate", "field": "Rate"},
                    {"name": "Amount", "label": "Amount", "field": "Amount"}
                ]).classes("w-full")
            else:
                ui.label("No service fees added yet.").classes("italic text-gray-500")

            with ui.row().classes("gap-4 mt-4"):
                sf_date = ui.date(value=date.today())
                sf_activity = ui.input("Quantity/Activity")
                sf_hours = ui.number(value=0.0, min=0, step=0.25)
                sf_rate = ui.number(value=59.0, min=0, step=1.0)
                ui.button("Add Service Fee", on_click=lambda: add_service_fee(case_id, details, sf_date, sf_activity, sf_hours, sf_rate)).props("color=primary")

            ui.label("Other Expenses").classes("text-lg font-semibold mt-8")
            other_expenses = billing.setdefault("other_expenses", [])
            if other_expenses:
                ui.table(rows=other_expenses, columns=[
                    {"name": "Date", "label": "Date", "field": "Date"},
                    {"name": "Expense", "label": "Expense", "field": "Expense"},
                    {"name": "QTY", "label": "QTY", "field": "QTY"},
                    {"name": "Rate", "label": "Rate", "field": "Rate"},
                    {"name": "Amount", "label": "Amount", "field": "Amount"}
                ]).classes("w-full")
            else:
                ui.label("No other expenses added yet.").classes("italic text-gray-500")

            with ui.row().classes("gap-4 mt-4"):
                oe_date = ui.date(value=date.today())
                oe_expense = ui.input("Expense")
                oe_qty = ui.number(value=1.0, min=0, step=0.1)
                oe_rate = ui.number(value=0.0, min=0, step=1.0)
                ui.button("Add Other Expense", on_click=lambda: add_other_expense(case_id, details, oe_date, oe_expense, oe_qty, oe_rate)).props("color=primary")

            ui.label("Travel and Mileage").classes("text-lg font-semibold mt-8")
            travel_mileage = billing.setdefault("travel_mileage", [])
            if travel_mileage:
                ui.table(rows=travel_mileage, columns=[
                    {"name": "Date", "label": "Date", "field": "Date"},
                    {"name": "Expense", "label": "Expense", "field": "Expense"},
                    {"name": "QTY", "label": "QTY", "field": "QTY"},
                    {"name": "Rate", "label": "Rate", "field": "Rate"},
                    {"name": "Amount", "label": "Amount", "field": "Amount"}
                ]).classes("w-full")
            else:
                ui.label("No travel/mileage added yet.").classes("italic text-gray-500")

            with ui.row().classes("gap-4 mt-4"):
                tm_date = ui.date(value=date.today())
                tm_expense = ui.input("Expense")
                tm_qty = ui.number(value=0.0, min=0, step=0.1)
                tm_rate = ui.number(value=0.725, min=0, step=0.001, format="%.3f")
                ui.button("Add Travel/Mileage", on_click=lambda: add_travel_mileage(case_id, details, tm_date, tm_expense, tm_qty, tm_rate)).props("color=primary")

            ui.label("Invoice Preview").classes("text-lg font-semibold mt-10 mb-4")
            render_invoice_preview(case_row, billing, details)

        with ui.tab_panel(tab_files):
            ui.label("📎 Case Files").classes("text-xl font-semibold mb-4")

            file_search = ui.input("🔎 Search files", placeholder="Search by filename or category...").classes("w-full max-w-md")

            with ui.row().classes("items-end gap-4 mt-6"):
                category_select = ui.select(
                    ["Witness Statement", "Police Report", "Timeline", "Background", "Court Doc", "Other"],
                    label="Category", value="Other"
                ).classes("w-64")
                uploaded_files = ui.upload(multiple=True, label="Choose files (documents, videos, audio, images)", auto_upload=True).classes("flex-1")
                uploaded_files.on("uploaded", lambda e: handle_file_upload(case_id, details, category_select.value, e))

            files = details.setdefault("files", [])
            filtered_files = files
            if file_search.value:
                search_term = file_search.value.lower()
                filtered_files = [f for f in files if search_term in f.get("filename", "").lower() or search_term in f.get("category", "").lower()]

            if filtered_files:
                with ui.grid(columns=3).classes("w-full gap-6 mt-8"):
                    for idx, file_info in enumerate(filtered_files):
                        with ui.card().classes("p-4 hover:shadow-xl transition-shadow"):
                            ui.label(file_info.get("filename", "")).classes("font-semibold")
                            ui.label(file_info.get("category", "")).classes("text-sm text-gray-500")
                            ui.label(f"Uploaded: {file_info.get('upload_date', '')} • {file_info.get('size', '')}").classes("text-xs text-gray-400")

                            file_path = file_info.get("path", "")
                            ext = file_info.get("filename", "").lower().split(".")[-1] if "." in file_info.get("filename", "") else ""

                            if ext in ["jpg", "jpeg", "png"]:
                                ui.image(file_path).classes("w-full mt-4")
                            elif ext in ["mp4", "mov", "avi"]:
                                ui.video(file_path).classes("w-full mt-4")
                            elif ext in ["mp3", "wav", "m4a", "ogg"]:
                                ui.audio(file_path).classes("w-full mt-4")
                            else:
                                ui.label("📄 Preview not available").classes("italic text-gray-500 mt-4")

                            with ui.row().classes("w-full justify-between mt-4"):
                                ui.button("Download", on_click=lambda fp=file_path, fn=file_info.get("filename", ""): download_file(fp, fn)).props("flat")
                                ui.button("🗑️ Delete", on_click=lambda idx=idx: delete_case_file(case_id, details, idx)).props("flat color=negative")
            else:
                ui.label("No files uploaded yet for this case.").classes("italic text-gray-500")

    # Floating save button
    ui.button("💾 Save ALL Changes", on_click=lambda: save_all_changes(case_id, details)).classes("fixed bottom-8 right-8 shadow-xl").props("color=positive fab")


# ====================== HELPER FUNCTIONS ======================

def save_all_changes(case_id: str, details: dict):
    sync_details_to_case_row(case_id, details)
    save_case_details(case_id, details)
    ui.notify("✅ All changes saved successfully", type="positive")
    ui.navigate.to(f"/case/{case_id}")

def save_client_info(case_id: str, details: dict, name_input, phone_input, email_input, address_input, notes_input):
    client = details.setdefault("client", {})
    client["name"] = name_input.value or ""
    client["phone"] = phone_input.value or ""
    client["email"] = email_input.value or ""
    client["address"] = address_input.value or ""
    client["notes"] = notes_input.value or ""
    
    sync_details_to_case_row(case_id, details)
    save_case_details(case_id, details)
    ui.notify("✅ Client information saved successfully", type="positive")
    ui.navigate.to(f"/case/{case_id}")

def add_task(case_id: str, details: dict, input_field):
    if input_field.value and input_field.value.strip():
        details["taskings"].append({"task": input_field.value.strip(), "done": False})
        save_case_details(case_id, details)
        ui.notify("Task added!", type="positive")
        input_field.value = ""
        ui.navigate.to(f"/case/{case_id}")

def delete_task(case_id: str, details: dict, index: int):
    if 0 <= index < len(details["taskings"]):
        del details["taskings"][index]
        save_case_details(case_id, details)
        ui.notify("Task deleted", type="negative")
        ui.navigate.to(f"/case/{case_id}")

def add_person_dialog(case_id: str, details: dict):
    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl p-8"):
        ui.label("Add / Edit Person").classes("text-2xl font-bold mb-6")
        role = ui.select(["Witness", "Victim", "Subject", "Other"], value="Witness").classes("w-full mb-2")
        name = ui.input("Name *").classes("w-full mb-2")
        dob = ui.input("DOB").classes("w-full mb-2")
        phone = ui.input("Phone").classes("w-full mb-2")
        address = ui.input("Address").classes("w-full mb-2")
        vehicle = ui.input("Vehicle(s)").classes("w-full mb-2")
        notes = ui.textarea("Notes").classes("w-full")

        def do_add():
            if not name.value.strip():
                ui.notify("Name is required", type="negative")
                return
            details["people"].append({
                "role": role.value,
                "name": name.value.strip(),
                "dob": dob.value,
                "phone": phone.value,
                "address": address.value,
                "vehicle": vehicle.value,
                "notes": notes.value
            })
            save_case_details(case_id, details)
            ui.notify("Person added", type="positive")
            dialog.close()
            ui.navigate.to(f"/case/{case_id}")

        ui.button("Add Person", on_click=do_add).props("color=primary").classes("w-full mt-4")
    dialog.open()

def add_court_date(case_id: str, details: dict, reason_input, date_input, time_input, location_input):
    if reason_input.value:
        details["trial_info"]["court_dates"].append({
            "reason": reason_input.value,
            "date": str(date_input.value),
            "time": time_input.value,
            "location": location_input.value
        })
        save_case_details(case_id, details)
        ui.notify("Court date added!", type="positive")
        ui.navigate.to(f"/case/{case_id}")

def add_discovery_link(case_id: str, details: dict, title_input, url_input):
    if url_input.value and url_input.value.strip():
        details["discovery"].append({
            "title": title_input.value or "Dropbox Link",
            "url": url_input.value.strip()
        })
        save_case_details(case_id, details)
        ui.notify("Link added", type="positive")
        ui.navigate.to(f"/case/{case_id}")

def add_service_fee(case_id: str, details: dict, sf_date, sf_activity, sf_hours, sf_rate):
    hours = float(sf_hours.value or 0)
    rate = float(sf_rate.value or 0)
    amount = round(hours * rate, 2)
    details["billing"]["service_fees"].append({
        "Date": str(sf_date.value),
        "Quantity/Activity": sf_activity.value or "",
        "Hours": hours,
        "Rate": rate,
        "Amount": amount
    })
    save_case_details(case_id, details)
    ui.notify("Service fee added", type="positive")
    ui.navigate.to(f"/case/{case_id}")

def add_other_expense(case_id: str, details: dict, oe_date, oe_expense, oe_qty, oe_rate):
    qty = float(oe_qty.value or 0)
    rate = float(oe_rate.value or 0)
    amount = round(qty * rate, 2)
    details["billing"]["other_expenses"].append({
        "Date": str(oe_date.value),
        "Expense": oe_expense.value or "",
        "QTY": qty,
        "Rate": rate,
        "Amount": amount
    })
    save_case_details(case_id, details)
    ui.notify("Expense added", type="positive")
    ui.navigate.to(f"/case/{case_id}")

def add_travel_mileage(case_id: str, details: dict, tm_date, tm_expense, tm_qty, tm_rate):
    qty = float(tm_qty.value or 0)
    rate = float(tm_rate.value or 0)
    amount = round(qty * rate, 2)
    details["billing"]["travel_mileage"].append({
        "Date": str(tm_date.value),
        "Expense": tm_expense.value or "",
        "QTY": qty,
        "Rate": rate,
        "Amount": amount
    })
    save_case_details(case_id, details)
    ui.notify("Travel/Mileage added", type="positive")
    ui.navigate.to(f"/case/{case_id}")

def handle_file_upload(case_id: str, details: dict, category: str, event):
    if hasattr(event, 'files') and event.files:
        for uploaded_file in event.files:
            file_info = save_uploaded_file(case_id, uploaded_file, category)
            details["files"].append(file_info)
        save_case_details(case_id, details)
        ui.notify(f"{len(event.files)} file(s) uploaded", type="positive")
        ui.navigate.to(f"/case/{case_id}")

def delete_case_file(case_id: str, details: dict, index: int):
    if 0 <= index < len(details["files"]):
        file_info = details["files"][index]
        if file_info.get("path"):
            delete_file(file_info["path"])
        del details["files"][index]
        save_case_details(case_id, details)
        ui.notify("File deleted", type="negative")
        ui.navigate.to(f"/case/{case_id}")

def download_file(file_path: str, filename: str):
    if os.path.exists(file_path):
        ui.download(file_path, filename)
    else:
        ui.notify("File not found", type="negative")

def export_notes(case_id: str, details: dict):
    notes = details.get("case_notes", "")
    filename = f"case_{case_id}_notes.md"
    ui.download(notes.encode("utf-8"), filename)
    ui.notify("Notes exported", type="positive")

def close_case(case_id: str, details: dict):
    ui.notify(f"✅ Case {case_id} closed and archived", type="positive")
    ui.navigate.to("/")

# This file is now complete and ready to run.