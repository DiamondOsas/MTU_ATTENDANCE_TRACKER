import customtkinter as ctk
import pandas as pd
from func.viewer import get_attendance_data, get_all_students_data

class ViewerWindow(ctk.CTk):
    """
    A window to display attendance data for a selected level.
    """
    def __init__(self, level):
        super().__init__()
        self.level = level

        self.title(f"{self.level.capitalize()} Level Attendance Viewer")
        self.geometry("800x600")
        self.minsize(700, 500)

        self.grid_row_configure(0, weight=0)
        self.grid_row_configure(1, weight=1)
        self.grid_column_configure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text=f"{self.level.capitalize()} Level Attendance", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10)

        self.attendance_frame = ctk.CTkFrame(self)
        self.attendance_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.attendance_frame.grid_column_configure(0, weight=1)
        self.attendance_frame.grid_row_configure(0, weight=1)

        self.display_attendance()

        self.back_button = ctk.CTkButton(self, text="Back to Level Selection", command=self.back_to_level_selection)
        self.back_button.grid(row=2, column=0, padx=20, pady=10)

    def display_attendance(self):
        """
        Fetches and displays attendance data in a scrollable text widget.
        """
        attendance_df = get_attendance_data(self.level)
        all_students_df = get_all_students_data(self.level)

        if attendance_df.empty and all_students_df.empty:
            display_text = "No attendance or student data available for this level."
        else:
            # For now, just display the raw dataframes. This can be enhanced later.
            display_text = "--- ATTENDANCE DATA ---\n"
            display_text += attendance_df.to_string(index=False) if not attendance_df.empty else "No attendance records.\n"
            display_text += "\n\n--- ALL STUDENTS DATA ---\n"
            display_text += all_students_df.to_string(index=False) if not all_students_df.empty else "No student records.\n"

        self.attendance_text_widget = ctk.CTkTextbox(self.attendance_frame, wrap="word")
        self.attendance_text_widget.insert("1.0", display_text)
        self.attendance_text_widget.configure(state="disabled") # Make it read-only
        self.attendance_text_widget.grid(row=0, column=0, sticky="nsew")

    def back_to_level_selection(self):
        """
        Closes this window and returns to the level selection window.
        """
        self.destroy()
        from gui.viewer.chooseviewergui import ChooseViewerWindow
        choose_level_app = ChooseViewerWindow()
        choose_level_app.mainloop()
