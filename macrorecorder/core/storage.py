"""Utility functions for persisting recorded macro data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

TOTAL_SLOTS = 3


def _ensure_slots(data: List[Dict[str, Any]], total_slots: int = TOTAL_SLOTS) -> None:
    while len(data) < total_slots:
        data.append({})


def load_slots(log_file: Path) -> List[Dict[str, Any]]:
    if log_file.exists():
        with log_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    else:
        data = []

    _ensure_slots(data)
    return data


def save_slot(slot_index: int, events: List[Dict[str, Any]], settings: Dict[str, Any], log_file: Path) -> None:
    data = load_slots(log_file)
    data[slot_index] = {
        "events": events,
        "settings": settings,
    }

    with log_file.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
