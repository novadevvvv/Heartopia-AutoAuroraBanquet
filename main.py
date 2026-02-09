from time import sleep as wait
from src.log import log
from src.interfacing import click
from src.cookingManager import cookFood
import json

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

    if SUCCESS:
        log(f"Successfully Cooked {food}, Moving Onto Next Food...")
    else:
        log(f"Cooking {food} failed after appearance check.")
        exit()

    wait(1)


