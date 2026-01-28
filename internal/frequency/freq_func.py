import pandas as pd
from datetime import datetime
from internal.records.records_func import load_attendance_file, get_session_info

def calculate_frequency(file_path, start_date, end_date, target_marks):
    """
    Calculates the frequency of target_marks for each student within the date range.
    Returns a list of dictionaries: {'Surname': ..., 'Firstname': ..., 'Matric NO': ..., 'Count': ...}
    """
    df = load_attendance_file(file_path)
    if df is None:
        return []

    sessions = get_session_info(file_path)
    if not sessions:
        return []

    # Identify relevant columns based on date range
    relevant_indices = []
    
    # sessions is { 'dd/mm/yy': [{'activity': 'Name', 'col_index': int}, ...] }
    for date_str, session_list in sessions.items():
        try:
            # Parse date. Assuming format dd/mm/yy as seen in get_session_info
            current_date = datetime.strptime(date_str, "%d/%m/%y").date()
            
            if start_date <= current_date <= end_date:
                for session in session_list:
                    relevant_indices.append(session['col_index'])
        except ValueError:
            continue

    if not relevant_indices:
        return []

    # Prepare data for processing
    local_df = df.copy()
    if len(local_df.columns) < 3:
        return []

    # Rename standard columns
    local_df.rename(columns={'0': 'Surname', '1': 'Firstname', '2': 'Matric NO'}, inplace=True)

    # Filter out header/metadata rows
    mask_valid_rows = ~local_df['Surname'].str.upper().isin(['DATE', 'ACTIVITY', 'SURNAME', 'NAN', 'NONE'])
    mask_valid_rows &= local_df['Surname'].notna()
    
    clean_df = local_df[mask_valid_rows].copy()

    # Calculate counts
    results = []
    
    for index, row in clean_df.iterrows():
        count = 0
        for col_idx in relevant_indices:
            col_name = str(col_idx)
            # Check if column exists in row
            if col_name in row:
                cell_value = str(row[col_name]).strip()
                if cell_value in target_marks:
                    count += 1
        
        results.append({
            'Surname': str(row['Surname']),
            'Firstname': str(row['Firstname']),
            'Matric NO': str(row['Matric NO']),
            'Count': count
        })

    return results
