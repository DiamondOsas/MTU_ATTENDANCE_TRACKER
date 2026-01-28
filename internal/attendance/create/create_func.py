import csv
import glob
import os
from pathlib import Path
from tkinter import filedialog
import pandas as pd
from internal.utils.general import _get_documents_folder

# Constants for folder structure
DB_DIR = Path("db")
STUDENTS_DIR = DB_DIR / "allstudents"
ATTENDANCE_DIR = DB_DIR / "attendance"

def normalize_matric(val: any) -> str:
    """
    Cleans up matric numbers (removes spaces and .0 from Excel numbers).
    """
    s = str(val).strip()
    if s.endswith(".0"):
        return s[:-2]
    return s

def prepare_attendance_files():
    """
    Reads student lists and creates/updates attendance sheets.
    Think of this as copying names from the 'Admission List' to the 'Class Register'.
    """
    ATTENDANCE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get all student CSV files
    student_files = list(STUDENTS_DIR.glob("*.csv"))

    for source_path in student_files:
        file_name = source_path.name
        dest_path = ATTENDANCE_DIR / file_name

        try:
            # 1. Read Source Students
            source_students = {}
            with open(source_path, mode='r', newline='', encoding='utf-8-sig') as infile:
                reader = csv.reader(infile)
                next(reader, None)  # Skip header
                # Store student data using (Surname, Firstname, Matric) as a unique ID
                for row in reader:
                    if len(row) >= 3:
                        key = (row[0], row[1], row[2]) 
                        source_students[key] = row

            # 2. If Attendance Sheet doesn't exist, create it from scratch
            if not dest_path.exists():
                with open(dest_path, mode='w', newline='', encoding='utf-8-sig') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows([
                        ["Surname", "Firstname", "Matric NO"],
                        [],
                        ["DATE"],
                        ["ACTIVITY"],
                        []
                    ])
                    # Write all students
                    writer.writerows(source_students.values())
                print(f"Created new sheet: {file_name}")
                continue

            # 3. If it exists, append new students only
            with open(dest_path, mode='r', newline='', encoding='utf-8-sig') as infile:
                lines = list(csv.reader(infile))

            # Analyze existing file
            has_activity_row = any(row and row[0] == "ACTIVITY" for row in lines)
            existing_matrics = set()
            
            # Extract existing matric numbers to avoid duplicates
            for row in lines:
                # specific logic to skip metadata rows and find student rows
                if len(row) >= 3 and row[0] not in ["DATE", "ACTIVITY", "Surname", ""]:
                    # Assumption: Matric is always at index 2
                    existing_matrics.add(row[2].strip())

            # Identify who is new
            new_students = [
                row for row in source_students.values() 
                if row[2].strip() not in existing_matrics
            ]

            # Write updates
            if not has_activity_row:
                print(f"Reformatting to add ACTIVITY row: {file_name}")
                # If structure is wrong, we rewrite the whole file safely
                with open(dest_path, mode='w', newline='', encoding='utf-8-sig') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerows([
                        ["Surname", "Firstname", "Matric NO"],
                        [],
                        ["DATE"],
                        ["ACTIVITY"],
                        []
                    ])
                    # Write old valid data + new students
                    # (Note: simpler logic applied here to ensure safety)
                    valid_old_rows = [row for row in lines if len(row) >= 3 and row[0] not in ["DATE", "ACTIVITY", "Surname"]]
                    writer.writerows(valid_old_rows)
                    writer.writerows(new_students)
            
            elif new_students:
                with open(dest_path, mode='a', newline='', encoding='utf-8-sig') as append_file:
                    writer = csv.writer(append_file)
                    writer.writerows(new_students)
                print(f"Appended {len(new_students)} new students to {file_name}")
            else:
                print(f"No changes needed for {file_name}")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

def get_attendance_files() -> list[str]:
    """Returns a list of all CSV filenames in the attendance folder."""
    if not ATTENDANCE_DIR.exists():
        return []
    return [f.name for f in ATTENDANCE_DIR.glob("*.csv")]

