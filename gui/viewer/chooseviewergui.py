import customtkinter as ctk

class ChooseViewerWindow(ctk.CTk):
    """
    A window that allows the user to choose between viewing 100-level or 200-level attendance.
    """
    def __init__(self, viewer_type="attendance"):
        super().__init__()

        self.title("Choose Level to View")
        self.geometry("400x300")
        self.minsize(300, 250)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Select Level to View Attendance", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=1, column=0, padx=20, pady=20)

        self.level_100_button = ctk.CTkButton(self, text="100 Level", command=lambda: self.open_viewer("100level"))
        self.level_100_button.grid(row=2, column=0, padx=40, pady=10, sticky="ew")

        self.level_200_button = ctk.CTkButton(self, text="200 Level", command=lambda: self.open_viewer("200level"))
        self.level_200_button.grid(row=3, column=0, padx=40, pady=10, sticky="ew")

        self.back_button = ctk.CTkButton(self, text="Back to Main Menu", command=self.back_to_main_menu)
        self.back_button.grid(row=4, column=0, padx=40, pady=10, sticky="ew")

    def open_viewer(self, level):
        """
        Closes this window and opens the attendance viewer for the selected level.
        """
        self.destroy()
        from gui.viewer.viewergui import ViewerWindow
        viewer_app = ViewerWindow(level)
        viewer_app.mainloop()

    def back_to_main_menu(self):
        """
        Closes this window and returns to the main menu.
        """
        self.destroy()
        from gui.root import AttendanceApp
        main_app = AttendanceApp()
        main_app.mainloop()
