import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import threading
import macrorecorder.macro_recorder as macro_recorder # Import the backend functions

class MacroRecorderApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Macro Recorder")
        self.set_border_width(10)
        self.set_default_size(300, 200)

        # Vertical Box Layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Macro Slots (1, 2, 3) - Buttons in a horizontal box
        self.slot_label = Gtk.Label(label="Macro Slots")
        vbox.pack_start(self.slot_label, True, True, 0)

        hbox_slots = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(hbox_slots, True, True, 0)

        self.current_slot = 0  # Default slot is 0

        # Create the radio buttons for macro slots
        self.slot_button_1 = Gtk.RadioButton.new_with_label_from_widget(None, "Slot 1")
        self.slot_button_1.connect("toggled", self.on_slot_button_toggled, 1)
        hbox_slots.pack_start(self.slot_button_1, True, True, 0)

        self.slot_button_2 = Gtk.RadioButton.new_with_label_from_widget(
            self.slot_button_1, "Slot 2"
        )
        self.slot_button_2.connect("toggled", self.on_slot_button_toggled, 2)
        hbox_slots.pack_start(self.slot_button_2, True, True, 0)

        self.slot_button_3 = Gtk.RadioButton.new_with_label_from_widget(
            self.slot_button_1, "Slot 3"
        )
        self.slot_button_3.connect("toggled", self.on_slot_button_toggled, 3)
        hbox_slots.pack_start(self.slot_button_3, True, True, 0)

        # Set Slot 1 as active by default
        self.slot_button_1.set_active(True)

        # Record Button
        self.record_button = Gtk.Button(label="Start Recording")
        self.record_button.connect("clicked", self.on_record_button_clicked)
        vbox.pack_start(self.record_button, True, True, 0)

        # Play Button
        self.play_button = Gtk.Button(label="Play Recorded Script")
        self.play_button.connect("clicked", self.on_play_button_clicked)
        vbox.pack_start(self.play_button, True, True, 0)

        # Slider for Repetitions
        self.repetitions_label = Gtk.Label(
            label=f"Repetitions: {macro_recorder.settings['repetitions']}"
        )
        vbox.pack_start(self.repetitions_label, True, True, 0)

        adjustment_repetitions = Gtk.Adjustment(
            value=macro_recorder.settings["repetitions"],
            lower=1,
            upper=10,
            step_increment=1,
        )
        self.repetitions_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_repetitions
        )
        self.repetitions_slider.set_digits(0)
        self.repetitions_slider.connect("value-changed", self.on_repetitions_changed)
        vbox.pack_start(self.repetitions_slider, True, True, 0)

        # Slider for Regular Stroke Delay
        self.regular_delay_label = Gtk.Label(
            label=f"Regular Stroke Delay: {macro_recorder.settings['regular_delay']:.3f}s"
        )
        vbox.pack_start(self.regular_delay_label, True, True, 0)

        adjustment_regular_delay = Gtk.Adjustment(
            value=macro_recorder.settings["regular_delay"],
            lower=0.001,
            upper=0.1,
            step_increment=0.01,
        )
        self.regular_delay_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_regular_delay
        )
        self.regular_delay_slider.set_digits(3)
        self.regular_delay_slider.connect(
            "value-changed", self.on_regular_delay_changed
        )
        vbox.pack_start(self.regular_delay_slider, True, True, 0)

        # Slider for Alt+Tab Delay
        self.alt_tab_delay_label = Gtk.Label(
            label=f"Alt+Tab Delay: {macro_recorder.settings['alt_tab_delay']:.2f}s"
        )
        vbox.pack_start(self.alt_tab_delay_label, True, True, 0)

        adjustment_alt_tab_delay = Gtk.Adjustment(
            value=macro_recorder.settings["alt_tab_delay"],
            lower=0.1,
            upper=1.0,
            step_increment=0.1,
        )
        self.alt_tab_delay_slider = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment_alt_tab_delay
        )
        self.alt_tab_delay_slider.set_digits(2)
        self.alt_tab_delay_slider.connect(
            "value-changed", self.on_alt_tab_delay_changed
        )
        vbox.pack_start(self.alt_tab_delay_slider, True, True, 0)

        # Status Label
        self.status_label = Gtk.Label(label="Status: Idle")
        vbox.pack_start(self.status_label, True, True, 0)

        # Recorded Events Expander
        self.expander = Gtk.Expander(label="Recorded Events")
        self.expander.set_expanded(False)  # Start collapsed

        # Scrolled, non-editable TextView
        self.events_textview = Gtk.TextView()
        self.events_textview.set_editable(False)
        self.events_textview.set_cursor_visible(False)
        self.events_textview.set_wrap_mode(Gtk.WrapMode.WORD)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_min_content_height(100)
        scrolled_window.add(self.events_textview)

        self.expander.add(scrolled_window)
        vbox.pack_start(self.expander, True, True, 0)

        # Initial load of slot events
        self.update_events_view()

    def on_record_button_clicked(self, widget):
        current_recording_status = macro_recorder.toggle_recording(self.current_slot)
        if current_recording_status:
            self.record_button.set_label("Stop Recording")
            self.status_label.set_text("Status: Recording")
        else:
            self.record_button.set_label("Start Recording")
            self.status_label.set_text("Status: Stopped")
            self.update_events_view()

    def on_play_button_clicked(self, widget):
        if not macro_recorder.RECORDING and not macro_recorder.PLAYING:
            repetitions = int(self.repetitions_slider.get_value())
            regular_delay = self.regular_delay_slider.get_value()
            alt_tab_delay = self.alt_tab_delay_slider.get_value()

            # Update settings
            macro_recorder.settings["repetitions"] = repetitions
            macro_recorder.settings["regular_delay"] = regular_delay
            macro_recorder.settings["alt_tab_delay"] = alt_tab_delay

            self.status_label.set_text("Status: Playing")
            thread = threading.Thread(
                target=macro_recorder.play_recorded_script,
                args=[self.current_slot],
            )
            thread.start()
            GLib.timeout_add(100, self.check_if_playing)

    def on_slot_button_toggled(self, button, slot):
        if button.get_active():
            self.current_slot = slot - 1
            print(f"Selected Slot {slot}")
            self.update_events_view()

    def check_if_playing(self):
        if not macro_recorder.PLAYING:
            self.status_label.set_text("Status: Idle")
            return False
        return True

    def on_repetitions_changed(self, widget):
        value = int(widget.get_value())
        self.repetitions_label.set_text(f"Repetitions: {value}")

    def on_regular_delay_changed(self, widget):
        value = widget.get_value()
        self.regular_delay_label.set_text(f"Regular Stroke Delay: {value:.3f}s")

    def on_alt_tab_delay_changed(self, widget):
        value = widget.get_value()
        self.alt_tab_delay_label.set_text(f"Alt+Tab Delay: {value:.2f}s")
    
    def update_events_view(self):
        """Update the text view with recorded events from the selected slot."""
        data = macro_recorder.load_data()
        slot = data[self.current_slot]

        buffer = self.events_textview.get_buffer()
        if "events" in slot:
            lines = []
            for event in slot["events"]:
                key = event.get("key", "")
                action = event.get("action", "")
                duration = event.get("duration", None)
                if duration is not None:
                    lines.append(f"{key} {action} ({duration:.3f}s)")
                else:
                    lines.append(f"{key} {action}")
            text = "\n".join(lines)
        else:
            text = "(No events recorded)"

        buffer.set_text(text)


def main():
    app = MacroRecorderApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()