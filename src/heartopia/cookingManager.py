from time import sleep as wait
from .getStates import detectOvens
from .log import log
from .interfacing import click
from .findFood import findFood
import json
import pyautogui


"""
Get Users Positional Data
"""

with open("config.json", "r") as file:
    data = json.load(file)

cookingPositionData = data.get("startCooking")

with open("config.json", "r") as file:
    data = json.load(file)

newItemCheck = data.get("newItemCheck")

if (not cookingPositionData or "x" not in cookingPositionData or "y" not in cookingPositionData):
    log(
        "- ONE TIME ALIGNMENT -\nOnce you hit Enter, tab into Heartopia, move your mouse over the 'Start Cooking' button, wait a couple seconds, then come back here."
    )
    input("Press Enter to continue")

    wait(2)
    pos = pyautogui.position()
    cookingPosition = (pos.x, pos.y)

    data["startCooking"] = {"x": pos.x, "y": pos.y}
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

    log("Successfully set cooking position!")
    input("Press Enter to continue")

if (not newItemCheck or "x" not in newItemCheck or "y" not in newItemCheck):
    log(
        "- ONE TIME ALIGNMENT -\nOnce you hit Enter, tab into Heartopia, move your mouse over the area where the white box appears 'bottom left corner', wait a couple seconds, then come back here."
    )
    input("Press Enter to continue")

    wait(2)
    pos = pyautogui.position()
    cookingPosition = (pos.x, pos.y)

    data["newItemCheck"] = {"x": pos.x, "y": pos.y}
    with open("config.json", "w") as f:
        json.dump(data, f, indent=4)

    log("Successfully set new item check position!")
    input("Press Enter to continue")


cookingPosition = (cookingPositionData["x"], cookingPositionData["y"])
newItemCheckPosition = (newItemCheck["x"], newItemCheck["y"])

def cookFood(foodname : str) -> bool:
    """
    Uses keyboard interactions to cook food inside of heartopia

    Returns Success Afterwards!
    """

    # Detect ovens
    ovens = detectOvens()

    if len(ovens) < 1:
        log("ERROR : No ovens detected")
        return False

    # Start cooking if oven is ready
    if ovens[0][1] == "Select Food":

        click(ovens[0][2]) # Oven Button

        wait(1.5) # Await UI Rendering

        foodData = findFood(foodname)

        if foodData[0] is None:
            log(f"[ cookingManager ] : Food '{foodname}' not detected on screen!")
            return False

        log(f"\nRecieved Fooddata\n\n{foodData}\n")

        if foodData[0].lower() == foodname.lower():

            log(f"Successfully found `{foodname}`, continuing.")

        else:

            log(f"ERROR: Foodname `{foodname}` not detected. Ensure tesseract is installed.")

            return False

        click(foodData[1]) # Click On The Food

        click(cookingPosition) # Submit Cook To Begin

    # Cooking Loop

    finishedCooking = False

    try:
        while not finishedCooking:

            ovens = detectOvens() # Initial Oven Detection

            for oven in ovens:

                ovenName, ovenState, ovenPosition = oven

                if "overheating" in ovenState.lower():

                    log(f"Oven {ovenName} is overheating!")
                    click(ovenPosition)

                elif "finished" in ovenState.lower():

                    log(f"Oven {ovenName} has finished cooking!")
                    click(ovenPosition)
                    finishedCooking = True
                    break

            wait(0.25)

    except KeyboardInterrupt:
        log("Oven monitoring stopped by user.")
        return False

    return True