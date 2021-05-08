import logging

from time import sleep, time

from oa.core.util import command_registry

from oa.modules.abilities.interact import say, play, mind, yes_no, user_answer
from oa.modules.abilities.other import string_to_number

import oa
import oa.legacy

_logger = logging.getLogger(__name__)

kws = {}

command = command_registry(kws)

def start():
    try:
        last_command = oa.legacy.oa.last_command
        time = get_spoken_time(last_command)
        if time is None:
            ask_time()

    except Exception as ex:
        _logger.error(ex)
    finally:
        mind("dem")

def get_spoken_time(speech):
    numbers = string_to_number(speech)
    if len(numbers > 2):
        # Too many numbers for a time, ask again
        return None
    elif numbers[0] > 24:
        # Too high hours
        return None


    print(f'Time is: {numbers}')


def ask_time():
    say('What time should I set the alarm for?')