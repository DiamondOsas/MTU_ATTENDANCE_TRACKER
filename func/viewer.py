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
    """
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
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
