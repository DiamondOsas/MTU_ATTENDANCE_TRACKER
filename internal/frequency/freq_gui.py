import customtkinter as ctk
import os
import pandas as pd
from tkinter import messagebox, filedialog
from internal.choosecsv import ChooseCSVWindow
from internal.calender import CalendarDialog
from internal.frequency.freq_func import calculate_frequency
from internal.utils.excel_styler import apply_excel_styling

class ChooseFrequencyFileWindow(ChooseCSVWindow):
    def __init__(self, master):
        attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..", "db", "attendance")
        super().__init__(master, 
                         target_dir=attendance_dir, 
                         callback=self.open_frequency_window,
                         title="Select Attendance File for Frequency")

    def open_frequency_window(self, file_path):
        FrequencyWindow(self.master, file_path)

class FrequencyWindow(ctk.CTkToplevel):
    def __init__(self, master, file_path):
        super().__init__(master)
        self.master = master
        self.file_path = file_path
        self.start_date = None
        self.end_date = None
        self.current_data = [] # List of dicts
        self.current_mode = "" # "Attendance" or "Absence"

        self.title("Attendance Frequency")
        self.geometry("600x650")
        
        # UI Setup
        self._setup_ui()

    def _setup_ui(self):
        # Title
        ctk.CTkLabel(self, text="Frequency Analysis", font=("Arial", 20, "bold")).pack(pady=10)
        
        # File info
        file_name = os.path.basename(self.file_path)
        ctk.CTkLabel(self, text=f"File: {file_name}", text_color="gray").pack(pady=5)

        # Date Selection
        self.date_btn = ctk.CTkButton(self, text="Select Date Range", command=self._select_date_range)
        self.date_btn.pack(pady=10)
        
        self.lbl_date_range = ctk.CTkLabel(self, text="Range: Not Selected")
        self.lbl_date_range.pack(pady=5)

        # Action Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="Calculate Attendance", command=self._calc_attendance).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Calculate Absence", command=self._calc_absence).pack(side="left", padx=10)

        # Results Area
        self.textbox = ctk.CTkTextbox(self, width=500, height=350)
        self.textbox.pack(pady=10)
        self.textbox.configure(state="disabled")

        # Export Button
        self.btn_export = ctk.CTkButton(self, text="Export to Excel", command=self._export, state="disabled")
        self.btn_export.pack(pady=10)
        
        # Back Button
        ctk.CTkButton(self, text="Back", command=self._close).pack(pady=5)
        
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _select_date_range(self):
        cal = CalendarDialog(self, selection_mode="range")
        self.wait_window(cal)
        selection = cal.get_selection()
        if selection and selection[0] and selection[1]:
            self.start_date, self.end_date = selection
            self.lbl_date_range.configure(text=f"Range: {self.start_date.strftime('%d/%m/%y')}" - {self.end_date.strftime('%d/%m/%y')})
        elif selection and selection[0]:
            self.start_date = self.end_date = selection[0]
            self.lbl_date_range.configure(text=f"Range: {self.start_date.strftime('%d/%m/%y')} (Single Day)")

    def _calc_attendance(self):
        self._calculate(target_marks=['✓', 'P', 'p', 'Present'], mode="Attendance")

    def _calc_absence(self):
        self._calculate(target_marks=['✗', 'x', 'X', 'A', 'a', 'Absent'], mode="Absence")

    def _calculate(self, target_marks, mode):
        if not self.start_date or not self.end_date:
            messagebox.showwarning("Missing Date", "Please select a date range first.")
            return

        self.current_mode = mode
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", f"Calculating {mode} frequency...\n")
        self.update()

        results = calculate_frequency(self.file_path, self.start_date, self.end_date, target_marks)
        
        self.current_data = results
        
        self.textbox.delete("0.0", "end")
        if not results:
            self.textbox.insert("0.0", "No data found for the selected range.")
            self.btn_export.configure(state="disabled")
        else:
            header = f"SURNAME\tFIRSTNAME\tMATRIC NO\tCOUNT\n" 
            header += "-"*60 + "\n"
            self.textbox.insert("0.0", header)
            
            for row in results:
                line = f"{row['Surname']}\t{row['Firstname']}\t{row['Matric NO']}\t{row['Count']}\n"
                self.textbox.insert("end", line)
            
            self.btn_export.configure(state="normal")
            
        self.textbox.configure(state="disabled")

    def _export(self):
        if not self.current_data:
            return
            
        file_name = os.path.basename(self.file_path)
        level_name = os.path.splitext(file_name)[0].upper()
        
        # Construct default filename
        s_str = self.start_date.strftime("%d-%m-%y")
        e_str = self.end_date.strftime("%d-%m-%y")
        
        default_name = f"{level_name}_{self.current_mode.upper()}_FREQ_{s_str}_to_{e_str}.xlsx"
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile=default_name,
            title="Export Frequency Report"
        )
        
        if save_path:
            try:
                df = pd.DataFrame(self.current_data)
                # Rename Count column based on mode
                col_name = "NO Attended" if self.current_mode == "Attendance" else "NO Missed"
                df.rename(columns={'Count': col_name}, inplace=True)
                
                df.to_excel(save_path, index=False)
                apply_excel_styling(save_path)
                messagebox.showinfo("Success", f"Exported to {os.path.basename(save_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")

    def _close(self):
        self.master.deiconify()
        self.destroy()
