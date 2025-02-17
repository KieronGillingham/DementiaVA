# Open Assistant 0.21
# 2018 General Public License V3

"""Open Assistant reference implementation."""

import logging
_logger = logging.getLogger(__name__)

import os

import oa

import oa.legacy

def start(hub, **kwargs):
    """Initialize and run the OpenAssistant Agent"""
    from oa.util.repl import command_loop

    hub.run()

    _map = [
        ('ear', 'speech_recognition'),
        ('speech_recognition', 'mind'),
    ]
    for _in, _out in _map:
        hub.parts[_in].output += [hub.parts[_out]]

    while not hub.finished.is_set():
        try:
            command_loop(hub)
        except Exception as ex:
            _logger.error("Command Loop: {}".format(ex))

    hub.ready.wait()


if __name__ == '__main__':
    import sys
    from oa.util.args import _parser

    args = _parser(sys.argv[1:])

    log_template = "[%(asctime)s] %(levelname)s %(threadName)s %(name)s: %(message)s"
    logging.basicConfig(level=logging.WARNING if not args.debug else logging.DEBUG, filename=args.log_file, format=log_template)

    _logger.info("Start Open Assistant")

    config = {
        'module_path': [
            os.path.join(os.path.dirname(__file__), 'modules'),
        ],
        'modules': [
            'voice',
            'sound',
            'ear',
            'speech_recognition',
            'mind',
        ],
    }

    # Load configuration file
    import json
    # Get config from CL args
    config_path = args.config_file
    if config_path is not None:
        config.update(json.load(open(config_path)))
    else:  # Or from default config
        _logger.info("No config file specified. Searching for default.")
        try:
            config.update(json.load(open("config.json")))
            _logger.info("Default configuration file found")
        except Exception as ex:
            _logger.info("Default configuration file not found: {}".format(ex))

    hub = oa.Hub(config=config)

    # XXX: temporary compatability hack
    oa.legacy.hub = hub
    oa.legacy.core_directory = os.path.dirname(__file__)

    try:
        start(
            hub,
            config_path=args.config_file,
        )

    except KeyboardInterrupt:
        _logger.info("Ctrl-C Pressed")

        _logger.info("Signaling Shutdown")
        hub.finished.set()

        _logger.info('Waiting on threads')
        [thr.join() for thr in hub.thread_pool]
        _logger.info('Threads closed')
