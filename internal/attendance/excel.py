import customtkinter as ctk
import pandas as pd
import os 
from tkinter import messagebox, filedialog
from tksheet import Sheet
from internal.utils.csv_handler import read_csv_robust, save_csv, get_csv_columns, get_column_data

#I just love this particular module
#it just teels you how libires has made programming so simple that i can do a proper xcel in like how many lines of code???
#the tksheet is more like a tkcheat... not funny...
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
    

class ExcelWindow(ctk.CTkToplevel):
    """
    Dual-purpose window: 
    1. Eidtable deterine mode
    """
    def __init__(self, parent, file_path, editable=True):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.editable = editable
        self.selected_column_data = None
        
        self.title(f"{'Edit' if editable else 'View'} - {os.path.basename(file_path)}")
        self.geometry("800x600")

        # Load Data
        self.df = read_csv_robust(file_path)
        if self.df.empty:
            messagebox.showwarning("Warning", "File is empty or could not be read.")
            self.df = pd.DataFrame(columns=["No Data"])

        # Setup UI 
        
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
        else:
            ctk.CTkButton(btn_frame, text="Export File",command=self.export_file).pack(side="right", padx=5)

    def save_changes(self):
        """Saves current table data to the CSV."""
        new_df = self.table.get_dataframe()
        if save_csv(self.file_path, new_df):
            messagebox.showinfo("Success", "File saved successfully.")
            self.df = new_df # Update internal state
        else:
            messagebox.showerror("Error", "Failed to save file.")

    def export_file(self):
        level_name = os.path.splitext(os.path.basename(self.file_path))[0]
        filename =f"{level_name}_ATTENDANCE"
        filepath = filedialog.asksaveasfile(
            mode="w",
            confirmoverwrite="t",
            filetypes=[("Excel File", "*xlsx")],
            title="Export File to Computer",
            initialfile=filename
        )
        if filename:
            try:
                print("Trying to save file")
            except Exception as e:
                print(f"Error saving File: {e}")

    def on_close(self):
        self.parent.deiconify()
        self.destroy()





