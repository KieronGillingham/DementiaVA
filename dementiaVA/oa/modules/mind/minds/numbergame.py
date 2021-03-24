from oa.core.util import command_registry

from oa.modules.abilities.interact import say, play, mind, user_answer, yes_no, user_response
from oa.modules.abilities.highlow import Game
from oa.modules.abilities.other import read_news_feed, diagnostics, read_forecast
from oa.modules.abilities.other import say_day, say_last_command, say_time

import oa.legacy

kws = {}

command = command_registry(kws)

def _new_game():
    game = Game()
    game.start()

def yes():
    say("You said yes.")




@command(["close", "stop", "end"])
def stop_game():
    say('Let\'s stop playing.')
    mind("dem")

def start():
    say('Let\'s Begin')
    print("Interact test:", user_response('Say "yes" or "no"'))
    #_new_game()
    #stop_game()

