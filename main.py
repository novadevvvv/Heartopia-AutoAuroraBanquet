from time import sleep as wait
from src.log import log
from src.interfacing import click
from src.cookingManager import cookFood

wait(3)

cookFood("coffee")
