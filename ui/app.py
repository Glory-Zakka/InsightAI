"""Main NiceGUI application — layout and wiring."""
import sys
import os
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nicegui import ui

from config import APP_NAME, APP_TAGLINE
from ui.styles import get_css
from ui.handlers import handle_upload, toggle_run_btn, run_analysis, send_message, reset_app


class AppState:
    raw_df = None
    cleaned_df = None
    file_name = ""
    data_min = None
    data_max = None
    last_kpi = None
    last_event_log = None
    last_raw_events = None
    last_filtered = None
    last_narrative = ""
    last_start = None
    last_end = None
    chat_history = []


state = AppState()


@ui.page("/")
def main_page():
    ui.add_head_html(get_css())

    ui_elements = {}

    # ── Navbar ────────────────────────────────────────────
    with ui.header().classes("navbar"):
        with ui.row().classes("navbar-inner"):
            ui.html(
                f"<div class='navbar-brand'>"
                f"<span class='logo-icon'>⚡</span>"
                f"<div>"
                f"<div class='navbar-title'>{APP_NAME}</div>"
                f"<div class='navbar-subtitle'>{APP_TAGLINE}</div>"
                "</div>"
                "</div>"
            )
            ui.space()
            with ui.row().classes("navbar-right"):
                ui.html("<span class='status-dot online'></span>")
                ui.label("MVP Trial").classes("badge-trial")

    # ── Sidebar ───────────────────────────────────────────
    def scroll_to(target_id):
        ui.run_javascript(f"document.getElementById('{target_id}').scrollIntoView()")

    with ui.left_drawer().classes("sidebar"):
        nav_items = [
            ("Dashboard", "upload-section"),
            ("Upload Data", "upload-section"),
            ("Analytics", "analytics-section"),
            ("Ask AI", "chat-section"),
            ("Reports", "reports-section"),
        ]
        for label, target_id in nav_items:
            ui.button(label, on_click=lambda target_id=target_id: scroll_to(target_id)).props(
                "flat align=left"
            ).classes("nav-item")

        ui.space()
        with ui.column().classes("sidebar-footer"):
            ui.label("v1.0 MVP").classes("sidebar-version")
            ui.label("Free Trial Active").classes("sidebar-trial-text")

    # ── Main Content ──────────────────────────────────────
    with ui.column().classes("main-content"):

        # ════ UPLOAD CARD ══════════════════════════════════
        with ui.element("div").props('id="upload-section"'):
            with ui.card().classes("upload-card w-full"):
                ui.html("<div class='card-header'>📁 Upload Workbook</div>")

                async def on_upload(e):
                    await handle_upload(e, state, ui_elements)

                ui.upload(
                    on_upload=on_upload,
                    auto_upload=True,
                    multiple=False,
                ).props('accept=".xlsx,.xls,.csv"').classes("upload-zone")

                ui_elements["upload_status"] = ui.label("").classes("status-badge")

                ui.button(
                    "New Upload / Reset",
                    on_click=lambda _: reset_app(state, ui_elements)
                ).classes("btn-reset")

        # ════ DATE RANGE CARD ══════════════════════════════
        with ui.element("div").props('id="date-section"'):
            date_card = ui.card().classes("filter-card w-full")
            date_card.set_visibility(False)
            ui_elements["date_card"] = date_card

            with date_card:
                ui.html("<div class='card-header'>📅 Select Date Range</div>")

                with ui.row().classes("date-row"):
                    start_picker = ui.date().props('label="Start Date"').classes("date-picker")
                    end_picker = ui.date().props('label="End Date"').classes("date-picker")
                    ui_elements["start_picker"] = start_picker
                    ui_elements["end_picker"] = end_picker

                    ui.space()

                    run_btn = ui.button(
                        "Run Analysis",
                        on_click=lambda _: run_analysis(state, ui_elements)
                    ).classes("btn-run")
                    run_btn.set_visibility(False)
                    ui_elements["run_btn"] = run_btn

                start_picker.on("update:model-value", lambda _: toggle_run_btn(state, ui_elements))
                end_picker.on("update:model-value", lambda _: toggle_run_btn(state, ui_elements))

        # ════ RESULTS SECTION ══════════════════════════════
        results_section = ui.column().classes("w-full results-section")
        results_section.set_visibility(False)
        ui_elements["results_section"] = results_section

        with results_section:

            with ui.element("div").props('id="analytics-section"'):
                ui.html("<div class='page-title'>Analytics Dashboard</div>")
                ui.html("<div class='page-subtitle'>Key Performance Indicators</div>")

                ui_elements["kpi_container"] = ui.row().classes("kpi-grid w-full")
                ui_elements["narrative_box"] = ui.html("")

            with ui.element("div").props('id="reports-section"'):
                with ui.card().classes("chart-card w-full"):
                    ui.html("<div class='card-header'>📈 Load Profile Chart</div>")
                    ui_elements["chart_container"] = ui.column().classes("w-full")

                with ui.card().classes("table-card w-full"):
                    ui.html("<div class='card-header'>📋 Event Log</div>")
                    ui_elements["table_container"] = ui.column().classes("w-full")

            # ════ CHAT SECTION ══════════════════════════════
            with ui.element("div").props('id="chat-section"'):
                with ui.card().classes("chat-card w-full"):
                    ui.html("<div class='card-header'>💬 Ask InsightAI</div>")
                    ui.html("<div class='card-subtitle'>Ask questions about your data in plain English</div>")

                    # ── Suggested Questions ──────────────────
                    suggested_questions = [
                        "What do the KPIs tell you?",
                        "Why are there so many transitions?",
                        "How can we reduce DG runtime?",
                        "Which days had the most DG usage?",
                    ]

                    with ui.row().classes("suggested-questions"):
                        for q in suggested_questions:
                            def make_callback(question):
                                def callback(_):
                                    ui_elements["chat_input"].value = question
                                    asyncio.get_event_loop().create_task(
                                        send_message(state, ui_elements)
                                    )
                                return callback

                            ui.button(q, on_click=make_callback(q)).classes("suggestion-chip")

                    # ── Chat Messages Area ───────────────────
                    ui_elements["chat_messages"] = ui.column().classes("chat-messages")

                    # ── Chat Input ───────────────────────────
                    chat_input = ui.input(
                        placeholder="Ask about the data..."
                    ).classes("chat-input-full")
                    ui_elements["chat_input"] = chat_input

                    # Enter key sends the message
                    chat_input.on("keydown.enter", lambda _: send_message(state, ui_elements))

                    # ── Send & Clear Buttons ─────────────────
                    def on_send(_):
                        send_message(state, ui_elements)

                    def on_clear(_):
                        ui_elements["chat_messages"].clear()
                        state.chat_history = []

                    with ui.row().classes("chat-actions"):
                        ui.button("Send", on_click=on_send).classes("btn-send")
                        ui.button("Clear Chat", on_click=on_clear).classes("btn-clear")


ui.run(title=APP_NAME, port=8080, reload=True)