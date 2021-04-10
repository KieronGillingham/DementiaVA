import oa.legacy

from oa.modules.abilities.core import call_function, put
from oa.modules.abilities.system import find_file

from statistics import mode

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
        # Use keywords of current mind as options
        options = oa.legacy.mind.kws

    # Functions matched to text
    matched_functions = []
    for keyword in options:
        # If a keyword is identified in the given text
        if _find(keyword, text) != -1:
            # Get the function associated with the keyword
            func = options[keyword]
            # Add it to the list of matched functions
            matched_functions.append([func, keyword])

    if not matched_functions:
        # No function identified
        fn = None
        _logger.debug(f'Processing "{text}": No keywords found')
    else:
        # If one or more functions matched, select most common
        fn = mode(matched_functions[:][0])
        _logger.debug(f'Processing "{text}": Identified keywords: {[f[1] for f in matched_functions]}')

    return fn

def _find(keyword, text):
    structure = keyword.split('+')
    if len(structure) == 1:
        return text.find(keyword)
    else:
        start = 0
        for part in structure:
            start = text.find(part, start)
            if start == -1:
                break
        return start

def yes_no(msg, yes, no):
    """ Receive a yes or no answer from the user. """
    say(msg)
    choices = {}
    for k in ['yes', 'yeah', 'yah', 'yea', 'sure', 'okay']:
        choices[k] = yes
    for k in ['no', 'nope', 'nah', 'don\'t']:
        choices[k] = no
    user_answer(choices)


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
