import json
import os
import tempfile
import unittest

from app_configuration import AppConfiguration, ConfigurationError


class TestAppConfiguration(unittest.TestCase):
    def setUp(self):
        # Create a temporary config file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, mode="w+", encoding="utf-8")
        self.config_data = {
            "seat_statuses": {
                "available": "A",
                "booked": "X",
                "proposed": "Y"
            },
            "nested": {
                "level1": {
                    "level2": [1, 2, 3]
                }
            }
        }
        json.dump(self.config_data, self.temp_file)
        self.temp_file.close()
        AppConfiguration.reset_instance()

    def tearDown(self):
        os.unlink(self.temp_file.name)
        AppConfiguration.reset_instance()

    def test_singleton(self):
        config1 = AppConfiguration(self.temp_file.name)
        config2 = AppConfiguration(self.temp_file.name)
        self.assertIs(config1, config2)

    def test_get_existing_key(self):
        config = AppConfiguration(self.temp_file.name)
        self.assertEqual(config.get("seat_statuses:available"), "A")

    def test_get_missing_key_with_default(self):
        config = AppConfiguration(self.temp_file.name)
        self.assertEqual(config.get("seat_statuses:missing", default="Z"), "Z")

    def test_get_missing_key_raises(self):
        config = AppConfiguration(self.temp_file.name)
        with self.assertRaises(ConfigurationError):
            config.get("seat_statuses:missing", raise_on_missing=True)

    def test_contains(self):
        config = AppConfiguration(self.temp_file.name)
        self.assertTrue(config.contains("seat_statuses:available"))
        self.assertFalse(config.contains("seat_statuses:missing"))

    def test_reload(self):
        config = AppConfiguration(self.temp_file.name)
        self.assertEqual(config.get("seat_statuses:available"), "A")
        # Change config file
        new_data = self.config_data.copy()
        new_data["seat_statuses"]["available"] = "Z"
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            json.dump(new_data, f)
        config.reload()
        self.assertEqual(config.get("seat_statuses:available"), "Z")

    def test_nested_list_access(self):
        config = AppConfiguration(self.temp_file.name)
        self.assertEqual(config.get("nested:level1:level2:1"), 2)

    def test_invalid_json(self):
        # Write invalid JSON
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        AppConfiguration.reset_instance()
        with self.assertRaises(ConfigurationError):
            AppConfiguration(self.temp_file.name)

    def test_file_not_found(self):
        AppConfiguration.reset_instance()
        with self.assertRaises(ConfigurationError):
            AppConfiguration("nonexistent.json")


if __name__ == "__main__":
    unittest.main()