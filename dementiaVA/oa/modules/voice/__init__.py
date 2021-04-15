import pyttsx3
import logging

from oa.modules.abilities.core import get

_logger = logging.getLogger(__name__)


def _in(ctx):
    tts = pyttsx3.init()

    while not ctx.finished.is_set():
        s = get()

        tts.setProperty('rate', ctx.config["talkspeed"])

        _logger.debug(f'Speaking: {s}')
        print(f'Speaking: {s}')
        tts.say(s)
        tts.runAndWait()
