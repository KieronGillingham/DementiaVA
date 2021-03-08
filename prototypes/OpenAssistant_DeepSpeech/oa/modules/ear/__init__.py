# init
import collections
import math
import audioop
import sounddevice

# mic_vad
import time, logging
from datetime import datetime
import threading, collections, queue, os, os.path
import deepspeech
import numpy as np
import pyaudio
import wave
import webrtcvad
from halo import Halo
from scipy import signal

logging.basicConfig(level=20)

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
        elif file is not None:
            self.chunk = 320
            self.wf = wave.open(file, 'rb')

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

    def write_wav(self, filename, data):
        logging.info("write wav %s", filename)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert self.FORMAT == pyaudio.paInt16
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()


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

    def vad_collector(self, padding_ms=1000, ratio=0.75, frames=None):
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
            if len(frame) < 640:
                return

            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()

# init.py


DEFAULT_CONFIG = {
    # The `timeout` parameter is the maximum number of seconds
    # that a phrase continues before stopping and returning a
    # result. If the `timeout` is None there will be no phrase time limit.
    "timeout": None,

    "channels": 1,

    # Sampling rate in Hertz
    "sample_rate": 16000,

    # size of each sample
    "sample_width": 2,

    # Number of frames stored in each buffer.
    "chunk": 1024,

    # Minimum audio energy to consider for recording.
    "energy_threshold": 300,

    "dynamic_energy_threshold": False,
    "dynamic_energy_adjustment_damping": 0.15,
    "dynamic_energy_ratio": 1.5,

    # Seconds of non-speaking audio before a phrase is considered complete.
    "pause_threshold": 0.8,

    # Minimum seconds of speaking audio before we consider the audio a phrase - values
    # below this are ignored (for filtering out clicks and pops).
    "phrase_threshold": 0.3,

    # Seconds of non-speaking audio to keep on both sides of the recording.
    "non_speaking_duration": 0.8,

    # Set aggressiveness of VAD: an integer between 0 and 3, 0 being the least
    # aggressive about filtering out non-speech, 3 the most aggressive.
    "vad_aggressiveness": 3,
    "model": "/home/mycroft/deepspeech-0.9.3-models.pbmm",
    "scorer": "/home/mycroft/deepspeech-0.9.3-models.scorer",
}

def _in(ctx):

    # OpenVA
    _config = DEFAULT_CONFIG.copy()

    seconds_per_buffer = _config.get("chunk") / _config.get("sample_rate")
    pause_buffer_count = math.ceil(_config.get("pause_threshold") / seconds_per_buffer)

    # Deepspeech
    # Load DeepSpeech model
    print(_config)
    if os.path.isdir(_config.get("model")):
        model_dir = _config.get("model")
        _config.set("model", os.path.join(model_dir, 'output_graph.pb'))
        _config.set("scorer", os.path.join(model_dir, _config.get("scorer")))

    print('Initializing model...')
    logging.info("_config.get('model'): %s", _config.get("model"))
    model = deepspeech.Model(_config.get("model"))
    if _config.get("scorer"):
        logging.info("_config.get('scorer'): %s", _config.get("scorer"))
        model.enableExternalScorer(_config.get("scorer"))

    # Start audio with VAD
    vad_audio = VADAudio(aggressiveness=_config.get("vad_aggressiveness"),
                         device=None,  # Use default audio device
                         input_rate=_config.get("sample_rate"))
    print("Listening (ctrl-C to exit)...")
    frames = vad_audio.vad_collector()

    # Stream from microphone to DeepSpeech using VAD
    stream_context = model.createStream()
    for frame in frames:
        if frame is not None:
            logging.debug("streaming frame")
            stream_context.feedAudioContent(np.frombuffer(frame, np.int16))

        else:
            logging.debug("end utterence")
            text = stream_context.finishStream()
            print("Recognized: %s" % text)
            stream_context = model.createStream()
            yield text

    """
    # Number of buffers of non-speaking audio during a phrase before the phrase should be considered complete.
    phrase_buffer_count = math.ceil(_config.get("phrase_threshold") / seconds_per_buffer) # Minimum number of buffers of speaking audio before we consider the speaking audio a phrase.
    non_speaking_buffer_count = math.ceil(_config.get("non_speaking_duration") / seconds_per_buffer)  # Maximum number of buffers of non-speaking audio to retain before and after a phrase.

    stream = sounddevice.Stream(samplerate=_config.get("sample_rate"), channels=_config.get("channels"), dtype='int16')
    with stream:
        while not ctx.finished.is_set():
            elapsed_time = 0  # Number of seconds of audio read
            buf = b""  # An empty buffer means that the stream has ended and there is no data left to read.
            while not ctx.finished.is_set():
                frames = collections.deque()

                # Store audio input until the phrase starts
                while not ctx.finished.is_set():
                    # Handle waiting too long for phrase by raising an exception
                    elapsed_time += seconds_per_buffer
                    if _config.get("timeout") and (elapsed_time > _config.get("timeout")):
                        raise Exception("Listening timed out while waiting for phrase to start.")

                    buf = stream.read(_config.get("chunk"))[0]
                    frames.append(buf)
                    if len(frames) > non_speaking_buffer_count:  
                    # Ensure we only keep the required amount of non-speaking buffers.
                        frames.popleft()

                    # Detect whether speaking has started on audio input.
                    energy = audioop.rms(buf, _config.get("sample_width"))  # Energy of the audio signal.
                    if energy > _config.get("energy_threshold"):
                        break

                    # Dynamically adjust the energy threshold using asymmetric weighted average.
                    if _config.get("dynamic_energy_threshold"):
                        damping = _config.get("dynamic_energy_adjustment_damping") ** seconds_per_buffer  # Account for different chunk sizes and rates.
                        target_energy = energy * _config.get("dynamic_energy_ratio")
                        _config["energy_threshold"] = _config.get("energy_threshold") * damping + target_energy * (1 - damping)

                # Read audio input until the phrase ends.
                pause_count, phrase_count = 0, 0
                phrase_start_time = elapsed_time
                while not ctx.finished.is_set():
                    # Handle phrase being too long by cutting off the audio.
                    elapsed_time += seconds_per_buffer
                    if _config.get("timeout") and (elapsed_time - phrase_start_time > _config.get("timeout")):
                        break

                    buf = stream.read(_config.get("chunk"))[0]
                    frames.append(buf)
                    phrase_count += 1

                    # Check if speaking has stopped for longer than the pause threshold on the audio input.
                    energy = audioop.rms(buf, _config.get("sample_width"))  # unit energy of the audio signal within the buffer.
                    if energy > _config.get("energy_threshold"):
                        pause_count = 0
                    else:
                        pause_count += 1
                    if pause_count > pause_buffer_count:  # End of the phrase.
                        break

                # Check how long the detected phrase is and retry listening if the phrase is too short.
                phrase_count -= pause_count  # Exclude the buffers for the pause before the phrase.
                if phrase_count >= phrase_buffer_count or len(buf) == 0: break  # Phrase is long enough or we've reached the end of the stream, so stop listening.

            # Obtain frame data.
            for _ in range(pause_count - non_speaking_buffer_count): frames.pop()  # Remove extra non-speaking frames at the end.
            frame_data = numpy.concatenate(frames)
            yield frame_data
	"""
