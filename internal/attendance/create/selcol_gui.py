import customtkinter as ctk
from tkinter import messagebox
import os
import sys

# Add the parent directory to the path so we can import from func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from internal.utils.csv_handler import get_csv_columns, get_column_data

class SelectColumnWindow(ctk.CTkToplevel):
    """
    Window to select a column from a CSV file.
    """
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.selected_column_data = None
        
        file_name = os.path.basename(file_path)
        self.title(f"Select Column - {file_name}")
        self.geometry("400x250")
        
        self.setup_column_selection()
        
    def setup_column_selection(self):
        """
        Sets up the widgets for the column selection mode.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Title ---
        self.selection_title = ctk.CTkLabel(self, text="Select the Matric Number Column", font=ctk.CTkFont(size=16, weight="bold"))
        self.selection_title.grid(row=0, column=0, padx=20, pady=20)

        # --- Column Dropdown ---
        self.column_frame = ctk.CTkFrame(self)
        self.column_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.column_frame.grid_columnconfigure(0, weight=1)

        try:
            columns = get_csv_columns(self.file_path)
        except Exception as e:
            # Handle potential errors if file reading fails
            columns = []
            
        self.column_dropdown = ctk.CTkComboBox(
            self.column_frame,
            values=columns if columns else ["No columns found"],
            width=300
        )
        self.column_dropdown.grid(row=0, column=0, padx=20, pady=10)
        if not columns:
            self.column_dropdown.set("No columns found")
            self.column_dropdown.configure(state="disabled")
        else:
            self.column_dropdown.set(columns[0])

        # --- Action Buttons ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, padx=20, pady=20, sticky="s")
        self.action_frame.grid_columnconfigure((0, 1), weight=1)

        self.confirm_button = ctk.CTkButton(
            self.action_frame,
            text="Confirm Selection",
            command=self.confirm_column_selection,
            state="normal" if columns else "disabled"
        )
        self.confirm_button.grid(row=0, column=0, padx=10, pady=10)

        self.cancel_button = ctk.CTkButton(
            self.action_frame,
            text="Cancel",
            command=self.close_window
        )
        self.cancel_button.grid(row=0, column=1, padx=10, pady=10)

    def confirm_column_selection(self):
        """
        Handles the confirmation of the column selection.
        """
        selected_column = self.column_dropdown.get()
        if selected_column and selected_column != "No columns found":
            self.selected_column_data = get_column_data(self.file_path, selected_column)
            if self.selected_column_data is not None:
                messagebox.showinfo("Success", f"Successfully extracted {len(self.selected_column_data)} matric numbers from '{selected_column}'.")
                self.close_window()
            else:
                messagebox.showerror("Error", f"Could not retrieve data for column '{selected_column}'.")
        else:
            messagebox.showwarning("Warning", "Please select a valid column.")

    def close_window(self):
        self.destroy()
            
    def destroy(self):
        # Ensure parent is shown when this window is destroyed
        try:
            if self.parent and self.parent.winfo_exists():
                 self.parent.deiconify()
        except:
            pass
        super().destroy()
      