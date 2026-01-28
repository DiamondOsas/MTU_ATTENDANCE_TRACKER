import unittest
from unittest.mock import patch
from datetime import date
import pandas as pd
from internal.frequency.freq_func import calculate_frequency

class TestFrequencyCalculation(unittest.TestCase):

    def setUp(self):
        self.dummy_file = "dummy_path.csv"
        self.start_date = date(2023, 1, 1)
        self.end_date = date(2023, 1, 31)
        self.target_marks = ['P', 'Present', '✓', 'p']

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_basic_functionality(self, mock_get_session, mock_load_df):
        """Test basic counting logic with valid inputs."""
        mock_get_session.return_value = {
            '01/01/23': [{'activity': 'Class', 'col_index': 3}],
            '02/01/23': [{'activity': 'Lab', 'col_index': 4}]
        }
        
        # Columns must be strings '0', '1', '2', '3', '4'
        data = {
            '0': ['Surname', 'Doe', 'Smith'],
            '1': ['Firstname', 'John', 'Jane'],
            '2': ['Matric NO', 'M001', 'M002'],
            '3': ['Present', 'P', 'A'], # 01/01/23
            '4': ['Present', 'A', '✓']  # 02/01/23
        }
        mock_load_df.return_value = pd.DataFrame(data)

        # Execute
        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)

        # Verify
        # John: P (3) is target, A (4) is not. Count = 1
        # Jane: A (3) is not, ✓ (4) is target. Count = 1
        
        self.assertEqual(len(results), 2)
        
        john = next(r for r in results if r['Surname'] == 'Doe')
        self.assertEqual(john['Count'], 1)
        
        jane = next(r for r in results if r['Surname'] == 'Smith')
        self.assertEqual(jane['Count'], 1)

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_date_range_filtering(self, mock_get_session, mock_load_df):
        """Test that sessions outside the date range are ignored."""
        mock_get_session.return_value = {
            '01/01/22': [{'activity': 'Old', 'col_index': 3}], # Before
            '15/01/23': [{'activity': 'In', 'col_index': 4}],  # Inside
            '01/02/23': [{'activity': 'After', 'col_index': 5}] # After
        }
        
        data = {
            '0': ['Doe'],
            '1': ['John'],
            '2': ['M001'],
            '3': ['P'],
            '4': ['P'],
            '5': ['P']
        }
        mock_load_df.return_value = pd.DataFrame(data)

        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)

        # Only col 4 should be counted (date 15/01/23 is inside Jan 2023)
        self.assertEqual(results[0]['Count'], 1)

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_no_sessions_found(self, mock_get_session, mock_load_df):
        """Test when get_session_info returns empty dict."""
        mock_get_session.return_value = {} # Empty sessions
        mock_load_df.return_value = pd.DataFrame({'0':['A']})
        
        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)
        self.assertEqual(results, [])

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_load_file_failure(self, mock_get_session, mock_load_df):
        """Test when load_attendance_file returns None."""
        mock_load_df.return_value = None
        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)
        self.assertEqual(results, [])

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_metadata_row_filtering(self, mock_get_session, mock_load_df):
        """Test that header/metadata rows are filtered out."""
        mock_get_session.return_value = {'15/01/23': [{'activity': 'In', 'col_index': 3}]}
        
        data = {
            '0': ['DATE', 'ACTIVITY', 'Surname', 'Doe', 'NaN', 'None'], 
            '1': ['x', 'x', 'Firstname', 'John', 'x', 'x'],
            '2': ['x', 'x', 'Matric', 'M001', 'x', 'x'],
            '3': ['15/01/23', 'In', 'Mark', 'P', 'P', 'P']
        }
        
        mock_load_df.return_value = pd.DataFrame(data)

        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)
        
        # Only "Doe" row should remain. 
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['Surname'], 'Doe')
        self.assertEqual(results[0]['Count'], 1)

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_missing_columns_in_df(self, mock_get_session, mock_load_df):
        """Test when a session column is in session_info but missing in DataFrame."""
        mock_get_session.return_value = {'15/01/23': [{'activity': 'In', 'col_index': 10}]}
        
        data = {
            '0': ['Doe'],
            '1': ['John'],
            '2': ['M001']
            # Col 10 missing
        }
        mock_load_df.return_value = pd.DataFrame(data)

        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)
        
        # Should run without error and count 0
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['Count'], 0)

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_multiple_sessions_same_day(self, mock_get_session, mock_load_df):
        """Test counting multiple sessions on the same date."""
        mock_get_session.return_value = {
            '01/01/23': [
                {'activity': 'Morning', 'col_index': 3},
                {'activity': 'Evening', 'col_index': 4}
            ]
        }
        
        data = {
            '0': ['Doe'],
            '1': ['John'],
            '2': ['M001'],
            '3': ['P'],
            '4': ['P']
        }
        mock_load_df.return_value = pd.DataFrame(data)

        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)
        
        self.assertEqual(results[0]['Count'], 2)

    @patch('internal.frequency.freq_func.load_attendance_file')
    @patch('internal.frequency.freq_func.get_session_info')
    def test_invalid_date_format_in_session(self, mock_get_session, mock_load_df):
        """Test that sessions with invalid date formats are ignored."""
        mock_get_session.return_value = {
            'invalid-date': [{'activity': 'Bad', 'col_index': 3}],
            '01/01/23': [{'activity': 'Good', 'col_index': 4}]
        }
        
        data = {
            '0': ['Doe'],
            '1': ['John'],
            '2': ['M001'],
            '3': ['P'],
            '4': ['P']
        }
        mock_load_df.return_value = pd.DataFrame(data)

        results = calculate_frequency(self.dummy_file, self.start_date, self.end_date, self.target_marks)

        # 'invalid-date' should be skipped, '01/01/23' counted
        self.assertEqual(results[0]['Count'], 1)

if __name__ == '__main__':
    unittest.main()
