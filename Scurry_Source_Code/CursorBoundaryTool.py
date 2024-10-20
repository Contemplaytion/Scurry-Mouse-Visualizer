#KNOWN ISSUE: GUI LABEL OBJECTS FREEZE AND DO NOT ACCEPT UPDATES. I don't know why definitively, but if I had to guess, I'd say it happens when the clock moves too fast for the system to keep up.

#NOTE: 
# I tried multpile approaches to power this tool, but ultimately found that the GUI would freeze if updates to label objects were made too quickly.
# As such I settled creating a clock in a daemon thread to regularly call the update function
# Also I tried using threading.Lock() objects to try to safely access global variables, but I actually found that the tool was actually LESS stable with the locks in place.
# So either I used the locks wrong (very likely), or the problem is unrelated.

from CursorBoundaryToolUI import Ui_formCursorBoundaryTool
from pynput import mouse
from PyQt6.QtWidgets import QApplication, QDialog

import threading
import time

def initialize_global_variables(): #initialize global variables within this function to prevent unintended code execution.
    global clock_thread, terminate_clock, CLOCK_SPEED
    global cursor, cursor_x, cursor_y, listener, recording, min_x, max_x, min_y, max_y

    cursor = mouse.Controller()
    listener = mouse.Listener(on_click=on_click)
    terminate_clock = threading.Event()

    clock_thread = threading.Thread(target=clock, daemon=True)

    CLOCK_SPEED = 30 #measured in ticks / second. 
    # in my very unscientific testing I have found this to be the fastest that I can run the clock without the GUI freezing bug regularly.
    # I can still cause the gui to freeze by messing around and spamming middle mouse randomly, but I don't have the skills to actually diagnose and solve the problem.

    recording = False
    cursor_x = cursor.position[0]
    cursor_y = cursor.position[1]
    min_x = "NONE"
    max_x = "NONE"
    min_y = "NONE"
    max_y = "NONE"

class Cursor_Boundary_Measuring_Tool(Ui_formCursorBoundaryTool): #tool GUI
    def __init__(self, GUI_instance, window_icon=None):
        self.setupUi(GUI_instance)
        if window_icon:
            GUI_instance.setWindowIcon(window_icon)

    def update(self): #update the text of relevant label objects and display to the user
        self.lblCurrentX.setText(str(cursor_x))
        self.lblCurrentY.setText(str(cursor_y))
         
        self.lblLowerX.setText(str(min_x))
        self.lblUpperX.setText(str(max_x))
        self.lblLowerY.setText(str(min_y))
        self.lblUpperY.setText(str(max_y))

        if recording:
            self.lblRecordingStatus.setText("**RECORDING**")
        else:
            self.lblRecordingStatus.setText("NOT RECORDING")

def update_mouse_position(): #gets the current cursor position from the cursor.position() method, and then determines minimum and maximum values if recording
    global recording, cursor, cursor_x, min_x, max_x, cursor_y, min_y, max_y

    cursor_x = cursor.position[0]
    cursor_y = cursor.position[1]

    if recording:
        if min_x == "NONE": 
            min_x = cursor.position[0]
        if max_x == "NONE":
            max_x = cursor.position[0]
        if min_y == "NONE":
            min_y = cursor.position[1]
        if max_y == "NONE":
            max_y = cursor.position[1]
            
        if cursor_x < min_x:
            min_x = cursor_x
        elif cursor_x + 1 > max_x + 1:
            max_x = cursor_x + 1

        if cursor_y < min_y:
            min_y = cursor_y
        elif cursor_y + 1 > max_y + 1:
            max_y = cursor_y + 1
        
def on_click(x, y, button, pressed): #callback function for the mouse.Listener() object. listens for middle mouse presses and toggles recording. resets measurments if re-starting a recording.
    global recording, min_x, max_x, min_y, max_y

    if button == mouse.Button.middle and pressed == True:
        recording = not recording #toggle recording status on middle mouse click
    
        if recording: #when starting a recording, reset relevant values to record fresh.
            min_x = "NONE"
            max_x = "NONE"
            min_y = "NONE"
            max_y = "NONE"

def clock(): #controls the rate at which the GUI labels are updated with recorded data
    global ui

    while not terminate_clock.is_set():
        update_mouse_position()
        ui.update()
        time.sleep(1 / CLOCK_SPEED)   #call update functions CLOCK_SPEED times per second. 
        # In my very short amount of unscientific testing I have found that this is about the lowest amount of time the app can handle without the GUI freezing.

def run(window_icon=None): #main function. creates the GUI, starts and stops the daemon threads, and returns measurements made.
    global ui
    initialize_global_variables()

    gui = QDialog()
    ui = Cursor_Boundary_Measuring_Tool(gui,window_icon)
    gui.show()

    listener.start()
    clock_thread.start()
    
    response = gui.exec() 

    terminate_clock.set()
    clock_thread.join()
    listener.stop()
    
    if not __name__ == "__main__":
        return(response, min_x, max_x, min_y, max_y)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    run()
    sys.exit()