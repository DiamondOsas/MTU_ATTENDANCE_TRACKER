import customtkinter as ctk
import pandas as pd
from tksheet import Sheet
from func.viewer import get_students_data_from_file, save_students_data
import os

class ViewerWindow(ctk.CTk):
    """
    A window to display and optionally edit student data from a CSV file.
    """
    def __init__(self, file_path, viewer_type="attendance"):
        super().__init__()
        self.file_path = file_path
        self.viewer_type = viewer_type

        # Extract file name for the title
        file_name = os.path.basename(self.file_path)
        title_name = os.path.splitext(file_name)[0].replace('_', ' ').title()

        if self.viewer_type == "edit":
            self.title(f"Edit {title_name}")
        else:
            self.title(f"{title_name} Viewer")

        self.geometry("800x600")
        self.minsize(700, 500)

        self.grid_row_configure(1, weight=1)
        self.grid_column_configure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text=self.title(), font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10)

        self.sheet_frame = ctk.CTkFrame(self)
        self.sheet_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.sheet_frame.grid_column_configure(0, weight=1)
        self.sheet_frame.grid_row_configure(0, weight=1)

        self.display_data()

        # --- Buttons Frame ---
        self.buttons_frame = ctk.CTkFrame(self)
        self.buttons_frame.grid(row=2, column=0, padx=20, pady=10)

        self.back_button = ctk.CTkButton(self.buttons_frame, text="Back to Selection", command=self.back_to_choose_viewer)
        self.back_button.pack(side="left", padx=10)

        if self.viewer_type == "edit":
            self.save_button = ctk.CTkButton(self.buttons_frame, text="Save Changes", command=self.save_data)
            self.save_button.pack(side="left", padx=10)

    def display_data(self):
        """
        Fetches and displays student data in an editable sheet.
        """
        self.df = get_students_data_from_file(self.file_path)

        self.sheet = Sheet(self.sheet_frame, data=self.df.values.tolist(),
                           headers=self.df.columns.tolist(),
                           height=500, width=700)
        self.sheet.enable_bindings()
        self.sheet.pack(expand=True, fill="both")

        if self.viewer_type != "edit":
            self.sheet.disable_editing()

    def save_data(self):
        """
        Saves the current data in the sheet back to the CSV file.
        """
        # Get data from tksheet and convert to DataFrame
        data = self.sheet.get_sheet_data()
        new_df = pd.DataFrame(data, columns=self.df.columns)
        save_students_data(self.file_path, new_df)
        # Optionally, show a success message
        success_label = ctk.CTkLabel(self, text="Data saved successfully!", text_color="green")
        success_label.grid(row=3, column=0, pady=5)
        success_label.after(3000, success_label.destroy) # Remove message after 3 seconds


    def back_to_choose_viewer(self):
        """
        Closes this window and returns to the file selection window.
        """
        self.destroy()
        from gui.viewer.chooseviewergui import ChooseViewerWindow
        choose_level_app = ChooseViewerWindow(self.viewer_type)
        choose_level_app.mainloop()
