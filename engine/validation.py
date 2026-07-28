"""Column and file validation for uploaded workbooks."""
import os
import pandas as pd
from config import EXPECTED_SHEET_NAME, REQUIRED_COLUMNS


def validate_workbook(file_path):
    """
    Validate that an uploaded file (Excel or CSV) has the expected structure.

    Returns:
        (is_valid, message, dataframe)
        - If valid: (True, "", raw_df)
        - If invalid: (False, error_message, None)
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    # 1) Read the file based on its extension
    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            xl = pd.ExcelFile(file_path)

            # 2) Check expected sheet exists
            if EXPECTED_SHEET_NAME not in xl.sheet_names:
                available = ", ".join(xl.sheet_names)
                return (
                    False,
                    f"Sheet '{EXPECTED_SHEET_NAME}' not found. "
                    f"Available sheets: {available}",
                    None,
                )

            # 3) Read the sheet
            df = pd.read_excel(file_path, sheet_name=EXPECTED_SHEET_NAME)
        else:
            return False, f"Unsupported file format: {file_ext}. Please upload .xlsx or .csv", None
    except Exception as e:
        return False, f"Could not read the file: {e}", None

    # 4) Check required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        return (
            False,
            f"Missing required columns: {', '.join(missing)}",
            None,
        )

    # 5) Check there's actual data
    if df.empty:
        return False, "The file contains no data rows.", None

    return True, "", df


def get_available_date_range(df):
    """Return the min and max timestamps in the data."""
    df_temp = pd.to_datetime(df["Time"], errors="coerce").dropna()
    return df_temp.min(), df_temp.max()