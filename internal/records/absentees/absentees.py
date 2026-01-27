from internal.records.records_gui import ChooseRecordFileWindow

class ChooseAbsenteeFileWindow(ChooseRecordFileWindow):
    def __init__(self, master):
        super().__init__(master, record_type="Absentees", target_marks=['x', 'X', '✗'], export_prefix="ABSENTEES")
