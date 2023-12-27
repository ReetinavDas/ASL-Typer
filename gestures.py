import time
import pyautogui

def type_char(char):
    """
    Uses PyAutoGUI to simulate keyboard press of char
    """
    pyautogui.press(char)
    time.sleep(1)