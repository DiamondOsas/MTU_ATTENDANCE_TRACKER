import customtkinter as ctk
import pandas as pd
import os
from func.absentees import extract_absentees # Assuming this function will be created here
import csv
class PrintAbsenteesWindow(ctk.CTkToplevel):
    """
    A window that allows the user to select a date and activity from a chosen
    attendance CSV file and then extract and save absentee records.
    """
    def __init__(self, master, file_path):
        super().__init__(master)
        self.master = master
        self.file_path = file_path
        self.title(f"Extract Absentees from {os.path.basename(file_path)}")
        self.geometry("500x400")
        self.grab_set() # Make this window modal

        # Configure grid layout
        self.grid_rowconfigure((0, 6), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.data = self._load_attendance_data()
        if self.data is None:
            ctk.CTkLabel(self, text="Error loading attendance data.").grid(row=1, column=0, padx=20, pady=10)
            self.close_button = ctk.CTkButton(self, text="Close", command=self.destroy)
            self.close_button.grid(row=2, column=0, padx=20, pady=10)
            return

        self.dates, self.activities = self._extract_dates_and_activities()

        # --- 1. Title Label ---
        self.title_label = ctk.CTkLabel(self, text="Select Date and Activity", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=10)

        # --- 2. Date Selection ---
        ctk.CTkLabel(self, text="Select Date:").grid(row=2, column=0, padx=20, pady=5, sticky="w")
        self.selected_date_var = ctk.StringVar(value=self.dates[0] if self.dates else "")
        self.date_optionmenu = ctk.CTkOptionMenu(self, values=self.dates,
                                                 variable=self.selected_date_var)
        self.date_optionmenu.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # --- 3. Activity Selection ---
        ctk.CTkLabel(self, text="Select Activity:").grid(row=4, column=0, padx=20, pady=5, sticky="w")
        self.selected_activity_var = ctk.StringVar(value=self.activities[0] if self.activities else "")
        self.activity_optionmenu = ctk.CTkOptionMenu(self, values=self.activities,
                                                     variable=self.selected_activity_var)
        self.activity_optionmenu.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # --- 4. Extract Button ---
        self.extract_button = ctk.CTkButton(self, text="Extract Absentees", command=self._on_extract_absentees)
        self.extract_button.grid(row=6, column=0, padx=20, pady=20)

        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _load_attendance_data(self):
        """
        Loads the attendance data from the specified CSV file into a pandas DataFrame.
        Handles the specific format of the CSV with DATE and ACTIVITY rows and a
        variable number of columns.
        """
        try:
            with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)

            header_row_index = -1
            date_row_index = -1
            activity_row_index = -1

            for i, line in enumerate(lines):
                if line and "Surname" in line[0]:
                    header_row_index = i
                elif line and line[0].startswith("DATE"):
                    date_row_index = i
                elif line and line[0].startswith("ACTIVITY"):
                    activity_row_index = i

            if header_row_index == -1 or date_row_index == -1 or activity_row_index == -1:
                print("Error: Could not find header, DATE, or ACTIVITY rows in the CSV.")
                return None

            data_start_row = max(date_row_index, activity_row_index) + 1
            while data_start_row < len(lines) and not lines[data_start_row]:
                data_start_row += 1

            # --- Construct Headers ---
            fixed_headers = ["Surname", "Firstname", "Matric NO", "Chapel Seat"]
            dates_line = lines[date_row_index]
            activities_line = lines[activity_row_index]
            dynamic_headers = []
            for i in range(4, len(dates_line)):
                date_val = dates_line[i].strip()
                activity_val = activities_line[i].strip() if i < len(activities_line) else ""
                if date_val and activity_val:
                    dynamic_headers.append(f"{date_val} - {activity_val}")
                elif date_val:
                    dynamic_headers.append(date_val)
                else:
                    dynamic_headers.append(f"Unnamed_{i}")

            full_headers = fixed_headers + dynamic_headers

            # --- Load Data ---
            student_data = lines[data_start_row:]
            
            # Pad rows to have the same number of columns as the header
            for row in student_data:
                while len(row) < len(full_headers):
                    row.append('')

            df = pd.DataFrame(student_data, columns=full_headers)
            
            return df
        except Exception as e:
            print(f"Error loading attendance data: {e}")
            # Show a pop-up error message to the user
            import customtkinter as ctk
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to load attendance data.\n\nError: {e}\n\nPlease ensure the file is a valid CSV and not open in another program.")
            return None

    def _extract_dates_and_activities(self):
        """
        Extracts unique dates and activities from the DataFrame's columns.
        Assumes columns are in "DATE - ACTIVITY" format or just "DATE".
        """
        dates = []
        activities = []
        for col in self.data.columns[4:]: # Iterate over dynamic columns
            if " - " in col:
                date_part, activity_part = col.split(" - ", 1)
                dates.append(date_part.strip())
                activities.append(activity_part.strip())
            else:
                # If only date is present, use it as both date and a generic activity
                dates.append(col.strip())
                activities.append("General Activity") # Placeholder for activity

        return sorted(list(set(dates))), sorted(list(set(activities)))


    def _on_extract_absentees(self):
        """
        Calls the absentee extraction logic and handles saving the output.
        """
        selected_date = self.selected_date_var.get()
        selected_activity = self.selected_activity_var.get()

        if not selected_date or not selected_activity:
            ctk.CTkMessagebox.showerror("Error", "Please select both a date and an activity.")
            return

        # Call the function from func.absentees to get the absentee DataFrame
        absentee_df = extract_absentees(self.data, selected_date, selected_activity)

        if absentee_df is not None and not absentee_df.empty:
            # Prompt user to save the file
            self._save_absentee_file(absentee_df)
        else:
            ctk.CTkMessagebox.showinfo("No Absentees", "No absentees found for the selected date and activity.")

    def _save_absentee_file(self, df):
        """
        Opens a file dialog for the user to choose where to save the absentee CSV.
        """
        # Import filedialog here to avoid circular dependency if it's in another gui file
        from tkinter import filedialog 
        
        # Suggest a default filename
        default_filename = f"absentees_{self.selected_date_var.get().replace('/', '-')}_{self.selected_activity_var.get().replace(' ', '_')}.csv"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            title="Save Absentees Report",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                df.to_csv(file_path, index=False)
                ctk.CTkMessagebox.showinfo("Success", f"Absentees report saved to:\n{file_path}")
            except Exception as e:
                ctk.CTkMessagebox.showerror("Error", f"Failed to save file: {e}")

    def _on_closing(self):
        """
        Handles the window closing event. Re-enables the master window.
        """
        self.master.deiconify() # Show the main window again
        self.destroy()
