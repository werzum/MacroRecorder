# Macro Recorder

A simple GTK application for recording and replaying keyboard input. The app offers three macro slots, customizable playback timing, and persistent storage so you can automate repetitive tasks from the desktop.

![GUI Sample](sample_image.png)

## Features

- Record key presses/releases with their timing
- Store up to three independent macros
- Configure repetitions and per-key delays before playback
- Inspect recorded events directly within the GUI

## Requirements

- Python 3.10+
- GTK 3 runtime with GObject introspection
- Cairo graphics libraries (used by GTK bindings)

### System packages

On Debian/Ubuntu (and derivatives):

```console
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                 libcairo2-dev libgirepository-1.0-1
```

On Fedora:

```console
sudo dnf install python3-gobject gtk3 cairo-gobject-devel
```

On macOS (Homebrew):

```console
brew install pygobject3 gtk+3
```

> **Note:** The project uses `pynput` for keyboard hooks. On Linux, that dependency will additionally pull in `evdev` and `python-xlib`; on macOS it uses `pyobjc` frameworks; no extra action is needed beyond the Python install.

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

Macros and their per-slot settings are stored in `recorded_keys.json` in the project directory (or your current working directory when using the installed package).

## Typical workflow

1. Start the Macro Recorder GUI.
2. Choose a macro slot (1–3).
3. Click **Start Recording**, switch to the target application, and perform the actions you want captured.
4. Return to Macro Recorder and click **Stop Recording**.
5. Adjust repetitions and delays as needed.
6. Click **Play Recorded Script** to replay the macro.

The GUI displays the captured events for the active slot so you can review timing and key order before playback.