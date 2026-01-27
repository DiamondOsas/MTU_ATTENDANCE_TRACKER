import customtkinter as ctk
import os
import pandas as pd
from datetime import datetime
from tkinter import filedialog, messagebox
from internal.choosecsv import ChooseCSVWindow
from internal.records.records_func import get_session_info, extract_records, load_attendance_file
from internal.calender import CalendarDialog
from internal.utils.excel_styler import apply_excel_styling
from internal.utils.general import get_target_dir
class ChooseRecordFileWindow(ChooseCSVWindow):
    def __init__(self, master, record_type, target_marks, export_prefix):
        self.record_type = record_type
        self.target_marks = target_marks
        self.export_prefix = export_prefix
        
        attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..", "db", "attendance")
        super().__init__(master, 
                         target_dir=attendance_dir, 
                         callback=self.open_report,
                         title=f"Select Attendance File for {record_type}")

    def open_report(self, file_path):
        PrintRecordsWindow(self.master, file_path, self.record_type, self.target_marks, self.export_prefix)


class PrintRecordsWindow(ctk.CTkToplevel):
    def __init__(self, master, file_path, record_type, target_marks, export_prefix):
        super().__init__(master)
        self.master = master
        self.file_path = file_path
        self.record_type = record_type
        self.target_marks = target_marks
        self.export_prefix = export_prefix
        
        self.current_records = []
        self.start_date = None
        self.end_date = None
        
        self.title(f"View {self.record_type}")
        self.geometry("600x700")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1) 

        self.sessions = get_session_info(self.file_path)
        
        if not self.sessions:
            ctk.CTkLabel(self, text="No attendance data found.", text_color="red").grid(row=1, column=0, pady=20)
            ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=7, column=0, pady=20)
            return

        ctk.CTkLabel(self, text=f"{self.record_type} Report", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=(20, 10))

        self.mode_var = ctk.StringVar(value="Single Date")
        self.seg_button = ctk.CTkSegmentedButton(self, values=["Single Date", "Date Range"], variable=self.mode_var)
        self.seg_button.grid(row=1, column=0, pady=(0, 10))

        self.lbl_selected = ctk.CTkLabel(self, text="Selected: None", font=("Arial", 14))
        self.lbl_selected.grid(row=2, column=0, pady=(0, 5))
        
        ctk.CTkButton(self, text="Select Date", command=self.open_calendar).grid(row=3, column=0, padx=20, pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)
        
        ctk.CTkButton(btn_frame, text=f"Show {self.record_type}", command=self.show_records).pack(side="left", padx=10)
        self.export_btn = ctk.CTkButton(btn_frame, text="Export All", command=self.export_data, state="disabled")
        self.export_btn.pack(side="left", padx=10)
        
        self.textbox_result = ctk.CTkTextbox(self, width=500, height=400)
        self.textbox_result.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_result.configure(state="disabled")

        ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=7, column=0, pady=20)

    def close_window(self):
        self.master.deiconify()
        self.destroy()

    def open_calendar(self):
        mode = "single" if self.mode_var.get() == "Single Date" else "range"
        cal = CalendarDialog(self, selection_mode=mode)
        self.wait_window(cal)
        res = cal.get_selection()
        
        if mode == "single" and res:
            self.start_date = self.end_date = res
            self.lbl_selected.configure(text=f"Selected: {res.strftime('%d/%m/%y')}")
        elif mode == "range" and res and isinstance(res, tuple):
            self.start_date, self.end_date = res
            self.lbl_selected.configure(text=f"Range: {self.start_date.strftime('%d/%m/%y')} - {self.end_date.strftime('%d/%m/%y')}" if self.start_date and self.end_date else "Range: Invalid")

    def show_records(self):
        if not self.start_date or not self.end_date:
            self.textbox_result.configure(state="normal")
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", "Please select a date first.")
            self.textbox_result.configure(state="disabled")
            return

        self.export_btn.configure(state="disabled")
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end")
        self.textbox_result.insert("0.0", "Processing...\n")
        self.update()

        self.current_records = []
        df = load_attendance_file(self.file_path)
        if df is None:
             self.textbox_result.insert("end", "\nError loading file.")
             self.textbox_result.configure(state="disabled")
             return

        found_any = False
        display_text = ""
        sorted_dates = []
        for d_str in self.sessions.keys():
            try:
                dt = datetime.strptime(d_str, "%d/%m/%y").date()
                if self.start_date <= dt <= self.end_date:
                    sorted_dates.append((dt, d_str))
            except ValueError: pass
        
        sorted_dates.sort() 
        for dt, d_str in sorted_dates:
            for act in self.sessions[d_str]:
                records = extract_records(self.file_path, act['col_index'], self.target_marks, df=df)
                if records:
                    found_any = True
                    display_text += f"\n--- {d_str} : {act['activity']} (Total: {len(records)}) ---\n"
                    for person in records:
                        person['Date'], person['Activity'] = d_str, act['activity']
                        self.current_records.append(person)
                        display_text += f"{person['Surname']} {person['Firstname']} ({person['Matric NO']})\n"
                else:
                    display_text += f"\n--- {d_str} : {act['activity']} (No {self.record_type}) ---\n"

        if found_any:
            self.textbox_result.delete("0.0", "end")
            header = f"Results for {self.start_date.strftime('%d/%m/%y')}:\n" if self.start_date == self.end_date else f"Results for {self.start_date.strftime('%d/%m/%y')} to {self.end_date.strftime('%d/%m/%y')}:\n"
            self.textbox_result.insert("0.0", header + display_text)
            self.export_btn.configure(state="normal")
        else:
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", f"No {self.record_type.lower()} found.")
        self.textbox_result.configure(state="disabled")

    def export_data(self):
        if not self.current_records: return
        level_name = os.path.splitext(os.path.basename(self.file_path))[0].upper()
        
        if self.start_date != self.end_date:
            folder_path = filedialog.askdirectory(title="Select Folder to Save Files")
            if not folder_path: return
            try:
                df = pd.DataFrame(self.current_records)
                count = 0
                for date_str, group_df in df.groupby('Date'):
                    act_name = group_df.iloc[0]['Activity']
                    filename = f"{level_name}_{self.export_prefix}_{str(date_str).replace('/', '-')}_{act_name}.xlsx"
                    full_path = os.path.join(folder_path, filename)
                    group_df[[c for c in group_df.columns if c not in ['Date', 'Activity']]].to_excel(full_path, index=False)
                    apply_excel_styling(full_path)
                    count += 1
                messagebox.showinfo("Success", f"Exported {count} files.")
            except Exception as e: messagebox.showerror("Error", f"Export failed: {e}")
        else:
            act_name = self.current_records[0]['Activity'] if self.current_records else "REPORT"
            filename = f"{level_name}_{self.export_prefix}_{self.start_date.strftime('%d-%m-%y')}_{act_name}"
            target_dir = get_target_dir(level_name, self.export_prefix)
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")], initialfile=filename, initialdir=target_dir)
            if file_path:
                try:
                    df = pd.DataFrame(self.current_records)
                    df = df[[c for c in df.columns if c not in ['Date', 'Activity']]]
                    if file_path.endswith('.xlsx'):
                        df.to_excel(file_path, index=False)
                        apply_excel_styling(file_path)
                    else: df.to_csv(file_path, index=False)
                    messagebox.showinfo("Success", f"Saved to {file_path}")
                except Exception as e: messagebox.showerror("Error", f"Save failed: {e}")
