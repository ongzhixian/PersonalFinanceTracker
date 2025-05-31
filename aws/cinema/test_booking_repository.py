import unittest
import sqlite3
from booking_repository import BookingRepository, BookingRepositoryError

class TestBookingRepository(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a persistent in-memory SQLite database for testing."""
        cls.connection = sqlite3.connect(":memory:")
        cls.connection.row_factory = sqlite3.Row  # Ensure correct row access
        cls.repo = BookingRepository()

    @classmethod
    def tearDownClass(cls):
        """Close the database connection after tests."""
        cls.connection.close()

    def setUp(self):
        """Clear all bookings before each test."""
        self.repo.clear_all_bookings()

    def test_save_booking_success(self):
        """Test saving a valid booking."""
        self.repo.save_booking("TestPlan", "Booking1", [(1, 2), (3, 4)])
        bookings = self.repo.load_all_bookings("TestPlan")
        self.assertIn("Booking1", bookings)
        self.assertEqual(bookings["Booking1"], [(1, 2), (3, 4)])

    def test_save_booking_empty_seats(self):
        """Test that saving a booking with an empty seat list raises ValueError."""
        with self.assertRaises(ValueError):
            self.repo.save_booking("TestPlan", "Booking1", [])

    def test_save_duplicate_booking(self):
        """Test that duplicate bookings raise BookingRepositoryError."""
        self.repo.save_booking("TestPlan", "Booking1", [(1, 2)])
        with self.assertRaises(BookingRepositoryError):
            self.repo.save_booking("TestPlan", "Booking1", [(1, 2)])

    def test_delete_booking_success(self):
        """Test deleting an existing booking."""
        self.repo.save_booking("TestPlan", "Booking1", [(1, 2)])
        self.repo.delete_booking("TestPlan", "Booking1")
        self.assertFalse(self.repo.booking_exists("TestPlan", "Booking1"))

    def test_delete_nonexistent_booking(self):
        """Test that deleting a nonexistent booking raises BookingRepositoryError."""
        with self.assertRaises(BookingRepositoryError):
            self.repo.delete_booking("TestPlan", "NonExistentBooking")

    def test_load_all_bookings(self):
        """Test loading multiple bookings."""
        self.repo.save_booking("TestPlan", "Booking1", [(1, 2)])
        self.repo.save_booking("TestPlan", "Booking2", [(3, 4), (5, 6)])
        bookings = self.repo.load_all_bookings("TestPlan")
        self.assertEqual(bookings, {"Booking1": [(1, 2)], "Booking2": [(3, 4), (5, 6)]})

    def test_booking_exists(self):
        """Test checking if a booking exists."""
        self.repo.save_booking("TestPlan", "Booking1", [(1, 2)])
        self.assertTrue(self.repo.booking_exists("TestPlan", "Booking1"))
        self.assertFalse(self.repo.booking_exists("TestPlan", "NonExistentBooking"))

    def test_clear_all_bookings(self):
        """Test clearing all bookings."""
        self.repo.save_booking("TestPlan", "Booking1", [(1, 2)])
        self.repo.clear_all_bookings()
        bookings = self.repo.load_all_bookings("TestPlan")
        self.assertEqual(bookings, {})

if __name__ == "__main__":
    unittest.main()
