"""Configuration constants for the Macro Recorder backend."""

from pathlib import Path

from platformdirs import user_data_dir
from pynput.keyboard import Key

APP_NAME = "MacroRecorder"
APP_AUTHOR = "MacroRecorder"
LOG_FILE = Path(user_data_dir(APP_NAME, APP_AUTHOR)) / "recorded_keys.json"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_SETTINGS = {
    "repetitions": 1,
    "regular_delay": 0.01,
    "alt_tab_delay": 0.3,
}

SPECIAL_KEYS = {
    "Key.alt": Key.alt,
    "Key.alt_l": Key.alt_l,
    "Key.alt_r": Key.alt_r,
    "Key.tab": Key.tab,
    "Key.shift": Key.shift,
    "Key.shift_l": Key.shift_l,
    "Key.shift_r": Key.shift_r,
    "Key.ctrl": Key.ctrl,
    "Key.ctrl_l": Key.ctrl_l,
    "Key.ctrl_r": Key.ctrl_r,
    "Key.cmd": Key.cmd,
    "Key.cmd_l": Key.cmd_l,
    "Key.cmd_r": Key.cmd_r,
    "Key.enter": Key.enter,
    "Key.esc": Key.esc,
    "Key.space": Key.space,
    "Key.backspace": Key.backspace,
    "Key.delete": Key.delete,
    "Key.up": Key.up,
    "Key.down": Key.down,
    "Key.left": Key.left,
    "Key.right": Key.right,
    "Key.page_up": Key.page_up,
    "Key.page_down": Key.page_down,
    "Key.home": Key.home,
    "Key.end": Key.end,
    "Key.insert": Key.insert,
    "Key.f1": Key.f1,
    "Key.f2": Key.f2,
    "Key.f3": Key.f3,
    "Key.f4": Key.f4,
    "Key.f5": Key.f5,
    "Key.f6": Key.f6,
    "Key.f7": Key.f7,
    "Key.f8": Key.f8,
    "Key.f9": Key.f9,
    "Key.f10": Key.f10,
    "Key.f11": Key.f11,
    "Key.f12": Key.f12,
    "Key.caps_lock": Key.caps_lock,
    "Key.num_lock": Key.num_lock,
    "Key.scroll_lock": Key.scroll_lock,
    "Key.print_screen": Key.print_screen,
}
