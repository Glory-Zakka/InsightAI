"""Centralised CSS for the NiceGUI app."""
from config import ACCENT_COLOR, DARK_HEADER, LIGHT_BG


def get_css():
    return f"""
    <style>
    /* ═══ BASE ═════════════════════════════════════════ */
    * {{
        box-sizing: border-box;
    }}

    html {{
        scroll-behavior: smooth;
    }}

    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: {LIGHT_BG};
    }}

    /* ═══ NAVBAR ════════════════════════════════════════ */
    .navbar {{
        background: linear-gradient(135deg, {DARK_HEADER} 0%, #1a2a45 100%) !important;
        height: 64px !important;
        padding: 0 24px !important;
    }}

    .navbar-inner {{
        align-items: center;
        width: 100%;
        height: 100%;
    }}

    .navbar-brand {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .logo-icon {{
        font-size: 28px;
    }}

    .navbar-title {{
        color: white;
        font-size: 20px;
        font-weight: 700;
    }}

    .navbar-subtitle {{
        color: {ACCENT_COLOR};
        font-size: 12px;
    }}

    .navbar-right {{
        align-items: center;
        gap: 12px;
    }}

    .status-dot.online {{
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00cc99;
        box-shadow: 0 0 8px rgba(0, 204, 153, 0.6);
    }}

    .badge-trial {{
        background: rgba(255,255,255,0.15);
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }}

    /* ═══ SIDEBAR ═══════════════════════════════════════ */
    .sidebar {{
        background: white !important;
        border-right: 1px solid #e0e0e0;
        padding-top: 16px;
    }}

    .nav-item {{
        color: #555 !important;
        font-size: 14px !important;
        font-weight: 500;
        padding: 12px 20px !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }}

    .nav-item:hover {{
        background: {LIGHT_BG} !important;
        color: {DARK_HEADER} !important;
    }}

    .sidebar-footer {{
        padding: 16px 20px;
    }}

    .sidebar-version {{
        font-size: 12px;
        color: #999;
    }}

    .sidebar-trial-text {{
        font-size: 11px;
        color: {ACCENT_COLOR};
        font-weight: 600;
        margin-top: 4px;
    }}

    /* ═══ MAIN CONTENT ══════════════════════════════════ */
    .main-content {{
        max-width: 1200px;
        margin: 0 auto;
        padding: 24px 32px;
        width: 100%;
    }}

    .page-title {{
        font-size: 28px;
        font-weight: 700;
        color: {DARK_HEADER};
        margin-bottom: 4px;
    }}

    .page-subtitle {{
        font-size: 14px;
        color: #888;
        margin-bottom: 24px;
    }}

    #upload-section, #date-section, #analytics-section, #chat-section, #reports-section {{
        scroll-margin-top: 80px;
    }}

    /* ═══ CARDS ═════════════════════════════════════════ */
    .q-card {{
        border-radius: 12px !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
        margin-bottom: 20px !important;
        padding: 24px !important;
    }}

    .card-header {{
        display: flex;
        align-items: center;
        font-size: 18px;
        font-weight: 600;
        color: {DARK_HEADER};
        margin-bottom: 16px;
    }}

    .card-subtitle {{
        font-size: 13px;
        color: #888;
        margin-bottom: 16px;
    }}

    /* ═══ UPLOAD ════════════════════════════════════════ */
    .upload-zone {{
        border: 2px dashed {ACCENT_COLOR} !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background: {LIGHT_BG} !important;
    }}

    /* ═══ DATE PICKERS ══════════════════════════════════ */
    .date-row {{
        align-items: flex-end;
        gap: 16px;
    }}

    .date-picker {{
        max-width: 200px;
    }}

    /* ═══ KPI CARDS ═════════════════════════════════════ */
    .kpi-grid {{
        gap: 16px;
        margin-bottom: 24px;
    }}

    .kpi-card {{
        flex: 1;
        min-width: 160px;
        text-align: center;
        padding: 20px !important;
        border-top: 4px solid transparent;
        transition: transform 0.2s;
    }}

    .kpi-card:hover {{
        transform: translateY(-3px);
    }}

    .kpi-green {{ border-top-color: #00cc99; }}
    .kpi-red {{ border-top-color: #e74c3c; }}
    .kpi-blue {{ border-top-color: #3498db; }}

    .kpi-label {{
        font-size: 12px;
        color: #777;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    .kpi-value {{
        font-size: 22px;
        font-weight: 700;
        color: {DARK_HEADER};
    }}

    .kpi-green .kpi-value {{ color: #009966; }}
    .kpi-red .kpi-value {{ color: #8B0000; }}
    .kpi-blue .kpi-value {{ color: #003399; }}

    /* ═══ NARRATIVE ═════════════════════════════════════ */
    .narrative-box {{
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border-left: 4px solid {ACCENT_COLOR};
        padding: 16px;
        border-radius: 8px;
        font-size: 14px;
        line-height: 1.7;
        color: #333;
        margin-bottom: 24px;
    }}

    /* ═══ CHART ═════════════════════════════════════════ */
    .chart-image {{
        width: 100% !important;
        border-radius: 8px;
    }}

    /* ═══ BUTTONS ═══════════════════════════════════════ */
    .btn-run {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #00aa88 100%) !important;
        color: white !important;
        font-weight: 600;
        padding: 8px 32px;
        border-radius: 8px;
        text-transform: none !important;
    }}

    .btn-download {{
        background: white !important;
        color: {DARK_HEADER} !important;
        border: 1px solid {ACCENT_COLOR} !important;
        font-weight: 500;
        padding: 8px 16px;
        border-radius: 8px;
        text-transform: none !important;
        margin-top: 12px;
    }}

    .btn-reset {{
        background: #f0f0f0 !important;
        color: #e74c3c !important;
        border: 1px solid #e74c3c !important;
        font-weight: 500;
        padding: 8px 16px;
        border-radius: 8px;
        text-transform: none !important;
        margin-top: 12px;
    }}

    .btn-reset:hover {{
        background: #fdecea !important;
    }}

    .btn-send {{
        background: linear-gradient(135deg, {ACCENT_COLOR} 0%, #00aa88 100%) !important;
        color: white !important;
        font-weight: 600;
        border-radius: 8px;
        text-transform: none !important;
    }}

    .btn-clear {{
        background: #f0f0f0 !important;
        color: #666 !important;
        border-radius: 8px;
        text-transform: none !important;
    }}

    /* ═══ TABLE ═════════════════════════════════════════ */
    .event-table .q-table {{
        border-radius: 8px;
    }}

    .event-table th {{
        background: {DARK_HEADER} !important;
        color: white !important;
        font-weight: 600;
    }}

    .event-table tbody tr:hover {{
        background: {LIGHT_BG} !important;
    }}

    /* ═══ CHAT ══════════════════════════════════════════ */
    .chat-messages {{
        max-height: 400px;
        overflow-y: auto;
        padding: 16px;
        background: {LIGHT_BG};
        border-radius: 10px;
        margin-bottom: 12px;
        min-height: 200px;
    }}

    .chat-bubble-user {{
        background: {ACCENT_COLOR};
        color: white;
        padding: 10px 16px;
        border-radius: 12px 12px 4px 12px;
        margin-bottom: 12px;
        max-width: 80%;
        margin-left: auto;
        font-size: 14px;
    }}

    .chat-bubble-ai {{
        background: white;
        color: #333;
        padding: 10px 16px;
        border-radius: 12px 12px 12px 4px;
        margin-bottom: 12px;
        max-width: 80%;
        font-size: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}

    .chat-bubble-ai p {{
        margin: 4px 0;
    }}

    .chat-bubble-ai ul, .chat-bubble-ai ol {{
        margin: 4px 0;
        padding-left: 20px;
    }}

    .chat-bubble-ai li {{
        margin: 2px 0;
    }}

    .chat-bubble-ai strong {{
        color: {DARK_HEADER};
    }}

    .chat-bubble-ai code {{
        background: #f0f0f0;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 13px;
    }}

    .chat-input-full {{
        width: 100%;
    }}

    .chat-actions {{
        gap: 8px;
        margin-top: 8px;
    }}

    /* ═══ SUGGESTED QUESTIONS ═══════════════════════════ */
    .suggested-questions {{
        gap: 8px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }}

    .suggestion-chip {{
        background: white !important;
        border: 1px solid #d0d5dd !important;
        color: #555 !important;
        font-size: 12px !important;
        font-weight: 500;
        padding: 6px 14px;
        border-radius: 16px;
        text-transform: none !important;
        cursor: pointer;
        transition: all 0.2s;
    }}

    .suggestion-chip:hover {{
        border-color: {ACCENT_COLOR} !important;
        color: {ACCENT_COLOR} !important;
        background: #f0fdfa !important;
    }}

    /* ═══ LOADING SPINNER ═══════════════════════════════ */
    .chat-loading {{
        display: flex;
        align-items: center;
        gap: 8px;
        background: white;
        padding: 10px 16px;
        border-radius: 12px 12px 12px 4px;
        margin-bottom: 12px;
        max-width: 80%;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }}

    .typing-dots {{
        display: flex;
        gap: 4px;
    }}

    .typing-dots span {{
        width: 8px;
        height: 8px;
        background: {ACCENT_COLOR};
        border-radius: 50%;
        animation: typing-bounce 1.4s infinite;
    }}

    .typing-dots span:nth-child(2) {{
        animation-delay: 0.2s;
    }}

    .typing-dots span:nth-child(3) {{
        animation-delay: 0.4s;
    }}

    @keyframes typing-bounce {{
        0%, 60%, 100% {{
            transform: translateY(0);
            opacity: 0.4;
        }}
        30% {{
            transform: translateY(-8px);
            opacity: 1;
        }}
    }}

    .loading-text {{
        font-size: 13px;
        color: #999;
    }}

    /* ═══ ANALYSIS SPINNER ══════════════════════════════ */
    .analysis-spinner {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px;
        gap: 16px;
    }}

    .analysis-spinner .q-spinner {{
        color: {ACCENT_COLOR};
    }}

    .analysis-spinner-text {{
        font-size: 14px;
        color: #777;
    }}

    /* ═══ STATUS BADGE ══════════════════════════════════ */
    .status-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }}

    .status-badge.success {{
        background: #d4edda;
        color: #155724;
    }}

    .status-badge.error {{
        background: #f8d7da;
        color: #721c24;
    }}

    /* ═══ SCROLLBAR ═════════════════════════════════════ */
    ::-webkit-scrollbar {{
        width: 6px;
    }}

    ::-webkit-scrollbar-thumb {{
        background: #ccc;
        border-radius: 3px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {ACCENT_COLOR};
    }}
    </style>
    """