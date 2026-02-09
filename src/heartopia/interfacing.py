import pyautogui
from time import sleep as wait
import random
from .log import log

def click(position : tuple, duration : float = 0.01):

    log(f"Attempting to click at {position}")

    pyautogui.moveTo(position[0], position[1], duration=0)

    wait(0.01)

    pyautogui.moveRel(random.randint(1,2),random.randint(1,2),duration=0) # Offset slightly to allow multiple clicks in same spot

    wait(0.05)

    pyautogui.mouseDown()

    wait(duration)

    pyautogui.mouseUp()