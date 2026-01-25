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
    A wrapper around tksheet for displaying Pandas DataFrames with Excel-like features.
    """
    def __init__(self, parent, dataframe, editable=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.editable = editable
        
        # Header / Toolbar
        if self.editable:
            self.create_toolbar()

        # Configure tksheet
        self.sheet = Sheet(self, height=500, width=800)
        self.sheet.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bindings
        bindings = [
            "single_select", "drag_select", "row_select", "column_select", 
            "column_width_resize", "row_height_resize", "arrowkeys", 
            "right_click_popup_menu", "rc_select", "copy", "cut", "paste", 
            "delete", "undo", "edit_cell"
        ]
        
        if self.editable:
            bindings.extend(["rc_insert_row", "rc_delete_row", "rc_insert_column", "rc_delete_column"])
        
        # Filter bindings for non-editable mode if needed, but keeping read-only ones is safe
        if not self.editable:
            # Restrict to viewing bindings
            bindings = ["single_select", "drag_select", "row_select", "column_select", 
                        "copy", "right_click_popup_menu", "rc_select"]

        self.sheet.enable_bindings(tuple(bindings))
        self.load_dataframe(dataframe)

    def create_toolbar(self):
        """Creates a concise header with Excel-like actions."""
        toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        toolbar.pack(side="top", fill="x", padx=5, pady=(5, 0))

        # Action Buttons
        buttons = [
            ("Add Row", self.add_row), ("Del Row", self.delete_row),
            ("Add Col", self.add_col), ("Del Col", self.delete_col),
            ("|", None),
            ("Cut", lambda: self.sheet_action("<<Cut>>")),
            ("Copy", lambda: self.sheet_action("<<Copy>>")),
            ("Paste", lambda: self.sheet_action("<<Paste>>")),
        ]

        for text, cmd in buttons:
            if text == "|":
                ctk.CTkLabel(toolbar, text="|", width=10).pack(side="left", padx=2)
            else:
                ctk.CTkButton(toolbar, text=text, width=70, height=24, command=cmd).pack(side="left", padx=2)

    def sheet_action(self, event_name):
        self.sheet.focus_set()
        self.sheet.event_generate(event_name)

    def add_row(self):
        self.sheet.insert_row()
        self.sheet.redraw()

    def delete_row(self):
        selected = sorted(list(self.sheet.get_selected_rows()), reverse=True)
        if selected:
            for idx in selected:
                self.sheet.delete_row(idx)
            self.sheet.redraw()

    def add_col(self):
        self.sheet.insert_column()
        self.sheet.redraw()

    def delete_col(self):
        selected = sorted(list(self.sheet.get_selected_columns()), reverse=True)
        if selected:
            for idx in selected:
                self.sheet.delete_column(idx)
            self.sheet.redraw()

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
        """Exports the current table data to an Excel (.xlsx) file."""
        level_name = os.path.splitext(os.path.basename(self.file_path))[0]
        suggested_name = f"{level_name}_ATTENDANCE.xlsx"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel File", "*.xlsx")],
            title="Export File to Computer",
            initialfile=suggested_name
        )
        
        if filepath:
            try:
                df = self.table.get_dataframe()
                # Use openpyxl as the engine for Excel export
                df.to_excel(filepath, index=False, engine="openpyxl")
                messagebox.showinfo("Export Successful", f"File successfully exported to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred while exporting the file:\n{e}")

    def on_close(self):
        self.parent.deiconify()
        self.destroy()





