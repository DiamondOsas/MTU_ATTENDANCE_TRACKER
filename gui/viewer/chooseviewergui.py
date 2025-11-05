import customtkinter as ctk
from tkinter import messagebox
import os
import sys
import pandas as pd

# Add the parent directory to the path so we can import from func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from func.viewer import get_all_students_files


class ChooseViewerWindow(ctk.CTkToplevel):
    """
    Window that allows the user to choose a student data file to view or edit.
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
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Title
        title_text = "Edit Students Data - Choose File" if viewer_type == "edit" else "View Attendance - Choose File"
        self.title_label = ctk.CTkLabel(self, text=title_text, font=ctk.CTkFont(size=16, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # File selection frame
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        
        # Label for file selection
        self.select_label = ctk.CTkLabel(self.file_frame, text="Select a student data file:")
        self.select_label.grid(row=0, column=0, padx=20, pady=(10, 5))
        
        # Get available files
        self.available_files = get_all_students_files()
        
        if self.available_files:
            # Create dropdown with available files
            self.file_dropdown = ctk.CTkComboBox(
                self.file_frame,
                values=self.available_files,
                width=300
            )
            self.file_dropdown.grid(row=1, column=0, padx=20, pady=10)
            self.file_dropdown.set(self.available_files[0] if self.available_files else "No files available")
        else:
            # If no files found, show a label instead
            self.no_files_label = ctk.CTkLabel(self.file_frame, text="No student data files found!", text_color="red")
            self.no_files_label.grid(row=1, column=0, padx=20, pady=10)
            self.file_dropdown = None
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Open button
        self.open_button = ctk.CTkButton(
            self.button_frame,
            text="Open File",
            command=self.open_selected_file,
            state="disabled" if not self.available_files else "normal"
        )
        self.open_button.grid(row=0, column=0, padx=10, pady=10)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            command=self.close_window
        )
        self.cancel_button.grid(row=0, column=1, padx=10, pady=10)
        
        # If there are no files, show a message
        if not self.available_files:
            self.no_files_message = ctk.CTkLabel(
                self,
                text="No student data files found in the 'db/allstudents' directory.\nPlease register some students first.",
                text_color="orange"
            )
            self.no_files_message.grid(row=3, column=0, padx=20, pady=10)
    
    def open_selected_file(self):
        """
        Opens the selected file with the appropriate viewer based on viewer_type.
        """
        if not self.file_dropdown:
            messagebox.showerror("Error", "No files available to open!")
            return
            
        selected_file = self.file_dropdown.get()
        
        if not selected_file or selected_file == "No files available":
            messagebox.showwarning("Warning", "Please select a file first!")
            return
        
        # Get the full path to the selected file
        file_path = os.path.join("db", "allstudents", selected_file)
        
        # Validate that the file exists
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File does not exist: {file_path}")
            return
        
        # Check if the file is a valid CSV
        if not file_path.lower().endswith('.csv'):
            messagebox.showerror("Error", "Selected file is not a CSV file!")
            return
        
        try:
            # Try to read the file to make sure it's valid
            df = pd.read_csv(file_path)
            
            # If viewer_type is "edit", open the edit viewer, otherwise open a basic viewer
            if self.viewer_type == "edit":
                from gui.viewer.viewergui import ViewerWindow
                self.destroy() # Destroy this window before opening the new one
                
                # Open the viewer window with edit capability
                viewer_app = ViewerWindow(
                    parent=self.parent,
                    file_path=file_path,
                    editable=True
                )
            else:
                # For viewing attendance (not implemented in this task)
                from gui.viewer.viewergui import ViewerWindow
                self.destroy() # Destroy this window before opening the new one
                
                viewer_app = ViewerWindow(
                    parent=self.parent,
                    file_path=file_path,
                    editable=False
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def close_window(self):
        """
        Closes this window and shows the parent window again.
        """
        self.destroy()
        if self.parent:
            self.parent.deiconify()