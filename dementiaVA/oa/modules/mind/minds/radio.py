import vlc

from oa.core.util import command_registry

from oa.modules.abilities.interact import say, mind
from oa.modules.abilities.highlow import Game

import oa.legacy

kws = {}

command = command_registry(kws)

player = None

def _get_player():
    url = 'https://streaming.radio.co/s188ef6afc/listen'
    if not oa.legacy.mind.player:
        #instance = vlc.libvlc_new(0, None)
        #print(instance)
        oa.legacy.mind.player = vlc.MediaPlayer(url)
    return oa.legacy.mind.player


@command(["close", "stop", "end", "quiet"])
def stop_game():
    player = _get_player()
    player.quit()
    mind("dem")

def start():
    player = _get_player()
    player.play()
