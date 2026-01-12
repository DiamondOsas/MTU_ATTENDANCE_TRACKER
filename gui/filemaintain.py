import os
import shutil
import csv
import json
from pathlib import Path
from datetime import datetime

# Define the expected header for student data CSVs.
# This is a critical constant and should not be changed unless the entire system's data format changes.
EXPECTED_HEADER = ["Surname", "Firstname", "Matric NO"]

def _get_documents_folder() -> Path:
    """
    Attempts to find the user's "Documents" folder in a cross-platform way.
    For Windows, it uses the USERPROFILE environment variable.
    For other OS (Linux, macOS), it defaults to `~/Documents`.

    Returns:
        Path: The path to the user's Documents folder.
    """
    # Windows typically stores Documents under the USERPROFILE directory.
    if os.name == 'nt' and 'USERPROFILE' in os.environ:
        return Path(os.environ['USERPROFILE']) / "Documents"
    else:
        # For Unix-like systems, it's usually directly under the home directory.
        return Path.home() / "Documents"

def _validate_csv_header(file_path: Path) -> bool:
    """
    Validates if the first row (header) of a given CSV file matches the EXPECTED_HEADER.

    Args:
        file_path (Path): The path to the CSV file to validate.

    Returns:
        bool: True if the header matches, False otherwise or if the file cannot be read.
    """
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Read the first row
            return header == EXPECTED_HEADER
    except (IOError, StopIteration, csv.Error) as e:
        print(f"Error reading header of {file_path}: {e}")
        return False

def perform_daily_backup():
    """
    Creates a daily backup of the 'db' directory to the user's AppData/Roaming/MTU_BACKUP folder.
    This ensures we have a recovery point for every day the application is used.
    """
    try:
        # 1. Determine the AppData path (using APPDATA env var on Windows)
        if os.name == 'nt':
            app_data = os.getenv('APPDATA')
            if not app_data:
                app_data = Path.home() / "AppData" / "Roaming"
            else:
                app_data = Path(app_data)
        else:
            app_data = Path.home() / ".config"

        backup_root = app_data / "MTU_BACKUP"
        # Ensure root backup folder exists
        backup_root.mkdir(parents=True, exist_ok=True)

        # 2. Determine today's backup folder name
        today_str = datetime.now().strftime("%Y-%m-%d")
        today_backup_path = backup_root / today_str
        
        # 3. Check if backup for today already exists
        if not today_backup_path.exists():
            print(f"Creating daily backup at: {today_backup_path}")
            today_backup_path.mkdir()
            
            # Source is the 'db' directory in the current working directory
            source_dir = Path("db")
            dest_dir = today_backup_path / "db"
            
            if source_dir.exists():
                # Copy the entire db folder structure
                shutil.copytree(source_dir, dest_dir)
                
                # Create a metadata JSON file for version info
                metadata = {
                    "backup_date": today_str,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "version": "1.0"
                }
                
                with open(today_backup_path / "backup_info.json", "w") as f:
                    json.dump(metadata, f, indent=4)
                    
                print("Daily backup completed successfully.")
            else:
                print("Warning: 'db' directory not found. Backup skipped.")
        else:
            print(f"Backup for {today_str} already exists. Skipping creation.")
            
    except Exception as e:
        print(f"Error performing daily backup: {e}")

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
    
    # --- Step 0: Perform Daily Backup ---
    perform_daily_backup()

    # --- Step 1: Synchronization Logic ---
    # Path to the internal student data directory.
    internal_data_dir = Path("db") / "allstudents"

    # Path to the external student data directory in the user's Documents.
    documents_path = _get_documents_folder()
    external_data_dir = documents_path / "MTU-STUDENT-DATA"

    print(f"Internal data directory: {internal_data_dir.resolve()}")
    print(f"External data directory: {external_data_dir.resolve()}")

    # Ensure the external data directory exists.
    # If it doesn't exist, it will be created, including any necessary parent directories.
    external_data_dir.mkdir(parents=True, exist_ok=True)
    print(f"Ensured external directory exists: {external_data_dir}")

    # Process each CSV file found in the internal data directory.
    for internal_file_path in internal_data_dir.glob("*.csv"):
        file_name = internal_file_path.name
        external_file_path = external_data_dir / file_name

        print(f"\nProcessing file: {file_name}")

        # Case 1: External file does not exist.
        if not external_file_path.exists():
            print(f"  External file '{file_name}' not found. Copying from internal.")
            shutil.copy2(internal_file_path, external_file_path)
            print(f"  Created external copy: {external_file_path}")
            continue

        # Case 2: Both internal and external files exist, compare them.
        try:
            internal_mtime = internal_file_path.stat().st_mtime
            external_mtime = external_file_path.stat().st_mtime

            # Convert modification times to human-readable format for logging.
            internal_dt = datetime.fromtimestamp(internal_mtime)
            external_dt = datetime.fromtimestamp(external_mtime)
            print(f"  Internal modified: {internal_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  External modified: {external_dt.strftime('%Y-%m-%d %H:%M:%S')}")

            # If the external file is newer, check its validity.
            if external_mtime > internal_mtime:
                print(f"  External file '{file_name}' is newer. Validating its header.")
                if _validate_csv_header(external_file_path):
                    print(f"  External file header is VALID. Updating internal file from external.")
                    shutil.copy2(external_file_path, internal_file_path)
                else:
                    print(f"  External file header is INVALID. Overwriting external file with internal (correct) version.")
                    shutil.copy2(internal_file_path, external_file_path)
            # If the internal file is newer or they have the same timestamp, ensure external reflects internal.
            elif internal_mtime > external_mtime:
                 print(f"  Internal file '{file_name}' is newer. Updating external file from internal.")
                 shutil.copy2(internal_file_path, external_file_path)
            else:
                print(f"  Files '{file_name}' are in sync (same modification time). No action needed.")

        except OSError as e:
            print(f"  Error accessing file metadata for {file_name}: {e}")
        except Exception as e:
            print(f"  An unexpected error occurred while processing {file_name}: {e}")


if __name__ == "__main__":
    # This block allows you to run this script directly for testing purposes.
    # It will execute the maintenance logic when the script is run as the main program.
    maintain_student_data_files()