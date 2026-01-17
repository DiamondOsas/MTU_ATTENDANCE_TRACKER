import threading
from maintain.prepare import prepare_attendance_files
from maintain.maintain import maintain_student_data_files
from gui.root import AttendanceApp

# this ensures that the appliaction is run as a file and connot be  imported as a module form another package 
if __name__ == "__main__":
    #runs a background thread to mainitain the student data files (you can always check the function)
    maintain_thread = threading.Thread(target=maintain_student_data_files)
    maintain_thread.daemon = True  # Allows the main app to exit even if the thread is running
    maintain_thread.start()
    
    #concurently like golang sharp
    #Runs file prepartion in the background which helps in making sure that the the GUI doens not lag simple 
    #Wait why am i now using aync in flet when this one exists maybe it is not compatible with FLET --- I hate this library just a Fultter Abstraction
    prepare_thread = threading.Thread(target=prepare_attendance_files)
    prepare_thread.daemon = True
    prepare_thread.start()

    #instatiate the application would have been nbettter if done this in gui.root what am i even saying you can import vairables form anther apcakage this sii snot golang
    #ok assisng app to the function is inusty standard on cusotom tkinter but i am goin go break that right now bro
    myapp = AttendanceApp()
    #Started below
    myapp.mainloop()
    #Who changes app to myappp !!!


