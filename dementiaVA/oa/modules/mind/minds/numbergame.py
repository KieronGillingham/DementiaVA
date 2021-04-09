from oa.core.util import command_registry

from oa.modules.abilities.interact import say, mind
from oa.modules.abilities.highlow import Game

import oa.legacy

kws = {}

command = command_registry(kws)

import logging
_logger = logging.getLogger(__name__)

current_game = None

def _new_game():
    if not oa.legacy.mind.current_game:
        oa.legacy.mind.current_game = Game()
        oa.legacy.mind.current_game.start()
    else:
        _logger.debug("Game instance already exists")


@command(["close", "stop", "end"])
def stop_game():
    if oa.legacy.mind.current_game:
        oa.legacy.mind.current_game.end_game()
        oa.legacy.mind.current_game = None
        mind("dem")

@command(["rules", "how", "instructions", "explain"])
def instructions():
    say('Here is how the game works. First I will say two numbers, and you will say if the second number ' +
        'is higher or lower than the first. ' +
        'I will then say another number, and you will say if it is higher or lower than the last number I said.')

def start():
    say('Let\'s begin.')
    _new_game()
