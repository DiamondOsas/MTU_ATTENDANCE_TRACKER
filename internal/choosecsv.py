import customtkinter as ctk
import os
import glob

class ChooseCSVWindow(ctk.CTkToplevel):
    """
    A window that allows the user to choose a CSV file from a specified directory.
    """
    def __init__(self, master, target_dir, callback, title="Choose CSV File"):
        super().__init__(master)
        self.master = master
        self.target_dir = os.path.abspath(target_dir)
        self.callback = callback
        
        self.title(title)
        self.geometry("400x250")
        self.grab_set()  # Make this window modal

        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 1. Title Label ---
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=10)

        # --- 2. File Selection Dropdown ---
        self.csv_files = self._get_csv_files()
        
        if not self.csv_files:
            ctk.CTkLabel(self, text=f"No CSV files found in:\n{self.target_dir}").grid(row=2, column=0, padx=20, pady=10)
            self.select_button = ctk.CTkButton(self, text="Close", command=self.destroy)
            self.select_button.grid(row=3, column=0, padx=20, pady=10)
            return

        self.selected_file_var = ctk.StringVar(value=self.csv_files[0]) # Set initial value
        self.file_optionmenu = ctk.CTkOptionMenu(self, values=self.csv_files,
                                                 variable=self.selected_file_var)
        self.file_optionmenu.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # --- 3. Select Button ---
        self.select_button = ctk.CTkButton(self, text="Select File", command=self._on_select_file)
        self.select_button.grid(row=3, column=0, padx=20, pady=10)
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _get_csv_files(self):
        """
        Scans the target directory for CSV files.
        Returns a list of filenames.
        """
        if not os.path.exists(self.target_dir):
            return []
            
        csv_files = glob.glob(os.path.join(self.target_dir, "*.csv"))
        # Return only the base names of the files
        return [os.path.basename(f) for f in csv_files]

    def _on_select_file(self):
        """
        Handles the selection of a file. Calls the callback with the full path.
        """
        selected_filename = self.selected_file_var.get()
        if selected_filename:
            full_file_path = os.path.join(self.target_dir, selected_filename)
            self.destroy() # Close this window
            
            if self.callback:
                self.callback(full_file_path)

    def _on_closing(self):
        """
        Handles the window closing event. Re-enables the master window.
        """
        self.master.deiconify() # Show the main window again
        self.destroy()
