"""Keyboard macro recording and playback helpers."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from pynput import keyboard
from pynput.keyboard import Controller

from .config import DEFAULT_SETTINGS, LOG_FILE, SPECIAL_KEYS
from .storage import load_slots as _load_slots, save_slot as _save_slot

settings: Dict[str, Any] = DEFAULT_SETTINGS.copy()
_log: List[Dict[str, Any]] = []
_recording = False
_playing = False
_key_down_time: Optional[float] = None
_controller = Controller()
_listener: Optional[keyboard.Listener] = None


def load_slots() -> List[Dict[str, Any]]:
    """Return all recorded slots from disk."""
    return _load_slots(LOG_FILE)


def is_recording() -> bool:
    return _recording


def is_playing() -> bool:
    return _playing


def toggle_recording(slot_index: int = 0) -> bool:
    """Start or stop recording for the selected slot."""
    global _recording
    if _recording:
        _stop_recording(slot_index)
    else:
        _start_recording()
    return _recording


def play(slot_index: int = 0) -> None:
    """Replay the events stored in the requested slot."""
    global _playing
    if _recording:
        raise RuntimeError("Cannot play back while recording is active.")

    _playing = True
    try:
        slots = load_slots()
        slot = slots[slot_index]

        events = slot.get("events")
        if not events:
            print(f"No events recorded in slot {slot_index + 1}.")
            return

        stored_settings = slot.get("settings", {})
        for key, value in stored_settings.items():
            if key in settings:
                settings[key] = value

        repetitions = int(settings["repetitions"])
        for _ in range(repetitions):
            for event in events:
                key_name = event["key"]
                action = event["action"]
                resolved_key = _resolve_key(key_name)

                default_delay = (
                    settings["alt_tab_delay"]
                    if key_name in ("Key.tab", "Key.alt")
                    else settings["regular_delay"]
                )
                duration = event.get("duration", default_delay)

                if action == "press":
                    _controller.press(resolved_key)
                elif action == "release":
                    _controller.release(resolved_key)

                time.sleep(duration)
    finally:
        _playing = False


def _start_recording() -> None:
    global _recording, _listener, _key_down_time
    _recording = True
    _log.clear()
    _key_down_time = None
    _listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
    _listener.start()


def _stop_recording(slot_index: int) -> None:
    global _recording, _listener
    _recording = False
    if _listener:
        _listener.stop()
        _listener = None

    _save_slot(slot_index, _log.copy(), settings.copy(), LOG_FILE)


def _on_press(key: keyboard.KeyCode | keyboard.Key) -> None:
    if _recording:
        _log_key(key, "press")


def _on_release(key: keyboard.KeyCode | keyboard.Key) -> None:
    if _recording:
        _log_key(key, "release")


def _log_key(key: keyboard.KeyCode | keyboard.Key, action: str) -> None:
    global _key_down_time
    current_time = time.time()
    key_name = str(key)
    event: Dict[str, Any] = {"key": key_name, "action": action}

    if action == "press":
        _key_down_time = current_time
    elif action == "release" and _key_down_time is not None:
        event["duration"] = round(current_time - _key_down_time, 3)
        _key_down_time = None

    _log.append(event)
    print(event)


def _resolve_key(key_name: str):
    if key_name in SPECIAL_KEYS:
        return SPECIAL_KEYS[key_name]
    if len(key_name) == 3 and key_name.startswith("'") and key_name.endswith("'"):
        return key_name.strip("'")
    raise ValueError(f"Unknown key: {key_name}")
