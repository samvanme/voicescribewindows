import logging
import os
from pathlib import Path

import numpy as np

from config import get_models_dir

log = logging.getLogger(__name__)

# Map model names to their huggingface repo IDs used by faster-whisper
_MODEL_REPO = {
    "tiny.en": "Systran/faster-whisper-tiny.en",
    "base.en": "Systran/faster-whisper-base.en",
    "small.en": "Systran/faster-whisper-small.en",
    "medium.en": "Systran/faster-whisper-medium.en",
    "large-v3": "Systran/faster-whisper-large-v3",
}


class Transcriber:
    """Manages a faster-whisper model and runs transcription."""

    def __init__(self):
        self._model = None
        self._model_name: str | None = None

    def load_model(self, name: str) -> None:
        """Load (and download if necessary) a Whisper model by name."""
        from faster_whisper import WhisperModel

        if self._model_name == name and self._model is not None:
            return  # Already loaded

        models_dir = get_models_dir()
        download_root = str(models_dir)

        # Detect CUDA availability
        device = "cpu"
        compute_type = "int8"
        try:
            import torch
            if torch.cuda.is_available():
                device = "cuda"
                compute_type = "float16"
        except ImportError:
            pass

        log.info("Loading model %s on %s (%s)", name, device, compute_type)

        self._model = WhisperModel(
            name,
            device=device,
            compute_type=compute_type,
            download_root=download_root,
        )
        self._model_name = name
        log.info("Model %s loaded", name)

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe a float32 16kHz audio array to text."""
        if self._model is None:
            raise RuntimeError("No model loaded — call load_model() first")

        if audio.size == 0:
            return ""

        segments, info = self._model.transcribe(
            audio,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()

    @property
    def current_model(self) -> str | None:
        return self._model_name

    @staticmethod
    def is_model_downloaded(name: str) -> bool:
        """Check if a model's files exist in the local cache."""
        models_dir = get_models_dir()
        # faster-whisper stores models in subdirectories named after the repo
        repo = _MODEL_REPO.get(name, "")
        if not repo:
            return False
        # The cache directory uses "models--<org>--<model>" format
        cache_name = "models--" + repo.replace("/", "--")
        cache_path = models_dir / cache_name
        if cache_path.is_dir():
            # Check for a snapshots dir with content
            snapshots = cache_path / "snapshots"
            if snapshots.is_dir() and any(snapshots.iterdir()):
                return True
        return False
