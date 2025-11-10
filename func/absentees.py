import pandas as pd

def extract_absentees(df: pd.DataFrame, selected_date: str, selected_activity: str) -> pd.DataFrame:
    """
    Extracts absentee records from the attendance DataFrame for a specific date and activity.

    Args:
        df (pd.DataFrame): The attendance DataFrame loaded from the CSV.
        selected_date (str): The date chosen by the user (e.g., "20/11/25").
        selected_activity (str): The activity chosen by the user (e.g., "EVENING SERVICE").

    Returns:
        pd.DataFrame: A DataFrame containing the details of absent students
                      for the selected date and activity, or an empty DataFrame if none.
    """
    # Construct the full column name based on how it's stored in the DataFrame
    # This assumes the format "DATE - ACTIVITY" or just "DATE"
    target_column_full = f"{selected_date} - {selected_activity}"
    target_column_date_only = selected_date # Fallback if activity is not part of column name

    # Find the correct column in the DataFrame
    # We need to check if the exact column exists or if it's a date-only column
    if target_column_full in df.columns:
        attendance_column = target_column_full
    elif target_column_date_only in df.columns:
        attendance_column = target_column_date_only
    else:
        print(f"Warning: Column '{target_column_full}' or '{target_column_date_only}' not found in DataFrame.")
        return pd.DataFrame() # Return empty DataFrame if column not found

    # Filter for absentees (marked with '✗')
    # Ensure the column exists before trying to access it
    if attendance_column in df.columns:
        absentee_df = df[df[attendance_column] == '✗'].copy()
        
        # Select only the student identification columns
        # Assuming the first 4 columns are student details: Surname, Firstname, Matric NO, Chapel Seat
        student_details_columns = ["Surname", "Firstname", "Matric NO", "Chapel Seat"]
        
        # Ensure these columns exist in the original DataFrame before selecting
        existing_student_details_columns = [col for col in student_details_columns if col in absentee_df.columns]
        
        return absentee_df[existing_student_details_columns]
    else:
        return pd.DataFrame() # Should not happen if the above check is correct, but for safety
