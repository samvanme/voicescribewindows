# VoiceScribe for Windows

Push-to-talk local transcription. Hold a hotkey, speak, release — transcribed text is pasted into the active window.

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for local, offline transcription. No data leaves your machine.

## Requirements

- Windows 10/11
- Python 3.12+ ([Microsoft Store](https://apps.microsoft.com/detail/9NCVDN91XZQP))
- Administrator privileges (required for global hotkey detection)
- A microphone

## Install

1. Download the VoiceScribe folder
2. Open **PowerShell as Administrator** (right-click → Run as administrator)
3. Run:

```
cd "C:\path\to\VoiceScribe"
pip install -r requirements.txt
python main.py
```

First run downloads the Whisper model (~142 MB). After that, just `python main.py`.

CUDA is optional. If a CUDA-capable GPU and PyTorch with CUDA are installed, faster-whisper uses GPU acceleration automatically. Otherwise it runs on CPU with int8 quantization.

## Run Without a Terminal Window

To run VoiceScribe as a background app (no PowerShell window):

1. Right-click Desktop → **New** → **Shortcut**
2. Set location to: `pythonw.exe "C:\path\to\VoiceScribe\main.py"`
3. Name it **VoiceScribe**
4. Right-click the shortcut → **Properties** → **Advanced** → check **Run as administrator** → OK

Double-click the shortcut to launch. The app runs in the system tray — right-click the tray icon → **Quit** to close.

## Usage

**Hotkey:** Hold **Ctrl + Windows key**, speak, release. Transcribed text is pasted wherever your cursor is.

A system tray icon appears (bottom-right taskbar, may need to click `^`). Right-click it to:

- See current status (recording / idle / loading)
- Select a Whisper model (downloads on first use)
- Quit

### Models

| Model | Size | Notes |
|-------|------|-------|
| tiny.en | ~75 MB | Fastest, least accurate |
| base.en | ~142 MB | Default. Good balance |
| small.en | ~466 MB | Better accuracy |
| medium.en | ~1.5 GB | High accuracy |
| large-v3 | ~3 GB | Best accuracy, multilingual |

Models download automatically on first selection and are cached in `%APPDATA%/VoiceScribe/models/`.

## Configuration

Settings are stored in `%APPDATA%/VoiceScribe/config.json`:

```json
{
  "model": "base.en",
  "language": "en",
  "hotkey": ["ctrl", "left windows"]
}
```

## Limitations

- Windows only (uses winsound, keyboard library's Windows hooks)
- Non-text clipboard content (images, files) is not preserved when pasting
- Requires admin for global hotkey detection
