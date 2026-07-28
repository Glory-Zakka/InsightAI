"""Render functions for populating UI containers with analysis results."""
import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import base64
from nicegui import ui
from engine.charting import generate_chart, export_chart_to_bytes


def render_kpis(container, kpi):
    container.clear()
    with container:
        cards = [
            ("BESS Runtime", kpi["bess_runtime"], "green"),
            ("BESS Share", f"{kpi['bess_runtime_pct']:.1f}%", "green"),
            ("DG Runtime", kpi["dg_runtime"], "red"),
            ("DG Share", f"{kpi['dg_runtime_pct']:.1f}%", "red"),
            ("BESS Energy", f"{kpi['bess_energy_mwh']} MWh", "green"),
            ("DG Energy", f"{kpi['dg_energy_mwh']} MWh", "red"),
            ("Peak Load", f"{kpi['peak_load_mw']} MW", "blue"),
            ("Avg Load", f"{kpi['avg_load_mw']} MW", "blue"),
            ("Transitions", str(kpi["transitions"]), "blue"),
        ]
        for label, value, color_class in cards:
            with ui.card().classes(f"kpi-card kpi-{color_class}"):
                ui.html(f"<div class='kpi-label'>{label}</div>")
                ui.html(f"<div class='kpi-value'>{value}</div>")


def render_narrative(box, text):
    box.content = f"<div class='narrative-box'>{text}</div>"


def render_chart(container, df, raw_events, duration):
    container.clear()
    with container:
        fig = generate_chart(df, raw_events, duration)

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)

        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        ui.image(f"data:image/png;base64,{img_b64}").classes("chart-image")

        def do_download_chart():
            try:
                chart_bytes = export_chart_to_bytes(fig)
                # Write to a named temp file that persists until cleaned up
                tmp_path = "/tmp/bess_dg_chart_download.jpg"
                with open(tmp_path, "wb") as f:
                    f.write(chart_bytes)
                ui.download(tmp_path, "bess_dg_chart.jpg")
            except Exception as e:
                ui.notify(f"Download failed: {e}", type="negative")

        ui.button("Download Chart (HD)", on_click=do_download_chart).classes("btn-download")


def render_event_log(container, event_log_df):
    container.clear()
    with container:
        display_cols = [
            "Date", "BESS-DG Transitions", "Number of Transition",
            "Start Time", "End Time", "DG Duration (hh:mm:ss)",
            "EST. DG MWh", "Comments",
        ]
        available = [c for c in display_cols if c in event_log_df.columns]
        rows = event_log_df[available].to_dict("records")

        for row in rows:
            for key in row:
                val = row[key]
                if hasattr(val, "strftime"):
                    if key == "Date":
                        row[key] = val.strftime("%Y-%m-%d")
                    else:
                        row[key] = val.strftime("%H:%M:%S")
                elif isinstance(val, float):
                    row[key] = round(val, 3)

        ui.table(
            columns=[{"name": c, "label": c, "field": c} for c in available],
            rows=rows,
            pagination={"rowsPerPage": 10},
        ).classes("event-table w-full")

        def do_download_csv():
            try:
                tmp_path = "/tmp/event_log_download.csv"
                event_log_df.to_csv(tmp_path, index=False)
                ui.download(tmp_path, "event_log.csv")
            except Exception as e:
                ui.notify(f"Download failed: {e}", type="negative")

        ui.button("Download Event Log (CSV)", on_click=do_download_csv).classes("btn-download")