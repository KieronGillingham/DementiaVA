from os import wait
from time import sleep

import oa.legacy

from oa.modules.abilities.core import call_function, put
from oa.modules.abilities.system import find_file


def user_answer(choices):
    """ Within any `mind` we will receive a one word answer command (voice, file path, etc, any) from the user. """
    #mind(mind_for_answer, 0) # No history.
    oa.legacy.mind.user_choices = choices
    print(f"Setting choices: {choices}")


def answer(text):
    """ Save the return function parameter and switch to previous mind. """
    text = text.lower()
    print(f'Received: {text}')
    func = oa.legacy.mind.user_choices.get(text, None)
    if func:
        oa.legacy.mind.user_choices = None
        print("Clearing choices")
        call_function(func)
    else:
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
