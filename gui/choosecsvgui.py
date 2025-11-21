import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import pandas as pd

# Add the parent directory to the path so we can import from func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from func.viewer import get_all_students_files
from func.attendance import get_attendance_files


class ChooseViewerWindow(ctk.CTkToplevel):
    """
    Window that allows the user to choose a student data file to view or edit,
    or to view an attendance file.
    """
    def __init__(self, parent, viewer_type="view"):
        """
        Initializes the ChooseViewerWindow.
        
        Args:
            parent: The parent window that opened this window
            viewer_type: "view" for viewing attendance, "edit" for editing student data
        """
        super().__init__(parent)
        
        self.parent = parent
        self.viewer_type = viewer_type
        
        # Configure window
        self.title("Choose Student Data File" if viewer_type == "edit" else "View Attendance")
        self.geometry("500x400")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Let the file frame expand
        
        # --- Title ---
        title_text = "Edit Students Data - Choose File" if viewer_type == "edit" else "View Attendance - Choose File"
        self.title_label = ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # --- File Selection Frame ---
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        
        # --- Determine which files to show based on viewer_type ---
        if self.viewer_type == "edit":
            self.select_label_text = "Select a student data file to edit:"
            self.available_files = get_all_students_files()
            self.data_dir = os.path.join("db", "allstudents")
            self.no_files_message_text = "No student data files found in 'db/allstudents'.\nPlease register students first."
        else: # "view"
            self.select_label_text = "Select an attendance sheet to view:"
            self.available_files = get_attendance_files()
            self.data_dir = os.path.join("db", "attendance")
            self.no_files_message_text = "No attendance sheets found in 'db/attendance'.\nPlease prepare attendance sheets first."

        # Label for file selection
        self.select_label = ctk.CTkLabel(self.file_frame, text=self.select_label_text)
        self.select_label.grid(row=0, column=0, padx=20, pady=(10, 5))

        if self.available_files:
            # Create dropdown with available files
            self.file_dropdown = ctk.CTkComboBox(
                self.file_frame,
                values=self.available_files,
                width=300
            )
            self.file_dropdown.grid(row=1, column=0, padx=20, pady=10)
            self.file_dropdown.set(self.available_files[0])
        else:
            # If no files found, show a label instead
            self.no_files_label = ctk.CTkLabel(self.file_frame, text="No files found!", text_color="red")
            self.no_files_label.grid(row=1, column=0, padx=20, pady=10)
            self.file_dropdown = None
            
            # Show a more descriptive message below the frame
            self.no_files_message = ctk.CTkLabel(self, text=self.no_files_message_text, text_color="orange")
            self.no_files_message.grid(row=3, column=0, padx=20, pady=10, sticky="s")

        # --- Button Frame ---
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="s")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Open button
        self.open_button = ctk.CTkButton(
            self.button_frame,
            text="Open File",
            command=self.open_selected_file,
            state="normal" if self.available_files else "disabled"
        )
        self.open_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Back to Menu",
            command=self.close_window
        )
        self.cancel_button.grid(row=0, column=1, padx=10, pady=10)
    
    def open_selected_file(self):
        """
        Opens the selected file in the appropriate viewer based on viewer_type.
        If viewing attendance, it opens a read-only viewer.
        If editing student data, it opens an editable viewer.
        """
        if not self.file_dropdown:
            messagebox.showerror("Error", "No files available to open.")
            return
            
        selected_file = self.file_dropdown.get()
        
        if not selected_file or selected_file == "No files available":
            messagebox.showwarning("Selection Required", "Please select a file from the dropdown.")
            return
        
        # Construct the full path to the selected file using the directory determined in __init__
        file_path = os.path.join(self.data_dir, selected_file)
        
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"The file does not exist:\n{file_path}")
            return
        
        if not file_path.lower().endswith('.csv'):
            messagebox.showerror("Invalid File Type", "The selected file is not a valid CSV file.")
            return
        
        try:
            # Attempt to read the CSV to validate it before opening the viewer
            pd.read_csv(file_path)
            
            # The ViewerWindow can handle both viewing and editing
            from gui.viewergui import ViewerWindow
            
            is_editable = (self.viewer_type == "edit")
            
            # Destroy this selection window before opening the main viewer
            self.destroy()
            
            # Open the viewer window, passing the file path and edit status
            viewer_app = ViewerWindow(
                parent=self.parent,
                file_path=file_path,
                editable=is_editable
            )
                
        except Exception as e:
            messagebox.showerror("Error Opening File", f"An unexpected error occurred while trying to open the file:\n{str(e)}")
    
    def close_window(self):
        """
        Closes this window and de-iconifies the parent window.
        """
        self.destroy()
        if self.parent:
            self.parent.deiconify()