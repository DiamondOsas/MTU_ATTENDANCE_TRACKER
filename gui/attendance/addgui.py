import customtkinter as ctk
from tkinter import messagebox
import os
import sys

# Add the parent directory to the path so we can import from the func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from func.attendance import get_attendance_files, load_csv_file
from gui.viewergui import ViewerWindow

class AddAttendanceWindow(ctk.CTkToplevel):
    """
    A window for selecting an attendance sheet, a program type, and managing attendance.
    """
    def __init__(self, parent):
        """
        Initializes the AddAttendanceWindow.

        Args:
            parent: The parent window that opened this window.
        """
        super().__init__(parent)
        self.parent = parent
        self.loaded_csv_path = None # To store the path of the loaded CSV

        # --- 1. Window Configuration ---
        self.title("Add Attendance")
        self.geometry("500x450")
        self.resizable(False, False)

        # Center the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # --- 2. Title Label ---
        self.title_label = ctk.CTkLabel(self, text="Add Attendance", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # --- 3. CSV File Selection ---
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)

        self.select_file_label = ctk.CTkLabel(self.file_frame, text="Choose Attendance Sheet:")
        self.select_file_label.grid(row=0, column=0, padx=20, pady=(10, 5))

        # Get the list of available attendance CSV files.
        self.attendance_files = get_attendance_files()
        
        self.file_dropdown = ctk.CTkComboBox(
            self.file_frame,
            values=self.attendance_files if self.attendance_files else ["No files found"],
            width=300
        )
        self.file_dropdown.grid(row=1, column=0, padx=20, pady=10)
        if not self.attendance_files:
            self.file_dropdown.set("No files found")
            self.file_dropdown.configure(state="disabled")

        # --- 4. Program Type Selection ---
        self.program_frame = ctk.CTkFrame(self)
        self.program_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.program_frame.grid_columnconfigure(0, weight=1)

        self.select_program_label = ctk.CTkLabel(self.program_frame, text="Choose Program Type:")
        self.select_program_label.grid(row=0, column=0, padx=20, pady=(10, 5))

        # --- Easily modifiable list of programs ---
        # To add more options, just add a new string to this list.
        # For example: ["Morning", "Evening", "Special Program", "Mid-week Service"]
        self.program_types = ["MORNING", "EVENING", "MANNA WATER", "PMCH", "MTU PRAYS", "SPECIAL SERVICE"]

        self.program_dropdown = ctk.CTkComboBox(
            self.program_frame,
            values=self.program_types,
            width=300
        )
        self.program_dropdown.grid(row=1, column=0, padx=20, pady=10)
        self.program_dropdown.set(self.program_types[0]) # Set a default value

        # --- 5. Action Buttons ---
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=3, column=0, padx=20, pady=20)
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # This button will load the selected CSV file. (Functionality not yet implemented)
        self.load_csv_button = ctk.CTkButton(
            self.button_frame,
            text="Load CSV File",
            command=self.load_csv_file_handler,
        )
        self.load_csv_button.grid(row=0, column=0, padx=10, pady=10)

        # This button will handle adding attendance.
        self.add_attendance_button = ctk.CTkButton(
            self.button_frame,
            text="Add Attendance",
            command=self.add_attendance_placeholder,
            state="disabled" # Disabled until a file is loaded
        )
        self.add_attendance_button.grid(row=0, column=1, padx=10, pady=10)

        # --- New Label for loaded file ---
        self.loaded_file_label = ctk.CTkLabel(self, text="No external file loaded.", font=ctk.CTkFont(size=12))
        self.loaded_file_label.grid(row=4, column=0, padx=30, pady=(0,0), sticky="s")
        
        # --- 6. Back Button ---
        self.back_button = ctk.CTkButton(self, text="Back to Menu", command=self.close_window)
        self.back_button.grid(row=5, column=0, padx=20, pady=20, sticky="s")


    def load_csv_file_handler(self):
        """
        Handles the 'Load CSV File' button click. Opens a file dialog
        and updates the GUI to show the selected file.
        """
        file_path = load_csv_file()
        if file_path:
            self.loaded_csv_path = file_path
            file_name = os.path.basename(file_path)
            self.loaded_file_label.configure(text=f"Loaded: {file_name}")
            
            # Open the viewer window immediately after loading the file
            self.open_viewer_for_column_selection()

    def open_viewer_for_column_selection(self):
        """
        Opens the ViewerWindow to allow the user to select the matric number column.
        """
        if self.loaded_csv_path:
            # Hide the current window
            self.withdraw()
            # Open the viewer window, passing the file path and a specific mode
            viewer = ViewerWindow(self, self.loaded_csv_path, editable=False, mode="select_column")
            viewer.protocol("WM_DELETE_WINDOW", self.on_viewer_close)

    def on_viewer_close(self):
        """
        Callback function for when the viewer window is closed.
        """
        # Show the AddAttendanceWindow again
        self.deiconify()
        # You can add logic here to retrieve data from the viewer if needed
        # For example: selected_column = viewer.selected_column
        # For now, we just re-show the window.
        print("Viewer closed, returning to Add Attendance.")


    def load_csv_placeholder(self):
        """
        Placeholder function for the 'Load CSV File' button.
        In the future, this will load the selected CSV and enable the 'Add Attendance' button.
        """
        selected_file = self.file_dropdown.get()
        selected_program = self.program_dropdown.get()
        messagebox.showinfo("Placeholder", f"This will load '{selected_file}' for the '{selected_program}' program.")
        # For now, we'll just enable the other button as a demonstration.
        self.add_attendance_button.configure(state="normal")

    def add_attendance_placeholder(self):
        """
        Placeholder function for the 'Add Attendance' button.
        """
        messagebox.showinfo("Placeholder", "This will handle the attendance marking process.")

    def close_window(self):
        """
        Closes this window and shows the parent window again.
        """
        self.parent.deiconify()
        self.destroy()

if __name__ == '__main__':
    # This allows you to run and test this GUI file directly.
    # You would need a dummy parent window for it to work.
    class DummyRoot(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Dummy Parent")
            self.geometry("700x500")
            self.withdraw() # Hide the dummy root
            app = AddAttendanceWindow(self)
            app.protocol("WM_DELETE_WINDOW", self.quit)

    root = DummyRoot()
    root.mainloop()
