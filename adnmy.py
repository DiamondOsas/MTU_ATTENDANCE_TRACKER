import pathlib
import tkinter as tk
from tkinter import ttk,  messagebox

DIR = "/sdcard/DCIM/bbidLOGS/"



LOCALPATH = pathlib.Path()

class LogApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ADB Log")
        self.geometry("1000x500")


        tk.Label(self, text="ADB PULLER", font=("Arial", 20, "underline"), anchor= "e", cursor="xterm").pack(pady=10)
        
        

if __name__ == "__main__":
    app = LogApp()
    app.mainloop()