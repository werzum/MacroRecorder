# Macro Recorder

## Overview

The Macro Recorder is a Python-based application that allows users to record and replay keyboard actions. It features a simple graphical user interface (GUI) to manage and store multiple macro slots. Macros can be saved, loaded, and executed, making it a useful tool for automating repetitive keyboard tasks.

![GUI Sample](sample_image.png)

## Features

- **Record Keyboard Actions**: Capture key presses and releases in real time.
- **Multiple Macro Slots**: Store up to three separate macros for easy management.
- **Play Back Macros**: Replay recorded macros with customizable delays.
- **Settings Management**: Adjust settings for repetitions and delay times for alt-tab actions.

## Requirements

- Python 3.x
- `pynput` library for keyboard event handling
- Tkinter (included with Python standard library for GUI)

## Installation

   Clone the repository:

   ```console
   git clone https://github.com/werzum/MacroRecorder.git
   cd macro_recorder
   ```

## Usage

    Run the application:

    ```console
    python macro_gui.py
    ```
  
  Use the buttons in the GUI to start recording a macro or play back a stored macro.
  
  Select the desired macro slot (1, 2, or 3) before recording or playing back to manage different macros effectively.
