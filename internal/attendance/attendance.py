import os
import glob
import csv
from tkinter import filedialog
import pandas as pd
from internal.utils.csv_handler import read_csv_robust

def get_attendance_files():
    """Retrieves CSV files from 'db/attendance'."""
    attendance_dir = os.path.join("db", "attendance")
    if not os.path.isdir(attendance_dir):
        return []
    return [os.path.basename(f) for f in glob.glob(os.path.join(attendance_dir, "*.csv"))]

def load_csv_file():
    """Opens file dialog to select CSV files."""
    return filedialog.askopenfilenames(
        title="Select CSV Files",
        filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
    )

def normalize_matric(val):
    """Normalizes matric numbers (strips whitespace, removes .0)."""
    s = str(val).strip()
    return s[:-2] if s.endswith(".0") else s

def update_attendance_sheet(attendance_file, program, date, external_csv, matric_list=None):
    """
    Updates the attendance sheet.
    """
    file_path = os.path.join("db", "attendance", attendance_file)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # 1. Get Matric Numbers
    extracted_matrics = []
    if matric_list:
        extracted_matrics = [normalize_matric(x) for x in matric_list]
    elif external_csv and os.path.exists(external_csv):
        df = read_csv_robust(external_csv)
        if not df.empty:
            # Auto-detect column
            col = next((c for c in df.columns if c.lower() in ['matric no', 'matric', 'matric number']), None)
            if not col:
                # Check for numeric column
                for c in df.columns:
                    if pd.to_numeric(df[c], errors='coerce').notna().sum() > 0:
                         col = c
                         break
            if col:
                 extracted_matrics = [normalize_matric(x) for x in df[col].dropna().unique()]
    
    # 2. Update Attendance File (Manual CSV processing due to custom structure)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = list(csv.reader(f))

        # Find key rows
        date_idx = next((i for i, r in enumerate(lines) if r and r[0] == 'DATE'), None)
        act_idx = next((i for i, r in enumerate(lines) if r and r[0] == 'ACTIVITY'), None)

        # Structure correction (if missing rows)
        if date_idx is None:
            lines.insert(2, ['DATE'])
            date_idx = 2
        if act_idx is None:
            lines.insert(date_idx + 1, ['ACTIVITY'])
            act_idx = date_idx + 1

        student_start = act_idx + 1
        
        # Add new column header
        lines[date_idx].append(date)
        lines[act_idx].append(program)
        
        # Mark attendance
        col_count = len(lines[date_idx])
        for i in range(student_start, len(lines)):
            row = lines[i]
            # Ensure row has enough columns (pad with empty strings)
            while len(row) < col_count - 1:
                row.append('')
                
            if len(row) >= 3:
                matric = normalize_matric(row[2])
                mark = '✓' if matric in extracted_matrics else '✗'
                row.append(mark)
            else:
                row.append('')

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(lines)
            
        print(f"Updated {attendance_file} for {date}.")

    except Exception as e:
        print(f"Error updating attendance: {e}")
