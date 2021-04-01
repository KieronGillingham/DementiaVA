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
    url = 'https://streaming.radio.co/s188ef6afc/listen'
    if not oa.legacy.mind.player:
        _logger.debug('Loading media player')
        oa.legacy.mind.player = vlc.MediaPlayer(url)
    return oa.legacy.mind.player


@command(["close", "stop", "end", "no more"])
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


@command(["quieter", "quiet", "quite", "down"])
def volume_down():
    player = _get_player()
    new_volume = player.audio_get_volume() - 25
    if new_volume <= 0:
        stop()
    else:
        player.audio_set_volume(new_volume)
        print(f'\n---Lowering volume to {new_volume}---\n')

@command(["louder", "up", "loud", "allowed"])
def volume_up():
    player = _get_player()
    new_volume = player.audio_get_volume() + 25
    if new_volume >= 100:
        player.audio_set_volume(100)
        say('Maximum volume.')
    else:
        print(f'\n---Raising volume to {new_volume}---\n')
        player.audio_set_volume(new_volume)


def start():
    player = _get_player()
    player.play()
    if player.audio_get_volume() <= 50:
        player.audio_set_volume(50)
    print('\n---Playing Radio---\n')
