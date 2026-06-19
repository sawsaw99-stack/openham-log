import json
import os
import tempfile
import unittest

from source.core.settings import SettingsManager


class SettingsManagerTests(unittest.TestCase):
    def test_save_and_load_callsign(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings_path = os.path.join(temp_dir, "settings.json")
            settings = SettingsManager(settings_path)

            settings.save_callsign("  w1abc  ")
            loaded = settings.load_callsign()

            self.assertEqual(loaded, "W1ABC")

            with open(settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["callsign"], "W1ABC")


if __name__ == "__main__":
    unittest.main()
