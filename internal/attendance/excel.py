import os
import customtkinter as ctk
import pandas as pd
from tkinter import messagebox, filedialog
from tksheet import Sheet
from typing import Optional, List, Tuple, Any

from internal.utils.csv_handler import read_csv_robust, save_csv

class DataTable(ctk.CTkFrame):
    """
    A wrapper around tksheet for displaying Pandas DataFrames with Excel-like features.
    Includes editing capabilities, search functionality, and status updates.
    """
    def __init__(self, parent: Any, dataframe: pd.DataFrame, editable: bool = True, **kwargs):
        super().__init__(parent, **kwargs)
        self.editable = editable
        self.df = dataframe
        self.search_matches: List[Tuple[int, int]] = []
        self.current_match_index: int = -1
        self.last_query: str = ""

        # UI Components
        self._create_toolbar()
        self._create_sheet()
        self._create_statusbar()

        # Initial Data Load
        self.load_dataframe(self.df)

    def _create_sheet(self):
        """Initializes and packs the tksheet widget with appropriate bindings."""
        self.sheet = Sheet(self, height=500, width=800)
        self.sheet.pack(fill="both", expand=True, padx=5, pady=5)

        bindings = [
            "single_select", "drag_select", "row_select", "column_select", 
            "column_width_resize", "row_height_resize", "arrowkeys", 
            "right_click_popup_menu", "rc_select", "copy", "cut", "paste", 
            "delete", "undo", "edit_cell"
        ]
        
        if self.editable:
            bindings.extend(["rc_insert_row", "rc_delete_row", "rc_insert_column", "rc_delete_column"])
        else:
            # Restrict destructive bindings if not editable
            bindings = [
                "single_select", "drag_select", "row_select", "column_select", 
                "copy", "right_click_popup_menu", "rc_select", "arrowkeys"
            ]

        self.sheet.enable_bindings(tuple(bindings))

    def _create_statusbar(self):
        """Creates the status bar for displaying info and search results."""
        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w", font=("Arial", 11))
        self.status_label.pack(fill="x", padx=5, pady=2)

    def _create_toolbar(self):
        """Creates the toolbar with action buttons and search field."""
        toolbar = ctk.CTkFrame(self, height=40, fg_color="transparent")
        toolbar.pack(side="top", fill="x", padx=5, pady=(5, 0))

        # Left: Action Buttons
        actions_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        actions_frame.pack(side="left")

        # Define buttons configuration
        buttons_config = []
        if self.editable:
            buttons_config.extend([
                ("Add Row", self.add_row),
                ("Del Row", self.delete_row),
                ("Add Col", self.add_col),
                ("Del Col", self.delete_col),
                ("|", None) 
            ])
        
        buttons_config.extend([
            ("Cut", lambda: self.sheet_action("<<Cut>>")),
            ("Copy", lambda: self.sheet_action("<<Copy>>")),
            ("Paste", lambda: self.sheet_action("<<Paste>>")),
        ])

        for text, command in buttons_config:
            if text == "|":
                ctk.CTkLabel(actions_frame, text="|", width=10).pack(side="left", padx=2)
            else:
                ctk.CTkButton(
                    actions_frame, text=text, width=60, height=24, command=command
                ).pack(side="left", padx=2)

        # Right: Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(search_frame, width=150, placeholder_text="Search...")
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        
        ctk.CTkButton(
            search_frame, text="Find", width=50, height=24, command=self.perform_search
        ).pack(side="left")

    def perform_search(self):
        """
        Searches for the text in the sheet. 
        Cycles through matches on subsequent presses.
        """
        query = self.search_entry.get().lower()
        if not query:
            self.status_label.configure(text="Please enter a search term.")
            return

        # Reset search if query changed
        if query != self.last_query:
            self.search_matches = []
            self.current_match_index = -1
            self.last_query = query
            
            # Scan data for all matches
            data = self.sheet.get_sheet_data()
            for r_idx, row in enumerate(data):
                for c_idx, cell in enumerate(row):
                    if query in str(cell).lower():
                        self.search_matches.append((r_idx, c_idx))

        if not self.search_matches:
            self.status_label.configure(text=f"No matches found for '{query}'")
            return

        # Cycle to next match
        self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
        r, c = self.search_matches[self.current_match_index]
        
        # Select and scroll to match
        self.sheet.deselect("all")
        self.sheet.create_selection_box(r, c, r, c, "cells")
        self.sheet.see(r, c)
        
        self.status_label.configure(
            text=f"Match {self.current_match_index + 1} of {len(self.search_matches)} for '{query}'"
        )

    def sheet_action(self, event_name: str):
        """Triggers a tksheet virtual event."""
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
        else:
            messagebox.showinfo("Info", "No rows selected to delete.")

    def add_col(self):
        self.sheet.insert_column()
        self.update_status()

    def delete_col(self):
        selected = sorted(list(self.sheet.get_selected_columns()), reverse=True)
        if selected:
            for idx in selected:
                self.sheet.delete_column(idx)
            self.update_status()
        else:
            messagebox.showinfo("Info", "No columns selected to delete.")

    def load_dataframe(self, df: pd.DataFrame):
        """Loads a new dataframe into the sheet."""
        self.df = df
        headers = list(df.columns)
        # Convert all data to string to ensure consistency in display, 
        # handling NaN usually handled by tksheet or pandas, but safe casting helps.
        data = df.fillna("").values.tolist()
        
        self.sheet.headers(headers)
        self.sheet.set_sheet_data(data)
        self.sheet.set_all_column_widths()
        self.update_status()

    def update_status(self):
        """Updates the status bar with current dimensions."""
        rows = self.sheet.get_total_rows()
        cols = self.sheet.get_total_columns()
        self.status_label.configure(text=f"Rows: {rows} | Columns: {cols}")

    def get_dataframe(self) -> pd.DataFrame:
        """Returns the current sheet data as a DataFrame."""
        data = self.sheet.get_sheet_data()
        headers = self.sheet.headers()
        return pd.DataFrame(data, columns=headers)
    

