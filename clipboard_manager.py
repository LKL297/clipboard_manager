from pynput.keyboard import Key, KeyCode, Listener, Controller
import clipboard
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
from queue import Queue 
from threading import Thread 

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        window_width = 150
        window_height = 100
        window_up = 1080-window_height-40
        window_left = 1920-window_width

        self.setWindowTitle("Test Overlay")
        self.setWindowOpacity(0.5)
        self.setStyleSheet("background-color: black;")
        self.setGeometry(window_left, window_up, window_width, window_height) #width, height ,box width,box height
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.label_1 = QLabel("-----CLIPBOARD-----", self)
        self.label_1.setStyleSheet("color: white; border: 1px solid white;")
        
        label1_width = (window_width/2)-(self.label_1.width() /2)
            
        self.label_1.move(label1_width, 2)
        self.label_1.setAlignment(Qt.AlignCenter)
        
        self.label_total = QLabel("Stored: 1", self)
        self.label_total.move(10, 40)
        self.label_total.setStyleSheet("color: white; ")
        self.label_total.adjustSize()

        self.label_Clip = QLabel("Control C:\n"+"1. "+str(clipboard.paste()), self)
        self.label_Clip.move(10, 60)
        self.label_Clip.setStyleSheet("color: white; ")
        self.label_Clip.adjustSize()
        self.show()
     


App = QApplication(sys.argv)
window = Window()

keyboard = Controller()

prevCopies = []
CURRENT_CLIP = ""

KEY_MAPS = {
    97: 1,
    49: 1,
    98: 2,
    50: 2,
    99: 3,
    51: 3,
    100: 4,
    52: 4,
    101: 5,
    53: 5,
    102: 6,
    54: 6,
}

def ui(in_q):
    
    while True:
        data = in_q.get()
        dtypes = data.split(":")
        if dtypes[0] == "NEWCOPY":
            if len(dtypes[1]) > 20:
                window.label_Clip.setText("Control C:\n"+dtypes[1][0:20]+"...")
            else:
                window.label_Clip.setText("Control C:\n"+dtypes[1])
        else:
            print("Other data type")
            print(dtypes[1])
            window.label_total.setText(dtypes[1])
        window.label_Clip.adjustSize()
        window.update()






currentIndex = 0 

def function_ctrla(num):
    print("Control A pressed")


def function_ctrlc(num):
    print("Control C pressed")
    global CURRENT_CLIP
    print(CURRENT_CLIP)
    print(clipboard.paste())
    if(clipboard.paste() != CURRENT_CLIP):
        prevCopies.insert(0, CURRENT_CLIP)
        CURRENT_CLIP = clipboard.paste()
        q.put("NEWCOPY:1. "+CURRENT_CLIP)
        q.put("STORED:Stored. "+str(len(prevCopies)+1))
        currentIndex = 0

def function_change_clipboard(num):
    try:
        newclip = prevCopies[num-1]
        #print(newclip)
        #prevCopies.pop(num-1)
        global CURRENT_CLIP
        if not CURRENT_CLIP in prevCopies:
            #print("adding to list")
            prevCopies.insert(0, CURRENT_CLIP)
        CURRENT_CLIP = newclip
        q.put("NEWCOPY:"+str(num)+". "+CURRENT_CLIP)
    except IndexError:
        print("No clipboard at index "+str(num-1))


def function_ctrl_v_num(num):
    function_change_clipboard(num)



def function_ctrl_alt_up(num):
    print("up pressed")
    global currentIndex
    if currentIndex > 1:
        currentIndex = currentIndex - 1
    function_change_clipboard(currentIndex)

def function_ctrl_alt_down(num):
    print("down pressed")
    global currentIndex
    if currentIndex < len(prevCopies):
        currentIndex = currentIndex + 1
    function_change_clipboard(currentIndex)
   




KEY_COMBOS = {
    frozenset([Key.ctrl_l, KeyCode(vk=65)]): function_ctrla,
    frozenset([Key.ctrl_l, KeyCode(vk=67)]): function_ctrlc,
    
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=49)]): function_ctrl_v_num,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=97)]): function_ctrl_v_num,

    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=50)]): function_ctrl_v_num,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=98)]): function_ctrl_v_num,

    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=51)]): function_ctrl_v_num,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=99)]): function_ctrl_v_num,

    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=52)]): function_ctrl_v_num,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=100)]): function_ctrl_v_num,

    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=53)]): function_ctrl_v_num,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=101)]): function_ctrl_v_num,

    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=54)]): function_ctrl_v_num,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=102)]): function_ctrl_v_num,

    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=38)]): function_ctrl_alt_up,
    frozenset([Key.ctrl_l, Key.alt_l, KeyCode(vk=40)]): function_ctrl_alt_down,
}

pressed_vks = set()

def get_vk(key):
    return key.vk if hasattr(key, 'vk') else key.value.vk

def combo_pressed(keys_pressed):
    return all([get_vk(key) in pressed_vks for key in keys_pressed])

def on_press(key):
    vk = get_vk(key)
    pressed_vks.add(vk)
    #print(pressed_vks)
    for combination in KEY_COMBOS:
        if combo_pressed(combination):
            if vk in KEY_MAPS:
                KEY_COMBOS[combination](KEY_MAPS[vk])
            else:
                KEY_COMBOS[combination](vk)
def on_release(key):
    vk = get_vk(key)
    try:
        pressed_vks.remove(vk)
    except KeyError:
        print("KeyError")


def control(out_q):
    while True:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()


CURRENT_CLIP = clipboard.paste()
q = Queue()
t1 = Thread(target = control, args=(q,))
t2 = Thread(target = ui, args=(q,))
t1.start()
t2.start()


sys.exit(App.exec())