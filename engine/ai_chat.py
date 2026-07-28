"""Groq AI chat integration for BESS/DG analytics."""
import pandas as pd
from groq import Groq
from config import (
    GROQ_API_KEY,
    AI_MODEL,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    AI_SYSTEM_PROMPT,
    AI_MAX_EVENT_ROWS,
)


def init_client():
    """Initialize and return a Groq client."""
    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY not found. Add it to your .env file."
        )
    return Groq(api_key=GROQ_API_KEY)


def build_data_context(kpis=None, event_log_df=None):
    """Build a text summary of current analysis data for the AI."""
    parts = []

    if kpis:
        parts.append("CURRENT ANALYSIS KPIs:")
        parts.append(f"- BESS Runtime: {kpis['bess_runtime']}")
        parts.append(f"- BESS Share: {kpis['bess_runtime_pct']:.1f}%")
        parts.append(f"- DG Runtime: {kpis['dg_runtime']}")
        parts.append(f"- DG Share: {kpis['dg_runtime_pct']:.1f}%")
        parts.append(f"- BESS Energy: {kpis['bess_energy_mwh']} MWh")
        parts.append(f"- DG Energy: {kpis['dg_energy_mwh']} MWh")
        parts.append(f"- Peak Load: {kpis['peak_load_mw']} MW")
        parts.append(f"- Avg Load: {kpis['avg_load_mw']} MW")
        parts.append(f"- Total Transitions: {kpis['transitions']}")
        parts.append("")

    if event_log_df is not None and not event_log_df.empty:
        parts.append(f"EVENT LOG (showing up to {AI_MAX_EVENT_ROWS} most recent rows):")
        display_cols = [
            "Date", "BESS-DG Transitions", "Number of Transition",
            "Start Time", "End Time", "DG Duration (hh:mm:ss)",
            "EST. DG MWh", "Comments",
        ]
        available = [c for c in display_cols if c in event_log_df.columns]
        recent = event_log_df[available].tail(AI_MAX_EVENT_ROWS).copy()
        for col in recent.columns:
            if recent[col].dtype == "object":
                recent[col] = recent[col].astype(str)
        parts.append(recent.to_string(index=False))
        parts.append("")

    if not parts:
        parts.append(
            "No data has been uploaded yet. "
            "Answer general BESS/DG questions and encourage the user to upload a file."
        )

    return "\n".join(parts)


def generate_response(user_message, chat_history, kpis=None, event_log_df=None):
    """Generate an AI response to the user's message.

    Args:
        user_message: The user's question.
        chat_history: List of (role, text) tuples from the UI.
        kpis: Optional dict of KPI values.
        event_log_df: Optional DataFrame of the event log.

    Returns:
        String response from the AI.
    """
    client = init_client()

    data_context = build_data_context(kpis, event_log_df)

    messages = [
        {"role": "system", "content": AI_SYSTEM_PROMPT},
        {"role": "system", "content": f"CURRENT OPERATIONAL DATA:\n{data_context}"},
    ]

    # Add prior conversation history
    for role, text in chat_history:
        mapped_role = "assistant" if role in ("model", "assistant") else "user"
        messages.append({"role": mapped_role, "content": text})

    # Add the current user message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=AI_MODEL,
        messages=messages,
        max_tokens=AI_MAX_TOKENS,
        temperature=AI_TEMPERATURE,
    )

    return response.choices[0].message.content