class ExcelWindow(ctk.CTkToplevel):
    """
    Top-level window for viewing or editing CSV files via DataTable.
    """
    def __init__(self, parent: Any, file_path: str, editable: bool = True):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.editable = editable
        
        self.title(f"{'Edit' if editable else 'View'} - {os.path.basename(file_path)}")
        self.geometry("900x650")
        
        # Ensure window is on top/focused
        self.lift()
        self.focus_force()

        # Load Data
        self.df = read_csv_robust(file_path)
        if self.df.empty:
            messagebox.showwarning("Warning", "File is empty or could not be read properly.")
            self.df = pd.DataFrame(columns=["Info"], data=[["No Data"]])

        self._setup_ui()

    def _setup_ui(self):
        """Sets up the window layout."""
        # Table 
        self.table = DataTable(self, self.df, self.editable)
        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        # Controls
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=10, pady=10)

        # Right-aligned buttons
        ctk.CTkButton(
            btn_frame, text="Close", command=self.on_close, fg_color="gray"
        ).pack(side="right", padx=5)
        
        if self.editable:
            ctk.CTkButton(
                btn_frame, text="Save Changes", command=self.save_changes
            ).pack(side="right", padx=5)
        else:
            ctk.CTkButton(
                btn_frame, text="Export as Excel", command=self.export_file
            ).pack(side="right", padx=5)

    def save_changes(self):
        """Saves the current table data back to the CSV file."""
        new_df = self.table.get_dataframe()
        if save_csv(self.file_path, new_df):
            messagebox.showinfo("Success", "File saved successfully.")
            self.df = new_df 
        else:
            messagebox.showerror("Error", "Failed to save file.")

    def export_file(self):
        """Exports the current data to an Excel file."""
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
                # Default to openpyxl for xlsx
                df.to_excel(filepath, index=False) 
                messagebox.showinfo("Export Successful", f"Saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Export Error", f"An error occurred while exporting:\n{e}")

    def on_close(self):
        """Handles window closing event."""
        self.parent.deiconify()
        self.destroy()





