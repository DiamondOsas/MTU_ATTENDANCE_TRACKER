# main.py

# Import the main application class from the root.py file.
from gui.root import AttendanceApp

if __name__ == "__main__":
    # This block ensures that the code inside it only runs when main.py is executed directly,
    # not when it's imported as a module into another script.

    # Create an instance of our AttendanceApp. This initializes the GUI window.
    app = AttendanceApp()
    # Start the CustomTkinter event loop. This makes the window appear and
    # keeps it running, listening for user interactions (like button clicks).
    app.mainloop()

