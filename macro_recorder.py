import time
import os
from pynput import keyboard
from pynput.keyboard import Controller, Key

LOG_FILE = os.path.join(os.path.expanduser("~"), "recorded_keys.txt")
RECORDING = False
PLAYING = False

log = []
key_down_time = None
key_controller = Controller()

# Map string representations to special keys
special_keys = {
    "Key.alt": Key.alt,
    "Key.alt_l": Key.alt_l,
    "Key.alt_r": Key.alt_r,
    "Key.tab": Key.tab,
    # Add the remaining keys here as in your original script
}

# To store the settings
settings = {
    "repetitions": 1,
    "regular_delay": 0.01,
    "alt_tab_delay": 0.3,
}


def resolve_key(key_name):
    if key_name in special_keys:
        return special_keys[key_name]
    elif len(key_name) == 3 and key_name.startswith("'") and key_name.endswith("'"):
        return key_name.strip("'")
    else:
        raise ValueError(f"Unknown key: {key_name}")


def log_key(key, action="press"):
    """Append key press/release events to the log"""
    global log, key_down_time
    print(f"{key} {action}")
    current_time = time.time()
    if action == "press":
        key_down_time = current_time
        log.append(f"{key} press")
    else:
        if key_down_time:
            duration = current_time - key_down_time
            log.append(f"{key} release ({duration:.3f}s)")
            key_down_time = None
        else:
            log.append(f"{key} release")


recording_listener = None  # Global variable to keep track of the listener


def toggle_recording():
    """Toggle recording on and off"""
    global RECORDING, recording_listener
    if RECORDING:
        RECORDING = False
        save_log()
        if recording_listener:
            recording_listener.stop()  # Stop the listener when recording ends
            recording_listener = None
    else:
        RECORDING = True
        log.clear()
        recording_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        recording_listener.start()  # Start the listener when recording starts


def save_log():
    """Save the settings and key log to the log file"""
    with open(LOG_FILE, "w") as f:
        # Save settings at the top of the file
        f.write(
            f"settings: repetitions={settings['repetitions']}, regular_delay={settings['regular_delay']}, alt_tab_delay={settings['alt_tab_delay']}\n"
        )
        # Save key strokes to the file
        for line in log:
            f.write(line + "\n")


def load_settings():
    """Load settings from the log file"""
    try:
        with open(LOG_FILE, "r") as f:
            first_line = f.readline().strip()
            if first_line.startswith("settings:"):
                # Extract settings from the first line
                _, settings_str = first_line.split("settings: ")
                parts = settings_str.split(", ")
                for part in parts:
                    key, value = part.split("=")
                    if key in settings:
                        settings[key] = float(value) if "." in value else int(value)
            else:
                # No settings line found, default to initial values
                pass
    except FileNotFoundError:
        print("No recorded script found.")


def play_recorded_script(repetitions=1, regular_delay=0.01, alt_tab_delay=0.3):
    """Play the recorded key strokes from the log file"""
    global PLAYING
    PLAYING = True
    try:
        load_settings()  # Load settings before playing
        with open(LOG_FILE, "r") as f:
            # Skip the first line (settings)
            lines = f.readlines()[1:]

        for _ in range(repetitions):
            for line in lines:
                key_action = line.strip().split()
                if len(key_action) < 2:
                    continue
                key_name = key_action[0]
                action = key_action[1]

                duration = 0
                if key_name == "Key.tab" or key_name == "Key.alt":
                    duration = alt_tab_delay
                else:
                    duration = regular_delay
                resolved_key = resolve_key(key_name)
                if action == "press":
                    key_controller.press(resolved_key)
                elif action == "release":
                    key_controller.release(resolved_key)
                time.sleep(duration)

    except FileNotFoundError:
        print("No recorded script found.")
    finally:
        PLAYING = False


def on_press(key):
    """Handler for key press events during recording"""
    if RECORDING:
        log_key(key, "press")


def on_release(key):
    """Handler for key release events during recording"""
    if RECORDING:
        log_key(key, "release")


def start_listener():
    """Start the keyboard listener to record key strokes"""
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
