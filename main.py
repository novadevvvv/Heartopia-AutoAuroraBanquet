from time import sleep as wait
from src.log import log
from src.heartopia.cookingManager import cookFood
from src.heartopia.itemChecker import checkNewItem

"""
Website: https://github.com/novadevvvv
Dependencies: Project in itself (https://github.com/novadevvvv/Heartopia-AutoAuroraBanquet)
"""

REQUIREMENTS = {
    "Steak": False,
    "Soup": False,
    "Drink": False,
    "Pancake": False,
    "Banquet": False
}

CORE_FOODS = ["Steak", "Soup", "Drink", "Pancake"]

wait(3)

while not all(REQUIREMENTS.values()):
    # Cook core foods first
    for food in CORE_FOODS:
        if REQUIREMENTS[food]:
            continue

        log(f"Attempting To Cook {food}!")

        if not cookFood(food.lower()):
            log(f"Failed To Cook {food}!")
            exit(1)

        REQUIREMENTS[food] = True
        checkNewItem()
        log(f"Successfully Cooked {food}")
        wait(3)

    # 🔒 Banquet gate — cannot run early
    if not all(REQUIREMENTS[f] for f in CORE_FOODS):
        continue

    if not REQUIREMENTS["Banquet"]:
        log("Attempting To Cook Banquet!")

        if not cookFood("banquet"):
            log("Failed To Cook Banquet!")
            exit(1)

        REQUIREMENTS["Banquet"] = True
        checkNewItem()
        log("Successfully Cooked Banquet")
        wait(3)
