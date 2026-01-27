import customtkinter as ctk
from tkinter import messagebox
import os
from datetime import date, datetime
from internal.attendance.create.create_func import get_attendance_files, load_csv_file, update_attendance_sheet
from internal.calender import CalendarDialog
from internal.attendance.create.selcol_gui import SelectColumnWindow

class AddAttendanceWindow(ctk.CTkToplevel):
    """
    Window to create a new attendance record (column) in the attendance sheet.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.loaded_csv_path = None 
        self.extracted_matric_numbers = []
        self.selected_date = date.today().strftime('%d/%m/%y')
        
        self.title("Add Attendance")
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.grid_columnconfigure(0, weight=1)
        
        # UI Setup
        ctk.CTkLabel(self, text="Create Attendance Record", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=20)
        
        # 1. File Selection
        frame_file = ctk.CTkFrame(self)
        frame_file.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(frame_file, text="Choose Attendance Sheet:").pack(pady=5)
        
        files = get_attendance_files()
        self.file_dropdown = ctk.CTkComboBox(frame_file, values=files if files else ["No files found"], width=300)
        self.file_dropdown.pack(pady=10)
        if not files: self.file_dropdown.configure(state="disabled")

        # 2. Program Type
        frame_prog = ctk.CTkFrame(self)
        frame_prog.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(frame_prog, text="Choose Program Type:").pack(pady=5)
        
        programs = ["MORNING SERVICE", "EVENING SERVICE", "MANNA WATER", "SUNDAY SERVICE", "BIBLE STUDY" ,"PMCH", "MTU PRAYS", "SPECIAL SERVICE"]
        self.prog_dropdown = ctk.CTkComboBox(frame_prog, values=programs, width=300)
        self.prog_dropdown.pack(pady=10)
        self.prog_dropdown.set(programs[0])

        # 3. Date Selection
        frame_date = ctk.CTkFrame(self)
        frame_date.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        ctk.CTkLabel(frame_date, text="Select Date:").pack(side="left", padx=10)
        
        self.date_entry = ctk.CTkEntry(frame_date, width=120)
        self.date_entry.pack(side="left", padx=5)
        self.date_entry.insert(0, self.selected_date)
        
        ctk.CTkButton(frame_date, text="📅", width=30, command=self.open_calendar).pack(side="left", padx=5)

        # 4. Load External CSV
        frame_btns = ctk.CTkFrame(self)
        frame_btns.grid(row=4, column=0, padx=20, pady=20)
        
        ctk.CTkButton(frame_btns, text="Load External CSV (Matric Nos)", command=self.load_csv_handler).pack(fill="x", pady=5)
        self.btn_add = ctk.CTkButton(frame_btns, text="Add Attendance", command=self.add_attendance, state="disabled")
        self.btn_add.pack(fill="x", pady=5)
        
        self.lbl_loaded = ctk.CTkLabel(self, text="No external file loaded.", font=("Arial", 12))
        self.lbl_loaded.grid(row=5, column=0)

        # 5. Back
        ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=6, column=0, pady=20)

    def open_calendar(self):
        cal = CalendarDialog(self, self.selected_date)
        self.wait_window(cal)
        if cal.selected_date:
            self.selected_date = cal.selected_date.strftime('%d/%m/%y')
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, self.selected_date)

    def load_csv_handler(self):
        # load_csv_file returns a tuple of paths (from filedialog)
        paths = load_csv_file() 
        if not paths: return
        
        self.extracted_matric_numbers = []
        
        for path in paths:
            self.loaded_csv_path = path
            self.lbl_loaded.configure(text=f"Processing: {os.path.basename(path)}")
            
            # Open Viewer to select column
            self.withdraw()
            viewer = SelectColumnWindow(self, path)
            self.wait_window(viewer)
            self.deiconify()
            
            if viewer.selected_column_data:
                self.extracted_matric_numbers.extend(viewer.selected_column_data)
        
        if self.extracted_matric_numbers:
            self.btn_add.configure(state="normal")
            self.lbl_loaded.configure(text=f"Loaded {len(self.extracted_matric_numbers)} matric numbers.")
        else:
            self.lbl_loaded.configure(text="No data loaded.")

    def add_attendance(self):
        sheet = self.file_dropdown.get()
        program = self.prog_dropdown.get()
        date_val = self.date_entry.get()
        
        if not all([sheet, program, date_val, self.extracted_matric_numbers]):
            messagebox.showerror("Error", "Missing information.")
            return

        update_attendance_sheet(sheet, program, date_val, self.loaded_csv_path, self.extracted_matric_numbers)
        messagebox.showinfo("Success", "Attendance updated successfully!")

    def close_window(self):
        self.parent.deiconify()
        self.destroy()