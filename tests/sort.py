import unittest
import os
import csv
import sys
import tempfile
import shutil
from datetime import datetime

# Add the project root to sys.path so we can import internal modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from internal.maintain.prepare import sort_attendance_files

class TestSortAttendanceFiles(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure mimicking the project
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        self.db_dir = os.path.join(self.test_dir, "db", "attendance")
        os.makedirs(self.db_dir)

    def tearDown(self):
        # Restore CWD and clean up
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_csv(self, filename, content):
        path = os.path.join(self.db_dir, filename)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(content)
        return path

    def read_csv(self, filename):
        path = os.path.join(self.db_dir, filename)
        with open(path, 'r', newline='', encoding='utf-8') as f:
            return list(csv.reader(f))

    def test_standard_sort(self):
        """Test basic sorting by date."""
        content = [
            ["Surname", "Firstname", "Matric NO", "", "", ""],
            [],
            ["DATE", "", "", "02/01/26", "01/01/26", "03/01/26"],
            ["ACTIVITY", "", "", "SERVICE", "SERVICE", "SERVICE"],
            ["Student1", "A", "123", "P", "A", "P"]
        ]
        self.create_csv("standard.csv", content)
        
        sort_attendance_files()
        
        rows = self.read_csv("standard.csv")
        dates = rows[2][3:]
        self.assertEqual(dates, ["01/01/26", "02/01/26", "03/01/26"])
        
        # Check data moved correctly
        student_row = rows[4][3:]
        self.assertEqual(student_row, ["A", "P", "P"])

    def test_priority_sort(self):
        """Test sorting by activity priority when dates are the same."""
        # Priorities: MORNING SERVICE (0) < EVENING SERVICE (1) < BIBLE STUDY (5)
        content = [
            ["Surname", "Firstname", "Matric NO", "", "", ""],
            [],
            ["DATE", "", "", "01/01/26", "01/01/26", "01/01/26"],
            ["ACTIVITY", "", "", "BIBLE STUDY", "MORNING SERVICE", "EVENING SERVICE"],
            ["Student1", "A", "123", "BS", "MS", "ES"]
        ]
        self.create_csv("priority.csv", content)
        
        sort_attendance_files()
        
        rows = self.read_csv("priority.csv")
        activities = rows[3][3:]
        self.assertEqual(activities, ["MORNING SERVICE", "EVENING SERVICE", "BIBLE STUDY"])
        
        # Check data aligned
        student_marks = rows[4][3:]
        self.assertEqual(student_marks, ["MS", "ES", "BS"])

    def test_invalid_date_format(self):
        """Test handling of invalid dates (defaults to datetime.min)."""
        content = [
            ["Surname", "Firstname", "Matric NO", "", "", ""],
            [],
            ["DATE", "", "", "InvalidDate", "01/01/26", ""],
            ["ACTIVITY", "", "", "A1", "A2", "A3"],
            ["S1", "F", "M", "1", "2", "3"]
        ]
        self.create_csv("invalid.csv", content)
        
        sort_attendance_files()
        
        rows = self.read_csv("invalid.csv")
        dates = rows[2][3:]
        # logic says d_obj is datetime.min if invalid.
        # So InvalidDate (min) -> "" (min) -> 01/01/26 (real date)
        # Stability for equal dates (both min) depends on original order or priority.
        # Priority for unknown activities is 999.
        # So "InvalidDate" (A1=999) vs "" (A3=999). Stable sort preserves order.
        
        self.assertEqual(dates[2], "01/01/26") # The real date should be last
        self.assertIn("InvalidDate", dates[:2]) # The invalid ones first

    def test_short_file(self):
        """Test file that is too short to be processed."""
        content = [
            ["Surname", "Firstname", "Matric NO"]
        ]
        self.create_csv("short.csv", content)
        
        sort_attendance_files()
        
        # Should remain unchanged
        rows = self.read_csv("short.csv")
        self.assertEqual(rows, content)

    def test_missing_markers(self):
        """Test file missing DATE or ACTIVITY rows."""
        content = [
            ["Surname", "Firstname", "Matric NO"],
            [],
            ["NOT_DATE", "something"],
            ["NOT_ACTIVITY", "something else"]
        ]
        self.create_csv("missing.csv", content)
        
        sort_attendance_files()
        
        rows = self.read_csv("missing.csv")
        self.assertEqual(rows[2][0], "NOT_DATE")

    def test_mixed_formats(self):
        """Test mixing dd/mm/yy and dd/mm/YYYY."""
        content = [
            ["Header", "", "", "", ""],
            [],
            ["DATE", "", "", "01/01/2026", "01/01/25"],
            ["ACTIVITY", "", "", "A", "B"],
        ]
        self.create_csv("mixed_formats.csv", content)
        
        sort_attendance_files()
        
        rows = self.read_csv("mixed_formats.csv")
        dates = rows[2][3:]
        # 01/01/25 comes before 01/01/2026
        self.assertEqual(dates, ["01/01/25", "01/01/2026"])

if __name__ == '__main__':
    unittest.main()
