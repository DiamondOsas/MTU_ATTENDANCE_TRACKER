import customtkinter as ctk
from tkinter import messagebox
import os
import pandas as pd
from internal.utils.csv_handler import get_files_in_dir
from internal.attendance.attendance import get_attendance_files
from internal.attendance.view.viewer_gui import ViewerWindow

class ChooseViewerWindow(ctk.CTkToplevel):
    """
    Window to select a student data file (Edit mode) or attendance sheet (View mode).
    """
    def __init__(self, parent, viewer_type="view"):
        super().__init__(parent)
        self.parent = parent
        self.viewer_type = viewer_type
        
        self.title("Edit Students" if viewer_type == "edit" else "View Attendance")
        self.geometry("500x400")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 
        
        # Determine paths and lists
        if self.viewer_type == "edit":
            self.data_dir = os.path.join("db", "allstudents")
            self.available_files = get_files_in_dir(self.data_dir)
            label_text = "Select Student Data File:"
        else:
            self.data_dir = os.path.join("db", "attendance")
            self.available_files = get_attendance_files() # Using existing logic for attendance which handles complex paths? 
            # Actually get_attendance_files just did glob in db/attendance. 
            # We can use get_files_in_dir here too but I'll stick to the import for safety if it does special filtering.
            # Checked internal/attendance/attendance.py: it just uses glob.
            label_text = "Select Attendance Sheet:"

        # UI
        ctk.CTkLabel(self, text=label_text, font=("Arial", 16, "bold")).grid(row=0, column=0, pady=20)
        
        self.file_frame = ctk.CTkFrame(self)
        self.file_frame.grid(row=1, column=0, padx=20, sticky="ew")
        
        if self.available_files:
            self.file_dropdown = ctk.CTkComboBox(self.file_frame, values=self.available_files, width=300)
            self.file_dropdown.pack(pady=20)
            self.file_dropdown.set(self.available_files[0])
            btn_state = "normal"
        else:
            ctk.CTkLabel(self.file_frame, text="No files found.", text_color="red").pack(pady=20)
            self.file_dropdown = None
            btn_state = "disabled"

        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, pady=20)
        
        ctk.CTkButton(btn_frame, text="Open File", command=self.open_selected_file, state=btn_state).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Back", command=self.close_window).pack(side="left", padx=10)

    def open_selected_file(self):
        if not self.file_dropdown: return
        
        selected_file = self.file_dropdown.get()
        file_path = os.path.join(self.data_dir, selected_file)
        
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "File not found.")
            return

        # Open Viewer
        try:
            is_editable = (self.viewer_type == "edit")
            self.destroy() # Close selector
            ViewerWindow(self.parent, file_path, editable=is_editable)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")
            self.parent.deiconify()

    def close_window(self):
        self.parent.deiconify()
        self.destroy()
