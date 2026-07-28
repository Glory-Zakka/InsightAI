"""Central configuration. All tunable values live here."""
import os
from dotenv import load_dotenv

load_dotenv()

# -- Data Source --
EXPECTED_SHEET_NAME = "ITD BESS DG Interraction"

COLUMN_MAPPINGS = {
    "time_col": "Time",
    "load_col_original": "Total Plant Load (Including Plant Auxilliary + Kitchen)",
    "load_col_renamed": "LOAD (MW)",
    "source_col": "SOURCE",
    "reason1_col": "DG Transition Reason 1",
    "reason2_col": "DG Transition Reason 2",
}

REQUIRED_COLUMNS = [
    "Time",
    "Total Plant Load (Including Plant Auxilliary + Kitchen)",
    "SOURCE",
    "DG Transition Reason 1",
    "DG Transition Reason 2",
]

# -- Chart Defaults --
THRESHOLD_MW_DEFAULT = 2.15
BOUNDARY_MW_DEFAULT = 2.50

TRIGGER_COLORS = {
    "Load-Triggered": "#FFA500",
    "Distribution Grid Outage-Triggered": "#A94442",
    "Unplanned BESS-Related": "#003399",
    "Planned BESS-Related": "#ADD8E6",
    "TCN Grid Outage-Triggered": "#A020F0",
}

BESS_COLOR = "#00CC99"
UNKNOWN_COLOR = "#D3D3D3"
LOAD_LINE_COLOR = "#000000"
THRESHOLD_COLOR = "#FF0000"
BOUNDARY_COLOR = "#800000"

CHART_FIGSIZE = (24, 12)
CHART_DPI = 300
EXPORT_DPI = 600

# -- Branding --
APP_NAME = "Kudenda Energy Intelligence"
APP_TAGLINE = "BESS-DG Analytics & AI Assistant"
ACCENT_COLOR = "#00CC99"
DARK_HEADER = "#0F1B2D"
LIGHT_BG = "#F5F7FA"

# -- AI --
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AI_MODEL = "llama-3.3-70b-versatile"
AI_MAX_TOKENS = 2048
AI_TEMPERATURE = 0.4

# -- AI System Prompt --
AI_SYSTEM_PROMPT = """You are the AI assistant for Kudenda Energy Intelligence, a BESS/DG analytics platform.
You specialize in Battery Energy Storage Systems (BESS), Diesel Generators (DG), and power plant operations.

Your role:
- Analyze operational data from the BESS-DG interaction log
- Explain metrics like runtime percentages, energy throughput, transitions, and load patterns
- Identify anomalies, inefficiencies, and optimization opportunities
- Answer questions about the chart, event log, and KPIs
- Provide actionable engineering insights

Guidelines:
- Be concise and professional. Use bullet points for multi-part answers.
- When data context is provided, reference specific numbers from it.
- If no data has been uploaded yet, answer general BESS/DG questions but mention that uploading a file will give specific insights.
- If asked about something outside energy analytics, politely redirect to BESS/DG topics.
- Use units consistently (MW, MWh, hours, %).
- When discussing transitions, explain the trigger type and implications.
- Suggest optimizations when you see patterns like excessive transitions, long DG runtimes, or low BESS utilization.

Key domain context:
- The system monitors a plant that switches between BESS and DG based on load and grid conditions
- Threshold load is 2.15 MW, boundary load is 2.50 MW
- Transition triggers include: Load-Triggered, Distribution Grid Outage, TCN Grid Outage, Planned/Unplanned BESS-Related
- The goal is to maximize BESS runtime (cheaper, cleaner) and minimize DG runtime (expensive, high emissions)
"""

AI_MAX_EVENT_ROWS = 50