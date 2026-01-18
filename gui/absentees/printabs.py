import customtkinter as ctk
from tkinter import filedialog
from internal.attendance.analysis.absentees_func import get_session_info, extract_absentees, save_absentees
import os

class PrintAbsenteesWindow(ctk.CTkToplevel):
    """
    Window for viewing and exporting absentee reports.
    """
    def __init__(self, master, file_path):
        super().__init__(master)
        self.master = master
        self.file_path = file_path
        self.current_absentees = []
        
        self.title("View Absentees")
        self.geometry("500x650")
        
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1) 

        # Load Data
        self.sessions = get_session_info(self.file_path)
        self.dates = list(self.sessions.keys())

        if not self.dates:
            ctk.CTkLabel(self, text="No attendance data found in this file.", text_color="red").grid(row=1, column=0, pady=20)
            return

        # --- UI Components ---
        
        # 1. Title
        ctk.CTkLabel(self, text="Absentees Report", font=("Arial", 20, "bold")).grid(row=0, column=0, pady=(20, 10))

        # 2. Date Selection
        ctk.CTkLabel(self, text="Select Date:").grid(row=1, column=0, padx=20, sticky="w")
        self.selected_date = ctk.StringVar(value=self.dates[0])
        self.option_date = ctk.CTkOptionMenu(self, values=self.dates, command=self.update_activities, variable=self.selected_date)
        self.option_date.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # 3. Activity Selection
        ctk.CTkLabel(self, text="Select Activity:").grid(row=3, column=0, padx=20, sticky="w")
        self.selected_activity = ctk.StringVar()
        self.option_activity = ctk.CTkOptionMenu(self, variable=self.selected_activity)
        self.option_activity.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.update_activities(self.dates[0]) # Init activities

        # 4. Buttons
        ctk.CTkButton(self, text="Show Absentees", command=self.show_absentees).grid(row=5, column=0, padx=20, pady=10)
        self.export_btn = ctk.CTkButton(self, text="Export to File", command=self.export_data, state="disabled")
        self.export_btn.grid(row=6, column=0, padx=20, pady=(0, 20))
        
        # 5. Result Display
        self.textbox_result = ctk.CTkTextbox(self, width=400, height=300)
        self.textbox_result.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.textbox_result.configure(state="disabled")

        # 6. Back Button
        ctk.CTkButton(self, text="Back to Menu", command=self.close_window).grid(row=8, column=0, pady=20)

    def close_window(self):
        self.master.deiconify()
        self.destroy()

    def update_activities(self, date):
        """Updates activity dropdown based on selected date."""
        specific_activities = self.sessions.get(date, [])
        activity_names = [item['activity'] for item in specific_activities]
        
        if activity_names:
            self.option_activity.configure(values=activity_names)
            self.selected_activity.set(activity_names[0]) 
        else:
            self.option_activity.configure(values=["No Activities"])
            self.selected_activity.set("No Activities")

    def show_absentees(self):
        """Fetches and displays absentees."""
        date = self.selected_date.get()
        activity = self.selected_activity.get()
        
        self.current_absentees = []
        self.export_btn.configure(state="disabled")
        
        # Find column index
        col_index = -1
        if date in self.sessions:
            for item in self.sessions[date]:
                if item['activity'] == activity:
                    col_index = item['col_index']
                    break
        
        self.textbox_result.configure(state="normal")
        self.textbox_result.delete("0.0", "end") 
        
        if col_index != -1:
            absentees = extract_absentees(self.file_path, col_index)
            
            if absentees is not None:
                self.current_absentees = absentees
                if absentees:
                    formatted_list = [f"{s['Surname']} {s['Firstname']} ({s['Matric']})" for s in absentees]
                    self.textbox_result.insert("0.0", f"Total Absentees: {len(absentees)}\n\n" + "\n".join(formatted_list))
                    self.export_btn.configure(state="normal")
                else:
                    self.textbox_result.insert("0.0", "No absentees found for this activity.")
            else:
                self.textbox_result.insert("0.0", "Error: Failed to extract absentee data.")
        else:
            self.textbox_result.insert("0.0", "Error: Activity not found.")
            
        self.textbox_result.configure(state="disabled")

    def export_data(self):
        if not self.current_absentees: return

        filename = f"{self.selected_activity.get()}_{self.selected_date.get()}".replace("/", "-")
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("Excel file", "*.xlsx")],
            title="Save Absentees List",
            initialfile=filename
        )

        if file_path:
            success = save_absentees(self.current_absentees, file_path)
            self.textbox_result.configure(state="normal")
            msg = f"\n\n[SUCCESS] Saved to {file_path}" if success else "\n\n[ERROR] Save failed."
            self.textbox_result.insert("end", msg)
            self.textbox_result.configure(state="disabled")