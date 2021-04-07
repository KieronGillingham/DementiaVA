import logging
_logger = logging.getLogger(__name__)


def command_registry(kws):
    def command(cmd):
        def _command(fn):
            if type(cmd) == str:
                kws[cmd.upper()] = fn
            elif type(cmd) == list:
                for kw in cmd:
                    kws[kw.upper()] = fn
            return fn
        return _command
    return command


def load_module(path):
    """Load an OA module from path."""
    import os
    import logging
    import importlib
    import queue

    from oa.legacy import Core

    # Raise exception if module not found
    if not os.path.isdir(path):
        raise Exception("Invalid module: {}".format(path))

    # Import package
    module_name = os.path.basename(path)
    _logger.info('{} <- {}'.format(module_name, path))
    M = importlib.import_module("oa.modules"+'.{}'.format(module_name))

    # If the module provides an input queue, link it
    # if getattr(M, '_in', None) is not None:

    m = Core(**M.__dict__)
    m.__dict__.setdefault('wire_in', queue.Queue())
    m.__dict__.setdefault('output', [])
    # m.__dict__.update(M.__dict__)

    return m
