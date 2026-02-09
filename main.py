from time import sleep as wait
from src.getStates import detectOvens
from src.log import log
from src.interfacing import click
from src.findFood import findFood

wait(1)

data = detectOvens()

if data[0][1] == "Select Food":
    click(data[0][2])

    wait(0.1)

    click(findFood("coffee")[1])

