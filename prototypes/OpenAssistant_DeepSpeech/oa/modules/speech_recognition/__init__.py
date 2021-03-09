# stt.py - Speech to text.

import logging
_logger = logging.getLogger(__name__)

import os, re, time

import pocketsphinx
import requests

import oa.legacy

from datetime import datetime
import threading, collections, queue, os, os.path
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal

from oa.modules.abilities.core import get, empty, info
from oa.modules.abilities.system import download_file, write_file, stat_mtime

_decoders = {}

def config_stt(cache_dir, keywords, kws_last_modification_time_in_sec = None):
    _ = oa.legacy.Core()
    cache_path = lambda x: os.path.join(cache_dir, x)
    _.lang_file = cache_path('lm')
    _.fsg_file = None
    _.dic_file = cache_path('dic')
    _.hmm_dir = cache_path('hmm')

    # Save keywords for further pattern matching. Call `config_stt()` when switching minds to check for command file changes.
    _.kwords = {}
    _.max_w_cnt = 3
    for phrase in keywords:
        spl_ph = phrase.strip().split(' ')
        w_cnt = len(spl_ph)
        if w_cnt > _.max_w_cnt:
            _.max_w_cnt = w_cnt
        for kword in spl_ph:
            # Combine all phrases which use keywords.
            r_phrases = _.kwords.setdefault(kword,{})
            r_phrases[phrase] = w_cnt

    # Save phrases.
    _.phrases = [x.strip().replace('%d', '').upper() for x in sorted(keywords)]

    # Check if commands file was modified.
    if kws_last_modification_time_in_sec:
        if os.path.exists(_.dic_file) and (kws_last_modification_time_in_sec < stat_mtime(_.dic_file)):
            return _
    _.strings_file = cache_path("sentences.corpus")
    data = '\n'.join(_.phrases)
    write_file(_.strings_file, data)

    return _

def get_decoder():
    # XXX: race condition when mind isn't set yet
    mind = oa.legacy.mind
    if not hasattr(_decoders, mind.name):

        print('Initializing model...')
        model = deepspeech.Model("/home/mycroft/deepspeech-0.9.3-models.pbmm")
        model.enableExternalScorer("/home/mycroft/deepspeech-0.9.3-models.scorer")
        return model

        """
        # Start audio with VAD
        vad_audio = VADAudio(aggressiveness=3,
                             device=None,
                             input_rate=16000)
        print("Listening (ctrl-C to exit)...")
        frames = vad_audio.vad_collector()

        # Stream from microphone to DeepSpeech using VAD
        stream_context = model.createStream()
        """

        """  
        # Configure Speech to text dictionaries.
        ret = config_stt(mind.cache_dir, mind.kws.keys(), stat_mtime(mind.module))
              
        # Process audio chunk by chunk. On a keyphrase detected perform the action and restart search.
        config = pocketsphinx.Decoder.default_config()

        # Set paths for the language model files.
        config.set_string('-hmm', ret.hmm_dir)
        config.set_string("-lm", ret.lang_file)
        config.set_string("-dict", ret.dic_file)
        config.set_string("-logfn", os.devnull)  # Disable logging.
        

        ret.decoder = pocketsphinx.Decoder(config)
        _decoders[mind.name] = ret
    else:
        return _decoders[mind.name]

    return ret
    """

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
                    #print(data)
                    _logger.debug("streaming frame")
                    stream_context.feedAudioContent(np.frombuffer(data, np.int16))
                else:
                    _logger.debug("end utterence")

                    text = stream_context.finishStream()

                    if text is not None:
                        if (text is None) or (text.strip() == ''):
                            continue
                        _logger.info("Heard: {}".format(text))
                        yield text
                        #if text.upper() in dinf.phrases:
                        #    yield text
                        #else:
                        #    continue
                    else:
                        _logger.warn('Speech not recognized')


        except Exception as e:
            _logger.error(e)

        """else:
            if text is not None:
                if text.strip() == '':
                    continue
                _logger.info("Heard: {}".format(text))
                if text.upper() in dinf.phrases:
                    yield text
                else:
                    continue

            else:
                _logger.warn('Speech not recognized')"""

"""
# Obtain audio data.
        try:
            dinf = get_decoder()
            decoder = dinf.decoder
            decoder.start_utt()  # Begin utterance processing.

            # Process audio data with recognition enabled (no_search = False), as a full utterance (full_utt = True)
            decoder.process_raw(raw_data, False, False)  

            decoder.end_utt()  # Stop utterance processing.

        except Exception as e:
            _logger.error(e)

        else:
            hypothesis = decoder.hyp()
            if hypothesis is not None: 
                hyp = hypothesis.hypstr
                if (hyp is None) or (hyp.strip() == ''):
                    continue
                _logger.info("Heard: {}".format(hyp))
                if hyp.upper() in dinf.phrases:
                    yield hyp
                else:
                    continue

            else:
                _logger.warn('Speech not recognized')
"""