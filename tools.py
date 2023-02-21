import random
import socket
import sys
from os import listdir

import toml
from PyQt5.QtWidgets import (QGraphicsDropShadowEffect)
from rich.console import Console

con = Console()


def get_random_question():
    with open('questions.txt', 'r') as file:
        # Read all the lines into a list
        lines = file.readlines()
    return random.choice(lines)


def setShadow(obj, blurradius: int):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blurradius)
    obj.setGraphicsEffect(shadow)


def get_apps_list(path):
    return listdir(path)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_config():
    return toml.load("config.toml")


def get_cputemp(sensor: str):
    with open(sensor) as cpu_term:
        raw_t = float(cpu_term.read()) / 1000
        return raw_t


def get_size(bytes):
    """
    Returns size of bytes in a nice format
    """
    for unit in ['K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.1f}{unit}B"
        bytes /= 1024


def extended_exception_hook(exec_type, value, traceback):
    # Print the error and traceback
    con.log(exec_type, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exec_type, value, traceback)
    sys.exit(1)


def loadStylesheet(sshFile):
    with open(sshFile, "r") as fh:
        return fh.read()


def degrees_to_cardinal(d):
    '''
    note: this is highly approximate...
    '''
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(d / (360. / len(dirs)))
    return dirs[ix % len(dirs)]
