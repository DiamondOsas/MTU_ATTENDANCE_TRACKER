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
        self.activity_checkboxes = [] # Stores our checkboxes
        
        self.title(f"View {self.record_type}")
        self.geometry("600x750") # Made slightly taller to fit the list
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1) 

        self.sessions = get_session_info(self.file_path)
        
        if not self.sessions:
            ctk.CTkLabel(self, text="No attendance data found.", text_color="red").grid(row=1, column=0, pady=20)
            ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=8, column=0, pady=20)
            return

        ctk.CTkLabel(self, text=f"{self.record_type} Report", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=(20, 10))

        self.mode_var = ctk.StringVar(value="Single Date")
        self.seg_button = ctk.CTkSegmentedButton(self, values=["Single Date", "Date Range"], variable=self.mode_var)
        self.seg_button.grid(row=1, column=0, pady=(0, 10))

        self.lbl_selected = ctk.CTkLabel(self, text="Selected: None", font=("Arial", 14))
        self.lbl_selected.grid(row=2, column=0, pady=(0, 5))
        
        ctk.CTkButton(self, text="Select Date", command=self.open_calendar).grid(row=3, column=0, padx=20, pady=(0, 10))
        
        # --- NEW SECTION: Activity Selector ---
        ctk.CTkLabel(self, text="Select Activities to Include:", font=("Arial", 12, "bold")).grid(row=4, column=0, pady=(5,0))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=120, label_text="Activities")
        self.scroll_frame.grid(row=5, column=0, padx=20, pady=5, sticky="ew")
        # --------------------------------------

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=6, column=0, pady=10)
        
        ctk.CTkButton(btn_frame, text=f"Show {self.record_type}", command=self.show_records).pack(side="left", padx=10)
        self.export_btn = ctk.CTkButton(btn_frame, text="Export Results", command=self.export_data, state="disabled")
        self.export_btn.pack(side="left", padx=10)
        
        self.textbox_result = ctk.CTkTextbox(self, width=500, height=300)
        self.textbox_result.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_result.configure(state="disabled")

        ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=8, column=0, pady=20)

    def close_window(self):
        self.master.deiconify()
        self.destroy()

    def open_calendar(self):
        mode = "single" if self.mode_var.get() == "Single Date" else "range"
        cal = CalendarDialog(self, selection_mode=mode)
        self.wait_window(cal)
        res = cal.get_selection()
        
        valid_selection = False
        if mode == "single" and res:
            self.start_date = self.end_date = res
            self.lbl_selected.configure(text=f"Selected: {res.strftime('%d/%m/%y')}")
            valid_selection = True
        elif mode == "range" and res and isinstance(res, tuple):
            self.start_date, self.end_date = res
            if self.start_date and self.end_date:
                self.lbl_selected.configure(text=f"Range: {self.start_date.strftime('%d/%m/%y')} - {self.end_date.strftime('%d/%m/%y')}")
                valid_selection = True
            else:
                 self.lbl_selected.configure(text="Range: Invalid")
        
        # When date is picked, show the activities found in that range
        if valid_selection:
            self.update_activity_options()

    def update_activity_options(self):
        """Scans the selected dates and creates checkboxes for found activities."""
        # 1. Clear old checkboxes
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.activity_checkboxes.clear()

        if not self.start_date or not self.end_date:
            return

        # 2. Find unique activities in the date range
        found_activities = set()
        for d_str, sessions_list in self.sessions.items():
            try:
                dt = datetime.strptime(d_str, "%d/%m/%y").date()
                if self.start_date <= dt <= self.end_date:
                    for s in sessions_list:
                        found_activities.add(s['activity'])
            except ValueError:
                pass
        
        # 3. Create a checkbox for each activity
        if not found_activities:
            ctk.CTkLabel(self.scroll_frame, text="No activities in range").pack()
        else:
            for act_name in sorted(list(found_activities)):
                # Default value is 1 (Checked)
                var = ctk.StringVar(value=act_name) 
                chk = ctk.CTkCheckBox(self.scroll_frame, text=act_name, onvalue=act_name, offvalue="")
                chk.select() # Check by default
                chk.pack(anchor="w", pady=2, padx=5)
                self.activity_checkboxes.append(chk)

    def show_records(self):
        if not self.start_date or not self.end_date:
            self.textbox_result.configure(state="normal")
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", "Please select a date first.")
            self.textbox_result.configure(state="disabled")
            return

        # Get list of activities user actually wants to see
        selected_activities = [chk.get() for chk in self.activity_checkboxes if chk.get() != ""]
        
        if not selected_activities:
            messagebox.showwarning("Warning", "Please select at least one activity.")
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
        
        # Sort dates
        for d_str in self.sessions.keys():
            try:
                dt = datetime.strptime(d_str, "%d/%m/%y").date()
                if self.start_date <= dt <= self.end_date:
                    sorted_dates.append((dt, d_str))
            except ValueError: pass
        sorted_dates.sort() 
        
        # Process Logic
        for dt, d_str in sorted_dates:
            for act in self.sessions[d_str]:
                # ONLY Process if the activity name is in our selected list
                if act['activity'] in selected_activities:
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
            header = f"Results for selected activities ({self.start_date.strftime('%d/%m/%y')} - {self.end_date.strftime('%d/%m/%y')}):\n"
            self.textbox_result.insert("0.0", header + display_text)
            self.export_btn.configure(state="normal")
        else:
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", f"No {self.record_type.lower()} found for selected activities.")
        self.textbox_result.configure(state="disabled")

    def export_data(self):
        file_name = os.path.basename(self.file_path)
        name_without_ext = os.path.splitext(file_name)[0]
        level_name = str(name_without_ext).upper()
    
        if not self.current_records: return
       
        # Since 'show_records' already filtered 'current_records' based on your checkboxes,
        # we don't need to change much logic here. It exports whatever is shown in the textbox.
        
        # If multiple dates OR multiple activities, we use folder export
        unique_dates = len(set(r['Date'] for r in self.current_records))
        unique_acts = len(set(r['Activity'] for r in self.current_records))
        
        if unique_dates > 1 or unique_acts > 1:
            folder_path = filedialog.askdirectory(title="Select Folder to Save Files")
            if not folder_path: return
            try:
                df = pd.DataFrame(self.current_records)
                count = 0
                # Group by Date AND Activity to ensure separate files for separate activities on same day
                for (date_str, act_name), group_df in df.groupby(['Date', 'Activity']):
                    filename = f"{level_name}_{self.export_prefix}_{str(date_str).replace('/', '-')}_{act_name}.xlsx"
                    full_path = os.path.join(folder_path, filename)
                    group_df[[c for c in group_df.columns if c not in ['Date', 'Activity']]].to_excel(full_path, index=False)
                    apply_excel_styling(full_path)
                    count += 1
                messagebox.showinfo("Success", f"Exported {count} files.")
            except Exception as e: messagebox.showerror("Error", f"Export failed: {e}")
        else:
            # Single Date AND Single Activity
            act_name = self.current_records[0]['Activity']
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