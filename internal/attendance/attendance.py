import os
import glob
import csv
from tkinter import filedialog
import pandas as pd
from pathlib import Path
def get_attendance_files():
    """
    Retrieves a list of all CSV file names from the 'db/attendance' directory.

    Returns:
        list: A list of strings, where each string is the basename of a CSV file.
              Returns an empty list if the directory doesn't exist or contains no CSV files.
    """
    # Go to
    attendance_dir = os.path.join("db", "attendance")

    # Check if the directory exists.
    if not os.path.isdir(attendance_dir):
        print(f"Directory not found: {attendance_dir}")
        return []

    # Find all files ending with .csv in the directory.
    try:
        # Use glob to find all files matching the pattern "*.csv".
        csv_files = glob.glob(os.path.join(attendance_dir, "*.csv"))
        
        # Use a list comprehension to extract just the file names (basenames).
        # e.g., from "db/attendance/100level.csv" to "100level.csv"
        file_names = [os.path.basename(f) for f in csv_files]
        
        return file_names
    except Exception as e:
        # Print an error if something goes wrong during file searching.
        print(f"An error occurred while searching for attendance files: {e}")
        return []

def load_csv_file():
    """
    Opens a file dialog for the user to select a CSV file.

    Returns:
        str: The path to the selected CSV file, or None if no file is chosen.
    """
    # Ask the user to select a file, defaulting to CSV files.
    file_path = filedialog.askopenfilenames(
        title="Select a CSV  file/files",
        filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
    )
    return file_path

def load_csv_file_range(days)-> bool:
    
    file_path = filedialog.askopenfilenames(
        title=f" Select {days} CSV Files",
        filetypes =[("CSV Files", "*csv"), ("All Files", "*.*")]
    )
    if len(file_path) < days:
        print(f"Please select {days} number of CSV")
        return False
    else:
        return True 

    

def normalize_matric(val):
    """
    Helper to normalize matric numbers to ensure consistent matching.
    - Converts to string.
    - Strips whitespace.
    - Removes trailing '.0' if present (common in data read from Excel/Pandas).
    """
    s = str(val).strip()
    if s.endswith(".0"):
        return s[:-2]
    return s

