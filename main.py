from nicegui import ui, app
from config import PRIMARY_COLOR, ACCENT_COLOR
import ui.case_list as case_list
import ui.case_detail as case_detail
from database import init_db

# Initialize database
init_db()

# NiceGUI pages for clean navigation
@ui.page('/')
def home():
    case_list.show()

@ui.page('/case/{case_id}')
def case_detail_page(case_id: str):
    case_detail.show(case_id)

# Global static files for uploaded documents/images/videos
app.add_static_files('/uploads', 'uploads')

# Start the app (professional window title, auto-reload for development)
ui.run(
    title="HSI Case Tracker — Hideaway Source Intelligence",
    port=8080,
    reload=True,
    dark=False,
    favicon="🚀",
    storage_secret="hideaway-case-tracker-secret-key-2026"
)
