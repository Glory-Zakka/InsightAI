# ═══════════════════════════════════════════════════════════════════════
# ui/handlers.py
# ═══════════════════════════════════════════════════════════════════════
# Handler functions for UI events — upload, analysis, chat, and reset.
#
# ARCHITECTURE NOTE:
# All handler functions are SYNCHRONOUS. NiceGUI preserves the client
# context automatically for sync functions bound to on_click / on_keydown.
#
# For blocking work (analytics pipeline, Groq API call), we use
# Python's threading module to run tasks in a background thread.
# The `with client:` context manager re-enters the NiceGUI client
# context so we can safely update the UI when the thread finishes.
# ═══════════════════════════════════════════════════════════════════════

import sys
import os
import threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import markdown as md
from nicegui import ui

from engine.validation import validate_workbook, get_available_date_range
from engine.analytics import (
    load_data, filter_data, generate_analytics, generate_narrative_summary,
)
from engine.ai_chat import generate_response
from ui.renders import render_kpis, render_narrative, render_chart, render_event_log


# ═══════════════════════════════════════════════════════════════════════
# 1. FILE UPLOAD HANDLER
# ═══════════════════════════════════════════════════════════════════════

async def handle_upload(e, state, ui_elements):
    """Process an uploaded Excel file."""
    content = await e.file.read()
    state.file_name = e.file.name

    temp_path = f"/tmp/{state.file_name}"
    with open(temp_path, "wb") as f:
        f.write(content)

    is_valid, message, raw_df = validate_workbook(temp_path)

    if not is_valid:
        ui.notify(f"Validation failed: {message}", type="negative")
        ui_elements["upload_status"].set_text(f"Failed: {message}")
        ui_elements["upload_status"].classes(replace="status-badge error")
        return

    state.raw_df = raw_df
    state.cleaned_df = load_data(raw_df)
    state.data_min, state.data_max = get_available_date_range(state.cleaned_df)

    ui.notify(f"File loaded: {len(raw_df)} rows", type="positive")
    ui_elements["upload_status"].set_text(
        f"Loaded {state.file_name} - {len(raw_df)} rows"
    )
    ui_elements["upload_status"].classes(replace="status-badge success")

    ui_elements["date_card"].set_visibility(True)
    ui_elements["start_picker"].value = state.data_min.strftime("%Y-%m-%d")
    ui_elements["end_picker"].value = state.data_max.strftime("%Y-%m-%d")


# ═══════════════════════════════════════════════════════════════════════
# 2. DATE PICKER TOGGLE
# ═══════════════════════════════════════════════════════════════════════

def toggle_run_btn(state, ui_elements, _=None):
    """Show the 'Run Analysis' button once both date pickers have values."""
    if ui_elements["start_picker"].value and ui_elements["end_picker"].value:
        ui_elements["run_btn"].set_visibility(True)


# ═══════════════════════════════════════════════════════════════════════
# 3. RUN ANALYSIS
# ═══════════════════════════════════════════════════════════════════════

