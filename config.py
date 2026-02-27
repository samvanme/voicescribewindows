import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "model": "base.en",
    "language": "en",
    "hotkey": ["left ctrl", "left windows"],
}

AVAILABLE_MODELS = [
    {"name": "tiny.en", "label": "Tiny (English)", "size_mb": 75},
    {"name": "base.en", "label": "Base (English)", "size_mb": 142},
    {"name": "small.en", "label": "Small (English)", "size_mb": 466},
    {"name": "medium.en", "label": "Medium (English)", "size_mb": 1528},
    {"name": "large-v3", "label": "Large v3 (Multilingual)", "size_mb": 3094},
]


def get_app_dir() -> Path:
    """Return %APPDATA%/VoiceScribe, creating it if needed."""
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    app_dir = Path(base) / "VoiceScribe"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_config_path() -> Path:
    return get_app_dir() / "config.json"


def get_models_dir() -> Path:
    models_dir = get_app_dir() / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def load_config() -> dict:
    path = get_config_path()
    if path.exists():
        try:
            with open(path, "r") as f:
                saved = json.load(f)
            # Merge with defaults so new keys are always present
            config = {**DEFAULT_CONFIG, **saved}
            return config
        except (json.JSONDecodeError, IOError):
            pass
    return dict(DEFAULT_CONFIG)


def save_config(config: dict) -> None:
    path = get_config_path()
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