def load_csv_file() -> tuple:
    """Opens a file picker dialog."""
    documents_path =_get_documents_folder()
    target_dir = documents_path / "ATTENDANCE"
    return filedialog.askopenfilenames(
        title="Select CSV file(s)",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialdir=target_dir
    )

def _get_external_matrics(external_csv_path: str) -> list[str]:
    """
    Helper function to extract matric numbers from an uploaded CSV.
    It tries to guess the column name automatically.
    """
    try:
        df = pd.read_csv(external_csv_path)
        
        # 1. Try name matching
        possible_names = ['Matric No', 'Matric NO', 'Matric Number', 'Matric', 'Registration Number']
        col_name = next((col for col in df.columns if col in possible_names), None)

        # 2. Try content matching (looking for numbers)
        if not col_name:
            for col in df.columns:
                sample = df[col].dropna()
                if not sample.empty and all(str(v).strip().isdigit() for v in sample):
                    col_name = col
                    break
        
        if col_name:
            return [normalize_matric(x) for x in df[col_name].dropna().unique()]
        
        return []
    except Exception as e:
        print(f"Error reading external CSV: {e}")
        return []

def update_attendance_sheet(attendance_file_name: str, program_type: str, date: str, 
                            external_csv_path: str, matric_numbers_list: list[str] | None = None):
    """
    Updates the attendance sheet with checkmarks/crosses.
    """
    file_path = ATTENDANCE_DIR / attendance_file_name
    
    if not file_path.exists():
        print(f"Error: {file_path} not found.")
        return

    try:
        # Load entire sheet
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as f:
            lines = list(csv.reader(f))

        # --- Step 1: locate key rows ---
        date_idx, activity_idx, student_start_idx = None, None, None
        
        for i, row in enumerate(lines):
            if not row: continue
            if row[0] == 'DATE': date_idx = i
            elif row[0] == 'ACTIVITY': activity_idx = i
        
        # --- Step 2: Repair file structure if broken ---
        # (If DATE or ACTIVITY rows are missing, insert them)
        if date_idx is None:
            lines.insert(2, ['DATE'])
            date_idx = 2
            # Reset indices as we shifted rows
            activity_idx = None 
            
        if activity_idx is None:
            lines.insert(date_idx + 1, ['ACTIVITY'])
            activity_idx = date_idx + 1

        # Find where students actually start (after metadata)
        # We look for the first row after ACTIVITY that isn't empty
        for i in range(activity_idx + 1, len(lines)):
            if lines[i] and lines[i][0]: 
                student_start_idx = i
                break
        
        if student_start_idx is None: 
            student_start_idx = len(lines) # Append to end if empty

        # --- Step 3: Get the attendance list ---
        present_matrics = []
        if matric_numbers_list:
            present_matrics = [normalize_matric(x) for x in matric_numbers_list]
        elif os.path.exists(external_csv_path):
            present_matrics = _get_external_matrics(external_csv_path)
        
        # --- Step 4: Add new columns ---
        # Ensure rectangular shape (all rows same length)
        max_cols = max(len(row) for row in lines) if lines else 0
        for row in lines:
            while len(row) < max_cols:
                row.append('')

        # Add Header Data
        lines[date_idx].append(date)
        lines[activity_idx].append(program_type)

        # Mark Students
        for i in range(student_start_idx, len(lines)):
            row = lines[i]
            if len(row) >= 3: # Must have matric col
                matric = normalize_matric(row[2])
                mark = '✓' if matric in present_matrics else '✗'
                row.append(mark)
            else:
                row.append('')

        # --- Step 5: Save ---
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(lines)
            
        print(f"Success: Updated {attendance_file_name} for {date}")

    except Exception as e:
        print(f"Failed to update attendance: {e}")

if __name__ == '__main__':
    # Test run
    prepare_attendance_files()