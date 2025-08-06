import time
import os
import json
from pynput import keyboard
from pynput.keyboard import Controller, Key

LOG_FILE = "recorded_keys.json"

RECORDING = False
PLAYING = False

log = []
key_down_time = None
key_controller = Controller()

settings = {
    "repetitions": 1,
    "regular_delay": 0.01,
    "alt_tab_delay": 0.3,
}

special_keys = {
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

def resolve_key(key_name):
    if key_name in special_keys:
        return special_keys[key_name]
    elif len(key_name) == 3 and key_name.startswith("'") and key_name.endswith("'"):
        return key_name.strip("'")
    else:
        raise ValueError(f"Unknown key: {key_name}")

def log_key(key, action="press"):
    global log, key_down_time
    current_time = time.time()
    key_name = str(key)
    event = {"key": key_name, "action": action}

    if action == "press":
        key_down_time = current_time
    elif action == "release":
        if key_down_time:
            event["duration"] = round(current_time - key_down_time, 3)
            key_down_time = None

    log.append(event)
    print(event)

recording_listener = None

def load_data(slot_index=None):
    """Load data from disk and optionally update settings from a specific slot."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    while len(data) < 3:
        data.append({})

    if slot_index is not None:
        slot = data[slot_index]
        if "settings" in slot:
            for k, v in slot["settings"].items():
                if k in settings:
                    settings[k] = v

    return data

def save_slot(slot_index=0):
    data = load_data()  # Don't update settings here
    slot = {
        "events": log.copy(),
        "settings": settings.copy()
    }
    data[slot_index] = slot
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def play_recorded_script(slot_index=0):
    global PLAYING
    PLAYING = True
    try:
        data = load_data(slot_index)  # Also loads settings
        slot = data[slot_index]

        if "events" not in slot or not slot["events"]:
            print(f"No events recorded in slot {slot_index}.")
            return

        for _ in range(settings["repetitions"]):
            for event in slot["events"]:
                key_name = event["key"]
                action = event["action"]
                resolved_key = resolve_key(key_name)

                duration = (
                    event.get("duration",
                        settings["alt_tab_delay"] if key_name in ("Key.tab", "Key.alt") else settings["regular_delay"])
                )

                if action == "press":
                    key_controller.press(resolved_key)
                elif action == "release":
                    key_controller.release(resolved_key)

                time.sleep(duration)
    finally:
        PLAYING = False

def toggle_recording(slot_index=0):
    global RECORDING, recording_listener
    if RECORDING:
        RECORDING = False
        save_slot(slot_index)
        if recording_listener:
            recording_listener.stop()
            recording_listener = None
    else:
        RECORDING = True
        log.clear()
        recording_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        recording_listener.start()

def on_press(key):
    if RECORDING:
        log_key(key, "press")

def on_release(key):
    if RECORDING:
        log_key(key, "release")

def start_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
