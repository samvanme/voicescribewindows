import queue
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper expects 16kHz
CHANNELS = 1
DTYPE = "float32"


class Recorder:
    """Microphone recorder using sounddevice callback pattern.

    Usage:
        recorder = Recorder()
        recorder.start()
        # ... user speaks ...
        audio = recorder.stop()  # np.ndarray of float32 samples at 16kHz
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        self._queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stream: sd.InputStream | None = None

    def _callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            pass  # Dropped frames — acceptable for speech
        self._queue.put(indata.copy())

    def start(self) -> None:
        """Begin recording from the default microphone."""
        # Drain any leftover data
        while not self._queue.empty():
            self._queue.get_nowait()

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return all captured audio as a 1-D float32 array."""
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        chunks = []
        while not self._queue.empty():
            chunks.append(self._queue.get_nowait())

        if not chunks:
            return np.array([], dtype=np.float32)

        audio = np.concatenate(chunks, axis=0).flatten()
        return audio
