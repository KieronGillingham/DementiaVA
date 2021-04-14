import logging
_logger = logging.getLogger(__name__)

import threading

import oa.legacy

import json

""" CORE FUNCTIONS """

def thread_name():
    """ Return the current thread name. """
    return threading.current_thread().name.split(' ')[0]

def current_part():
    """ Return the part name which is associated with the current thread. """
    name = thread_name()
    if name in oa.legacy.hub.parts:
        return oa.legacy.hub.parts[name]
    else:
        err = '%s Error: Cannot find a related part' %name
        _logger.error(err)
        raise Exception(err)

def call_function(func_or_value):
    """ A helper function. For Stubs, call `perform()`.
        For other functions, execute a direct call. """
    if oa.legacy.isCallable(func_or_value):
        if isinstance(func_or_value, oa.legacy.Stub):
            return func_or_value.perform()
        else:
            return func_or_value()
    else:
        return func_or_value

def info(*args, **kwargs):
    """ Display information to the screen. """
    string = "[{}]".format(thread_name()) + ' '
    if args:
        string += ' '.join([str(v) for v in args]) + '\n'
    if kwargs:
        string += '\n'.join([' %s: %s' %(str(k), str(v)) for k, v in kwargs.items()])
    if hasattr(oa.legacy.hub.parts, 'console') and not oa.legacy.hub.finished.is_set():
        oa.legacy.hub.parts.console.wire_in.put(string)
    else:
        print(string)

def get(part = None, timeout = .1):
    """ Get a message from the wire. If there is no part found, take a message from the current wire input thread. (No parameters. Thread safe) """
    if part is None:
        part = current_part()
    while not oa.legacy.hub.finished.is_set():
        try:
            return part.wire_in.get(timeout = timeout)
        except oa.legacy.queue.Empty:
            pass
    raise Exception('Open Assistant closed.')

def put(part, value):
    """ Put a message on the wire. """
    oa.legacy.hub.parts[part].wire_in.put(value)


def empty(part=None):
    """ Remove all messages from `part.wire_in` input queue. """
    # If no argument is given, set part to the current part
    if part is None:
        part = current_part()

    # Search for a part with a name that matches the given string
    elif isinstance(part, str):
        partname = part
        part = oa.legacy.hub.parts[partname]
        if part is None:
            raise Exception(f"Part '{partname}' could not be found")
    try:
        # Loop over the queue, discarding each item from it until it is empty.
        while not part.wire_in.empty():
            part.wire_in.get(False)
    except Exception as ex:
        _logger.error(f"Wire in to part {part} could not be emptied: {ex}")


def set_config(setting, new_value):
    oa.legacy.hub.config[setting] = new_value
    export_config()


def adjust_config(setting, adjustment):
    oa.legacy.hub.config[setting] += adjustment
    export_config()


def export_config():
    with open("config.json", "w") as conf:
        json.dump(oa.legacy.hub.config, conf)
        conf.close()
