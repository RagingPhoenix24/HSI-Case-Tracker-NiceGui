from nicegui import ui, app
from config import PRIMARY_COLOR, ACCENT_COLOR, BACKGROUND_COLOR
import ui.case_list as case_list
import ui.case_detail as case_detail
from database import init_db

# Initialize database on startup
init_db()

# Global navigation state
current_case_id = None

def show_case_list():
    global current_case_id
    current_case_id = None
    ui.context.client.content.clear()
    with ui.left_drawer(value=True, fixed=True).classes("bg-[#1a3c6e] text-white"):
        ui.label("🚀 Hideaway Source Intelligence").classes("text-2xl font-bold mx-4 my-6")
        ui.button("Active Cases", on_click=lambda: case_list.show()).classes("w-full text-left").props("flat color=white")
        ui.button("Closed Cases", on_click=lambda: case_list.show(closed=True)).classes("w-full text-left").props("flat color=white")
        ui.button("New Case", on_click=lambda: case_list.create_new_case_dialog()).classes("w-full text-left").props("flat color=accent")
    case_list.show()

def show_case_detail(case_id: str):
    global current_case_id
    current_case_id = case_id
    ui.context.client.content.clear()
    with ui.left_drawer(value=True, fixed=True).classes("bg-[#1a3c6e] text-white"):
        ui.button("← Back to Cases", on_click=show_case_list).classes("w-full text-left").props("flat color=white")
        ui.label(f"Case: {case_id}").classes("text-xl font-bold mx-4 my-6")
    case_detail.show(case_id)

# Start the app
app.add_static_files('/uploads', 'uploads')
ui.run(title="HSI Case Tracker", port=8080, reload=True, dark=False, favicon="🚀")
