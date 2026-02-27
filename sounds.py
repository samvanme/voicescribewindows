import threading


def _beep(frequency: int, duration_ms: int) -> None:
    """Play a beep in a background thread. Falls back to no-op on non-Windows."""
    def _play():
        try:
            import winsound
            winsound.Beep(frequency, duration_ms)
        except (ImportError, RuntimeError):
            # Not on Windows or no audio device — silently skip
            pass
    threading.Thread(target=_play, daemon=True).start()


def play_start() -> None:
    """Short high beep indicating recording started."""
    _beep(440, 100)


def play_stop() -> None:
    """Lower tone indicating recording stopped."""
    _beep(330, 120)
