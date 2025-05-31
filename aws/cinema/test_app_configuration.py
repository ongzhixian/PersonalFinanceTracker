import unittest
from app_configuration import AppConfiguration, ConfigurationError

class TestAppConfiguration(unittest.TestCase):
    def setUp(self):
        """Reset Singleton and Initialize a sample config for testing."""
        AppConfiguration.reset_instance()
        self.raw_config = {
            "application": {"name": "TEST_APP", "version": "1.0.1"},
            "booking_settings": {"booking_id_prefix": "BK"}
        }
        self.config = AppConfiguration(raw_config=self.raw_config)

    def test_get_existing_key(self):
        self.assertEqual(self.config.get("application:name"), "TEST_APP")

    def test_get_missing_key(self):
        self.assertIsNone(self.config.get("application:missing"))

    def test_contains_existing_key(self):
        self.assertTrue(self.config.contains("application:name"))

    def test_contains_missing_key(self):
        self.assertFalse(self.config.contains("application:missing"))

    def test_reload_with_raw_config_fails(self):
        """Ensure reload raises an error when using raw config."""
        with self.assertRaises(ConfigurationError):
            self.config.reload()

    def test_reset_instance(self):
        """Ensure singleton instance resets properly."""
        self.config.get("application:name")
        AppConfiguration.reset_instance()
        new_config = AppConfiguration(raw_config={"application": {"name": "NEW_APP"}})
        self.assertEqual(new_config.get("application:name"), "NEW_APP")

if __name__ == '__main__':
    unittest.main()
