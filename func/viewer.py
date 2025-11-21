import pandas as pd
import os

def get_students_data(level):
    """
    Reads the students data for a given level from the CSV file.
    """
    file_path = os.path.join("db", "allstudents", f"{level}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        return pd.DataFrame() # Return empty DataFrame if file doesn't exist

def get_students_data_by_level(level):
    """
    Reads the all students data for a given level from the CSV file.
    """
    file_path = os.path.join("db", "allstudents", f"{level}.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        return pd.DataFrame() # Return empty DataFrame if file doesn't exist


def get_all_students_files():
    """
    Gets a list of all CSV files in the db/allstudents directory.
    """
    directory = os.path.join("db", "allstudents")
    if os.path.exists(directory):
        return [f for f in os.listdir(directory) if f.endswith(".csv")]
    return []

def get_students_data_from_file(file_path):
    """
    Reads student data from a given file path.
    This function is designed to be robust against malformed CSV files,
    such as the attendance sheets which can have inconsistent column counts.
    It attempts a fast read first, then falls back to a more flexible method
    to prevent 'ParserError: Error tokenizing data'.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()
    
    try:
        # Try reading with the default, fast 'c' engine. This works for well-formed CSVs.
        return pd.read_csv(file_path)
    except (pd.errors.ParserError, ValueError) as e:
        # If a ParserError occurs, it's likely due to ragged columns (inconsistent column counts),
        # which is common in the attendance files as new dates are added.
        print(f"Parsing with C engine failed: {e}. Falling back to Python engine.")
        try:
            # The 'python' engine is more flexible and can handle ragged CSVs
            # when used with `header=None`. This will prevent the app from crashing.
            # The viewer will display the data with default integer column headers.
            return pd.read_csv(file_path, header=None, engine='python')
        except Exception as fallback_e:
            print(f"Critical: Fallback CSV reading with Python engine also failed for {file_path}: {fallback_e}")
            return pd.DataFrame()
    except Exception as general_e:
        print(f"An unexpected error occurred while reading {file_path}: {general_e}")
        return pd.DataFrame()

def save_students_data(file_path, dataframe):
    """
    Saves the dataframe to the specified CSV file.
    """
    dataframe.to_csv(file_path, index=False)

def get_csv_columns(file_path):
    """
    Reads a CSV file and returns its column headers.
    """
    if not file_path or not os.path.exists(file_path):
        return []
    try:
        df = pd.read_csv(file_path)
        return df.columns.tolist()
    except Exception as e:
        print(f"Error reading CSV columns: {e}")
        return []

def get_column_data(file_path, column_name):
    """
    Reads a specific column from a CSV file and returns its data.
    """
    if not file_path or not os.path.exists(file_path) or not column_name:
        return None
    try:
        df = pd.read_csv(file_path)
        if column_name in df.columns:
            return df[column_name].tolist()
        else:
            return None
    except Exception as e:
        print(f"Error reading column data: {e}")
        return None
