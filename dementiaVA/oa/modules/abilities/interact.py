from os import wait
from time import sleep

import oa.legacy

from oa.modules.abilities.core import call_function, put
from oa.modules.abilities.system import find_file

response = None
waiting_function = None


def answer(text):
    """ Save the return function parameter and switch to previous mind. """
    text = text.lower()
    print(f'Received: {text}')
    func = oa.legacy.mind.user_choices.get(text, None)
    if func:
        call_function(func)
    oa.legacy.mind.switch_back()


def confirm_react(response):
    waiting_function = None
    if response == 'yes':
        say(yes_msg)
        return True
    elif response == 'no':
       say(no_msg)
       return False
    else:
        confirm('Sorry. Was that a "yes" or "no"?')


def confirm(msg, yes_msg = None, no_msg = None):
    say(msg)
    waiting_function = confirm_react;


def yes_no(msg, mind, func):
    """ Receive a yes or no answer from the user. """
    say(msg)
    user_answer(mind, {'yes': func})
    # user_answer('yes_no', {'yes: func})


def user_answer(mind_for_answer, choices):
    """ Within any `mind` we will receive a one word answer command (voice, file path, etc, any) from the user. """
    #mind(mind_for_answer, 0) # No history.
    oa.legacy.mind.user_choices = choices


def user_response(msg):
    say(msg)
    #return response


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
