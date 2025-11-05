import pandas as pd
import os

def get_attendance_data(level):
    """
    Reads the attendance data for a given level from the CSV file.
    """
    file_path = os.path.join("db", "allstudents", f"{level}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        return pd.DataFrame() # Return empty DataFrame if file doesn't exist

def get_all_students_data(level):
    """
    Reads the all students data for a given level from the CSV file.
    """
    file_path = os.path.join("db", "allstudents", f"{level}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        return pd.DataFrame() # Return empty DataFrame if file doesn't exist

def get_absentees(level):
    """
    Compares the attendance data with the all students data to find absentees.
    """
    attendance_df = get_attendance_data(level)
    all_students_df = get_all_students_data(level)

    if attendance_df.empty or all_students_df.empty:
        return pd.DataFrame() # No absentees if either DataFrame is empty

    # Assuming 'Student ID' is the common column for comparison
    absentees_df = all_students_df[~all_students_df['Student ID'].isin(attendance_df['Student ID'])]
    return absentees_df
