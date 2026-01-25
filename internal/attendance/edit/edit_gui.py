from internal.choosecsv import ChooseCSVWindow
import os
from internal.attendance.excel import ExcelWindow



class ChooseEditorFileWindow(ChooseCSVWindow):
    """
    Wrapper for ChooseCSVWindow to select attendance files and open the absentee report.
    """
    def __init__(self, master):
        attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..","..", "db", "attendance")
        super().__init__(master, 
                         target_dir=attendance_dir, 
                         callback=self.open_report,
                         title="Select Attendance File")

    def open_report(self, file_path):
        """
        Callback function to open the PrintAbsenteesWindow.
        """
        ExcelWindow(self.master, file_path, editable=False)