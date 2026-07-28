"""Smoke test for chart generation."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from engine.validation import validate_workbook
from engine.analytics import load_data, filter_data, generate_analytics
from engine.charting import generate_chart

SAMPLE_FILE = "data/Kudenda_Load_Analysis_Model_SYNTHETIC.xlsx"

print("=" * 60)
print("PHASE 2 SMOKE TEST - CHART GENERATION")
print("=" * 60)

# Load and process
print("\n1. Loading workbook...")
is_valid, message, raw_df = validate_workbook(SAMPLE_FILE)
if not is_valid:
    print(f"   FAILED: {message}")
    exit(1)
print(f"   Validated! Rows: {len(raw_df)}")

print("\n2. Processing data...")
df = load_data(raw_df)
start = pd.Timestamp("2026-06-19 00:00")
end = pd.Timestamp("2026-06-20 23:59")
filtered = filter_data(df, start, end)
filtered, event_log, duration, raw_events, kpi = generate_analytics(filtered, start, end)
print(f"   Filtered rows: {len(filtered)}")

print("\n3. Generating chart...")
fig = generate_chart(filtered, raw_events, duration)

output_path = "data/test_chart_output.jpg"
fig.savefig(output_path, dpi=300, bbox_inches="tight")
print(f"   Chart saved to: {output_path}")

print("\n" + "=" * 60)
print("CHART TEST PASSED. Open the image to verify it looks correct.")
print("=" * 60)