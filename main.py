# main.py

import threading
from func.attendance import prepare_attendance_files
from gui.root import AttendanceApp
from gui.filemaintain import maintain_student_data_files # Import the new function

if __name__ == "__main__":
    # This block ensures that the code inside it only runs when main.py is executed directly,
    # not when it's imported as a module into another script.

    # --- Run the file maintenance in a background thread ---
    # This ensures that the student data in db/allstudents is synchronized
    # with the external folder before attendance files are prepared.
    maintain_thread = threading.Thread(target=maintain_student_data_files)
    maintain_thread.daemon = True  # Allows the main app to exit even if the thread is running
    maintain_thread.start()

    # Wait for file maintenance to finish if prepare_attendance_files strictly depends on it
    # For now, we assume prepare_attendance_files can run concurrently or handles partial sync states
    # If strict sequential execution is required, uncomment: maintain_thread.join()

    # --- Run the file preparation in a background thread ---
    # This prevents the GUI from freezing while files are being copied.
    prepare_thread = threading.Thread(target=prepare_attendance_files)
    prepare_thread.daemon = True  # Allows the main app to exit even if the thread is running
    prepare_thread.start()

    # Create an instance of our AttendanceApp. This initializes the GUI window.
    app = AttendanceApp()
    # Start the CustomTkinter event loop. This makes the window appear and
    # keeps it running, listening for user interactions (like button clicks).
    app.mainloop()


