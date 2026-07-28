import os
from nicegui import ui

from ui.layouts.main_layouts import create_main_layout

create_main_layout()

port = int(os.environ.get("PORT", 8080))

ui.run(
    title="InsightAI",
    favicon="📊",
    port=port,
    reload=False,
)