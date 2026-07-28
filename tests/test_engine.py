"""Quick smoke test for the analytics engine."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pandas as pd
from engine.validation import validate_workbook
from engine.analytics import load_data, filter_data, generate_analytics, generate_narrative_summary

# Path to your sample workbook
SAMPLE_FILE = "data/Kudenda_Load_Analysis_Model_SYNTHETIC.xlsx"

print("=" * 60)
print("PHASE 1 SMOKE TEST")
print("=" * 60)

# Step 1: Validate the workbook
print("\n1. Validating workbook...")
is_valid, message, raw_df = validate_workbook(SAMPLE_FILE)
if not is_valid:
    print(f"   FAILED: {message}")
    exit(1)
print(f"   Validated! Rows: {len(raw_df)}")

# Step 2: Load and clean
print("\n2. Loading and cleaning data...")
df = load_data(raw_df)
print(f"   Cleaned rows: {len(df)}")
print(f"   Columns: {list(df.columns)}")

# Step 3: Filter to a date range
print("\n3. Filtering to date range...")
start = pd.Timestamp("2026-06-19 00:00")
end = pd.Timestamp("2026-06-20 23:59")
filtered = filter_data(df, start, end)
print(f"   Filtered rows: {len(filtered)}")

# Step 4: Run analytics
print("\n4. Running analytics pipeline...")
filtered, event_log, duration, raw_events, kpi = generate_analytics(filtered, start, end)

# Step 5: Print KPIs
print("\n5. KPI Summary:")
print("-" * 40)
for key, value in kpi.items():
    print(f"   {key}: {value}")

# Step 6: Print event log
print("\n6. Event Log:")
print("-" * 40)
print(event_log.to_string(index=False))

# Step 7: Narrative
print("\n7. Narrative Summary:")
print("-" * 40)
narrative = generate_narrative_summary(kpi, start, end)
print(narrative)

print("\n" + "=" * 60)
print("ALL TESTS PASSED. Engine is ready.")
print("=" * 60)