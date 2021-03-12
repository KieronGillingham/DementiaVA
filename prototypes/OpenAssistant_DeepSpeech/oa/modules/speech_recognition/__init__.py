# Logging
import logging

# OS interaction
import os
import time
import oa.legacy
import os.path
import deepspeech
import numpy as np

from oa.modules.abilities.core import get, empty, info
from oa.modules.abilities.system import download_file, write_file, stat_mtime

_decoders = {}
_logger = logging.getLogger(__name__)

def get_decoder():
    # XXX: race condition when mind isn't set yet
    mind = oa.legacy.mind
    if not hasattr(_decoders, mind.name):
        _logger.info('Initializing speech recognition model')
        try:
            # TODO: Make configurable
            model = deepspeech.Model("/home/mycroft/deepspeech-0.9.3-models.pbmm")
            model.enableExternalScorer("/home/mycroft/deepspeech-0.9.3-models.scorer")
            if model is not None:
                _logger.info('Speech recognition model loaded')
                return model
        except Exception as e:
            _logger.info('Speech recognition model failed to load')
            _logger.error(e)
            return None

def _in(ctx):
    mute = 0

    while not ctx.finished.is_set():
        raw_data = get()
        raw_data.append(None)
        if isinstance(raw_data, str):
            if raw_data == 'mute':
                _logger.debug('Muted')
                mute = 1
            elif raw_data == 'unmute':
                _logger.debug('Unmuted')
                mute = 0
                time.sleep(.9)
                empty()
            continue
            
        # Mute mode. Do not listen until unmute.
        if mute:
            continue

        # Obtain audio data.
        try:
            model = get_decoder()
            stream_context = model.createStream()
            for frame in raw_data:
                if frame is not None:
                    data = frame.reshape(-1)
                    stream_context.feedAudioContent(np.frombuffer(data, np.int16))
                else:
                    _logger.debug("end utterence")

                    text = stream_context.finishStream()

                    if text is not None:
                        if (text is None) or (text.strip() == ''):
                            continue
                        _logger.info("Heard: {}".format(text))
                        yield text
                    else:
                        _logger.warn('Speech not recognized')


        except Exception as e:
            _logger.error(e)