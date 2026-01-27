import os
import shutil
import csv
import json
from pathlib import Path
from datetime import datetime
#Self Explantory
EXPECTED_HEADER = ["Surname", "Firstname", "Matric NO"]
attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..", "db", "allstudents")

def _get_documents_folder() -> Path:
    """
    Attempts to find the user's "Documents" folder in Widows.
    Who tf in MTU uses Linux NOBODY not even me YET>>>.
    """
    # Windows typically stores Documents under the USERPROFILE directory.
    return Path(os.environ['USERPROFILE']) / "Documents"


# def _validate_csv_header(file_path: Path) -> bool:
#     """
#     Validates if the first row (header) of a given CSV file matches the EXPECTED_HEADER.

#     Args:
#         file_path (Path): The path to the CSV file to validate.

#     Returns:
#         bool: True if the header matches, False otherwise or if the file cannot be read.
#     """
#     try:
#         with open(file_path, mode="r", newline="", encoding="utf-8") as f:
#             reader = csv.reader(f)
#             header = next(reader, None)
#             if header == EXPECTED_HEADER:
#                 return True
#     except (Exception, IOError, StopIteration, csv.Error) as e:
#         print(f"Error reading header File: {e}")
#         return False

# ==============================================================
def perform_daily_backup():
    """
    Creates a daily backup of the 'db' directory to the user's AppData/Roaming/MTU_BACKUP folder.
    This ensures we have a recovery point for every day the application is used.
    """
try:
    #GEt app data location on windows
    app_data = os.getenv('APPDATA')
    
    app_data_path = Path(app_data)
    backup_root = app_data_path / "MTU_BACKUP"

    #Ensuring that the flder exists

    backup_root.mkdir(parents=True, exist_ok= True)

    today_str = datetime.now().strftime("%d-%m-%Y")

    
    today_backup_path  =  backup_root / today_str
    
    #If the today_backup folder does not exist 
    if not today_backup_path.exists():
        print(f"Creatng backup today at {today_backup_path}")
        

        source = Path("db")
        #Create it 
        if source.exists():
            shutil.copytree(source ,today_backup_path)
            print("Daily backup successful")
        else:
            print(f"Error copying file to  {today_backup_path}")
    else:
        print(f"Backup skipped: Folder for today already exists.")
except Exception as e:
    print(f"Error performing daily backup: {e}")

        
def create_attendance_mtu():
    documents_path= _get_documents_folder()

    folder = documents_path / "ATTENDANCE_MTU"

    folder.mkdir(parents=True, exist_ok=True)

    try:
        for attendance_file in Path(attendance_dir).glob("*.csv"):
            foldername = attendance_file.stem.upper()

            # Create a subfolder for this attendance file
            subfolder = folder / foldername
            subfolder.mkdir(parents=True, exist_ok=True)
            # I know this is a verry stupid way to implemnet this I hope someone will refactor later
            
            sub_subfolder1 = subfolder / "ATTENDEES"
            sub_subfolder2 = subfolder / "ABSENTEES"
            sub_subfolder3 = subfolder / "REPORT"

            sub_subfolder1.mkdir(parents=True, exist_ok=True)
            sub_subfolder2.mkdir(parents=True, exist_ok=True)
            sub_subfolder3.mkdir(parents=True, exist_ok=True)
            print("Created Attendance Folders")
    except Exception as e:
    
        print(f"Error creating attendance subfolders: {e}")

def maintain_student_data_files():
    """
    Maintains synchronization between student data CSVs in 'db/allstudents'
    and an external 'MTU-STUDENT-DATA' folder in the user's Documents directory.
    
    Also performs a daily backup of the database before synchronization.

    This function handles:
    1. Daily Backups to AppData.
    2. Creating the external folder if it doesn't exist.
    3. Copying internal files to external if external copies are missing.
    4. Synchronizing files based on modification timestamps:
        - If an external file is newer, its header is validated. If valid,
          the internal file is updated from the external one. If invalid,
          the external file is overwritten by the internal (correct) version.
        - If an internal file is newer, it overwrites the external file.
    """
    
    perform_daily_backup()
    create_attendance_mtu()

    internal_data_dir = Path("db") 

    documents_path = _get_documents_folder()
    
    external_data_dir = documents_path / "MTU-STUDENT-DATA"
    external_data_dir.mkdir(parents=True, exist_ok= True)

    for internal_file_path in internal_data_dir.glob("*.csv"):
        shutil.copy2(internal_file_path, external_data_dir)
    

    


if __name__ == "__main__":
    # This block allows you to run this script directly for testing purposes.
    # It will execute the maintenance logic when the script is run as the main program.
    maintain_student_data_files()