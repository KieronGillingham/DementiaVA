# mind.py - Core mind operations.
import logging
_logger = logging.getLogger(__name__)

import importlib
import os

import oa.legacy

from oa.modules.abilities.core import info, call_function, get, empty

""" Core mind functions. """

_history = []

def load_mind(path):
    """ Load a mind by its `name`. """
    mind = oa.legacy.Core()
    mind.module = path
    mind.name = os.path.splitext(os.path.basename(mind.module))[0]

    _logger.debug("Loading {} mind".format(mind.name))

    M = importlib.import_module("oa.modules.mind.minds"+".{}".format(mind.name))
    mind.__dict__.update(M.__dict__)

    # Add command keywords without spaces.
    mind.kws = {}
    for key, value in M.kws.items():
        for synonym in key.strip().split(','):
            mind.kws[synonym] = value

    return mind

def set_mind(name, history=True):
    """ Activate new mind. """
    _logger.info('Opening Mind: {}'.format(name))
    if history:
        _history.append(name)

    try:
        oa.legacy.mind = oa.legacy.minds[name]
        if oa.legacy.mind.start:
            _logger.debug(f'Running start function for {name}')
            oa.legacy.mind.start()
    except Exception as ex:
        _logger.error(f'{name} mind could not be set: {ex}')
    return oa.legacy.mind

def switch_back():
    """ Switch back to the previous mind. (from `switch_hist`). """
    set_mind(_history.pop(), history=False)

def load_minds():
    """ Load and check dictionaries for all minds. Handles updating language models using the online `lmtool`.
    """
    _logger.info('Loading minds...')
    mind_path = os.path.join(os.path.dirname(__file__), 'minds')
    for mind in os.listdir(mind_path):
        if mind.lower().endswith('.py'):
            m = load_mind(os.path.join(mind_path, mind))
            oa.legacy.minds[m.name] = m
    _logger.info('Minds loaded!')

def _in(ctx):

    default_mind = 'dem'
    load_minds()
    oa.legacy.oa.last_command = None
    set_mind(default_mind)
    _logger.info(f'"{default_mind}" is now listening.')

    while not ctx.finished.is_set():
        text = get()
        if (text is None) or (text.strip() == ''):
            # Nothing to do
            continue

        # Keep note of most recent command
        oa.legacy.oa.last_command = text

        t = text.upper()

        # Check for a matching command
        # TODO: Implement yet more robust intent detection
        fn = oa.modules.abilities.interact.match_intent(t)

        # If a function is identified, call it
        if fn is not None:
            oa.legacy.mind.choices = None # Clear any outstanding choices
            if oa.legacy.isCallable(fn):
                call_function(fn)

        elif t is not None:
            # If function is none, than pass the text to interact
            oa.modules.abilities.interact.answer(text)
        else:
            # Input not registered as command.
            _logger.debug(f"'{text}' was not processed.")
        yield text


