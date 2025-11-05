import os
import csv

def register_student(surname, name, matric_no, level, chapel_seat):
    """
    Registers a new student by saving their details to a CSV file corresponding to their level.
    Returns True if registration is successful, False if the student already exists.

    Args:
        surname (str): The student's surname.
        name (str): The student's first name.
        matric_no (str): The student's matriculation number.
        level (str): The student's level (e.g., '100', '200').
        chapel_seat (str): The student's chapel seat in 'Line/Seat' format.
    """
    # Construct the file path
    file_path = os.path.join('db', 'allstudents', f"{level}level.csv")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check for existing matric number
    if os.path.exists(file_path):
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Matric NO'] == matric_no:
                    return False # Student already exists

    # If student doesn't exist, proceed with registration
    write_header = not os.path.exists(file_path) or os.path.getsize(file_path) == 0

    with open(file_path, 'a', newline='') as csvfile:
        fieldnames = ['Surname', 'Firstname', 'Matric NO', 'Chapel Seat']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()
        
        writer.writerow({'Surname': surname, 'Firstname': name, 'Matric NO': matric_no, 'Chapel Seat': chapel_seat})
    
    return True # Registration successful
