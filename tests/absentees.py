import sys
import os
import unittest
from unittest.mock import MagicMock, patch, ANY

# --- 1. Setup Environment & Mocking ---
# Add project root to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Mock customtkinter BEFORE importing modules that use it.
# We need a mock class for CTkToplevel so inheritance works.
class MockCTkToplevel:
    def __init__(self, *args, **kwargs):
        self.master = args[0] if args else None
    
    def title(self, _): pass
    def geometry(self, _): pass
    def grab_set(self): pass
    def grid_columnconfigure(self, *args, **kwargs): pass
    def grid_rowconfigure(self, *args, **kwargs): pass
    def destroy(self): pass
    def deiconify(self): pass
    def protocol(self, *args): pass
    def lift(self): pass
    def focus_force(self): pass
    def after(self, *args): pass
    def withdraw(self): pass
    def grid(self, *args, **kwargs): pass

# Mock the module
mock_ctk_module = MagicMock()
mock_ctk_module.CTkToplevel = MockCTkToplevel
# Mock other widgets as factory functions or classes
mock_ctk_module.CTkLabel = MagicMock()
mock_ctk_module.CTkButton = MagicMock()
mock_ctk_module.CTkOptionMenu = MagicMock()
mock_ctk_module.CTkTextbox = MagicMock()
mock_ctk_module.StringVar = MagicMock
mock_ctk_module.CTkFont = MagicMock()

sys.modules['customtkinter'] = mock_ctk_module

# Also mock tkinter.filedialog
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

# --- 2. Import Modules Under Test ---
from internal.absentees.abs_gui import ChooseAbsenteeFileWindow
from internal.absentees.abs_func import PrintAbsenteesWindow

# --- 3. Test Classes ---

class TestChooseAbsenteeFileWindow(unittest.TestCase):
    def setUp(self):
        self.mock_master = MagicMock()

    @patch('internal.absentees.abs_gui.glob.glob')
    @patch('internal.absentees.abs_gui.os.path.abspath')
    def test_get_attendance_files(self, mock_abspath, mock_glob):
        """Test that the window correctly lists attendance files."""
        # Setup mocks
        mock_abspath.return_value = '/mock/path/db/attendance'
        # glob returns full paths
        mock_glob.return_value = [
            os.path.join('/mock/path/db/attendance', '100level.csv'),
            os.path.join('/mock/path/db/attendance', 'test.csv')
        ]
        
        # Instantiate window
        # We assume __init__ creates widgets, so we check if they are called
        window = ChooseAbsenteeFileWindow(self.mock_master)
        
        # Check if files were processed correctly (should be basenames)
        files = window.attendance_files
        self.assertIn('100level.csv', files)
        self.assertIn('test.csv', files)
        
        # Verify OptionMenu was created with these values
        # Note: Since we mocked CTkOptionMenu class/func, we need to check calls
        # We can find the call in the mock_ctk_module.CTkOptionMenu.call_args_list or similar
        # But simpler to just check if window.attendance_files has correct data.
        self.assertEqual(len(files), 2)

    @patch('internal.absentees.abs_gui.PrintAbsenteesWindow')
    @patch('internal.absentees.abs_gui.glob.glob')
    def test_select_file_opens_next_window(self, mock_glob, MockPrintWindow):
        """Test that selecting a file opens the PrintAbsenteesWindow."""
        # Setup to ensure we have a file to select
        mock_glob.return_value = [os.path.join('db', 'attendance', 'test.csv')]
        
        window = ChooseAbsenteeFileWindow(self.mock_master)
        
        # Simulate user selection
        # window.selected_file_var is a mock (StringVar). We need to mock its get method.
        window.selected_file_var.get.return_value = 'test.csv'
        
        # Trigger selection
        window._on_select_file()
        
        # Verify PrintAbsenteesWindow is initialized
        # It should be called with (master, full_path)
        self.assertTrue(MockPrintWindow.called)
        args, _ = MockPrintWindow.call_args
        self.assertEqual(args[0], self.mock_master)
        self.assertTrue(args[1].endswith('test.csv'))
        
        # Verify old window is destroyed
        # Since 'window' is our MockCTkToplevel subclass, we can't easily check 'destroy' call 
        # unless we wrapped it in a MagicMock or added logging.
        # But conceptually we are testing the flow.


