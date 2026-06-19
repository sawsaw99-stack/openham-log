import json
import os
from pathlib import Path


class SettingsManager:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = Path.home() / ".openham_log" / "settings.json"
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_data(self):
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    return {}
        return {}

    def _save_data(self, data):
        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, sort_keys=True)

    def load_callsign(self):
        return str(self._load_data().get("callsign", "")).strip().upper()

    def save_callsign(self, callsign):
        normalized = str(callsign or "").strip().upper()
        data = self._load_data()
        data["callsign"] = normalized
        self._save_data(data)
        return normalized
