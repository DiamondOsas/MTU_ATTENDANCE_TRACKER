import csv
import pandas as pd
from internal.utils.csv_handler import read_csv_robust
import os

def load_attendance_file(file_path):
    """
    Loads the attendance CSV in a raw format suitable for processing.
    """
    try:
        # Read with dummy headers to capture all structure
        df = pd.read_csv(file_path, names=[str(i) for i in range(50)], dtype=str, on_bad_lines='skip')
        return df
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def get_session_info(file_path):
    """
    Scans a CSV to find unique sessions (Date + Activity pairs).
    Returns a dict: { 'dd/mm/yy': [{'activity': 'Name', 'col_index': int}, ...] }
    """
    sessions = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip().split(',') for line in f.readlines()]

        date_row = None
        activity_row = None
        
        # Find header rows
        for row in lines:
            if not row: continue
            first_cell = row[0].strip().upper()
            if first_cell == "DATE":
                date_row = row
            elif first_cell == "ACTIVITY":
                activity_row = row
            if date_row and activity_row:
                break
        
        if not date_row or not activity_row:
            return {}

        # Scan columns starting from index 3 (standard attendance format)
        limit = min(len(date_row), len(activity_row))
        
        for idx in range(3, limit):
            d_val = date_row[idx].strip()
            a_val = activity_row[idx].strip()
            
            if d_val and a_val:
                if d_val not in sessions:
                    sessions[d_val] = []
                sessions[d_val].append({'activity': a_val, 'col_index': idx})
                
    except Exception as e:
        print(f"Error getting session info: {e}")
        return {}

    return sessions

def extract_absentees(file_path, col_index, df=None):
    """
    Returns a list of students marked as absent ('x', 'X', '✗') in the specified column.
    Can accept a pre-loaded raw DataFrame (df) to save time.
    """
    try:
        if df is None:
            df = load_attendance_file(file_path)
        
        if df is None: return None

        # Work on a copy to avoid side effects if df is reused
        local_df = df.copy()

        # Rename first 3 columns for clarity (assuming standard structure)
        # Ensure we have enough columns
        if len(local_df.columns) < 3:
            return []
            
        local_df.rename(columns={'0': 'Surname', '1': 'Firstname', '2': 'Matric NO'}, inplace=True)
        
        # 1. Filter out metadata rows (DATE, ACTIVITY, or empty Surname)
        mask_valid_rows = ~local_df['Surname'].str.upper().isin(['DATE', 'ACTIVITY', 'SURNAME', 'NAN', 'NONE'])
        mask_valid_rows &= local_df['Surname'].notna()
        
        clean_df = local_df[mask_valid_rows].copy()
        
        # 2. Check the specific column for absentee marks
        target_col = str(col_index)
        if target_col not in clean_df.columns:
            return []

        # Filter for absentee marks
        # Ensure column is string
        clean_df[target_col] = clean_df[target_col].astype(str)
        absent_mask = clean_df[target_col].str.strip().isin(['x', 'X', '✗'])
        absentees = clean_df[absent_mask]
        
        return absentees[['Surname', 'Firstname', 'Matric NO']].to_dict('records')

    except Exception as e:
        print(f"Error extracting absentees: {e}")
        return None

def save_absentees(absentees_data, file_path):
    """Saves the absentee list to CSV or Excel."""
    try:
        df = pd.DataFrame(absentees_data)
        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving absentees: {e}")
        return False
