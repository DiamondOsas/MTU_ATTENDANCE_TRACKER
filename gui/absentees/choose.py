import customtkinter as ctk
import os
import glob

class ChooseAbsenteeFileWindow(ctk.CTkToplevel):
    """
    A window that allows the user to choose a CSV file from the 'db/attendance' directory
    to process for absentees.
    """
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Choose Attendance File")
        self.geometry("400x250")
        self.grab_set()  # Make this window modal

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 1. Title Label ---
        self.title_label = ctk.CTkLabel(self, text="Select Attendance File", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=10)

        # --- 2. File Selection Dropdown ---
        self.attendance_files = self._get_attendance_files()
        if not self.attendance_files:
            ctk.CTkLabel(self, text="No attendance files found in db/attendance/").grid(row=2, column=0, padx=20, pady=10)
            self.select_button = ctk.CTkButton(self, text="Close", command=self.destroy)
            self.select_button.grid(row=3, column=0, padx=20, pady=10)
            return

        self.selected_file_var = ctk.StringVar(value=self.attendance_files[0]) # Set initial value
        self.file_optionmenu = ctk.CTkOptionMenu(self, values=self.attendance_files,
                                                 variable=self.selected_file_var)
        self.file_optionmenu.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # --- 3. Select Button ---
        self.select_button = ctk.CTkButton(self, text="Select File", command=self._on_select_file)
        self.select_button.grid(row=3, column=0, padx=20, pady=10)

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _get_attendance_files(self):
        """
        Scans the 'db/attendance' directory for CSV files.
        Returns a list of filenames (e.g., '100level.csv').
        """
        attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..", "db", "attendance")
        attendance_dir = os.path.abspath(attendance_dir) # Get absolute path
        
        csv_files = glob.glob(os.path.join(attendance_dir, "*.csv"))
        # Return only the base names of the files
        return [os.path.basename(f) for f in csv_files]

    def _on_select_file(self):
        """
        Handles the selection of a file. Closes this window and opens the PrintAbsenteesWindow.
        """
        selected_filename = self.selected_file_var.get()
        if selected_filename:
            # Construct the full path to the selected file
            attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..", "db", "attendance")
            attendance_dir = os.path.abspath(attendance_dir)
            full_file_path = os.path.join(attendance_dir, selected_filename)
            
            self.destroy() # Close this window
            # Open the next window, passing the full file path
            from gui.absentees.printabs import PrintAbsenteesWindow
            PrintAbsenteesWindow(self.master, full_file_path)

    def _on_closing(self):
        """
        Handles the window closing event. Re-enables the master window.
        """
        self.master.deiconify() # Show the main window again
        self.destroy()
