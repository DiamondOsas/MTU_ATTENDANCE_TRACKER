import pandas as pd
import os

def _read_csv_robustly(file_path):
    """
    Reads a CSV file robustly, handling errors commonly found in this project's files.
    
    It first tries to read the file using pandas' faster 'c' engine.
    If it encounters a ParserError or ValueError (often caused by inconsistent
    column counts, like in the attendance files), it falls back to the more
    flexible, but slower, 'python' engine.
    
    When falling back, it uses `header=None` to prevent the engine from getting
    confused by trying to match header columns to data columns. This prevents
    the "Error tokenizing data. C error: Expected X fields in line Y, saw Z" crash.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        pd.DataFrame: A pandas DataFrame containing the CSV data. Returns an
                      empty DataFrame if the file cannot be read.
    """
    try:
        # Try with the default, fast C engine. This works for clean CSVs.
        return pd.read_csv(file_path, skip_blank_lines=True)
    except (pd.errors.ParserError, ValueError):
        # If parsing fails, fall back to the more lenient 'python' engine.
        # This is essential for reading the attendance files, which have
        # a variable number of columns.
        try:
            return pd.read_csv(file_path, header=None, engine='python', skip_blank_lines=True)
        except Exception as e:
            print(f"CRITICAL: The fallback CSV reader also failed for {file_path}. Error: {e}")
            return pd.DataFrame() # Return empty on critical failure
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return pd.DataFrame()

def get_students_data(level):
    """
    Reads the students data for a given level from the CSV file.
    """
    file_path = os.path.join("db", "allstudents", f"{level}.csv")
    if os.path.exists(file_path):
        return _read_csv_robustly(file_path)
    else:
        return pd.DataFrame() # Return empty DataFrame if file doesn't exist

def get_students_data_by_level(level):
    """
    Reads the all students data for a given level from the CSV file.
    """
    file_path = os.path.join("db", "allstudents", f"{level}.csv")
    if os.path.exists(file_path):
        return _read_csv_robustly(file_path)
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
    Reads student data from a given file path using a robust method.
    """
    if os.path.exists(file_path):
        return _read_csv_robustly(file_path)
    return pd.DataFrame()

def save_students_data(file_path, dataframe):
    """
    Saves the dataframe to the specified CSV file.
    """
    dataframe.to_csv(file_path, index=False)

def get_csv_columns(file_path):
    """
    Reads a CSV file robustly and returns its column headers.
    """
    if not file_path or not os.path.exists(file_path):
        return []
    try:
        df = _read_csv_robustly(file_path)
        # The list of columns will be integers if the fallback reader was used,
        # but it will prevent the application from crashing.
        return df.columns.tolist()
    except Exception as e:
        print(f"Error reading CSV columns: {e}")
        return []

def get_column_data(file_path, column_name):
    """
    Reads a specific column from a CSV file robustly and returns its data.
    """
    if not file_path or not os.path.exists(file_path) or not column_name:
        return None
    try:
        df = _read_csv_robustly(file_path)
        # If the fallback reader was used, columns are integers.
        # The calling code might send a string `column_name` which won't work.
        if column_name in df.columns:
            return df[column_name].tolist()
        else:
            # If a string name isn't found, we can try to see if it's a valid index
            try:
                col_index = int(column_name)
                if col_index in df.columns:
                    return df[col_index].tolist()
            except (ValueError, TypeError):
                # The column name is not a valid column in the dataframe.
                print(f"Column '{column_name}' not found. Available: {df.columns.tolist()}")
                return None
    except Exception as e:
        print(f"Error reading column data: {e}")
        return None
