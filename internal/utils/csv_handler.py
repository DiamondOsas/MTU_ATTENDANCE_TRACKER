import pandas as pd
import os
import csv

def _get_max_cols(file_path):
    """
    Scans the file to find the maximum number of columns (commas + 1).
    Useful for ragged CSVs where header has fewer columns than data.
    """
    max_cols = 0
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > max_cols:
                    max_cols = len(row)
    except Exception as e:
        print(f"Error identifying max columns in {file_path}: {e}")
    return max_cols

def read_csv_robust(file_path):
    """
    Reads a CSV file into a pandas DataFrame, handling common encoding and engine errors.
    Supports ragged CSVs (variable column lengths) by detecting max columns.
    Returns an empty DataFrame on failure.
    """
    if not os.path.exists(file_path):
        return pd.DataFrame()

    try:
        # Attempt 1: Standard read
        return pd.read_csv(file_path, skip_blank_lines=True, encoding='utf-8')
    except (pd.errors.ParserError, ValueError):
        # Fallback for files with inconsistent column counts (ragged CSVs)
        try:
            max_cols = _get_max_cols(file_path)
            # Read with manually specified column names to force reading all data
            df = pd.read_csv(
                file_path, 
                header=None, 
                names=range(max_cols), 
                engine='python', 
                skip_blank_lines=True,
                encoding='utf-8'
            )
            
            # Heuristic: Promote first row to header if we fell back to this method
            # (Standard CSVs usually have a header in the first row)
            if not df.empty:
                first_row = df.iloc[0]
                
                # Create clean header names
                new_header = []
                for i, val in enumerate(first_row):
                    if pd.isna(val) or str(val).strip() == "":
                        new_header.append(f"Column {i+1}")
                    else:
                        new_header.append(str(val).strip())
                
                df.columns = new_header
                df = df.iloc[1:].reset_index(drop=True)
                
            return df
        except Exception as e:
            print(f"Critical error reading {file_path} with fallback: {e}")
            return pd.DataFrame()
    except UnicodeDecodeError:
        # Fallback for encoding issues
        try:
             return pd.read_csv(file_path, skip_blank_lines=True, encoding='latin1')
        except Exception as e:
             print(f"Encoding error reading {file_path}: {e}")
             return pd.DataFrame()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

def save_csv(file_path, df):
    """Saves a DataFrame to CSV."""
    try:
        df.to_csv(file_path, index=False, encoding='utf-8')
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
