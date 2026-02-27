import logging
import time
import threading

import pyperclip
import pyautogui

log = logging.getLogger(__name__)


def paste_text(text: str) -> None:
    """Copy text to clipboard, simulate Ctrl+V, then restore the original clipboard."""
    if not text:
        return

    log.info("Pasting text: %s", text[:80])

    # Backup current clipboard
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    # Set transcription on clipboard and paste
    try:
        pyperclip.copy(text)
        log.info("Text copied to clipboard")
    except Exception:
        log.exception("Failed to copy to clipboard")
        return

    time.sleep(0.05)

    try:
        pyautogui.hotkey("ctrl", "v")
        log.info("Ctrl+V simulated")
    except Exception:
        log.exception("Failed to simulate Ctrl+V")

    # Restore original clipboard after paste completes
    def _restore():
        time.sleep(0.3)
        try:
            pyperclip.copy(original)
        except Exception:
            pass

    threading.Thread(target=_restore, daemon=True).start()
