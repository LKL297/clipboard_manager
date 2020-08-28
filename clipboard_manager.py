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
        window_width = 300

        self.setWindowTitle("Test Overlay")
        self.setWindowOpacity(0.5)
        self.setStyleSheet("background-color: black;")
        self.setGeometry(1620, 970, window_width, 70) #width, height ,box width,box height
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.label_1 = QLabel("-----CLIPBOARD-----", self)
        self.label_1.setStyleSheet("color: white; border: 1px solid white;")
        
        label1_width = (window_width/2)-(self.label_1.width() /2)
            
        self.label_1.move(label1_width, 2)
        self.label_1.setAlignment(Qt.AlignCenter)
        
        self.label_stored = QLabel("Stored: 0", self)
        self.label_stored.setStyleSheet("color: white;")
        self.label_stored.adjustSize()
        self.label_stored.move(10, 10)

        self.label_Clip = QLabel("Control C: "+str(clipboard.paste()), self)
        self.label_Clip.move(10, 40)
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
            if len(dtypes[1]) > 40:
                window.label_Clip.setText("1. "+dtypes[1][0:40]+"...")
            else:
                window.label_Clip.setText("1. "+dtypes[1][0:40])
        else:
            window.label_stored.setText("Stored: "+dtypes[1])
        window.label_Clip.adjustSize()
        window.update()






 

def function_ctrla(num):
    print("Control A pressed")


def function_ctrlc(num):
    print("Control C pressed")
    global CURRENT_CLIP
    if CURRENT_CLIP != clipboard.paste():
        prevCopies.insert(0, CURRENT_CLIP)
        CURRENT_CLIP = clipboard.paste()
        q.put("NEWCOPY:"+CURRENT_CLIP)
        q.put("STORE:"+str(len(prevCopies)))

def pasteHandle(num):
    try:
        newPaste = prevCopies[num-1]
        print(newPaste)
        oldClip = clipboard.paste()
        if not prevCopies.__contains__(oldClip):
            prevCopies.insert(0, oldClip)
        clipboard.copy(newPaste)
        q.put("NEWCOPY:"+newPaste)
        q.put("STORE:"+str(len(prevCopies)))
        #paste()
    except IndexError:
        print("No Index here")

def function_ctrl_v_num(num):
    print(prevCopies[num-1])
    pasteHandle(num)




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

q = Queue()
t1 = Thread(target = control, args=(q,))
t2 = Thread(target = ui, args=(q,))
t1.start()
t2.start()


sys.exit(App.exec())