
import csv
import os

def normalize_matric(val):
    """
    Helper to normalize matric numbers.
    - Converts to string.
    - Strips whitespace.
    - Removes trailing '.0' if present.
    """
    s = str(val).strip()
    if s.endswith(".0"):
        return s[:-2]
    return s

def test_matric_matching():
    # Simulate data from the attendance sheet (DB)
    # These are usually strings as read by csv.reader
    db_students = [
        ["Doe", "John", "250101"],
        ["Smith", "Jane", "250102"],
        ["Brown", "Bob", "FOUNDATION"]
    ]
    
    # Simulate data from external CSV (read by pandas)
    # Pandas might read integers as floats if there are NaNs elsewhere, or just as ints.
    # Case 1: Floats (e.g. 250101.0)
    external_data_floats = [250101.0, 250102.0, "FOUNDATION"]
    
    # Case 2: Ints
    external_data_ints = [250101, 250102, "FOUNDATION"]
    
    # Case 3: Strings
    external_data_strings = ["250101", "250102", "FOUNDATION"]

    print("--- Current Implementation ---")
    # Current implementation in func/attendance.py:
    # extracted_matric_numbers = [str(x).strip() for x in matric_numbers_list]
    
    def check_implementation(label, external_list):
        extracted_matric_numbers = [str(x).strip() for x in external_list]
        print(f"\nTesting {label}:")
        print(f"Extracted list: {extracted_matric_numbers}")
        
        matches = 0
        for student in db_students:
            matric_no = str(student[2]).strip()
            if matric_no in extracted_matric_numbers:
                matches += 1
            else:
                print(f"  Failed match: {matric_no}")
        print(f"  Total Matches: {matches}/{len(db_students)}")

    check_implementation("Floats", external_data_floats)
    check_implementation("Ints", external_data_ints)
    check_implementation("Strings", external_data_strings)

    print("\n--- Proposed Fix ---")
    def check_fix(label, external_list):
        extracted_matric_numbers = [normalize_matric(x) for x in external_list]
        print(f"\nTesting {label} with fix:")
        print(f"Extracted list: {extracted_matric_numbers}")
        
        matches = 0
        for student in db_students:
            matric_no = normalize_matric(student[2]) # Normalize DB side too just in case
            if matric_no in extracted_matric_numbers:
                matches += 1
            else:
                print(f"  Failed match: {matric_no}")
        print(f"  Total Matches: {matches}/{len(db_students)}")

    check_fix("Floats", external_data_floats)

if __name__ == "__main__":
    test_matric_matching()
