import customtkinter as ctk

# --- Global CustomTkinter Settings ---
# These settings apply to the entire application and can be easily changed.
# 1. Appearance Mode: Controls whether the app uses a light, dark, or system-default theme.
#    Options: "Light", "Dark", "System" (System uses your OS's current theme).
ctk.set_appearance_mode("Dark")
# 2. Color Theme: Sets the primary color scheme for widgets like buttons and frames.
#    Options: "blue", "dark-blue", "green"
ctk.set_default_color_theme("dark-blue")

class AttendanceApp(ctk.CTk):
    """
    Main application class for the Attendance Tracker GUI.
    This class now serves as the main menu, providing navigation to different parts of the application.
    """
    def __init__(self):
        """
        Initializes the AttendanceApp main menu.
        This constructor sets up the main window and displays the available options.
        """
        super().__init__()
        # --- 1. Main Window Configuration ---
        self.title("Attendance Tracker - Main Menu")
        self.geometry("500x550")
        self.minsize(400, 450)

        # Configure the main window's grid layout to center the content.
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1) # Adjusted to account    for the new row
        self.grid_columnconfigure(0, weight=1)

        # --- 2. Title Label ---
        self.title_label = ctk.CTkLabel(self, text=" MTU Attendance Tracker Beta v0.0.1", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=20)

        # --- 3. Menu Buttons ---
        # Each button corresponds to a major feature of the application.
        # Clicking a button will close the main menu and open the respective window.

        self.register_button = ctk.CTkButton(self, text="Register New Students", command=self.open_register_window)
        self.register_button.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        self.edit_students_button = ctk.CTkButton(self, text="Edit Students Data", command=self.open_edit_students_window)
        self.edit_students_button.grid(row=3, column=0, padx=40, pady=10, sticky="ew")


        self.add_attendance_button = ctk.CTkButton(self, text="Add Attendance", command=self.open_add_attendance_window)
        self.add_attendance_button.grid(row=4, column=0, padx=40, pady=10, sticky="ew")

        self.view_attendance_button = ctk.CTkButton(self, text="View Attendance", command=self.open_viewer_window)
        self.view_attendance_button.grid(row=5, column=0, padx=40, pady=10, sticky="ew")

        self.print_absentees_button = ctk.CTkButton(self, text="Print Absentees", command=self.open_absentees_viewer_window)
        self.print_absentees_button.grid(row=6, column=0, padx=40, pady=10, sticky="ew")

        self.settings_button = ctk.CTkButton(self, text="Settings", command=self.placeholder_command)
        self.settings_button.grid(row=7, column=0, padx=40, pady=10, sticky="ew")

        self.restore_button = ctk.CTkButton(self, text="Restore Database Backup", command=self.open_revert_window, fg_color="#7743F2", hover_color="#B71C1C")
        self.restore_button.grid(row=8, column=0, padx=40, pady=10, sticky="ew")


    def open_register_window(self):
        """
        Closes the main menu and opens the student registration window
        """
        self.withdraw()
        # We import here to avoid a circular import at the module level.
        from internal.reigister.register_gui import RegisterWindow
        RegisterWindow(self)    

    def open_add_attendance_window(self):
        """
        Closes the main menu and opens the add attendance window.
        """
        self.withdraw()
        # We import here to avoid a circular import at the module level.
        from internal.attendance.create.create_gui import AddAttendanceWindow
        AddAttendanceWindow(self)

    def open_viewer_window(self):
        """
        Closes the main menu and opens the attendance viewer window.
        """
        self.withdraw()
        # We import here to avoid a circular import at the module level.
        from internal.attendance.view.viewer_gui import ChooseViewerFileWindow
        ChooseViewerFileWindow(self)  #
        
    def open_edit_students_window(self):
        """
        Closes the main menu and opens the window to choose a student list to edit.
        """
        self.withdraw()
        from internal. import ChooseViewerWindow
        ChooseViewerWindow(self, viewer_type="edit") # Pass a parameter to distinguish

    def open_absentees_viewer_window(self):
        """
        Closes the main menu and opens the window to choose an attendance file for absentee printing.
        """
        self.withdraw()
        from internal.absentees.abs_gui import ChooseAbsenteeFileWindow
        absentees_app = ChooseAbsenteeFileWindow(self)

    def open_revert_window(self):
        """
        Closes the main menu and opens the database restore window.
        """
        self.withdraw()
        from internal.revertdb import RevertDBWindow
        revert_app = RevertDBWindow(self)

    def placeholder_command(self):
        """
        A placeholder command for buttons that don't have functionality yet.
        In a real application, each button would have its own method like open_register_window.
        """
        print("This button's functionality is not yet implemented.")

