# Audio input
import collections
import math
import audioop
import sounddevice
import logging
import time
from datetime import datetime
import threading, collections, queue, os, os.path
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal
from oa.modules.abilities.core import put

_logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    # The `timeout` parameter is the maximum number of seconds that a phrase continues before stopping and returning a result. If the `timeout` is None there will be no phrase time limit.
    "timeout": None,

    "channels": 1,

    # Sampling rate in Hertz
    "sample_rate": 16000,

    # size of each sample
    "sample_width": 2,

    # Number of frames stored in each buffer.
    "chunk": 1024,

    # Minimum audio energy to consider for recording.
    "energy_threshold": 150,

    "dynamic_energy_threshold": False,
    "dynamic_energy_adjustment_damping": 0.15,
    "dynamic_energy_ratio": 1.5,

    # Seconds of non-speaking audio before a phrase is considered complete.
    "pause_threshold": 2,

    # Minimum seconds of speaking audio before we consider the audio a phrase - values below this are ignored (for filtering out clicks and pops).
    "phrase_threshold": 0.1,

    # Seconds of non-speaking audio to keep on both sides of the recording.
    "non_speaking_duration": 2,
}

def _in(ctx):
    _config = DEFAULT_CONFIG.copy()

    # Start audio with VAD
    vad_audio = VADAudio(aggressiveness=3,
                         device=None,
                         input_rate=16000)

    collector = vad_audio.vad_collector()

    while not ctx.finished.is_set():
        for frame in collector:
            yield frame
        collector = vad_audio.vad_collector()

class Audio(object):
    """Streams raw audio from microphone. Data is received in a separate thread, and stored in a buffer, to be read from."""

    FORMAT = pyaudio.paInt16
    # Network/VAD rate-space
    RATE_PROCESS = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50

    def __init__(self, callback=None, device=None, input_rate=RATE_PROCESS, file=None):
        def proxy_callback(in_data, frame_count, time_info, status):
            #pylint: disable=unused-argument
            if self.chunk is not None:
                in_data = self.wf.readframes(self.chunk)
            callback(in_data)
            return (None, pyaudio.paContinue)
        if callback is None: callback = lambda in_data: self.buffer_queue.put(in_data)
        self.buffer_queue = queue.Queue()
        self.device = device
        self.input_rate = input_rate
        self.sample_rate = self.RATE_PROCESS
        self.block_size = int(self.RATE_PROCESS / float(self.BLOCKS_PER_SECOND))
        self.block_size_input = int(self.input_rate / float(self.BLOCKS_PER_SECOND))
        self.pa = pyaudio.PyAudio()

        kwargs = {
            'format': self.FORMAT,
            'channels': self.CHANNELS,
            'rate': self.input_rate,
            'input': True,
            'frames_per_buffer': self.block_size_input,
            'stream_callback': proxy_callback,
        }

        self.chunk = None
        # if not default device
        if self.device:
            kwargs['input_device_index'] = self.device

        self.stream = self.pa.open(**kwargs)
        self.stream.start_stream()

    def resample(self, data, input_rate):
        """
        Microphone may not support our native processing sampling rate, so
        resample from input_rate to RATE_PROCESS here for webrtcvad and
        deepspeech
        Args:
            data (binary): Input audio stream
            input_rate (int): Input audio rate to resample from
        """
        data16 = np.fromstring(string=data, dtype=np.int16)
        resample_size = int(len(data16) / self.input_rate * self.RATE_PROCESS)
        resample = signal.resample(data16, resample_size)
        resample16 = np.array(resample, dtype=np.int16)
        return resample16.tostring()

    def read_resampled(self):
        """Return a block of audio data resampled to 16000hz, blocking if necessary."""
        return self.resample(data=self.buffer_queue.get(),
                             input_rate=self.input_rate)

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(lambda self: 1000 * self.block_size // self.sample_rate)

class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness=3, device=None, input_rate=None, file=None):
        super().__init__(device=device, input_rate=input_rate, file=file)
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.RATE_PROCESS:
            while True:
                yield self.read()
        else:
            while True:
                yield self.read_resampled()

    def vad_collector(self, padding_ms=1000, ratio=0.25, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        if frames is None: frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            if len(frame) < 160:
                return

            # Determine if audio input is loud enough to count as speech
            is_speech = self.vad.is_speech(frame, self.sample_rate)

            # If audio is not currently being streamed out
            if not triggered:
                # Save frame to buffer
                ring_buffer.append((frame, is_speech))

                # If ratio of speaking frames in buffer is higher than threshold
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    # Start streaming
                    triggered = True
                    _logger.debug("Utterance detected")

                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    _logger.debug("Utterance complete")
                    yield None
                    ring_buffer.clear()
                    break
