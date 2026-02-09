from time import sleep as wait
from src.log import log
from src.heartopia.interfacing import click
from src.heartopia.cookingManager import cookFood
from src.heartopia.itemChecker import checkNewItem
import json

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

wait(3)

for food in REQUIREMENTS:
    log(f"Attempting To Cook {food}!")

    SUCCESS = cookFood(food.lower())

    if not SUCCESS:
        log(f"Failed To Cook {food}?")
        exit()

    REQUIREMENTS[food] = SUCCESS

    checkNewItem()

    log(f"Successfully Cooked {food}, Moving Onto Next Food...")

    wait(1)


