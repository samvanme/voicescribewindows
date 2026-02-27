import logging
import threading
from typing import Callable

import keyboard

log = logging.getLogger(__name__)

_CTRL = "ctrl"
_LEFT_WIN = "left windows"


class HotkeyMonitor:
    """Monitors Ctrl + Left Windows key combo for push-to-talk.

    Requires running as admin on Windows for global key hooks.

    Args:
        on_start: Called when the hotkey combo is pressed (both keys down).
        on_stop: Called when either key is released while recording.
    """

    def __init__(self, on_start: Callable, on_stop: Callable):
        self._on_start = on_start
        self._on_stop = on_stop
        self._ctrl_down = False
        self._win_down = False
        self._recording = False
        self._lock = threading.Lock()
        self._hooked = False

    def start(self) -> None:
        """Install the global keyboard hook."""
        if self._hooked:
            return

        keyboard.hook(self._on_key_event, suppress=False)
        self._hooked = True
        log.info("Hotkey monitor started (Ctrl + Left Win)")

    def stop(self) -> None:
        """Remove the global keyboard hook."""
        if not self._hooked:
            return
        try:
            keyboard.unhook_all()
        except Exception:
            pass
        self._hooked = False
        log.info("Hotkey monitor stopped")

    def _on_key_event(self, event: keyboard.KeyboardEvent) -> None:
        name = event.name
        if name not in (_CTRL, _LEFT_WIN):
            return

        log.debug("Key event: %s %s", event.event_type, name)

        with self._lock:
            if event.event_type == keyboard.KEY_DOWN:
                if name == _CTRL:
                    self._ctrl_down = True
                elif name == _LEFT_WIN:
                    self._win_down = True

                # Both keys now held — start recording
                if self._ctrl_down and self._win_down and not self._recording:
                    self._recording = True
                    log.info("Hotkey pressed — starting recording")
                    threading.Thread(
                        target=self._on_start, daemon=True
                    ).start()

            elif event.event_type == keyboard.KEY_UP:
                if name == _CTRL:
                    self._ctrl_down = False
                elif name == _LEFT_WIN:
                    self._win_down = False

                # Either key released while recording — stop
                if self._recording:
                    self._recording = False
                    log.info("Hotkey released — stopping recording")
                    threading.Thread(
                        target=self._on_stop, daemon=True
                    ).start()
