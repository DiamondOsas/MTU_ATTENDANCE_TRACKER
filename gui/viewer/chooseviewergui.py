import customtkinter as ctk
import os
from func.viewer import get_all_students_files

class ChooseViewerWindow(ctk.CTk):
    """
    A window that allows the user to choose a student data file to view or edit.
    """
    def __init__(self, viewer_type="attendance"):
        super().__init__()

        self.viewer_type = viewer_type
        if self.viewer_type == "edit":
            self.title("Choose File to Edit")
        else:
            self.title("Choose Level to View")

        self.geometry("400x400")
        self.minsize(300, 250)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_text = "Select File to Edit" if self.viewer_type == "edit" else "Select Level to View Attendance"
        self.title_label = ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=20)

        self.student_files = get_all_students_files()
        
        # Dynamically create buttons for each student file
        for i, file_name in enumerate(self.student_files):
            # Clean up file name for button text
            button_text = os.path.splitext(file_name)[0].replace('_', ' ').title()
            file_path = os.path.join("db", "allstudents", file_name)
            button = ctk.CTkButton(self, text=button_text, command=lambda path=file_path: self.open_viewer(path))
            button.grid(row=i + 2, column=0, padx=40, pady=10, sticky="ew")

        self.back_button = ctk.CTkButton(self, text="Back to Main Menu", command=self.back_to_main_menu)
        self.back_button.grid(row=len(self.student_files) + 2, column=0, padx=40, pady=20, sticky="ew")
        
        self.grid_rowconfigure(len(self.student_files) + 3, weight=1)


    def open_viewer(self, file_path):
        """
        Closes this window and opens the viewer/editor for the selected file.
        """
        self.destroy()
        from gui.viewer.viewergui import ViewerWindow
        viewer_app = ViewerWindow(file_path, self.viewer_type)
        viewer_app.mainloop()

    def back_to_main_menu(self):
        """
        Closes this window and returns to the main menu.
        """
        self.destroy()
        from gui.root import AttendanceApp
        main_app = AttendanceApp()
        main_app.mainloop()
