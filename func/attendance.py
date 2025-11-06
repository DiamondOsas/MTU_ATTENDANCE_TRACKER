import os
import shutil
import glob
import csv

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

if __name__ == '__main__':
    # This block allows you to test the function directly by running this script.
    prepare_attendance_files()
