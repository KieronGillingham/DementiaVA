from itertools import groupby

import oa.legacy

import random
from time import sleep

from oa.modules.abilities.core import info
from oa.modules.abilities.interact import say


def _get_random_number():
    return random.randrange(1, 100)

def get_response():
    response = None
    if response in ("higher", "high", "up", "bigger", "larger", "more"):
        return "higher"
    elif response in ("lower", "low", "down", "smaller", "less"):
        return "lower"
    elif response in ("same", "equal"):
        return "equal"