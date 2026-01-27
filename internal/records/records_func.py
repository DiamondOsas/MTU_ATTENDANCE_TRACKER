import csv
import pandas as pd
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

def extract_records(file_path, col_index, target_marks, df=None):
    """
    Returns a list of students marked with any of the target_marks in the specified column.
    """
    try:
        if df is None:
            df = load_attendance_file(file_path)
        
        if df is None: return None

        local_df = df.copy()
        if len(local_df.columns) < 3: 
            return []
            
        local_df.rename(columns={'0': 'Surname', '1': 'Firstname', '2': 'Matric NO'}, inplace=True)
        
        mask_valid_rows = ~local_df['Surname'].str.upper().isin(['DATE', 'ACTIVITY', 'SURNAME', 'NAN', 'NONE'])
        mask_valid_rows &= local_df['Surname'].notna()
        
        clean_df = local_df[mask_valid_rows].copy()
        
        target_col = str(col_index)
        if target_col not in clean_df.columns:
            return []

        clean_df[target_col] = clean_df[target_col].astype(str)
        mask = clean_df[target_col].str.strip().isin(target_marks)
        records = clean_df[mask]
        
        return records[['Surname', 'Firstname', 'Matric NO']].to_dict('records')

    except Exception as e:
        print(f"Error extracting records: {e}")
        return None

def save_records(records_data, file_path):
    """Saves the records list to CSV or Excel."""
    try:
        df = pd.DataFrame(records_data)
        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        else:
            df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving records: {e}")
        return False
