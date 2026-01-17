import os
import csv
import glob
def prepare_attendance_files():
    """
    Processes student list CSV files from 'db/allstudents' and creates or updates
    formatted attendance sheets in 'db/attendance'.

    If an attendance file doesn't exist, it's created with a header and student data.
    If it exists, new students from the source file are appended without
    deleting existing records or attendance marks.

    ASSUMPTION: The source CSV files in 'db/allstudents' are expected to have
    the following column structure:
    - Column 1 (index 0): Surname
    - Column 2 (index 1): Firstname
    - Column 3 (index 2): MATRIC NO
    """
    source_dir = os.path.join("db", "allstudents")
    destination_dir = os.path.join("db", "attendance")
    os.makedirs(destination_dir, exist_ok=True)

    student_lists = glob.glob(os.path.join(source_dir, "*.csv"))

    for source_file_path in student_lists:
        file_name = os.path.basename(source_file_path)
        destination_file_path = os.path.join(destination_dir, file_name)

        try:
            # --- Read source students ---
            with open(source_file_path, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.reader(infile)
                next(reader, None)  # Skip header
                source_students = {tuple(row[:3]): row for row in reader if len(row) >= 3} # Use first 3 cols as key

            # --- If destination file doesn't exist, create it ---
            if not os.path.exists(destination_file_path):
                with open(destination_file_path, mode='w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow(["Surname", "Firstname", "Matric NO"])
                    writer.writerow([])
                    writer.writerow(["DATE"])
                    writer.writerow(["ACTIVITY"])
                    writer.writerow([])
                    for student_row in source_students.values():
                        writer.writerow(student_row)
                print(f"Created new attendance sheet: {file_name}")
                continue # Move to the next file

            # --- If destination file exists, check structure and append new students ---
            # We use 'r' to read everything first
            with open(destination_file_path, mode='r', newline='', encoding='utf-8') as infile:
                lines = list(csv.reader(infile))

            has_activity = False
            existing_data_rows = []
            existing_matric_nos = set()

            for row in lines:
                if not row: continue
                # Check if ACTIVITY row is present
                if row[0] == "ACTIVITY":
                    has_activity = True
                
                # Collect valid student rows to preserve them and check for duplicates
                # Exclude metadata rows: Header, DATE, ACTIVITY
                # Student rows must have at least 3 columns. Matric NO is at index 2.
                if len(row) >= 3 and row[0] != "DATE" and row[0] != "ACTIVITY" and row[2] != "Matric NO":
                    existing_data_rows.append(row)
                    existing_matric_nos.add(row[2].strip())

            # Find students in source that are not in destination
            new_students_to_add = []
            for student_key, student_row in source_students.items():
                matric_no = student_row[2].strip()
                if matric_no not in existing_matric_nos:
                    new_students_to_add.append(student_row)

            # If ACTIVITY is missing, we must restructure the file to include it
            if not has_activity:
                print(f"Reformatting file to include ACTIVITY: {file_name}")
                with open(destination_file_path, mode='w', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    # Write standard structure
                    writer.writerow(["Surname", "Firstname", "Matric NO"])
                    writer.writerow([])
                    writer.writerow(["DATE"])
                    writer.writerow(["ACTIVITY"])
                    writer.writerow([])
                    
                    # Write back existing student data (preserving any attendance marks)
                    writer.writerows(existing_data_rows)
                    
                    # Write new students
                    writer.writerows(new_students_to_add)
                
                if new_students_to_add:
                    print(f"Also appended {len(new_students_to_add)} new students to: {file_name}")

            else:
                # File structure is good, just append new students if any
                if new_students_to_add:
                    with open(destination_file_path, mode='a', newline='', encoding='utf-8') as append_file:
                        writer = csv.writer(append_file)
                        for student_row in new_students_to_add:
                            writer.writerow(student_row)
                    print(f"Appended {len(new_students_to_add)} new students to: {file_name}")
                else:
                    print(f"No new students to add to: {file_name}")

        except Exception as e:
            print(f"Error processing file {source_file_path}: {e}")


if __name__ == '__main__':
    # This block allows you to test the function directly by running this script.
    prepare_attendance_files()