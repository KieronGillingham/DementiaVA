import oa.legacy

from oa.modules.abilities.core import call_function, put
from oa.modules.abilities.system import find_file

import logging
_logger = logging.getLogger(__name__)

def user_answer(choices):
    """ Set the possible user choices as a dict:
    {'SPOKEN PHRASE': function_to_call, ...}
    """
    #mind(mind_for_answer, 0) # No history.
    oa.legacy.mind.user_choices = choices
    _logger.debug(f"Setting choices: {choices}")

def answer(text):
    """ Process an unknown user response and compare it to the current choices in the mind. """
    # If no choice is active, do nothing.
    if not oa.legacy.mind.user_choices:
        return

    text = text.lower()
    _logger.debug(f'Received: {text}')
    # Get a function from the user_choices dict set by user_answer
    func = oa.legacy.mind.user_choices.get(text, None)

    # If a function is found, clear the choices dict and run the function
    if func:
        oa.legacy.mind.user_choices = None
        _logger.debug("Clearing choices")
        call_function(func)
    else:
        # If a function isn't found, alert the user.
        say('sorry, I didn\'t get that')

    #oa.legacy.mind.switch_back()


def yes_no(msg, yes, no):
    """ Receive a yes or no answer from the user. """
    say(msg)
    user_answer({'yes': yes, 'no': no})


def say(text):
    """ Text to speech using the `oa.audio.say` defined function. """
    # TODO: Remove
    text = call_function(text)
    oa.legacy.sys.last_say = text

    if text is not None:
        # Put message into voice.
        put('voice', text)


def keys(s):
    return None


def play(fname):
    """ Play a sound file. """
    put('sound', find_file(fname))


def mind(name, history = 1):
    """ Switch the current mind to `name`. """
    oa.legacy.hub.parts['mind'].set_mind(name, history)
