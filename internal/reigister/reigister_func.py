from pathlib import Path
import csv

def register_student(surname, name, matric_no, level):
    """
    Registers a new student by saving their details to a CSV file corresponding to their level.
    Returns True if registration is successful, False if the student already exists.

    Args:
        surname (str): The student's surname.
        name (str): The student's first name.
        matric_no (str): The student's matriculation number.
        level (str): The student's level (e.g., '100', '200').
    """
    
    # File path we are appending to 
    filepath = Path(f"db/allstudents/{level}level.csv")
    filepath.parent.mkdir(parents=True, exist_ok=True)

    student_exists = False
    if filepath.exists():
        with open(filepath, mode="r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                # Check if row is not empty and matric_no matches exactly (assuming 3rd column)
                if row and len(row) >= 3 and row[2] == matric_no:
                    student_exists = True
                    break
    
    if student_exists:
        return False
    else:
        with open(filepath, mode="a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([surname.upper(), name.upper(), matric_no])
            return True        
