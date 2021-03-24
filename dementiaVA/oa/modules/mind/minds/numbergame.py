from oa.core.util import command_registry

from oa.modules.abilities.interact import say, mind
from oa.modules.abilities.highlow import Game

import oa.legacy

kws = {}

command = command_registry(kws)

current_game = None

def _new_game():
    if not oa.legacy.mind.current_game:
        oa.legacy.mind.current_game = Game()
        oa.legacy.mind.current_game.start()
    else:
        print('Already a game going.')


@command(["close", "stop", "end"])
def stop_game():
    if oa.legacy.mind.current_game:
        oa.legacy.mind.current_game.end_game()
        oa.legacy.mind.current_game = None
        mind("dem")

def start():
    say('Let\'s Begin')
    _new_game()