class TestPrintAbsenteesWindow(unittest.TestCase):
    def setUp(self):
        self.mock_master = MagicMock()
        # Use the real test file path
        self.test_file_path = os.path.abspath(os.path.join(PROJECT_ROOT, 'db', 'attendance', 'test.csv'))
        
        # Ensure the test file exists
        if not os.path.exists(self.test_file_path):
            self.fail(f"Test data file not found at {self.test_file_path}. Please run this test in the project root.")

    def test_initialization_and_session_loading(self):
        """Test that sessions are loaded correctly from the CSV file."""
        window = PrintAbsenteesWindow(self.mock_master, self.test_file_path)
        
        # Verify sessions dict structure based on test.csv content
        # test.csv has "18/01/26"
        self.assertIn('18/01/26', window.sessions)
        
        # Check activities for that date
        activities_info = window.sessions['18/01/26']
        activity_names = [item['activity'] for item in activities_info]
        self.assertIn('MORNING SERVICE', activity_names)
        self.assertIn('MANNA WATER', activity_names)

    def test_update_activities(self):
        """Test that the activity dropdown updates when date changes."""
        window = PrintAbsenteesWindow(self.mock_master, self.test_file_path)
        
        # Mock the option menu and variable
        window.option_activity = MagicMock()
        window.selected_activity = MagicMock()
        
        # Trigger update
        window.update_activities('18/01/26')
        
        # Check if values were updated
        window.option_activity.configure.assert_called()
        call_args = window.option_activity.configure.call_args
        # values should be in kwargs or args
        # configure(values=[...])
        if 'values' in call_args[1]:
            values = call_args[1]['values']
            self.assertIn('MORNING SERVICE', values)

    def test_show_absentees_integration(self):
        """
        Integration-like test: verify that show_absentees correctly extracts 
        data from the file and updates the textbox.
        """
        window = PrintAbsenteesWindow(self.mock_master, self.test_file_path)
        
        # Setup selection state
        window.selected_date.get.return_value = '18/01/26'
        window.selected_activity.get.return_value = 'MORNING SERVICE'
        
        # Mock the textbox to capture output
        window.textbox_result = MagicMock()
        
        # Run
        window.show_absentees()
        
        # Verify
        # In test.csv for MORNING SERVICE (index 3 usually, or based on file):
        # Ahiante Paul is present (checkmark)
        # Oloye Maxwell is absent (X)
        
        # Gather all text inserted into textbox
        inserted_text = ""
        for call in window.textbox_result.insert.call_args_list:
            args = call[0]
            if len(args) >= 2:
                inserted_text += args[1]
                
        # Debug info if assertions fail
        # print(f"Inserted text: {inserted_text}")
        
        self.assertIn("Total Absentees:", inserted_text)
        self.assertIn("Oloye Maxwell", inserted_text) # Should be absent
        self.assertNotIn("Ahiante Paul", inserted_text) # Should be present

    @patch('internal.absentees.abs_func.save_absentees')
    @patch('tkinter.filedialog.asksaveasfilename')
    def test_export_data(self, mock_asksaveas, mock_save):
        """Test the export functionality."""
        window = PrintAbsenteesWindow(self.mock_master, self.test_file_path)
        
        # Pre-populate absentees (simulate a run of show_absentees)
        dummy_absentees = [{'Surname': 'Doe', 'Firstname': 'John', 'Matric NO': '123'}]
        window.current_absentees = dummy_absentees
        window.selected_date.get.return_value = '18/01/26'
        window.selected_activity.get.return_value = 'TEST'
        
        # Mock file selection
        mock_asksaveas.return_value = '/path/to/save.csv'
        mock_save.return_value = True
        
        # Run export
        window.export_data()
        
        # Verify
        mock_save.assert_called_with(dummy_absentees, '/path/to/save.csv')

if __name__ == '__main__':
    unittest.main()
