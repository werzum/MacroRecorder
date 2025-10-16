"""PySide6 application wrapper for the Macro Recorder."""

from __future__ import annotations

import sys
import threading
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from macrorecorder.core import recorder


class MacroRecorderApp(QWidget):
    def __init__(self, recorder_module=recorder):
        super().__init__()

        self.recorder = recorder_module
        self.current_slot = 0
        self.playback_timer: Optional[QTimer] = None

        self.setWindowTitle("Macro Recorder")
        self.resize(380, 460)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        self.setLayout(main_layout)

        slots_box = QGroupBox("Macro Slots")
        slots_layout = QHBoxLayout()
        slots_layout.setSpacing(12)
        slots_box.setLayout(slots_layout)

        self.slot_group = QButtonGroup(self)
        for index in range(3):
            button = QRadioButton(f"Slot {index + 1}")
            self.slot_group.addButton(button, index)
            slots_layout.addWidget(button)
            if index == 0:
                button.setChecked(True)
        self.slot_group.buttonToggled.connect(self.on_slot_button_toggled)
        main_layout.addWidget(slots_box)

        self.record_button = QPushButton("Start Recording")
        self.record_button.clicked.connect(self.on_record_button_clicked)
        main_layout.addWidget(self.record_button)

        self.play_button = QPushButton("Play Recorded Script")
        self.play_button.clicked.connect(self.on_play_button_clicked)
        main_layout.addWidget(self.play_button)

        self.repetitions_label = QLabel(
            f"Repetitions: {self.recorder.settings['repetitions']}"
        )
        main_layout.addWidget(self.repetitions_label)

        self.repetitions_spinbox = QSpinBox()
        self.repetitions_spinbox.setRange(1, 10)
        self.repetitions_spinbox.setValue(self.recorder.settings["repetitions"])
        self.repetitions_spinbox.valueChanged.connect(self.on_repetitions_changed)
        main_layout.addWidget(self.repetitions_spinbox)

        self.regular_delay_label = QLabel(
            f"Regular Stroke Delay: {self.recorder.settings['regular_delay']:.3f}s"
        )
        main_layout.addWidget(self.regular_delay_label)

        self.regular_delay_spinbox = QDoubleSpinBox()
        self.regular_delay_spinbox.setDecimals(3)
        self.regular_delay_spinbox.setRange(0.001, 0.1)
        self.regular_delay_spinbox.setSingleStep(0.01)
        self.regular_delay_spinbox.setValue(
            float(self.recorder.settings["regular_delay"])
        )
        self.regular_delay_spinbox.valueChanged.connect(
            self.on_regular_delay_changed
        )
        main_layout.addWidget(self.regular_delay_spinbox)

        self.alt_tab_delay_label = QLabel(
            f"Alt+Tab Delay: {self.recorder.settings['alt_tab_delay']:.2f}s"
        )
        main_layout.addWidget(self.alt_tab_delay_label)

        self.alt_tab_delay_spinbox = QDoubleSpinBox()
        self.alt_tab_delay_spinbox.setDecimals(2)
        self.alt_tab_delay_spinbox.setRange(0.1, 1.0)
        self.alt_tab_delay_spinbox.setSingleStep(0.1)
        self.alt_tab_delay_spinbox.setValue(
            float(self.recorder.settings["alt_tab_delay"])
        )
        self.alt_tab_delay_spinbox.valueChanged.connect(
            self.on_alt_tab_delay_changed
        )
        main_layout.addWidget(self.alt_tab_delay_spinbox)

        self.status_label = QLabel("Status: Idle")
        main_layout.addWidget(self.status_label)

        events_box = QGroupBox("Recorded Events")
        events_layout = QVBoxLayout()
        events_box.setLayout(events_layout)

        self.events_text = QTextEdit()
        self.events_text.setReadOnly(True)
        self.events_text.setLineWrapMode(QTextEdit.WidgetWidth)
        events_layout.addWidget(self.events_text)

        main_layout.addWidget(events_box)

        self.playback_timer = QTimer(self)
        self.playback_timer.setInterval(100)
        self.playback_timer.timeout.connect(self.check_if_playing)

        self.update_events_view()
        self.load_slot_settings()

    def on_record_button_clicked(self):
        current_recording_status = self.recorder.toggle_recording(self.current_slot)
        if current_recording_status:
            self.record_button.setText("Stop Recording")
            self.status_label.setText("Status: Recording")
        else:
            self.record_button.setText("Start Recording")
            self.status_label.setText("Status: Stopped")
            self.update_events_view()

    def on_play_button_clicked(self):
        if self.recorder.is_recording() or self.recorder.is_playing():
            return

        repetitions = int(self.repetitions_spinbox.value())
        regular_delay = float(self.regular_delay_spinbox.value())
        alt_tab_delay = float(self.alt_tab_delay_spinbox.value())

        self.recorder.settings["repetitions"] = repetitions
        self.recorder.settings["regular_delay"] = regular_delay
        self.recorder.settings["alt_tab_delay"] = alt_tab_delay

        self.status_label.setText("Status: Playing")
        thread = threading.Thread(
            target=self.recorder.play, args=(self.current_slot,), daemon=True
        )
        thread.start()
        self.playback_timer.start()

    def on_slot_button_toggled(self, button, checked):
        if checked:
            slot_index = self.slot_group.id(button)
            if slot_index != -1:
                self.current_slot = slot_index
                print(f"Selected Slot {slot_index + 1}")
                self.load_slot_settings()
                self.update_events_view()

    def on_repetitions_changed(self, value):
        value_int = int(value)
        self.recorder.settings["repetitions"] = value_int
        self.repetitions_label.setText(f"Repetitions: {value_int}")

    def on_regular_delay_changed(self, value):
        value_float = float(value)
        self.recorder.settings["regular_delay"] = value_float
        self.regular_delay_label.setText(
            f"Regular Stroke Delay: {value_float:.3f}s"
        )

    def on_alt_tab_delay_changed(self, value):
        value_float = float(value)
        self.recorder.settings["alt_tab_delay"] = value_float
        self.alt_tab_delay_label.setText(f"Alt+Tab Delay: {value_float:.2f}s")

    def check_if_playing(self):
        if not self.recorder.is_playing():
            self.status_label.setText("Status: Idle")
            self.playback_timer.stop()
            return

    def load_slot_settings(self):
        """Sync spin boxes with stored settings for the current slot."""
        slot = self.recorder.load_slots()[self.current_slot]
        stored = slot.get("settings", {})

        if "repetitions" in stored:
            self.repetitions_spinbox.setValue(int(stored["repetitions"]))
        if "regular_delay" in stored:
            self.regular_delay_spinbox.setValue(float(stored["regular_delay"]))
        if "alt_tab_delay" in stored:
            self.alt_tab_delay_spinbox.setValue(float(stored["alt_tab_delay"]))

    def update_events_view(self):
        """Update the text view with recorded events from the selected slot."""
        data = self.recorder.load_slots()
        slot = data[self.current_slot]

        if "events" in slot:
            lines = []
            for event in slot["events"]:
                key = event.get("key", "")
                action = event.get("action", "")
                duration = event.get("duration")
                if duration is not None:
                    lines.append(f"{key} {action} ({duration:.3f}s)")
                else:
                    lines.append(f"{key} {action}")
            text = "\n".join(lines)
        else:
            text = "(No events recorded)"

        self.events_text.setPlainText(text)

    def closeEvent(self, event):
        if self.recorder.is_recording():
            self.recorder.toggle_recording(self.current_slot)
        if self.playback_timer and self.playback_timer.isActive():
            self.playback_timer.stop()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = MacroRecorderApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
