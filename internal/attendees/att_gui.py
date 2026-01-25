import customtkinter as ctk
import os
import pandas as pd
from datetime import datetime
from tkinter import filedialog, messagebox
from internal.choosecsv import ChooseCSVWindow
from internal.attendees.att_func import get_session_info, extract_attendees, save_attendees, load_attendance_file
from internal.calender import CalendarDialog
from internal.utils.excel_styler import apply_excel_styling

class ChooseAbsenteeFileWindow(ChooseCSVWindow):
    """
    Wrapper for ChooseCSVWindow to select attendance files and open the absentee report.
    """
    def __init__(self, master):
        attendance_dir = os.path.join(os.path.dirname(__file__), "..", "..", "db", "attendance")
        super().__init__(master, 
                         target_dir=attendance_dir, 
                         callback=self.open_report,
                         title="Select Attendance File")

    def open_report(self, file_path):
        """
        Callback function to open the PrintAttendeesWindow
        .
        """
        PrintAttendeesWindow(self.master, file_path)


class PrintAttendeesWindow(ctk.CTkToplevel):
    """
    Window for viewing and exporting absentee reports with date range support.
    """
    def __init__(self, master, file_path):
        super().__init__(master)
        self.master = master
        self.file_path = file_path
        self.current_attendees = [] # List of extracted data
        
        self.start_date = None
        self.end_date = None
        
        self.title("View attendees")
        self.geometry("600x700")
        
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1) 

        # Load Data
        self.sessions = get_session_info(self.file_path)
        
        if not self.sessions:
            ctk.CTkLabel(self, text="No attendance data found in this file.", text_color="red").grid(row=1, column=0, pady=20)
            return

        # --- UI Components ---
        
        # 1. Title
        ctk.CTkLabel(self, text="attendees Report", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=(20, 10))

        # 2. Selection Mode & Display
        self.mode_var = ctk.StringVar(value="Single Date")
        self.seg_button = ctk.CTkSegmentedButton(self, values=["Single Date", "Date Range"], variable=self.mode_var)
        self.seg_button.grid(row=1, column=0, pady=(0, 10))

        self.lbl_selected = ctk.CTkLabel(self, text="Selected: None", font=("Arial", 14))
        self.lbl_selected.grid(row=2, column=0, pady=(0, 5))
        
        ctk.CTkButton(self, text="Select Date", command=self.open_calendar).grid(row=3, column=0, padx=20, pady=(0, 10))
        
        # 3. Actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)
        
        ctk.CTkButton(btn_frame, text="Show attendees", command=self.show_attendees).pack(side="left", padx=10)
        self.export_btn = ctk.CTkButton(btn_frame, text="Export All", command=self.export_data, state="disabled")
        self.export_btn.pack(side="left", padx=10)
        
        # 4. Result Display
        self.textbox_result = ctk.CTkTextbox(self, width=500, height=400)
        self.textbox_result.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_result.configure(state="disabled")

        # 5. Back Button
        ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=7, column=0, pady=20)

    def close_window(self):
        self.master.deiconify()
        self.destroy()

    def open_calendar(self):
        """Opens the calendar dialog based on selected mode."""
        mode = "single" if self.mode_var.get() == "Single Date" else "range"
        cal = CalendarDialog(self, selection_mode=mode)
        self.wait_window(cal)
        
        res = cal.get_selection()
        
        if mode == "single":
            if res:
                self.start_date = res
                self.end_date = res
                self.lbl_selected.configure(text=f"Selected: {res.strftime('%d/%m/%y')}")
        else:
            if res and isinstance(res, tuple):
                s, e = res
                self.start_date = s
                self.end_date = e
                if s and e:
                    self.lbl_selected.configure(text=f"Range: {s.strftime('%d/%m/%y')} - {e.strftime('%d/%m/%y')}")
                else:
                    self.lbl_selected.configure(text="Range: Invalid")

    def show_attendees(self):
        """Fetches and displays attendees for the selected range."""
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

        self.current_attendees = [] # Clear previous results
        
        # Pre-load dataframe for efficiency
        df = load_attendance_file(self.file_path)
        if df is None:
             self.textbox_result.insert("end", "\nError: Could not load file.")
             self.textbox_result.configure(state="disabled")
             return

        # Iterate through sessions and filter by date
        found_any = False
        display_text = ""
        
        sorted_dates = []
        for d_str in self.sessions.keys():
            try:
                # Try parsing with year as 2 digits first (common in this app)
                dt = datetime.strptime(d_str, "%d/%m/%y").date()
                if self.start_date <= dt <= self.end_date:
                    sorted_dates.append((dt, d_str))
            except ValueError:
                print(f"Skipping invalid date format: {d_str}")
        
        sorted_dates.sort() 
        
        for dt, d_str in sorted_dates:
            activities = self.sessions[d_str]
            for act in activities:
                col_idx = act['col_index']
                act_name = act['activity']
                
                # Pass pre-loaded df
                attendees = extract_attendees(self.file_path, col_idx, df=df)
                
                if attendees:
                    found_any = True
                    count = len(attendees)
                    display_text += f"\n--- {d_str} : {act_name} (Total: {count}) ---\n"
                    
                    for person in attendees:
                        person['Date'] = d_str
                        person['Activity'] = act_name
                        self.current_attendees.append(person)
                        display_text += f"{person['Surname']} {person['Firstname']} ({person['Matric NO']})\n"
                else:
                    display_text += f"\n--- {d_str} : {act_name} (No attendees) ---\n"

        if found_any:
            self.textbox_result.delete("0.0", "end")
            
            # Update header based on mode
            if self.start_date == self.end_date:
                header = f"Results for {self.start_date.strftime('%d/%m/%y')}:\n"
            else:
                header = f"Results for {self.start_date.strftime('%d/%m/%y')} to {self.end_date.strftime('%d/%m/%y')}:\n"
            
            self.textbox_result.insert("0.0", header + display_text)
            self.export_btn.configure(state="normal")
        else:
            self.textbox_result.delete("0.0", "end")
            self.textbox_result.insert("0.0", "No attendees found for the selected period.")
            
        self.textbox_result.configure(state="disabled")

    def export_data(self):
        if not self.current_attendees: return

        level_name = os.path.splitext(os.path.basename(self.file_path))[0]
        
        # Check if we are in range mode with potential for multiple dates
        if self.start_date != self.end_date:
            # Multi-file export
            folder_path = filedialog.askdirectory(title="Select Folder to Save Files")
            if not folder_path: return
            
            try:
                df = pd.DataFrame(self.current_attendees)
                # Ensure date column exists (it should)
                if 'Date' not in df.columns:
                     messagebox.showerror("Error", "Date column missing in data.")
                     return

                # Group by Date and export
                count = 0
                for date_str, group_df in df.groupby('Date'):
                    # Safe filename
                    safe_date = str(date_str).replace("/", "-")
                    filename = f"{level_name}_attendees_{safe_date}.xlsx"
                    full_path = os.path.join(folder_path, filename)
                    
                    # Reorder cols
                    cols = [c for c in group_df.columns if c not in ['Date', 'Activity']]
                    group_df = group_df[cols]
                    
                    group_df.to_excel(full_path, index=False)
                    apply_excel_styling(full_path)
                    count += 1
                
                messagebox.showinfo("Success", f"Successfully exported {count} files to:\n{folder_path}")
            
            except Exception as e:
                messagebox.showerror("Error", f"Batch export failed: {e}")
                
        else:
            # Single file export (Existing logic)
            s_str = self.start_date.strftime("%d-%m-%y")
            filename = f"{level_name}_attendees_{s_str}"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel file", "*.xlsx"), ("CSV file", "*.csv")],
                title="Export attendees",
                initialfile=filename
            )

            if file_path:
                try:
                    df = pd.DataFrame(self.current_attendees)
                    cols = [c for c in df.columns if c not in ['Date', 'Activity']]
                    df = df[cols]
                    
                    if file_path.endswith('.xlsx'):
                        df.to_excel(file_path, index=False)
                        apply_excel_styling(file_path)
                    else:
                        df.to_csv(file_path, index=False)
                        
                    messagebox.showinfo("Success", f"Saved to {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Save failed: {e}")