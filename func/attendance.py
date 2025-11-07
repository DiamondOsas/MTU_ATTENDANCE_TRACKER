import os
import shutil
import glob
import csv
from tkinter import filedialog
import pandas as pd

def prepare_attendance_files():
    """
    Processes student list CSV files from 'db/allstudents' and creates
    formatted attendance sheets in 'db/attendance'.

    For each generated file, it adds a specific header, fields for DATE and
    ACTIVITY, and then populates the student data by extracting and reordering
    columns from the source file.

    ASSUMPTION: The source CSV files in 'db/allstudents' are expected to have
    the following column structure:
    - Column 1 (index 0): Matric NO
    - Column 2 (index 1): Surname
    - Column 3 (index 2): Firstname
    - Column 5 (index 4): Chapel Seat
    """
    # Define the source and destination directories.
    source_dir = os.path.join("db", "allstudents")
    destination_dir = os.path.join("db", "attendance")

    # Create the destination directory if it doesn't already exist.
    os.makedirs(destination_dir, exist_ok=True)

    # Find all .csv files in the source directory.
    student_lists = glob.glob(os.path.join(source_dir, "*.csv"))

    # Loop through each source CSV file to process it.
    for source_file_path in student_lists:
        file_name = os.path.basename(source_file_path)
        destination_file_path = os.path.join(destination_dir, file_name)

        try:
            # Open the source file for reading and destination file for writing.
            with open(source_file_path, mode='r', newline='', encoding='utf-8') as infile, \
                 open(destination_file_path, mode='w', newline='', encoding='utf-8') as outfile:

                reader = csv.reader(infile)
                writer = csv.writer(outfile)

                # --- 1. Write the new header and metadata ---
                # This is the main header for the attendance sheet.
                writer.writerow(["Surname", "Firstname", "Matric NO", "Chapel Seat"])
                writer.writerow([])  # Add a blank row for spacing.
                writer.writerow(["DATE"])
                writer.writerow(["ACTIVITY"])
                writer.writerow([])  # Add another blank row for spacing.


                # --- 2. Write the student data ---
                # Skip the header row of the source file to avoid duplicating it.
                next(reader, None)

                # Read each student's data and write it to the new file.
                for row in reader:
                    # Ensure the row has the 4 expected columns to prevent errors.
                    if len(row) >= 4:
                        # The columns are already in the correct order (Surname, Firstname, Matric, Seat),
                        # so we can write the row directly.
                        writer.writerow(row)

            print(f"Generated formatted attendance sheet: {file_name}")

        except Exception as e:
            # Print an error message if a file can't be processed.
            print(f"Error processing file {source_file_path}: {e}")

def get_attendance_files():
    """
    Retrieves a list of all CSV file names from the 'db/attendance' directory.

    Returns:
        list: A list of strings, where each string is the basename of a CSV file.
              Returns an empty list if the directory doesn't exist or contains no CSV files.
    """
    # Define the path to the attendance directory.
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
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    return file_path

def update_attendance_sheet(attendance_file_name, program_type, date, external_csv_path):
    """
    Updates the selected attendance sheet with the new date, program type, and marks attendance
    based on matric numbers from an external CSV file.

    Args:
        attendance_file_name (str): The name of the attendance CSV file (e.g., "100level.csv").
        program_type (str): The type of program (e.g., "MORNING SERVICE").
        date (str): The date of the attendance in "dd/mm/yy" format.
        external_csv_path (str): The absolute path to the external CSV file containing matric numbers.
    """
    attendance_file_path = os.path.join("db", "attendance", attendance_file_name)

    if not os.path.exists(attendance_file_path):
        print(f"Error: Attendance file not found at {attendance_file_path}")
        return

    if not os.path.exists(external_csv_path):
        print(f"Error: External CSV file not found at {external_csv_path}")
        return

    try:
        # Load the attendance sheet
        attendance_df = pd.read_csv(attendance_file_path, header=[0, 2, 3]) # Read main header, DATE, ACTIVITY

        # Load matric numbers from the external CSV
        external_df = pd.read_csv(external_csv_path)
        # Assuming the external CSV has a column named 'Matric No' or similar
        # You might need to adjust this based on the actual column name in the external CSV
        extracted_matric_numbers = external_df['Matric No'].dropna().unique().tolist()

        # Find the row indices for DATE and ACTIVITY
        date_row_index = attendance_df.index[attendance_df.iloc[:, 0] == 'DATE'].tolist()[0]
        activity_row_index = attendance_df.index[attendance_df.iloc[:, 0] == 'ACTIVITY'].tolist()[0]

        # Add the new date and program type
        attendance_df.loc[date_row_index, date] = date
        attendance_df.loc[activity_row_index, date] = program_type

        # Mark attendance
        for index, row in attendance_df.iterrows():
            if row['Matric NO'] in extracted_matric_numbers:
                attendance_df.loc[index, date] = '✅'
            else:
                attendance_df.loc[index, date] = '❎'

        # Save the updated attendance sheet
        attendance_df.to_csv(attendance_file_path, index=False)
        print(f"Attendance updated successfully for {attendance_file_name} on {date}.")

    except Exception as e:
        print(f"An error occurred while updating attendance: {e}")

if __name__ == '__main__':
    # This block allows you to test the function directly by running this script.
    prepare_attendance_files()
