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

_logger = logging.getLogger(__name__)

def get_model(ctx):
    _logger.info('Initializing speech recognition model')
    try:
        config = ctx.config
        model_path = config["deepspeech_model"]
        scorer_path = config["deepspeech_scorer"]
        model = deepspeech.Model(model_path)
        model.enableExternalScorer(scorer_path)
        if model is not None:
            _logger.info('Speech recognition model loaded')
    except Exception as ex:
        _logger.error('Speech recognition model/scorerz failed to load - {}'.format(ex))
        model = None
    return model

def _in(ctx):
    mute = 0
    model = get_model(ctx)
    if model is None:
        return None

    while not ctx.finished.is_set():
        raw_data = get()
        if isinstance(raw_data, str):
            if raw_data == 'mute':
                _logger.debug('Muted')
                mute = 1
            elif raw_data == 'unmute':
                _logger.debug('Unmuted')
                mute = 0
                time.sleep(.9)
                empty()
            else:
                _logger.error("Unknown string received: '{}'".format(raw_data))
            continue
        else:
            try:
                raw_data.append(None) ## Append empty frame to deque to indicate end of audio
            except Exception as ex:
                _logger.error("Audio data in invalid format - {}".format(ex))
        # Mute mode. Do not listen until unmute.
        if mute:
            continue

        # Obtain audio data.
        try:
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
