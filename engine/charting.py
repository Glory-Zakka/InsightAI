"""Chart generation - ported from reportgenerator.py."""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import math
import io
from config import (
    TRIGGER_COLORS, BESS_COLOR, UNKNOWN_COLOR, LOAD_LINE_COLOR,
    THRESHOLD_COLOR, BOUNDARY_COLOR, CHART_FIGSIZE, CHART_DPI, EXPORT_DPI,
)
from engine.analytics import format_hours_to_hhmmss


def configure_ticks(ax, df):
    duration_days = (df["Time"].max() - df["Time"].min()).days

    if duration_days <= 1:
        locator = mdates.HourLocator(interval=1)
    elif duration_days <= 3:
        locator = mdates.HourLocator(interval=6)
    elif duration_days <= 7:
        locator = mdates.DayLocator(interval=1)
    else:
        locator = mdates.DayLocator(interval=2)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b\n%H:%M"))


def plot_continuous_fill(ax, df, mask, color, label, alpha=0.65, zorder=1):
    groups = mask.ne(mask.shift()).cumsum()
    first_label = True

    for _, segment in df.groupby(groups):
        if not mask.loc[segment.index[0]]:
            continue

        ax.fill_between(
            segment["Time"],
            0,
            segment["LOAD (MW)"],
            step="post",
            color=color,
            alpha=alpha,
            label=label if first_label else None,
            zorder=zorder
        )
        first_label = False


def generate_chart(
    df,
    raw_events_df,
    report_duration_hours,
    threshold_mw=2.15,
    boundary_mw=2.50,
    trigger_colors=None,
    figsize=CHART_FIGSIZE,
    dpi=CHART_DPI,
):
    if trigger_colors is None:
        trigger_colors = TRIGGER_COLORS

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Load line
    ax.plot(
        df["Time"],
        df["LOAD (MW)"],
        color=LOAD_LINE_COLOR,
        linewidth=1.0,
        zorder=10
    )

    # BESS fill
    bess_mask = df["SOURCE"] == "BESS"
    plot_continuous_fill(ax, df, bess_mask, BESS_COLOR, "On BESS", zorder=2)

    # Trigger fills
    for trigger, color in trigger_colors.items():
        mask = (
            (df["SOURCE"] == "DG") &
            (df["DG Transition Reason 2"] == trigger)
        )
        if mask.any():
            plot_continuous_fill(ax, df, mask, color, trigger, zorder=1)

    # Unclassified state
    classified = df["SOURCE"] == "BESS"
    for trigger in trigger_colors.keys():
        classified |= (
            (df["SOURCE"] == "DG") &
            (df["DG Transition Reason 2"] == trigger)
        )

    unknown_mask = ~classified
    if unknown_mask.any():
        plot_continuous_fill(
            ax, df, unknown_mask, UNKNOWN_COLOR,
            "Unclassified State", alpha=0.35, zorder=0
        )

    # Threshold lines
    ax.axhline(
        threshold_mw, color=THRESHOLD_COLOR, linestyle="--",
        linewidth=2, label=f"{threshold_mw} MW Threshold"
    )

    ax.axhline(
        boundary_mw, color=BOUNDARY_COLOR, linestyle="--",
        linewidth=2, label=f"{boundary_mw} MW Boundary"
    )

    # Y-axis
    max_load = df["LOAD (MW)"].max()
    upper_limit = max(3.0, math.ceil(max_load * 1.15 * 2) / 2)
    ax.set_ylim(0, upper_limit)

    configure_ticks(ax, df)

    ax.set_xlabel("Time", fontsize=18, fontweight="bold")
    ax.set_ylabel("Load (MW)", fontsize=18, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.4)
    plt.xticks(rotation=0, fontsize=11)

    # ============================================
    # KPI BAR AT BOTTOM
    # ============================================

    total_hours = report_duration_hours

    bess_seconds = raw_events_df[raw_events_df["Source"] == "BESS"]["Duration Secs"].sum()
    dg_seconds = raw_events_df[raw_events_df["Source"] == "DG"]["Duration Secs"].sum()

    bess_hours = bess_seconds / 3600
    dg_hours = dg_seconds / 3600

    bess_energy = raw_events_df[raw_events_df["Source"] == "BESS"]["Energy"].sum()
    dg_energy = raw_events_df[raw_events_df["Source"] == "DG"]["Energy"].sum()

    peak_load = df["LOAD (MW)"].max()
    min_load = df["LOAD (MW)"].min()
    avg_load = df["LOAD (MW)"].mean()

    transition_count = int(
        ((df["SOURCE"].shift(1) == "BESS") & (df["SOURCE"] == "DG")).sum()
    )

    summary_items = [
        ("Total Duration", format_hours_to_hhmmss(total_hours), "black"),
        ("BESS Runtime", f"{format_hours_to_hhmmss(bess_hours)} ({(bess_hours/total_hours)*100:.1f}%)", "#009966"),
        ("DG Runtime", f"{format_hours_to_hhmmss(dg_hours)} ({(dg_hours/total_hours)*100:.1f}%)", "#8B0000"),
        ("Est. BESS Energy", f"{bess_energy:.2f} MWh", "#009966"),
        ("Est. DG Energy", f"{dg_energy:.2f} MWh", "#8B0000"),
        ("Peak Load", f"{peak_load:.2f} MW", "black"),
        ("Min Load", f"{min_load:.2f} MW", "black"),
        ("Avg Load", f"{avg_load:.2f} MW", "black"),
        ("Transitions", f"{transition_count}", "black"),
    ]

    start_x = 0.05
    spacing = 0.10
    y_pos = 0.035

    for i, (title, value, color) in enumerate(summary_items):
        x = start_x + (i * spacing)
        fig.text(x, y_pos + 0.018, title, fontsize=10, fontweight="bold", ha="center")
        fig.text(x, y_pos - 0.005, value, fontsize=10, fontweight="bold", ha="center", color=color)

    summary_box = Rectangle(
        (0.02, 0.01), 0.96, 0.065,
        transform=fig.transFigure, fill=False,
        edgecolor="#66AA33", linewidth=1.5
    )
    fig.patches.append(summary_box)

    # ============================================
    # LEGEND
    # ============================================

    handles, labels = ax.get_legend_handles_labels()
    unique = {}
    for h, l in zip(handles, labels):
        if l not in unique:
            unique[l] = h

    preferred_order = [
        "On BESS", "Load-Triggered", "Distribution Grid Outage-Triggered",
        "Unplanned BESS-Related", "Planned BESS-Related",
        "TCN Grid Outage-Triggered", "Unclassified State",
        f"{threshold_mw} MW Threshold", f"{boundary_mw} MW Boundary",
    ]

    ordered_handles = [unique[label] for label in preferred_order if label in unique]
    ordered_labels = [label for label in preferred_order if label in unique]

    ax.legend(
        ordered_handles, ordered_labels,
        loc="upper center", bbox_to_anchor=(0.5, -0.10),
        ncol=5, fontsize=10
    )

    plt.tight_layout(rect=[0, 0.11, 1, 1])

    return fig


def export_chart_to_bytes(fig, dpi=EXPORT_DPI):
    """Export figure to a bytes buffer for UI download."""
    buf = io.BytesIO()
    fig.savefig(buf, format="jpg", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    return buf.getvalue()