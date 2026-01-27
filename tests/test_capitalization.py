import os

file_paths = ["db/attendance/100level.csv", "db/attendance/200level.csv", "db/attendance/test.csv"]

for file_path in file_paths:
    base = os.path.splitext(os.path.basename(file_path))[0]
    print(f"Base: {base}")
    print(f"  upper():      {base.upper()}")
    print(f"  capitalize(): {base.capitalize()}")
    print(f"  title():      {base.title()}")