def update_attendance_sheet(attendance_file_name, program_type, date, external_csv_path, matric_numbers_list=None):
    """
    Updates the selected attendance sheet with the new date, program type, and marks attendance
    based on matric numbers from an external CSV file.

    Args:
        attendance_file_name (str): The name of the attendance CSV file (e.g., "100level.csv").
        program_type (str): The type of program (e.g., "MORNING SERVICE").
        date (str): The date of the attendance in "dd/mm/yy" format.
        external_csv_path (str): The absolute path to the external CSV file containing matric numbers.
        matric_numbers_list (list, optional): A list of matric numbers extracted from the external file.
                                              If provided, the function uses this list instead of reading the external file again.
    """
    attendance_file_path = os.path.join("db", "attendance", attendance_file_name)

    if not os.path.exists(attendance_file_path):
        print(f"Error: Attendance file not found at {attendance_file_path}")
        return

    # Only check for external CSV existence if we are not provided with the list directly
    if matric_numbers_list is None and not os.path.exists(external_csv_path):
        print(f"Error: External CSV file not found at {external_csv_path}")
        return

    try:
        # Read the attendance file as a regular CSV first to understand its structure
        with open(attendance_file_path, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            lines = list(reader)
        
        # Find the DATE and ACTIVITY rows
        date_row_index = None
        activity_row_index = None
        student_data_start_index = None
        
        for i, line in enumerate(lines):
            if line and line[0] == 'DATE':
                date_row_index = i
            elif line and line[0] == 'ACTIVITY':
                activity_row_index = i
            elif date_row_index is not None and activity_row_index is not None and line and line[0] != '' and line[0] != 'DATE' and line[0] != 'ACTIVITY':
                # This is where student data starts
                student_data_start_index = i
                break
        
        # If DATE row doesn't exist, create it after the header
        if date_row_index is None:
            # Find the header row (first non-empty row)
            header_index = 0
            for i, line in enumerate(lines):
                if line and len(line) > 0 and line[0] != '':
                    header_index = i
                    break
            
            # Insert DATE row after header and a blank row
            lines.insert(header_index + 1, [])
            lines.insert(header_index + 2, ['DATE'])
            date_row_index = header_index + 2
            activity_row_index = None  # Reset to find new position
            student_data_start_index = None  # Reset to find new position
        
        # If ACTIVITY row doesn't exist, create it after the DATE row
        if activity_row_index is None:
            # Insert ACTIVITY row after DATE row
            lines.insert(date_row_index + 1, ['ACTIVITY'])
            activity_row_index = date_row_index + 1
            student_data_start_index = None  # Reset to find new position
        
        # Find student data start index if not already found
        if student_data_start_index is None:
            for i in range(max(date_row_index, activity_row_index) + 1, len(lines)):
                if lines[i] and len(lines[i]) > 0 and lines[i][0] != '' and lines[i][0] != 'DATE' and lines[i][0] != 'ACTIVITY':
                    student_data_start_index = i
                    break
        
        # If still no student data found, start adding after ACTIVITY row
        if student_data_start_index is None:
            student_data_start_index = activity_row_index + 1
            # Add a blank row for spacing if not already there
            if student_data_start_index >= len(lines) or (len(lines[student_data_start_index]) > 0 and lines[student_data_start_index][0] != ''):
                lines.insert(student_data_start_index, [])
                student_data_start_index += 1
        
        extracted_matric_numbers = []
        
        if matric_numbers_list is not None:
            # Use the provided list
            extracted_matric_numbers = [normalize_matric(x) for x in matric_numbers_list]
        else:
            # Load matric numbers from the external CSV
            external_df = pd.read_csv(external_csv_path)
            
            # Try to find the matric number column
            matric_column = None
            
            # 1. Try to find by common header names
            possible_names = ['Matric No', 'Matric NO', 'Matric Number', 'Matric', 'Registration Number']
            for col in external_df.columns:
                if col in possible_names:
                    matric_column = col
                    break
            
            # 2. If not found, try to find by content (numeric)
            if matric_column is None:
                print("Matric column name not found, checking for numeric data...")
                for col in external_df.columns:
                    # Get non-empty values
                    sample_data = external_df[col].dropna()
                    if len(sample_data) > 0:
                        # Check if values look like digits (matric numbers)
                        if all(str(val).strip().isdigit() for val in sample_data):
                             matric_column = col
                             print(f"Auto-detected matric column by data: '{col}'")
                             break

            if matric_column is None:
                print("Error: Could not find matric number column. Checked names and numeric content.")
                return
            
            # Normalize matric numbers read from dataframe
            extracted_matric_numbers = [normalize_matric(x) for x in external_df[matric_column].dropna().unique()]
        
        # Add the new date column to DATE and ACTIVITY rows if it doesn't exist
        # First, ensure all rows have the same number of columns
        max_cols = max(len(line) for line in lines)
        for i, line in enumerate(lines):
            if len(line) < max_cols:
                lines[i].extend([''] * (max_cols - len(line)))
        
        # Add the new date column to DATE and ACTIVITY rows
        lines[date_row_index].append(date)
        lines[activity_row_index].append(program_type)
        
        # Mark attendance for each student
        for i in range(student_data_start_index, len(lines)):
            if i < len(lines) and len(lines[i]) >= 3:  # Ensure we have at least 3 columns (Surname, Firstname, Matric NO)
                matric_no = normalize_matric(lines[i][2])  # Normalize matric no from file
                if matric_no in extracted_matric_numbers:
                    lines[i].append('✓')
                else:
                    lines[i].append('✗')
            else:
                # If this row doesn't have enough columns, add an empty cell
                lines[i].append('')
        
        # Write the updated data back to the file
        with open(attendance_file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(lines)
        
        print(f"Attendance updated successfully for {attendance_file_name} on {date}.")

    except Exception as e:
        print(f"An error occurred while updating attendance: {e}")




##332