import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
import os
import sys
from tksheet import Sheet
import tkinter as tk

# Add the parent directory to the path so we can import from func module
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from func.viewer import get_students_data_from_file, save_students_data


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


class ViewerWindow(ctk.CTk):
    """
    Window that displays student data in an Excel-like interface for viewing and editing.
    """
    def __init__(self, parent, file_path, editable=True):
        """
        Initializes the ViewerWindow.
        
        Args:
            parent: The parent window
            file_path: Path to the CSV file to be displayed
            editable: Whether the data should be editable
        """
        super().__init__()
        
        self.parent = parent
        self.file_path = file_path
        self.editable = editable
        self.is_modified = False
        
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
        self.title(f"{'Edit' if editable else 'View'} - {file_name}")
        self.geometry("900x600")
        
        # Create the table
        self.table = DataTable(self, self.df, editable)
        
        # Create button frame
        if self.editable:
            self.button_frame = ctk.CTkFrame(self)
            self.button_frame.pack(fill="x", padx=10, pady=(0, 10))
            
            # Button to add new row
            self.add_row_button = ctk.CTkButton(
                self.button_frame,
                text="Add Row",
                command=self.add_new_row
            )
            self.add_row_button.pack(side="left", padx=5, pady=5)
            
            # Button to delete selected row
            self.delete_row_button = ctk.CTkButton(
                self.button_frame,
                text="Delete Selected Row",
                command=self.delete_selected_row
            )
            self.delete_row_button.pack(side="left", padx=5, pady=5)
            
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
    
    def add_new_row(self):
        """
        Adds a new empty row to the table.
        """
        # Add empty values for each column
        new_row = {col: "" for col in self.df.columns}
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Refresh the table
        self.table.refresh_table(self.df)
        self.is_modified = True
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.configure(text="Modified - Save to keep changes")
    
    def delete_selected_row(self):
        """
        Deletes the currently selected row from the table.
        """
        try:
            # Get the currently focused cell to determine which row to delete
            current_widget = self.focus_get()
            
            # Find which row this widget belongs to
            for i, row in enumerate(self.table.cells):
                if current_widget in row:
                    # Remove the row from the dataframe
                    self.df = self.df.drop(self.df.index[i]).reset_index(drop=True)
                    
                    # Refresh the table
                    self.table.refresh_table(self.df)
                    self.is_modified = True
                    
                    # Update status
                    if hasattr(self, 'status_label'):
                        self.status_label.configure(text="Modified - Save to keep changes")
                    
                    return
            
            # If no specific row was identified, show a message
            messagebox.showinfo("Info", "Click on a row to select it, then click 'Delete Selected Row'")
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete row: {str(e)}")
    
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
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        super().destroy()