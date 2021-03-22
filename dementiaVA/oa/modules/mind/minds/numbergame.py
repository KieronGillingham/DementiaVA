from oa.core.util import command_registry

from oa.modules.abilities.interact import say, play, mind
from oa.modules.abilities.other import read_news_feed, diagnostics, read_forecast
from oa.modules.abilities.other import say_day, say_last_command, say_time

import oa.legacy

kws = {}

command = command_registry(kws)

def start():
    say('Let\'s Begin')

@command(["close", "stop", "end"])
def stop_game():
    say('Let\'s stop playing.')
    mind("dem")