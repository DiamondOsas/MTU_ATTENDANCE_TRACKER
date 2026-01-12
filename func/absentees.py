import csv
import pandas as pd

def get_session_info(file_path):
    """
    Reads a CSV attendance file to extract available dates and activities.
    It scans the 'DATE' and 'ACTIVITY' rows to identify each unique session
    (combination of date and activity) and its corresponding column index.

    Junior developer: This function is crucial for populating the date and
    activity dropdowns in the GUI, allowing the user to select a specific session.
    
    Args:
        file_path (str): The full path to the CSV attendance file.
        
    Returns:
        dict: A dictionary where:
              - Keys are date strings (e.g., '26/11/25').
              - Values are lists of dictionaries. Each inner dictionary contains:
                - 'activity' (str): The name of the activity (e.g., 'MANNA WATER').
                - 'col_index' (int): The column index in the CSV where attendance
                                     status for this activity is recorded.
    """
    sessions = {} # Initialize an empty dictionary to store session information
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f) # Create a CSV reader object
            rows = list(reader)    # Read all rows into a list to allow multiple passes
            
            date_row = None     # Variable to store the row containing dates
            activity_row = None # Variable to store the row containing activities
            
            # --- Locate the DATE and ACTIVITY header rows ---
            # Junior developer: This loop finds which rows contain the date and activity headers.
            for row in rows:
                if not row: continue # Skip any completely empty rows
                
                # Check the first column of each row for keywords (case-insensitive)
                if row[0].strip().upper() == "DATE":
                    date_row = row
                elif row[0].strip().upper() == "ACTIVITY":
                    activity_row = row
                
                # Once both header rows are found, we can stop searching
                if date_row and activity_row:
                    break
            
            # If either header row was not found, return an empty dictionary
            if not date_row or not activity_row:
                print(f"Warning: 'DATE' or 'ACTIVITY' row not found in {file_path}")
                return {}
            
            # --- Extract sessions from identified header rows ---
            # Attendance data columns start from index 3 (which is the 4th column, 0-indexed).
            # Junior developer: If your CSV format changes and attendance starts earlier/later,
            #                       you can easily change 'start_col' here.
            start_col = 3
            # Ensure we don't go out of bounds when iterating through columns.
            max_len = min(len(date_row), len(activity_row))
            
            # Iterate through columns, starting from 'start_col', to find session details
            for col_idx in range(start_col, max_len):
                date_val = date_row[col_idx].strip()      # Get date value from the current column
                activity_val = activity_row[col_idx].strip() # Get activity value from the current column
                
                # Only add to sessions if both date and activity values are present for the column
                if date_val and activity_val:
                    # If this date is new, create a new list for its activities
                    if date_val not in sessions:
                        sessions[date_val] = []
                    # Add the activity and its column index to the list for this date
                    sessions[date_val].append({'activity': activity_val, 'col_index': col_idx})
                    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return {}
    except Exception as e:
        # Catch any other potential errors during file processing
        print(f"Error reading session info from '{file_path}': {e}")
        return {}

    return sessions

def extract_absentees(file_path, col_index):
    """
    Extracts the list of absentees for a specific session identified by its column index.
    It reads through the attendance rows and identifies students marked with an
    absentee symbol ('x', 'X', or '✗') in the specified column.

    Junior developer: This function processes the attendance marks and returns structured data.
    
    Args:
        file_path (str): The full path to the CSV attendance file.
        col_index (int): The 0-based column index representing the specific session
                         to check for absentees.
        
    Returns:
        list: A list of dictionaries, where each dictionary contains keys:
              'Surname', 'Firstname', 'Matric'.
              Returns None if an error occurs.
    """
    absentees_list = [] # Initialize an empty list to store the absentee data
    
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f) # Create a CSV reader object
            rows = list(reader)    # Read all rows into a list
            
            for row in rows:
                # Skip rows that are empty or have insufficient data (less than 3 columns needed for name/matric)
                if not row or len(row) < 3:
                    continue
                
                # Junior developer: This section skips header/metadata rows.
                # If your CSV has different header rows, you can adjust these conditions.
                first_col = row[0].strip().upper()
                if first_col in ["DATE", "ACTIVITY", "SURNAME", ""]:
                    continue
                
                # Check if the column index is valid for the current row to prevent errors
                if col_index < len(row):
                    status = row[col_index].strip() # Get the attendance status from the specified column
                    
                    # --- Customizable absentee marks ---
                    # Junior developer: If your attendance sheet uses different symbols for 'absent',
                    #                       you can easily add or modify them in this list.
                    if status in ['x', 'X', '✗']: # Check for common absentee marks
                        surname = row[0].strip()   # Get surname from the first column
                        firstname = row[1].strip() # Get first name from the second column
                        matric = row[2].strip()    # Get matric number from the third column
                        
                        # Store as a dictionary for easier handling and export
                        absentees_list.append({
                            'Surname': surname,
                            'Firstname': firstname,
                            'Matric': matric
                        })
                        
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        # Catch any other potential errors during absentee extraction
        print(f"Error extracting absentees from '{file_path}': {e}")
        return None

    return absentees_list

def save_absentees(absentees_data, file_path):
    """
    Saves the list of absentees to a file (CSV or Excel).
    
    Args:
        absentees_data (list): List of dictionaries containing absentee info.
        file_path (str): The full path where the file should be saved.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Create a Pandas DataFrame from the list of dictionaries
        # Junior developer: Pandas makes it very easy to handle and export table-like data.
        df = pd.DataFrame(absentees_data)
        
        if file_path.endswith('.csv'):
            # Save as CSV file
            df.to_csv(file_path, index=False)
        elif file_path.endswith('.xlsx'):
            # Save as Excel file (requires openpyxl library)
            df.to_excel(file_path, index=False)
        else:
            print("Unsupported file format. Please use .csv or .xlsx")
            return False
            
        return True
    except Exception as e:
        print(f"Error saving absentees: {e}")
        return False
