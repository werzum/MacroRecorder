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


def save_log(current_slot=1):
    """Save the settings and key log to the log file, divided into slots"""
    slot_separator = f"--- Macro Slot {current_slot} ---"
    all_macros = load_all_macros()

    # Update the macro in the current slot
    all_macros[current_slot - 1] = "\n".join(log)

    with open(LOG_FILE, "w") as f:
        # Save settings at the top of the file
        f.write(
            f"settings: repetitions={settings['repetitions']}, regular_delay={settings['regular_delay']}, alt_tab_delay={settings['alt_tab_delay']}\n"
        )
        # Write the macros into the file
        for i, macro in enumerate(all_macros):
            f.write(f"--- Macro Slot {i+1} ---\n")
            f.write(macro + "\n")


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


def load_all_macros():
    """Load all macros from the log file, ensuring there are exactly 3 slots."""
    try:
        with open(LOG_FILE, "r") as f:
            data = f.read()
        # Split the data based on macro slot delimiters and clean up
        slots = [s.strip() for s in data.split("--- Macro Slot") if s]
        slots[1:] = [s[6:] for s in slots[1:]]  # Remove the slot number from the rest

        # Ensure that there are exactly 3 slots (fill with empty strings if needed)
        if len(slots) < 3:
            slots += [""] * (3 - len(slots))  # Add empty slots if fewer than 3

        return slots[1:3]  # Ensure we only return 3 slots, no settings
    except FileNotFoundError:
        # If no file exists, create one with 3 empty slots
        save_all_macros(["", "", ""])
        return [""] * 3


def save_all_macros(macros):
    """Save all macros to the log file, ensuring they are stored in 3 slots."""
    with open(LOG_FILE, "w") as f:
        for i, macro in enumerate(macros, start=1):
            f.write(f"--- Macro Slot {i} ---\n")
            f.write(macro + "\n")


def play_recorded_script(repetitions=1, regular_delay=0.01, alt_tab_delay=0.3, slot=1):
    """Play the recorded key strokes from the specified macro slot"""
    global PLAYING
    PLAYING = True
    try:
        load_settings()  # Load settings before playing
        all_macros = load_all_macros()  # Load all macros from file
        # Ensure the slot exists
        if slot < 1 or slot > len(all_macros):
            print(f"Error: Slot {slot} is out of range.")
            return

        # Get the macro for the selected slot
        macro = all_macros[slot - 1].strip()

        if not macro:
            print(f"No macro recorded in slot {slot}.")
            return

        lines = macro.split("\n")

        for _ in range(repetitions):
            for line in lines:
                line = line.strip()

                # Skip non-keypress lines, like settings
                if not line or line.startswith("settings:") or "--- Macro Slot" in line:
                    continue

                key_action = line.split(" ")

                if len(key_action) < 2:
                    # If the line doesn't contain both key and action, skip it
                    continue

                key_name, action = key_action[0], key_action[1]

                duration = (
                    alt_tab_delay
                    if key_name in ("Key.tab", "Key.alt")
                    else regular_delay
                )

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
