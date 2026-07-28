"""Core analytics engine - data processing, event detection, KPI computation."""
import pandas as pd
import numpy as np
from config import COLUMN_MAPPINGS


def format_hours_to_hhmmss(hours):
    """Convert decimal hours to HH:MM:SS string."""
    total_seconds = int(round(hours * 3600))
    hh = total_seconds // 3600
    mm = (total_seconds % 3600) // 60
    ss = total_seconds % 60
    return f"{hh:02}:{mm:02}:{ss:02}"


def load_data(df):
    """
    Clean and standardise the raw dataframe from the Excel sheet.
    Takes a dataframe instead of a file path.
    """
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
    df = df.dropna(subset=["Time"]).sort_values("Time").reset_index(drop=True)

    # Rename the load column
    df = df.rename(columns={
        COLUMN_MAPPINGS["load_col_original"]: COLUMN_MAPPINGS["load_col_renamed"]
    })

    # Ensure load is numeric
    df[COLUMN_MAPPINGS["load_col_renamed"]] = pd.to_numeric(
        df[COLUMN_MAPPINGS["load_col_renamed"]], errors="coerce"
    ).fillna(0)

    # Standardise SOURCE column
    df[COLUMN_MAPPINGS["source_col"]] = (
        df[COLUMN_MAPPINGS["source_col"]]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Ensure reason columns exist
    r1 = COLUMN_MAPPINGS["reason1_col"]
    r2 = COLUMN_MAPPINGS["reason2_col"]
    if r1 not in df.columns:
        df[r1] = ""
    if r2 not in df.columns:
        df[r2] = ""
    df[r1] = df[r1].fillna("").astype(str).str.strip()
    df[r2] = df[r2].fillna("").astype(str).str.strip()

    return df


def filter_data(df, start, end):
    """Filter dataframe to the selected date range."""
    filtered = df[(df["Time"] >= start) & (df["Time"] <= end)].copy()
    if filtered.empty:
        raise ValueError("No data found for the selected date range.")
    return filtered


def split_events_at_midnight(df, start, end):
    """
    Groups continuous events by source, splitting them at midnight boundaries.
    Ported directly from the original script.
    """
    # Calculate interval in minutes
    df["Interval_Min"] = df["Time"].diff().dt.total_seconds().div(60)
    median_interval = df["Interval_Min"].median()
    if pd.isna(median_interval):
        median_interval = 5
    df["Interval_Min"] = df["Interval_Min"].fillna(median_interval)

    df["STATE_CHANGE"] = df["SOURCE"] != df["SOURCE"].shift()
    df["EVENT_GROUP"] = df["STATE_CHANGE"].cumsum()

    df["Estimated Energy (MWh)"] = df["LOAD (MW)"] * df["Interval_Min"] / 60

    # Add date column to detect day boundaries
    df["Date"] = df["Time"].dt.date

    raw_events = []
    groups = list(df.groupby("EVENT_GROUP"))

    for i, (_, group) in enumerate(groups):
        start_time = group["Time"].iloc[0]

        if i < len(groups) - 1:
            end_time = groups[i + 1][1]["Time"].iloc[0]
        else:
            end_time = end + pd.Timedelta(minutes=1)

        source = group["SOURCE"].iloc[0]
        reason1 = group["DG Transition Reason 1"].iloc[0]
        reason2 = group["DG Transition Reason 2"].iloc[0]

        current_start = start_time

        # Calculate average MW for the group to distribute energy proportionally
        total_energy = group["Estimated Energy (MWh)"].sum()
        total_duration = (end_time - start_time).total_seconds()
        avg_mw = total_energy / (total_duration / 3600) if total_duration > 0 else 0

        while current_start.date() < end_time.date() or (
            current_start.date() == end_time.date() and current_start < end_time
        ):
            # Calculate next midnight
            next_midnight = pd.Timestamp(current_start.date() + pd.Timedelta(days=1))

            # Determine end of this segment
            segment_end = min(end_time, next_midnight)

            # Calculate segment duration and energy
            segment_duration = (segment_end - current_start).total_seconds()
            segment_energy = avg_mw * (segment_duration / 3600)

            # Only add if duration is > 0
            if segment_duration > 0:
                raw_events.append({
                    "Date": current_start.date(),
                    "Start Time": current_start,
                    "End Time": segment_end,
                    "Duration Secs": segment_duration,
                    "Source": source,
                    "Reason 1": reason1,
                    "Reason 2": reason2,
                    "Energy": segment_energy,
                    "Original_Start": start_time,
                })

            # Move to next segment
            current_start = segment_end

    return pd.DataFrame(raw_events)


def generate_analytics(df, start, end):
    """
    Full analytics pipeline.

    Returns:
        - df (with energy columns added)
        - event_log_df (formatted for display)
        - report_duration_hours
        - raw_events_df (for chart and KPI computation)
        - kpi_summary (dict of all KPIs)
    """
    # First, split events at midnight
    raw_events_df = split_events_at_midnight(df, start, end)

    # Calculate report duration
    report_duration_hours = (end + pd.Timedelta(minutes=1) - start).total_seconds() / 3600

    # Build the formatted event log
    formatted_log = []

    # Get unique dates in the range
    all_dates = pd.date_range(start.date(), end.date()).date

    # Track which transitions started on which day
    transition_start_dates = {}

    for current_date in all_dates:
        day_events = raw_events_df[raw_events_df["Date"] == current_date]

        if day_events.empty:
            continue

        # Filter for DG events for the transitions
        dg_events = day_events[day_events["Source"] == "DG"]

        # Calculate total BESS energy for the day
        bess_energy = day_events[day_events["Source"] == "BESS"]["Energy"].sum()

        # Calculate total DG energy for the day
        dg_energy_total = dg_events["Energy"].sum()

        if dg_events.empty:
            # Day with no DG transitions
            formatted_log.append({
                "Date": current_date.strftime("%d-%b-%Y"),
                "BESS-DG Transitions": "None",
                "Number of Transition": 0,
                "Start Time": "-",
                "End Time": "-",
                "DG Duration (hh:mm:ss)": "00:00:00",
                "DG Duration per Day (hh:mm:ss)": "00:00:00",
                "Total DG MWh": round(dg_energy_total, 3),
                "Comments": "",
                "EST. DG MWh": 0.0,
                "BESS MWh": round(bess_energy, 3)
            })
        else:
            # Day with DG transitions
            for idx, (_, row) in enumerate(dg_events.iterrows()):
                transition_id = (row["Original_Start"], row["Reason 2"])

                if transition_id not in transition_start_dates:
                    transition_start_dates[transition_id] = current_date
                    num_trans_display = 1
                else:
                    num_trans_display = "Extended from previous day"

                transitions_label = row["Reason 2"]

                st_str = row["Start Time"].strftime("%H:%M:%S")
                et_str = row["End Time"].strftime("%H:%M:%S")

                duration_str = format_hours_to_hhmmss(row["Duration Secs"] / 3600)

                comment = row["Reason 1"]

                bess_mwh_val = round(bess_energy, 3) if idx == 0 else ""
                date_val = current_date.strftime("%d-%b-%Y") if idx == 0 else ""
                total_dg_val = round(dg_energy_total, 3) if idx == 0 else ""

                dg_duration_per_day_val = (
                    format_hours_to_hhmmss(dg_events["Duration Secs"].sum() / 3600)
                    if idx == 0 else ""
                )

                formatted_log.append({
                    "Date": date_val,
                    "BESS-DG Transitions": transitions_label,
                    "Number of Transition": num_trans_display,
                    "Start Time": st_str,
                    "End Time": et_str,
                    "DG Duration (hh:mm:ss)": duration_str,
                    "DG Duration per Day (hh:mm:ss)": dg_duration_per_day_val,
                    "Total DG MWh": total_dg_val,
                    "Comments": comment,
                    "EST. DG MWh": round(row["Energy"], 3),
                    "BESS MWh": bess_mwh_val
                })

    event_log_df = pd.DataFrame(formatted_log)

    # Add a total row
    if len(formatted_log) > 0:
        total_duration_seconds = 0
        total_dg_energy = 0
        total_bess_energy = 0
        total_transitions = 0

        for row in formatted_log:
            dur = row["DG Duration (hh:mm:ss)"]
            if dur not in ("00:00:00", "-"):
                try:
                    hh, mm, ss = map(int, dur.split(":"))
                    total_duration_seconds += hh * 3600 + mm * 60 + ss
                except Exception:
                    pass

            if isinstance(row["EST. DG MWh"], (int, float)):
                total_dg_energy += row["EST. DG MWh"]
            if isinstance(row["BESS MWh"], (int, float)):
                total_bess_energy += row["BESS MWh"]

            if isinstance(row["Number of Transition"], int) and row["Number of Transition"] == 1:
                total_transitions += 1

        total_row = {
            "Date": "TOTAL",
            "BESS-DG Transitions": "",
            "Number of Transition": total_transitions,
            "Start Time": "",
            "End Time": "",
            "DG Duration (hh:mm:ss)": format_hours_to_hhmmss(total_duration_seconds / 3600),
            "DG Duration per Day (hh:mm:ss)": format_hours_to_hhmmss(total_duration_seconds / 3600),
            "Total DG MWh": round(total_dg_energy, 3),
            "Comments": "",
            "EST. DG MWh": round(total_dg_energy, 3),
            "BESS MWh": round(total_bess_energy, 3)
        }

        formatted_log.append(total_row)
        event_log_df = pd.DataFrame(formatted_log)

    # Recompute energy columns on filtered df (for chart)
    df["Interval_Min"] = df["Time"].diff().dt.total_seconds().div(60)
    median_interval = df["Interval_Min"].median()
    if pd.isna(median_interval):
        median_interval = 5
    df["Interval_Min"] = df["Interval_Min"].fillna(median_interval)
    df["Estimated Energy (MWh)"] = df["LOAD (MW)"] * df["Interval_Min"] / 60

    # KPI Summary
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

    kpi_summary = {
        "total_duration": format_hours_to_hhmmss(report_duration_hours),
        "total_duration_hours": report_duration_hours,
        "bess_runtime": format_hours_to_hhmmss(bess_hours),
        "bess_runtime_pct": (bess_hours / report_duration_hours) * 100 if report_duration_hours else 0,
        "dg_runtime": format_hours_to_hhmmss(dg_hours),
        "dg_runtime_pct": (dg_hours / report_duration_hours) * 100 if report_duration_hours else 0,
        "bess_energy_mwh": round(bess_energy, 2),
        "dg_energy_mwh": round(dg_energy, 2),
        "peak_load_mw": round(peak_load, 2),
        "min_load_mw": round(min_load, 2),
        "avg_load_mw": round(avg_load, 2),
        "transitions": transition_count,
    }

    return df, event_log_df, report_duration_hours, raw_events_df, kpi_summary


def generate_narrative_summary(kpi, start, end):
    """Auto-generate a one-paragraph summary of the analytics."""
    return (
        f"Between {start.strftime('%d %b %Y')} and {end.strftime('%d %b %Y')}, "
        f"the system ran on BESS for {kpi['bess_runtime']} "
        f"({kpi['bess_runtime_pct']:.1f}%) and on DG for {kpi['dg_runtime']} "
        f"({kpi['dg_runtime_pct']:.1f}%), with {kpi['transitions']} "
        f"transition(s) recorded. Peak load reached {kpi['peak_load_mw']} MW, "
        f"with an average of {kpi['avg_load_mw']} MW. "
        f"Estimated BESS energy: {kpi['bess_energy_mwh']} MWh. "
        f"Estimated DG energy: {kpi['dg_energy_mwh']} MWh."
    )