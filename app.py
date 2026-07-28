from nicegui import ui

from ui.layouts.main_layouts import create_main_layout

create_main_layout()

ui.run(
    title="InsightAI",
    favicon="📊",
    reload=True,
)