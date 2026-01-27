import customtkinter as ctk
from internal.reigister.reigister_func import register_student
from tkinter import messagebox

class RegisterWindow(ctk.CTkToplevel):
    """
    GUI window for registering new students.
    This window provides a simple form for entering student details.
    """
    def __init__(self, master):
        """
        Initializes the RegisterWindow.
        Sets up the window properties, creates the registration form widgets,
        and a button to go back to the main menu.
        """
        super().__init__(master)

        # --- 1. Window Configuration ---
        self.title("Register Students")
        self.geometry("500x420")

        # Center the content
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Add weight to a row to push content up

        # --- 2. Title Label ---
        self.title_label = ctk.CTkLabel(self, text="Register New Student", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # --- 3. Registration Form ---
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Surname
        self.surname_label = ctk.CTkLabel(self.form_frame, text="Surname:")
        self.surname_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.surname_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Enter surname")
        self.surname_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Name
        self.name_label = ctk.CTkLabel(self.form_frame, text="Name:")
        self.name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Enter name")
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Matric No
        self.matric_label = ctk.CTkLabel(self.form_frame, text="Matric No:")
        self.matric_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.matric_var = ctk.StringVar()
        self.matric_var.trace_add("write", self.update_level)
        self.matric_var.trace_add("write", self.update_coll)
        self.matric_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Enter matriculation number", textvariable=self.matric_var)
        self.matric_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        #College
        self.coll_label = ctk.CTkLabel(self.form_frame, text= "College")
        self.coll_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.coll_menu =  ctk.CTkOptionMenu(self.form_frame, values=["CBAS","CHMS","CAHS"])
        self.coll_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Level
        self.level_label = ctk.CTkLabel(self.form_frame, text="Level:")
        self.level_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.level_menu = ctk.CTkOptionMenu(self.form_frame, values=["100", "200", "300", "400", "500"])
        self.level_menu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # --- 4. Register Button ---
        self.register_button = ctk.CTkButton(self, text="Register Student", command=self.register_student)
        self.register_button.grid(row=5, column=0, padx=20, pady=20, sticky="ew")

        # --- 5. Back Button ---
        self.back_button = ctk.CTkButton(self, text="Back to Main Menu", command=self.back_to_main_menu, fg_color="transparent", border_width=2)
        self.back_button.grid(row=6, column=0, padx=20, pady=10, sticky="s")


    def update_level(self, *args):
        """Automatically update the level based on the matriculation number."""
        matric_no = self.matric_var.get()
        if len(matric_no) >= 2:
            prefix = matric_no[:2]
            level_map = {"25": "100", "24": "200", "23": "300", "22": "400", "21": "500"}
            if prefix in level_map:
                self.level_menu.set(level_map[prefix])

    def update_coll(self, *args):
        """Automatically Update the College Entry Box"""
        matric_no = self.matric_var.get()

        if len(matric_no) == 4:
            prefix = matric_no[-1]
            level_map = {"1": "CBAS", "2": "CHMS", "3": "CAHS"}
            if prefix in level_map:
                self.coll_menu.set(level_map[prefix])
            

    def register_student(self):
        """
        This function will be called when the register button is pressed.
        It will gather the information from the form and pass it to the register function.
        """

        surname = self.surname_entry.get()
        name = self.name_entry.get()
        matric_no = self.matric_entry.get()
        level = self.level_menu.get()

        if not all([surname, name, matric_no, level]):
            messagebox.showerror("Error", "All fields must be filled.")
            return

        if not surname.isalpha():
            messagebox.showerror("Error", "Surname must contain only alphabets.")
            return

        if not name.isalpha():
            messagebox.showerror("Error", "Name must contain only alphabets.")
            return

        if not matric_no.isdigit():
            messagebox.showerror("Error", "Matric number must contain only numbers.")
            return

        if register_student(surname, name, matric_no, level):
            messagebox.showinfo("Success", f"Student {name} {surname} has been registered successfully.")
            # Clear the fields
            self.surname_entry.delete(0, 'end')
            self.name_entry.delete(0, 'end')
            self.matric_entry.delete(0, 'end')
        else:
            messagebox.showerror("Error", f"A student with matric number {matric_no} already exists.")


    def back_to_main_menu(self):
        """
        Closes the current register window and opens the main menu window.
        """
        self.master.deiconify()
        self.destroy()

if __name__ == "__main__":
    # This allows running this file directly for testing purposes
    # Note: To run this standalone, you might need to handle the import of AttendanceApp differently
    # or mock it, as it creates a dependency loop if not structured carefully.
    app = RegisterWindow()
    app.mainloop()