import customtkinter as ctk
from tkinter import messagebox
import os
import sys
# from tkcalendar import Calendar # Removed tkcalendar import
from datetime import date, timedelta, datetime

# Add the parent directory to the path so we can import from the func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from func.attendance import get_attendance_files, load_csv_file, update_attendance_sheet
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
        self.selected_date = date.today().strftime('%d/%m/%y') # To store the selected date, default to today

        # --- 1. Window Configuration ---
        self.title("Add Attendance")
        self.geometry("500x600") # Increased height for new widgets
        self.resizable(False, False)

        # Center the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1) # Adjusted row configure

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

        self.select_program_label = ctk.CTkLabel(self.program_frame, text="Choose Program Type: ")
        self.select_program_label.grid(row=0, column=0, padx=20, pady=(10, 5))

        # --- Easily modifiable list of programs ---
        # To add more options, just add a new string to this list.
        # For example: ["Morning", "Evening", "Special Program", "Mid-week Service"]
        self.program_types = ["MORNING SERVICE", "EVENING SERVICE", "MANNA WATER", "PMCH", "MTU PRAYS", "SPECIAL SERVICE"]

        self.program_dropdown = ctk.CTkComboBox(
            self.program_frame,
            values=self.program_types,
            width=300
        )
        self.program_dropdown.grid(row=1, column=0, padx=20, pady=10)
        self.program_dropdown.set(self.program_types[0]) # Set a default value

        # --- 4.5 Date Selection (Custom Calendar) ---
        self.date_frame = ctk.CTkFrame(self)
        self.date_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.date_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.date_label = ctk.CTkLabel(self.date_frame, text="Select Date:")
        self.date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.date_entry = ctk.CTkEntry(self.date_frame, width=120)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.date_entry.insert(0, self.selected_date)
        self.date_entry.bind("<FocusOut>", self.validate_date_entry)

        self.prev_day_button = ctk.CTkButton(self.date_frame, text="<", width=30, command=lambda: self.adjust_date(-1))
        self.prev_day_button.grid(row=0, column=2, padx=(5, 2), pady=5, sticky="w")

        self.next_day_button = ctk.CTkButton(self.date_frame, text=">", width=30, command=lambda: self.adjust_date(1))
        self.next_day_button.grid(row=0, column=3, padx=(2, 5), pady=5, sticky="e")

        # --- 5. Action Buttons ---
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=4, column=0, padx=20, pady=20)
        self.button_frame.grid_columnconfigure(0, weight=1)

        # This button will load the selected CSV file.
        self.load_csv_button = ctk.CTkButton(
            self.button_frame,
            text="Load External CSV File",
            command=self.load_csv_file_handler,
        )
        self.load_csv_button.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # This button will handle adding attendance.
        self.add_attendance_button = ctk.CTkButton(
            self.button_frame,
            text="Add Attendance",
            command=self.add_attendance_handler,
            state="disabled" # Disabled until a file is loaded
        )
        self.add_attendance_button.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")

        # --- New Label for loaded file ---
        self.loaded_file_label = ctk.CTkLabel(self, text="No external file loaded.", font=ctk.CTkFont(size=12))
        self.loaded_file_label.grid(row=5, column=0, padx=30, pady=(0,0), sticky="s")
        
        # --- 6. Back Button ---
        self.back_button = ctk.CTkButton(self, text="Back to Menu", command=self.close_window)
        self.back_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

    def validate_date_entry(self, event=None):
        """
        Validates the date entered in the entry field.
        """
        date_str = self.date_entry.get()
        try:
            # Attempt to parse the date in dd/mm/yy format
            datetime.strptime(date_str, '%d/%m/%y')
            self.selected_date = date_str
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter the date in DD/MM/YY format.")
            self.date_entry.delete(0, ctk.END)
            self.date_entry.insert(0, date.today().strftime('%d/%m/%y'))
            self.selected_date = date.today().strftime('%d/%m/%y')

    def adjust_date(self, delta):
        """
        Adjusts the selected date by the given delta (number of days).
        """
        current_date = datetime.strptime(self.selected_date, '%d/%m/%y').date()
        new_date = current_date + timedelta(days=delta)
        self.selected_date = new_date.strftime('%d/%m/%yy')
        self.date_entry.delete(0, ctk.END)
        self.date_entry.insert(0, self.selected_date)

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
        self.add_attendance_button.configure(state="normal")
        # You can add logic here to retrieve data from the viewer if needed
        # For example: selected_column = viewer.selected_column
        # For now, we just re-show the window.
        print("Viewer closed, returning to Add Attendance.")

    def add_attendance_handler(self):
        """
        Handles the attendance marking process by gathering all the required data.
        """
        attendance_file = self.file_dropdown.get()
        program_type = self.program_dropdown.get()
        date_to_add = self.selected_date # Renamed to avoid conflict with datetime.date
        external_csv = self.loaded_csv_path

        if not all([attendance_file, program_type, date_to_add, external_csv]):
            messagebox.showerror("Error", "Please ensure all fields are selected.")
            return

        # Call the backend function to update the attendance sheet
        update_attendance_sheet(attendance_file, program_type, date_to_add, external_csv)
        messagebox.showinfo("Success", "Attendance updated successfully!")

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
