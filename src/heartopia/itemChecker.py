import json
import time
import pyautogui
import numpy as np
from ..log import log   # relative import from parent directory
from .interfacing import click

# Load config
with open("config.json", "r") as file:
    data = json.load(file)

newItemCheckConfig = data.get("newItemCheck")
newItemCheckPosition = (newItemCheckConfig["x"], newItemCheckConfig["y"])

def checkNewItem():
    x, y = newItemCheckPosition
    screenshot = pyautogui.screenshot(region=(x, y, 5, 5))  # 5x5 pixel area
    brightness = np.array(screenshot.convert("L")).mean()
    
    if brightness > 50:  # adjust threshold if needed
        log("New Item Detected, Attempting to Fix...")
        count = 0
        center_x, center_y = pyautogui.size()[0] // 2, pyautogui.size()[1] // 2
        while count < 10:
            click((center_x, center_y))
            count += 1
            time.sleep(0.1)
        return True

    return False