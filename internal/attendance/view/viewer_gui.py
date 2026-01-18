import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
import os
from tksheet import Sheet
from internal.utils.csv_handler import read_csv_robust, save_csv, get_csv_columns, get_column_data

class DataTable(ctk.CTkFrame):
    """
    A wrapper around tksheet for displaying Pandas DataFrames.
    """
    def __init__(self, parent, dataframe, editable=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.editable = editable
        
        # Configure tksheet
        self.sheet = Sheet(self, height=500, width=800)
        self.sheet.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Setup bindings
        if self.editable:
            self.sheet.enable_bindings(("single_select", "row_select", "column_width_resize", 
                                        "arrowkeys", "right_click_popup_menu", "rc_select", 
                                        "copy", "cut", "paste", "delete", "undo", "edit_cell"))
        else:
            self.sheet.enable_bindings(("single_select", "row_select", "copy", "right_click_popup_menu"))

        self.load_dataframe(dataframe)

    def load_dataframe(self, df):
        """Loads a new dataframe into the sheet."""
        self.df = df
        headers = list(df.columns)
        data = df.values.tolist()
        self.sheet.headers(headers)
        self.sheet.set_sheet_data(data)
        self.sheet.set_all_column_widths()

    def get_dataframe(self):
        """Returns the current sheet data as a DataFrame."""
        data = self.sheet.get_sheet_data()
        headers = self.sheet.headers()
        return pd.DataFrame(data, columns=headers)


class ViewerWindow(ctk.CTkToplevel):
    """
    Dual-purpose window: 
    1. 'view' mode: View/Edit CSV data.
    2. 'select_column' mode: Select a specific column from a CSV.
    """
    def __init__(self, parent, file_path, editable=True, mode="view"):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.editable = editable
        self.mode = mode
        self.selected_column_data = None
        
        self.title(f"{'Edit' if editable else 'View'} - {os.path.basename(file_path)}")
        self.geometry("800x600" if mode == "view" else "400x250")

        # Load Data
        self.df = read_csv_robust(file_path)
        if self.df.empty:
            messagebox.showwarning("Warning", "File is empty or could not be read.")
            self.df = pd.DataFrame(columns=["No Data"])

        # Setup UI based on mode
        if self.mode == "select_column":
            self.setup_column_selector()
        else:
            self.setup_viewer()

    def setup_viewer(self):
        """Sets up the table viewer with Save/Close buttons."""
        # Table
        self.table = DataTable(self, self.df, self.editable)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        # Controls
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="Close", command=self.on_close, fg_color="gray").pack(side="right", padx=5)
        
        if self.editable:
            ctk.CTkButton(btn_frame, text="Save Changes", command=self.save_changes).pack(side="right", padx=5)

    def setup_column_selector(self):
        """Sets up the dropdown to select a column."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="Select Column", font=("Arial", 16, "bold")).grid(row=0, column=0, pady=20)

        columns = self.df.columns.tolist()
        self.col_var = ctk.StringVar(value=columns[0] if columns else "")
        
        self.dropdown = ctk.CTkComboBox(self, values=columns, variable=self.col_var, width=250)
        self.dropdown.grid(row=1, column=0, pady=10)
        if not columns: self.dropdown.configure(state="disabled")

        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=2, column=0, pady=20)
        
        ctk.CTkButton(btn_frame, text="Confirm", command=self.confirm_selection).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="gray").pack(side="left", padx=10)

    def save_changes(self):
        """Saves current table data to the CSV."""
        new_df = self.table.get_dataframe()
        if save_csv(self.file_path, new_df):
            messagebox.showinfo("Success", "File saved successfully.")
            self.df = new_df # Update internal state
        else:
            messagebox.showerror("Error", "Failed to save file.")

    def confirm_selection(self):
        col_name = self.col_var.get()
        if col_name and col_name in self.df.columns:
            self.selected_column_data = self.df[col_name].dropna().tolist()
            self.destroy()
        else:
            messagebox.showerror("Error", "Invalid column selected.")

    def on_close(self):
        self.destroy()

    def destroy(self):
        # Ensure parent window reappears
        if self.parent:
            try: self.parent.deiconify()
            except: pass
        super().destroy()