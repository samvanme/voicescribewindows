"""VoiceScribe — Push-to-talk local transcription for Windows.

Hold Left Ctrl + Left Windows key to record, release to transcribe and paste.
Runs as a system-tray application.
"""

import logging
import threading
import sys
from pathlib import Path

from PIL import Image
import pystray

from config import (
    AVAILABLE_MODELS,
    load_config,
    save_config,
)
from audio import Recorder
from transcriber import Transcriber
from text_inserter import paste_text
from hotkey import HotkeyMonitor
from sounds import play_start, play_stop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("voicescribe")


class App:
    def __init__(self):
        self.config = load_config()
        self.recorder = Recorder()
        self.transcriber = Transcriber()
        self.hotkey_monitor = HotkeyMonitor(
            on_start=self._on_record_start,
            on_stop=self._on_record_stop,
        )
        self._status = "Loading model..."
        self._icon: pystray.Icon | None = None
        self._recording = False
        self._lock = threading.Lock()

    # -- Recording callbacks --------------------------------------------------

    def _on_record_start(self) -> None:
        with self._lock:
            if self._recording:
                return
            if self._status == "Loading model...":
                return  # Model not ready yet
            self._recording = True

        play_start()
        self.recorder.start()
        log.info("Recording started")
        self._set_status("Recording...")

    def _on_record_stop(self) -> None:
        with self._lock:
            if not self._recording:
                return
            self._recording = False
            self._set_status("Transcribing...")

        log.info("Recording stopped, transcribing...")
        audio = self.recorder.stop()
        play_stop()

        if audio.size == 0:
            log.warning("No audio captured")
            self._set_status("Ready")
            return

        try:
            text = self.transcriber.transcribe(audio)
            log.info("Transcribed: %s", text[:80] if text else "(empty)")
            if text:
                paste_text(text)
        except Exception:
            log.exception("Transcription failed")

        self._set_status("Ready")

    # -- Status management ----------------------------------------------------

    def _set_status(self, status: str) -> None:
        self._status = status
        if self._icon is not None:
            self._icon.update_menu()

    # -- Model management -----------------------------------------------------

    def _load_model_async(self, model_name: str) -> None:
        """Load a model in a background thread."""
        def _load():
            self._set_status(f"Loading {model_name}...")
            try:
                self.transcriber.load_model(model_name)
                self.config["model"] = model_name
                save_config(self.config)
                self._set_status("Ready")
                log.info("Model %s ready", model_name)
            except Exception:
                log.exception("Failed to load model %s", model_name)
                self._set_status("Model load failed")

        threading.Thread(target=_load, daemon=True).start()

    def _on_model_select(self, model_name: str):
        """Return a callback for selecting a model from the tray menu."""
        def _callback(icon, item):
            self._load_model_async(model_name)
        return _callback

    def _is_current_model(self, model_name: str):
        """Return a callable that checks if model_name is the active model."""
        def _check(item) -> bool:
            return self.transcriber.current_model == model_name
        return _check

    # -- Tray menu ------------------------------------------------------------

    def _build_menu(self) -> pystray.Menu:
        model_items = []
        for m in AVAILABLE_MODELS:
            name = m["name"]
            label = m["label"]
            downloaded = Transcriber.is_model_downloaded(name)
            suffix = "" if downloaded else " (download)"
            model_items.append(
                pystray.MenuItem(
                    f"{label}{suffix}",
                    self._on_model_select(name),
                    checked=self._is_current_model(name),
                    radio=True,
                )
            )

        return pystray.Menu(
            pystray.MenuItem(self._status, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Model", pystray.Menu(*model_items)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )

    # -- Lifecycle ------------------------------------------------------------

    def _on_quit(self, icon, item) -> None:
        log.info("Quitting")
        self.hotkey_monitor.stop()
        icon.stop()

    def _load_icon_image(self) -> Image.Image:
        """Load the tray icon. Falls back to a generated icon if file missing."""
        icon_path = Path(__file__).parent / "icon.png"
        if icon_path.exists():
            return Image.open(icon_path)
        # Generate a simple icon: blue circle on transparent background
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([8, 8, 56, 56], fill=(50, 120, 220, 255))
        # Microphone shape: simple white rectangle + circle
        draw.rectangle([26, 16, 38, 36], fill=(255, 255, 255, 255))
        draw.ellipse([22, 30, 42, 48], outline=(255, 255, 255, 255), width=2)
        draw.line([32, 48, 32, 54], fill=(255, 255, 255, 255), width=2)
        return img

    def run(self) -> None:
        """Start the application."""
        log.info("VoiceScribe starting")

        # Start hotkey monitor
        self.hotkey_monitor.start()

        # Load model in background
        self._load_model_async(self.config["model"])

        # Create and run tray icon (blocks on main thread)
        image = self._load_icon_image()
        self._icon = pystray.Icon(
            "VoiceScribe",
            image,
            "VoiceScribe",
            menu=self._build_menu(),
        )
        self._icon.run()


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
