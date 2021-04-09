import oa.legacy

from oa.modules.abilities.core import call_function, put
from oa.modules.abilities.system import find_file

import logging
_logger = logging.getLogger(__name__)

def user_answer(choices):
    """ Set the possible user choices as a dict:
    {'SPOKEN PHRASE': function_to_call, ...}
    """
    # mind(mind_for_answer, 0) # No history.
    try:
        oa.legacy.mind.user_choices = choices
        _logger.debug(f"Setting choices: {choices}")
    except Exception as ex:
        # _logger.debug(f'{oa.legacy.mind} does not accept user choices')
        return

def answer(text):
    """ Process an unknown user response and compare it to the current choices in the mind. """
    # If no choice is active, do nothing.
    choices = None
    try:
        choices = oa.legacy.mind.user_choices

        # If choices dict empty or nonexistent is set then the mind is not awaiting a response
        # n.b. An empty dict returns False
        if choices is None or choices is False:
            _logger.debug(f'{oa.legacy.mind} is not pending an answer')
            return

    except Exception as ex:
        # If choices cannot be accessed, then the mind does not accept user choices
        # _logger.debug(f'{oa.legacy.mind} does not accept user choices')
        return

    text = text.lower()
    _logger.debug(f'Received: {text}')
    # Get a function from the user_choices dict set by user_answer
    func = match_intent(text, choices)

    # If a function is found, clear the choices dict and run the function
    if func:
        oa.legacy.mind.user_choices = None
        _logger.debug("Clearing choices")
        call_function(func)
    else:
        # If a function isn't found, alert the user.
        say('Sorry, I didn\'t get that.')

    #oa.legacy.mind.switch_back()


def match_intent(text, options=None):
    """Given an input text, match it to either a function in the current mind, or one of a dict of options."""
    if options is None:
        # Use kws of current mind as options
        options = oa.legacy.mind.kws

    keywords = []
    for keyword in options:
        if text.find(keyword) != -1:
            func = options[keyword]
            keywords.append([func, keyword])

    if (len(keywords) > 1):
        from statistics import mode
        fn = mode(keywords[:][0])
        _logger.debug(f'Identified keywords: {keywords}')
    elif (len(keywords) == 1):
        fn = keywords[0][0]
        _logger.debug(f'Identified keyword: {keywords}')
    else:
        fn = None
        _logger.debug(f'No keywords identified.')
    return fn

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


def play(fname, description='Sound Effect'):
    """ Play a sound file. """
    print(f'Sound: {description}')
    put('sound', find_file(fname))


def mind(name, history = 1):
    """ Switch the current mind to `name`. """
    oa.legacy.hub.parts['mind'].set_mind(name, history)
