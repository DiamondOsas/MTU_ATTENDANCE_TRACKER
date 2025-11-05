import customtkinter as ctk
import pandas as pd
from func.viewer import get_absentees

class AbsenteesViewerWindow(ctk.CTk):
    """
    A window to display absentees data for a selected level.
    """
    def __init__(self, level):
        super().__init__()
        self.level = level

        self.title(f"{self.level.capitalize()} Level Absentees Viewer")
        self.geometry("800x600")
        self.minsize(700, 500)

        self.grid_row_configure(0, weight=0)
        self.grid_row_configure(1, weight=1)
        self.grid_column_configure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text=f"{self.level.capitalize()} Level Absentees", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10)

        self.absentees_frame = ctk.CTkFrame(self)
        self.absentees_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.absentees_frame.grid_column_configure(0, weight=1)
        self.absentees_frame.grid_row_configure(0, weight=1)

        self.display_absentees()

        self.back_button = ctk.CTkButton(self, text="Back to Level Selection", command=self.back_to_level_selection)
        self.back_button.grid(row=2, column=0, padx=20, pady=10)

    def display_absentees(self):
        """
        Fetches and displays absentees data in a scrollable text widget.
        """
        absentees_df = get_absentees(self.level)

        if absentees_df.empty:
            display_text = "No absentees found for this level."
        else:
            display_text = "--- ABSENTEES DATA ---
"
            display_text += absentees_df.to_string(index=False)

        self.absentees_text_widget = ctk.CTkTextbox(self.absentees_frame, wrap="word")
        self.absentees_text_widget.insert("1.0", display_text)
        self.absentees_text_widget.configure(state="disabled") # Make it read-only
        self.absentees_text_widget.grid(row=0, column=0, sticky="nsew")

    def back_to_level_selection(self):
        """
        Closes this window and returns to the level selection window.
        """
        self.destroy()
        from gui.viewer.chooseviewergui import ChooseViewerWindow
        choose_level_app = ChooseViewerWindow()
        choose_level_app.mainloop()
