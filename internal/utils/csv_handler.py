import pandas as pd
import os
import csv

def read_csv_robust(file_path):
    """
    Reads a CSV file into a pandas DataFrame, handling common encoding and engine errors.
    Returns an empty DataFrame on failure.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        # standard read
        return pd.read_csv(file_path, skip_blank_lines=True)
    except (pd.errors.ParserError, ValueError):
        # Fallback for files with inconsistent column counts (common in this project's attendance sheets)
        try:
            # warn_bad_lines=False and error_bad_lines=False are deprecated in newer pandas, 
            # on_bad_lines='skip' is the replacement.
            return pd.read_csv(file_path, engine='python', on_bad_lines='skip', skip_blank_lines=True)
        except Exception as e:
            print(f"Critical error reading {file_path}: {e}")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

    """Saves a DataFrame to CSV."""
def save_csv(file_path, df):
    try:
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def get_files_in_dir(directory, extension=".csv"):
    """Returns a list of files with the given extension in the directory."""
    if not os.path.exists(directory):
        return []
    return [f for f in os.listdir(directory) if f.endswith(extension)]

def get_csv_columns(file_path):
    """Returns the list of column names from a CSV file."""
    df = read_csv_robust(file_path)
    return df.columns.tolist() if not df.empty else []

def get_column_data(file_path, column_name):
    """Returns a list of values from a specific column."""
    df = read_csv_robust(file_path)
    if df.empty:
        return None
    
    if column_name in df.columns:
        return df[column_name].tolist()
    
    # Fallback: check if column_name is actually an index integer
    try:
        idx = int(column_name)
        if idx < len(df.columns):
             return df.iloc[:, idx].tolist()
    except (ValueError, TypeError):
        pass
        
    print(f"Column '{column_name}' not found in {file_path}")
    return None
