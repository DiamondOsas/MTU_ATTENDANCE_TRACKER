from internal.records.records_gui import ChooseRecordFileWindow

class ChooseAttendeesFileWindow(ChooseRecordFileWindow):
    def __init__(self, master):
        super().__init__(master, record_type="Attendees", target_marks=['✓'], export_prefix="ATTENDEES")
