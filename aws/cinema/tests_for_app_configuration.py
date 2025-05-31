import unittest
from app_configuration import AppConfiguration, ConfigurationError

class TestAppConfiguration(unittest.TestCase):

    def setUp(self) -> None:
        """Reset Singleton instance before each test."""
        AppConfiguration.reset_instance()
        self.config = AppConfiguration("app_configuration.json")

    def test_get_valid_key(self):
        """Test retrieving a valid configuration key."""
        self.assertEqual(self.config.get("booking_settings:booking_id_prefix"), "BK")

    def test_get_invalid_key_with_default(self):
        """Test retrieving an invalid key with a default value."""
        self.assertEqual(self.config.get("invalid:key", default="default_value"), "default_value")

    def test_get_invalid_key_with_exception(self):
        """Test retrieving an invalid key with exception."""
        with self.assertRaises(ConfigurationError):
            self.config.get("invalid:key", raise_on_missing=True)

    def test_contains_existing_key(self):
        """Test checking existence of a key."""
        self.assertTrue(self.config.contains("booking_settings:booking_id_prefix"))

    def test_contains_non_existing_key(self):
        """Test checking non-existence of a key."""
        self.assertFalse(self.config.contains("invalid:key"))

if __name__ == '__main__':
    unittest.main()