def run_analysis(state, ui_elements, _=None):
    """
    Filter data by date range and render all results.
    Uses threading to keep the WebSocket alive during heavy computation.
    """
    if state.cleaned_df is None:
        ui.notify("Upload a file first.", type="warning")
        return

    start_str = ui_elements["start_picker"].value
    end_str = ui_elements["end_picker"].value

    if not start_str or not end_str:
        ui.notify("Please select both dates.", type="warning")
        return

    start = pd.Timestamp(f"{start_str} 00:00:00")
    end = pd.Timestamp(f"{end_str} 23:59:59")

    if start > end:
        ui.notify("Start date must be before end date.", type="warning")
        return

    kpi_container = ui_elements["kpi_container"]
    chart_container = ui_elements["chart_container"]
    table_container = ui_elements["table_container"]
    narrative_box = ui_elements["narrative_box"]

    # ── Show results section and spinners immediately
    ui_elements["results_section"].set_visibility(True)

    kpi_container.clear()
    chart_container.clear()
    table_container.clear()
    narrative_box.content = ""

    with kpi_container:
        with ui.column().classes("analysis-spinner w-full"):
            ui.spinner(size="xl", color="primary")
            ui.label("Running analysis...").classes("analysis-spinner-text")

    with chart_container:
        with ui.column().classes("analysis-spinner w-full"):
            ui.spinner(size="lg", color="primary")
            ui.label("Generating chart...").classes("analysis-spinner-text")

    with table_container:
        with ui.column().classes("analysis-spinner w-full"):
            ui.spinner(size="lg", color="primary")
            ui.label("Building event log...").classes("analysis-spinner-text")

    client = ui.context.client

    def analysis_worker():
        """Runs in a background thread. Pure computation only."""
        try:
            filtered = filter_data(state.cleaned_df, start, end)

            if filtered.empty:
                result = {"error": "No data found in the selected date range."}
            else:
                filtered, event_log, duration, raw_events, kpi = generate_analytics(
                    filtered, start, end
                )
                result = {
                    "filtered": filtered,
                    "event_log": event_log,
                    "duration": duration,
                    "raw_events": raw_events,
                    "kpi": kpi,
                }
        except Exception as ex:
            import traceback
            traceback.print_exc()
            result = {"error": str(ex)}

        # ── Update UI back in the client context
        with client:
            if result.get("error"):
                kpi_container.clear()
                with kpi_container:
                    ui.label(f"Analysis error: {result['error']}").classes("analysis-spinner-text")
                ui.notify(f"Error: {result['error']}", type="negative")
            else:
                state.last_filtered = result["filtered"]
                state.last_event_log = result["event_log"]
                state.last_raw_events = result["raw_events"]
                state.last_kpi = result["kpi"]
                state.last_start = start
                state.last_end = end
                state.last_narrative = generate_narrative_summary(result["kpi"], start, end)

                render_kpis(kpi_container, result["kpi"])
                narrative_box.content = f"<div class='narrative-box'>{state.last_narrative}</div>"
                render_chart(chart_container, result["filtered"], result["raw_events"], result["duration"])
                render_event_log(table_container, result["event_log"])

                ui.notify("Analysis complete!", type="positive")

    threading.Thread(target=analysis_worker, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════
# 4. CHAT MESSAGE HANDLER
# ═══════════════════════════════════════════════════════════════════════

def send_message(state, ui_elements, _=None):
    """
    Handle a chat message from the user and get an AI response.
    Uses threading to keep the WebSocket alive during the Groq API call.
    """
    if not state.last_kpi:
        ui.notify("Run analysis first.", type="warning")
        return

    chat_input = ui_elements["chat_input"]
    chat_messages = ui_elements["chat_messages"]

    user_text = chat_input.value.strip()
    if not user_text:
        return

    # ── Show user message and loading dots immediately
    with chat_messages:
        ui.html(f"<div class='chat-bubble-user'>{user_text}</div>")
        loading = ui.html(
            "<div class='chat-loading'>"
            "<div class='typing-dots'><span></span><span></span><span></span></div>"
            "<span class='loading-text'>Analyzing...</span>"
            "</div>"
        )

    chat_input.value = ""

    chat_history = getattr(state, "chat_history", [])
    client = ui.context.client

    def chat_worker():
        """Runs in a background thread. Calls the Groq API."""
        try:
            response_text = generate_response(
                user_message=user_text,
                chat_history=chat_history,
                kpis=state.last_kpi,
                event_log_df=state.last_event_log,
            )
            result = {"response": response_text}
        except Exception as e:
            result = {"error": str(e)}

        # ── Update UI back in the client context
        with client:
            with chat_messages:
                loading.delete()

                if result.get("error"):
                    ui.html(
                        f"<div class='chat-bubble-ai'>Error: {result['error']}</div>"
                    )
                    ui.notify(f"AI Error: {result['error']}", type="negative")
                else:
                    if not hasattr(state, "chat_history"):
                        state.chat_history = []
                    state.chat_history.append(("user", user_text))
                    state.chat_history.append(("assistant", result["response"]))

                    html_response = md.markdown(
                        result["response"],
                        extensions=["extra", "nl2br"],
                    )
                    ui.html(f"<div class='chat-bubble-ai'>{html_response}</div>")

    threading.Thread(target=chat_worker, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════
# 5. RESET APP
# ═══════════════════════════════════════════════════════════════════════

def reset_app(state, ui_elements):
    """Reset the app to its initial state for a fresh upload."""
    state.raw_df = None
    state.cleaned_df = None
    state.file_name = ""
    state.data_min = None
    state.data_max = None
    state.last_kpi = None
    state.last_event_log = None
    state.last_raw_events = None
    state.last_filtered = None
    state.last_narrative = ""
    state.last_start = None
    state.last_end = None
    state.chat_history = []

    ui_elements["upload_status"].set_text("")
    ui_elements["upload_status"].classes(replace="status-badge")
    ui_elements["date_card"].set_visibility(False)
    ui_elements["run_btn"].set_visibility(False)
    ui_elements["results_section"].set_visibility(False)
    ui_elements["kpi_container"].clear()
    ui_elements["narrative_box"].content = ""
    ui_elements["chart_container"].clear()
    ui_elements["table_container"].clear()
    ui_elements["chat_messages"].clear()

    ui.notify("App reset. Upload a new file to begin.", type="info")