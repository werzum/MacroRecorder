# Macro Recorder

A simple PySide6/Qt application for recording and replaying keyboard input. The app offers three macro slots, customizable playback timing, and persistent storage so you can automate repetitive tasks from the desktop.

![GUI Sample](sample_image.png)

## Features

- Record key presses/releases with their timing
- Store up to three independent macros
- Configure repetitions and per-key delays before playback
- Inspect recorded events directly within the GUI

## Requirements

- Python 3.10+
- PySide6 (Qt 6) runtime — installing the project with `pip` pulls the prebuilt Qt wheels for Linux, macOS, and Windows

> **Note:** The project uses `pynput` for keyboard hooks. On Linux, that dependency will additionally pull in `evdev` and `python-xlib`; on macOS it uses `pyobjc` frameworks, and on Windows it installs `pywin32`. macOS users must grant the terminal or Python executable “Accessibility” permissions so key capture can work, and Windows users should allow the app through any desktop security prompts the first time they run it.

## Installation

Install from PyPI:

```console
pip install linux_macrorecorder
```

Or work from source:

```console
git clone https://github.com/werzum/MacroRecorder.git
cd MacroRecorder
python -m venv .venv
source .venv/bin/activate  # use .venv\Scripts\activate on Windows PowerShell
pip install -e .
```

## Running the application

Launch the GUI with:

```console
python -m macrorecorder
```

If you installed the package globally, you can also use the console script:

```console
macrorecorder
```

Macros, slot-specific delays, and repetition counts are stored in your platform’s user data directory (for example: `~/.local/share/MacroRecorder/recorded_keys.json` on Linux, `%APPDATA%\\MacroRecorder\\recorded_keys.json` on Windows, or `~/Library/Application Support/MacroRecorder/recorded_keys.json` on macOS). Your latest GUI adjustments are saved automatically when you stop recording or close the app, so the same values are restored the next time you launch Macro Recorder on any supported platform.

## Typical workflow

1. Start the Macro Recorder GUI.
2. Choose a macro slot (1–3).
3. Click **Start Recording**, switch to the target application, and perform the actions you want captured.
4. Return to Macro Recorder and click **Stop Recording**.
5. Adjust repetitions and delays as needed.
6. Click **Play Recorded Script** to replay the macro.

The GUI displays the captured events for the active slot so you can review timing and key order before playback.
