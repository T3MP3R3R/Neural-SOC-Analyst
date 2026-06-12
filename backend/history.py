import json
import os
from config import HISTORY_FILE, MAX_HISTORY

def _load():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def _save(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_incident(incident):
    history = _load()
    history.insert(0, {
        "input":    incident["input"],
        "analysis": incident["result"]
    })
    if len(history) > MAX_HISTORY:
        history = history[:MAX_HISTORY]
    _save(history)

def get_history():
    return _load()