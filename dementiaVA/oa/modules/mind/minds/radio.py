import random
from time import sleep

import vlc

from oa.core.util import command_registry

from oa.modules.abilities.interact import say, mind

import oa.legacy

import logging
_logger = logging.getLogger(__name__)

kws = {}

command = command_registry(kws)

player = None

def _get_player():
    if not oa.legacy.mind.player:
        _logger.debug('Loading media player')
        station = get_station()
        print(station)
        oa.legacy.mind.player = vlc.MediaPlayer(station)
    return oa.legacy.mind.player


@command(["change", "song", "next", "station", "different"])
def change_station():
    print('+ Changing Station +')
    oa.legacy.mind.player.stop()
    oa.legacy.mind.player.release()
    oa.legacy.mind.player = None
    player = _get_player()
    player.play()
    player.audio_set_volume(50)
    oa.legacy.mind.player = player
def get_station():
    stations = [
        'http://s2.radio.co/s07cd038f1/listen',
        'http://s2.radio.co/sf0e4f0fe8/listen',
        'http://streaming.radio.co/s188ef6afc/listen',
        'http://streaming.radio.co/sba397e5cb/listen',
        'http://streamer.radio.co/sa37ec8d4a/listen'
    ]
    return random.choice(stations)

@command(["close", "stop", "end", "no more", "turn off"])
def stop():
    player = _get_player()

    say("Stopping the radio.")

    volume = player.audio_get_volume()
    while volume > 0:
        volume -= 4
        player.audio_set_volume(volume)
        sleep(.5)

    player.stop()
    mind("dem")


@command(["quieter", "quiet", "quite", "down", "lower", "volume+down"])
def volume_down():
    player = _get_player()
    new_volume = player.audio_get_volume() - 25
    if new_volume <= 0:
        print(f'+ Lowering volume to 0 and stopping +')
        stop()
    else:
        print(f'+ Lowering volume to {new_volume} +')
        player.audio_set_volume(new_volume)


@command(["louder", "up", "loud", "allowed", "volume+up"])
def volume_up():
    player = _get_player()
    new_volume = player.audio_get_volume() + 25
    print(f'+ Raising volume to {new_volume} +')
    if new_volume >= 100:
        player.audio_set_volume(100)
        say('Maximum volume.')
    else:

        player.audio_set_volume(new_volume)


def start():
    try:
        player = _get_player()
        if player.audio_get_volume() <= 50:
            player.audio_set_volume(50)
        player.play()
        change_station()
        print('+ Playing Radio +')
    except Exception as ex:
        _logger.error(ex)