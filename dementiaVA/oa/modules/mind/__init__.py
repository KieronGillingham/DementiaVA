# mind.py - Core mind operations.
import logging
_logger = logging.getLogger(__name__)

import importlib
import os

import oa.legacy

from oa.modules.abilities.core import info, call_function, get
from oa.modules.abilities.system import read_file, sys_exec


""" Core mind functions. """

_history = []

def load_mind(path):
    """ Load a mind by its `name`. """
    mind = oa.legacy.Core()
    mind.module = path
    mind.name = os.path.splitext(os.path.basename(mind.module))[0]
    mind.cache_dir = os.path.join(oa.legacy.core_directory, 'cache', mind.name)

    _logger.debug("Loading {} mind".format(mind.name))

    # Make directories.
    if not os.path.exists(mind.cache_dir):
        os.makedirs(mind.cache_dir)

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
            _logger.info("<- {}".format(mind))
            m = load_mind(os.path.join(mind_path, mind))
            oa.legacy.minds[m.name] = m
    _logger.info('Minds loaded!')

def _in(ctx):

    default_mind = 'dem'
    load_minds()
    set_mind(default_mind)
    _logger.info('"{}" is now listening.'.format(default_mind))

    while not ctx.finished.is_set():
        text = get()
        #_logger.debug('Input: {}'.format(text))
        mind = oa.legacy.mind
        if (text is None) or (text.strip() == ''):
            # Nothing to do.
            continue
        t = text.upper()

        # Check for a matching command.
        # TODO: Implement more robust intent detection

        fn = oa.modules.abilities.interact.match_intent(t)

        if fn is not None:
            # There are two types of commands, stubs and command line text.
            # For stubs, call `perform()`.
            if oa.legacy.isCallable(fn):
                call_function(fn)
                oa.legacy.oa.last_command = t
            # For strings, call `sys_exec()`.
            # TODO: Remove command line functions
            elif isinstance(fn, str):
                sys_exec(fn)
                oa.legacy.oa.last_command = t
            else:
                # Any unknown command raises an exception.
                raise Exception("Unable to process: {}".format(text))
        elif t is not None:
            # If function is not none, than pass the text to interact
            oa.modules.abilities.interact.answer(text)
        else:
            # Input not registered as command.
            _logger.debug("'{}' is not a command".format(text))
        yield text

