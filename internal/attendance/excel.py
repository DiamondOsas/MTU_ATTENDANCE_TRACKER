import customtkinter as ctk
import pandas as pd
import os 
from tkinter import messagebox, filedialog
from tksheet import Sheet
from internal.utils.csv_handler import read_csv_robust, save_csv

class DataTable(ctk.CTkFrame):
    """
    A wrapper around tksheet for displaying Pandas DataFrames with Excel-like features.
    """
    def __init__(self, parent, dataframe, editable=True, **kwargs):
        super().__init__(parent, **kwargs)
        self.editable = editable
        
        # Header / Toolbar
        self.create_toolbar()

        # Configure tksheet
        self.sheet = Sheet(self, height=500, width=800)
        self.sheet.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status Bar
        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w", font=("Arial", 11))
        self.status_label.pack(fill="x", padx=5, pady=2)
        
        # Bindings
        bindings = [
            "single_select", "drag_select", "row_select", "column_select", 
            "column_width_resize", "row_height_resize", "arrowkeys", 
            "right_click_popup_menu", "rc_select", "copy", "cut", "paste", 
            "delete", "undo", "edit_cell"
        ]
        
        if self.editable:
            bindings.extend(["rc_insert_row", "rc_delete_row", "rc_insert_column", "rc_delete_column"])
        
        if not self.editable:
            # Restrict to viewing bindings
            bindings = ["single_select", "drag_select", "row_select", "column_select", 
                        "copy", "right_click_popup_menu", "rc_select"]

        self.sheet.enable_bindings(tuple(bindings))
        self.load_dataframe(dataframe)

    def create_toolbar(self):
        """Creates a concise header with Excel-like actions and Search."""
        toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        toolbar.pack(side="top", fill="x", padx=5, pady=(5, 0))

        # Left: Action Buttons
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.pack(side="left")

        buttons = []
        if self.editable:
            buttons.extend([
                ("Add Row", self.add_row), ("Del Row", self.delete_row),
                ("Add Col", self.add_col), ("Del Col", self.delete_col),
                ("|", None)
            ])
        
        buttons.extend([
            ("Cut", lambda: self.sheet_action("<<Cut>>")),
            ("Copy", lambda: self.sheet_action("<<Copy>>")),
            ("Paste", lambda: self.sheet_action("<<Paste>>")),
        ])

        for text, cmd in buttons:
            if text == "|":
                ctk.CTkLabel(actions_frame, text="|", width=10).pack(side="left", padx=2)
            else:
                ctk.CTkButton(actions_frame, text=text, width=60, height=24, command=cmd).pack(side="left", padx=2)

        # Right: Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(search_frame, width=150, placeholder_text="Search...")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        ctk.CTkButton(search_frame, text="Find", width=50, height=24, command=self.perform_search).pack(side="left")

    def perform_search(self):
        """Simple search that highlights matching cells."""
        query = self.search_entry.get().lower()
        if not query: return
        
        # Clear previous selection
        self.sheet.deselect("all")
        
        # Scan data
        data = self.sheet.get_sheet_data()
        found = False
        
        for r_idx, row in enumerate(data):
            for c_idx, cell in enumerate(row):
                if query in str(cell).lower():
                    # Create selection
                    self.sheet.create_selection_box(r_idx, c_idx, r_idx, c_idx, "cells")
                    self.sheet.see(r_idx, c_idx) # Scroll to first match
                    found = True
                    # If we want to find all, we continue, but tksheet selection box is usually contiguous or specific.
                    # Multiple disjoint selections might be tricky in basic usage, so let's just highlight all or first.
                    # tksheet allows adding selections.
                    
        if found:
            self.status_label.configure(text=f"Found matches for '{query}'")
        else:
            self.status_label.configure(text=f"No matches for '{query}'")

    def sheet_action(self, event_name):
        self.sheet.focus_set()
        self.sheet.event_generate(event_name)

    def add_row(self):
        self.sheet.insert_row()
        self.update_status()

    def delete_row(self):
        selected = sorted(list(self.sheet.get_selected_rows()), reverse=True)
        if selected:
            for idx in selected:
                self.sheet.delete_row(idx)
            self.update_status()

    def add_col(self):
        self.sheet.insert_column()
        self.update_status()

    def delete_col(self):
        selected = sorted(list(self.sheet.get_selected_columns()), reverse=True)
        if selected:
            for idx in selected:
                self.sheet.delete_column(idx)
            self.update_status()

    def load_dataframe(self, df):
        """Loads a new dataframe into the sheet."""
        self.df = df
        headers = list(df.columns)
        data = df.values.tolist()
        self.sheet.headers(headers)
        self.sheet.set_sheet_data(data)
        self.sheet.set_all_column_widths()
        self.update_status()

    def update_status(self):
        rows = self.sheet.get_total_rows()
        cols = self.sheet.get_total_columns()
        self.status_label.configure(text=f"Rows: {rows} | Columns: {cols}")

    def get_dataframe(self):
        """Returns the current sheet data as a DataFrame."""
        data = self.sheet.get_sheet_data()
        headers = self.sheet.headers()
        return pd.DataFrame(data, columns=headers)
    

class ExcelWindow(ctk.CTkToplevel):
    """
    Window for viewing or editing CSV files.
    """
    def __init__(self, parent, file_path, editable=True):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.editable = editable
        
        self.title(f"{'Edit' if editable else 'View'} - {os.path.basename(file_path)}")
        self.geometry("900x650")

        # Load Data
        self.df = read_csv_robust(file_path)
        if self.df.empty:
            messagebox.showwarning("Warning", "File is empty or could not be read.")
            self.df = pd.DataFrame(columns=["No Data"])

        self.setup_viewer()

    def setup_viewer(self):
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
            ctk.CTkButton(btn_frame, text="Export as Excel", command=self.export_file).pack(side="right", padx=5)

    def save_changes(self):
        new_df = self.table.get_dataframe()
        if save_csv(self.file_path, new_df):
            messagebox.showinfo("Success", "File saved successfully.")
            self.df = new_df 
        else:
            messagebox.showerror("Error", "Failed to save file.")

    def export_file(self):
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
                df.to_excel(filepath, index=False) # engine="openpyxl" is default usually
                messagebox.showinfo("Export Successful", f"Saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Error:\n{e}")

    def on_close(self):
        self.parent.deiconify()
        self.destroy()





