import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
import os
import sys
from tksheet import Sheet
import tkinter as tk

# Add the parent directory to the path so we can import from func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from func.viewer import get_students_data_from_file, save_students_data, get_csv_columns, get_column_data


class DataTable:
    """
    A custom widget to display and edit tabular data similar to a spreadsheet using tksheet.
    """
    def __init__(self, parent, dataframe, editable=True):
        self.parent = parent
        self.dataframe = dataframe.copy()
        self.original_dataframe = dataframe.copy()
        self.editable = editable
        
        # Convert dataframe to the format needed by tksheet
        self.headers = list(dataframe.columns)
        self.data_list = dataframe.values.tolist()
        
        # Create the sheet widget
        self.sheet = Sheet(
            parent,
            data=self.data_list,
            headers=self.headers,
            height=500,
            width=800
        )
        
        # Configure the sheet based on editability
        if not self.editable:
            self.sheet.enable_bindings(("single_select", "row_select", "copy", "right_click_popup_menu", "rc_select"))
        else:
            self.sheet.enable_bindings(("single_select", "row_select", "column_width_resize", "arrowkeys", 
                                        "right_click_popup_menu", "rc_select", "copy", "cut", "paste", 
                                        "delete", "undo", "edit_cell"))
        
        # Pack the sheet
        self.sheet.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Set column widths to fit content
        self.sheet.set_all_column_widths()
        
    def get_data_as_dataframe(self):
        """
        Retrieves the current data from the sheet and returns it as a DataFrame.
        """
        # Get the current data from the sheet
        current_data = self.sheet.get_sheet_data()
        
        # Convert to DataFrame with the saved headers
        df = pd.DataFrame(current_data, columns=self.headers)
        
        # Convert numeric columns back to numeric types where possible
        for col in df.columns:
            orig_dtype = self.original_dataframe[col].dtype
            if pd.api.types.is_numeric_dtype(orig_dtype):
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except ValueError:
                    pass  # Keep as string if conversion fails
        
        return df
    
    def refresh_table(self, new_dataframe):
        """
        Refreshes the table with new dataframe data.
        """
        self.dataframe = new_dataframe.copy()
        self.original_dataframe = new_dataframe.copy()
        
        # Update headers and data
        self.headers = list(new_dataframe.columns)
        self.data_list = new_dataframe.values.tolist()
        
        # Update the sheet with new data
        self.sheet.data_reference(new_dataframe.values.tolist(), reset_col_positions=True, 
                                  reset_row_positions=True, redraw=True)
        self.sheet.headers(new_dataframe.columns.tolist())
        self.sheet.set_all_column_widths()


class ViewerWindow(ctk.CTkToplevel):
    """
    Window that displays student data in an Excel-like interface for viewing and editing.
    Can also be used to select a column from a CSV file.
    """
    def __init__(self, parent, file_path, editable=True, mode="view"):
        """
        Initializes the ViewerWindow.
        
        Args:
            parent: The parent window
            file_path: Path to the CSV file to be displayed
            editable: Whether the data should be editable
            mode: "view" for normal viewing/editing, "select_column" for column selection
        """
        super().__init__(parent)
        
        self.parent = parent
        self.file_path = file_path
        self.editable = editable
        self.is_modified = False
        self.mode = mode
        self.selected_column_data = None
        
        # Load the data from file
        try:
            self.df = get_students_data_from_file(file_path)
            if self.df.empty:
                messagebox.showwarning("Warning", f"No data found in file: {file_path}")
                # Create an empty dataframe with default columns
                self.df = pd.DataFrame(columns=["ID", "Name", "Email", "Level"])
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {str(e)}")
            self.df = pd.DataFrame()
        
        # Configure window
        file_name = os.path.basename(file_path)
        if self.mode == "select_column":
            self.title(f"Select Column - {file_name}")
            self.geometry("400x250")
        else:
            self.title(f"{'Edit' if editable else 'View'} - {file_name}")
            self.geometry("800x600")

        if self.mode == "select_column":
            self.setup_column_selection()
        else:
            self.setup_data_viewer()
    
    def setup_data_viewer(self):
        """
        Sets up the widgets for the data viewing/editing mode.
        """
        # Create the table
        self.table = DataTable(self, self.df, self.editable)
        
        # Create button frame
        if self.editable:
            self.button_frame = ctk.CTkFrame(self)
            self.button_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            # Save button
            self.save_button = ctk.CTkButton(
                self.button_frame,
                text="Save Changes",
                command=self.save_changes,
                fg_color="green"
            )
            self.save_button.pack(side="right", padx=5, pady=5)
            
            # Close without saving button
            self.close_button = ctk.CTkButton(
                self.button_frame,
                text="Close Without Saving",
                command=self.close_window
            )
            self.close_button.pack(side="right", padx=5, pady=5)
            
            # Status label
            self.status_label = ctk.CTkLabel(
                self.button_frame,
                text="Ready" if not self.is_modified else "Modified - Save to keep changes"
            )
            self.status_label.pack(side="right", padx=5, pady=5)

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

        columns = get_csv_columns(self.file_path)
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
                # You can now use self.selected_column_data in other parts of the app
                print(self.selected_column_data) # For debugging
                self.close_window()
            else:
                messagebox.showerror("Error", f"Could not retrieve data for column '{selected_column}'.")
        else:
            messagebox.showwarning("Warning", "Please select a valid column.")
    
    def save_changes(self):
        """
        Saves the modified data back to the file.
        """
        try:
            # Get the updated dataframe from the table
            updated_df = self.table.get_data_as_dataframe()
            
            # Save to file
            save_students_data(self.file_path, updated_df)
            
            # Update the internal dataframe
            self.df = updated_df.copy()
            self.table.original_dataframe = updated_df.copy()  # Update original for future comparisons
            self.is_modified = False
            
            # Show success message
            messagebox.showinfo("Success", "Changes saved successfully!")
            
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.configure(text="Ready")
                
        except Exception as e:
            messagebox.showerror("Error", f"Could not save changes: {str(e)}")
    
    def close_window(self):
        """
        Closes the window, but prompts to save if there are unsaved changes.
        """
        if self.is_modified:
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?"
            )
            
            if response is True:  # Yes - save and close
                self.save_changes()
                self.destroy()
                if self.parent:
                    self.parent.deiconify()
            elif response is False:  # No - close without saving
                self.destroy()
                if self.parent:
                    self.parent.deiconify()
            # If Cancel, do nothing
        else:
            self.destroy()
            if self.parent:
                self.parent.deiconify()
    
    def on_closing(self):
        """
        Handle window closing event.
        """
        self.close_window()
    
    def destroy(self):
        """
        Override destroy method to handle cleanup.
        """
        self.master.deiconify()
        
        super().destroy()




