import customtkinter as ctk
from tkinter import filedialog # Import filedialog for saving files
from func.absentees import get_session_info, extract_absentees, save_absentees
import os

class PrintAbsenteesWindow(ctk.CTkToplevel):
    """
    This class creates a new top-level window for viewing absentee reports.
    It allows users to select a date and an activity from a chosen attendance
    CSV file and then displays a list of students who were marked as absent
    for that specific session.

    It integrates with functions from 'func.absentees' to process the CSV data.
    """
    def __init__(self, master, file_path):
        """
        Initializes the PrintAbsenteesWindow.

        Args:
            master (ctk.CTk | ctk.CTkFrame): The parent window (master) of this Toplevel window.
                                             This is usually the main application window.
            file_path (str): The full path to the attendance CSV file selected by the user.
        """
        super().__init__(master)
        self.master = master # Store the reference to the parent window
        self.file_path = file_path # Store the path to the CSV file
        self.title("View Absentees") # Set the window title
        
        # Store current absentee data for export
        self.current_absentees = []
        
        # --- Customizable Settings ---
        # Junior developer: You can easily change the window size here.
        # Format: "WIDTHxHEIGHT" (e.g., "600x700")
        self.geometry("500x650") # Increased height slightly for the new button
        
        # Junior developer: You can change the font styles for labels and titles here.
        # ctk.CTkFont(size=FONT_SIZE, weight="bold" or "normal")
        title_font = ctk.CTkFont(size=20, weight="bold") 
        label_font = ctk.CTkFont(size=14) 
        # -----------------------------

        # Configure the grid layout for the window.
        # This makes the widgets expand nicely when the window is resized.
        self.grid_columnconfigure(0, weight=1) # The single column will expand horizontally
        # The 7th row (index 7) is for the textbox_result, allowing it to expand vertically.
        self.grid_rowconfigure(7, weight=1) 
        
        # Load attendance data from the CSV file.
        # get_session_info is a helper function from 'func/absentees.py'.
        # It parses the CSV and returns a dictionary where keys are dates
        # and values are lists of activities with their corresponding column indices.
        # Example: {'26/11/25': [{'activity': 'MANNA WATER', 'col_index': 3}, ...]}
        self.sessions = get_session_info(self.file_path)
        # Extract all unique dates available in the attendance file.
        self.dates = list(self.sessions.keys())
        
        # --- GUI Elements ---

        # 1. Title Label
        # Displays the main title for the absentee report.
        self.label_title = ctk.CTkLabel(self, text="Absentees Report", font=title_font)
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Check if any valid attendance data was found in the file.
        # If not, display an error message and exit the window initialization.
        if not self.dates:
            self.error_label = ctk.CTkLabel(self, text="No attendance data found in this file.", text_color="red")
            self.error_label.grid(row=1, column=0, padx=20, pady=20)
            # Junior developer: You might want to add a close button here if no data is found.
            return

        # 2. Date Selection Dropdown
        # Label for the date selection dropdown.
        self.label_date = ctk.CTkLabel(self, text="Select Date:", font=label_font)
        self.label_date.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        
        # ctk.StringVar is used to dynamically track the currently selected date.
        # The initial value is set to the first date found in the CSV.
        self.selected_date = ctk.StringVar(value=self.dates[0])
        # The CTkOptionMenu widget provides a dropdown for date selection.
        # When a date is chosen, 'update_activities' method is called to
        # refresh the activity dropdown based on the new date.
        self.option_date = ctk.CTkOptionMenu(self, values=self.dates, 
                                             command=self.update_activities, 
                                             variable=self.selected_date)
        self.option_date.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # 3. Activity Selection Dropdown
        # Label for the activity selection dropdown.
        self.label_activity = ctk.CTkLabel(self, text="Select Activity:", font=label_font)
        self.label_activity.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        
        # ctk.StringVar to track the selected activity.
        self.selected_activity = ctk.StringVar()
        # The CTkOptionMenu for activities. Its values will be updated
        # whenever a new date is selected.
        self.option_activity = ctk.CTkOptionMenu(self, variable=self.selected_activity)
        self.option_activity.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Initially populate the activity dropdown based on the first selected date.
        self.update_activities(self.dates[0])
        
        # 4. Action Button
        # Button to trigger the display of absentees.
        # When clicked, it calls the 'show_absentees' method.
        self.btn_show = ctk.CTkButton(self, text="Show Absentees", command=self.show_absentees)
        self.btn_show.grid(row=5, column=0, padx=20, pady=(20, 10))

        # 5. Export Button
        # Button to export the absentee list to CSV or Excel.
        # It is initially disabled and only enabled when absentees are found.
        self.export_btn = ctk.CTkButton(self, text="Export to File", command=self.export_data, state="disabled")
        self.export_btn.grid(row=6, column=0, padx=20, pady=(0, 20))
        
        # 6. Result Text Area
        # A scrollable textbox to display the names of absent students.
        self.textbox_result = ctk.CTkTextbox(self, width=400, height=300)
        self.textbox_result.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="nsew")
        # Make the textbox read-only by default so users cannot type in it.
        self.textbox_result.configure(state="disabled")

    def update_activities(self, date):
        """
        Updates the activity dropdown options based on the currently selected date.
        This method is automatically called when the selected date in the
        'option_date' dropdown changes.

        Args:
            date (str): The date string selected by the user from the date dropdown.
        """
        # Retrieve the list of activity dictionaries for the chosen date.
        # Example: [{'activity': 'MANNA WATER', 'col_index': 3}]
        specific_activities = self.sessions.get(date, [])
        
        # Extract just the 'activity' names from the list of dictionaries.
        activity_names = [item['activity'] for item in specific_activities]
        
        # Update the activity dropdown with the new list of activities.
        if activity_names:
            self.option_activity.configure(values=activity_names)
            # Automatically select the first activity in the list.
            self.selected_activity.set(activity_names[0]) 
        else:
            # If no activities are found for the selected date, display a default message.
            self.option_activity.configure(values=["No Activities"])
            self.selected_activity.set("No Activities")

    def show_absentees(self):
        """
        Retrieves the selected date and activity, finds the corresponding column index
        in the CSV, and then calls the external 'extract_absentees' function
        to get and display the list of absent students.
        """
        date = self.selected_date.get()     # Get the chosen date from the dropdown
        activity = self.selected_activity.get() # Get the chosen activity from the dropdown
        
        # Reset current data and disable export button
        self.current_absentees = []
        self.export_btn.configure(state="disabled")
        
        # Initialize column index to an invalid value.
        col_index = -1
        # Iterate through the activities for the selected date to find
        # the matching activity and retrieve its column index.
        if date in self.sessions:
            for item in self.sessions[date]:
                if item['activity'] == activity:
                    col_index = item['col_index']
                    break # Found the matching activity, so stop searching
        
        # Before updating, enable the textbox so content can be inserted.
        self.textbox_result.configure(state="normal")
        # Clear any previously displayed text in the result textbox.
        self.textbox_result.delete("0.0", "end") 
        
        # If a valid column index was found for the selected date and activity:
        if col_index != -1:
            # Call the helper function from 'func/absentees.py' to get the absentees.
            # This function returns a list of dictionaries: [{'Surname': ..., 'Firstname': ..., 'Matric': ...}]
            absentees = extract_absentees(self.file_path, col_index)
            
            # Check if absentees is not None (None indicates an error occurred)
            if absentees is not None:
                self.current_absentees = absentees # Store data for potential export
                
                if absentees:
                    # Format the list of dictionaries into readable strings for the text box
                    formatted_list = [
                        f"{student['Surname']} {student['Firstname']} ({student['Matric']})" 
                        for student in absentees
                    ]
                    
                    count = len(formatted_list)
                    self.textbox_result.insert("0.0", f"Total Absentees: {count}\n\n" + "\n".join(formatted_list))
                    
                    # Enable the export button since we have data
                    self.export_btn.configure(state="normal")
                else:
                    self.textbox_result.insert("0.0", "Good news! No absentees found for this activity.")
            else:
                # If None was returned, it means an error occurred in the backend function
                self.textbox_result.insert("0.0", "Error: Failed to extract absentee data.")
        else:
            # If the column index was not found, display an error message.
            self.textbox_result.insert("0.0", "Error: Could not find data for the selected combination (date and activity).")
            
        # After updating, disable the textbox again to make it read-only.
        self.textbox_result.configure(state="disabled")

    def export_data(self):
        """
        Opens a file dialog to let the user choose a location and format (CSV or Excel)
        to save the absentee list.
        """
        if not self.current_absentees:
            return # No data to export

        # Open file dialog
        # Junior developer: This opens a standard 'Save As' window.
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv"), ("Excel file", "*.xlsx")],
            title="Save Absentees List"
        )

        if file_path:
            # Call the helper function to save the data
            success = save_absentees(self.current_absentees, file_path)
            
            # Provide feedback to the user
            self.textbox_result.configure(state="normal")
            if success:
                self.textbox_result.insert("0.0", f"\n\n[SUCCESS] Data exported to:\n{file_path}\n")
            else:
                self.textbox_result.insert("0.0", f"\n\n[ERROR] Failed to export data.\n")
            self.textbox_result.configure(state="disabled")
