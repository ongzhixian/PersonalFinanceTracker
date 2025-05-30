# test_booking_repository.py

import unittest
import os
from booking_repository import BookingRepository, BookingRepositoryError

TEST_DB = "test_seating_planner.db"

class TestBookingRepository(unittest.TestCase):
    def setUp(self):
        # Use a separate test DB file
        self.repo = BookingRepository(TEST_DB)
        self.repo.clear_all_bookings()

    def tearDown(self):
        self.repo.clear_all_bookings()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_save_and_load_booking(self):
        seats = [(1, 2), (1, 3)]
        self.repo.save_booking("PlanA", "B1", seats)
        bookings = self.repo.load_all_bookings("PlanA")
        self.assertIn("B1", bookings)
        self.assertEqual(set(bookings["B1"]), set(seats))

    def test_save_booking_empty_seats(self):
        with self.assertRaises(ValueError):
            self.repo.save_booking("PlanA", "B2", [])

    def test_save_duplicate_booking_raises(self):
        seats = [(2, 2)]
        self.repo.save_booking("PlanA", "B3", seats)
        with self.assertRaises(BookingRepositoryError):
            self.repo.save_booking("PlanA", "B3", seats)

    def test_delete_booking(self):
        seats = [(3, 3)]
        self.repo.save_booking("PlanA", "B4", seats)
        self.repo.delete_booking("PlanA", "B4")
        self.assertFalse(self.repo.booking_exists("PlanA", "B4"))

    def test_delete_nonexistent_booking_raises(self):
        with self.assertRaises(BookingRepositoryError):
            self.repo.delete_booking("PlanA", "NOBOOK")

    def test_booking_exists(self):
        seats = [(4, 4)]
        self.repo.save_booking("PlanA", "B5", seats)
        self.assertTrue(self.repo.booking_exists("PlanA", "B5"))
        self.assertFalse(self.repo.booking_exists("PlanA", "B6"))

    def test_clear_all_bookings(self):
        self.repo.save_booking("PlanA", "B7", [(5, 5)])
        self.repo.save_booking("PlanA", "B8", [(6, 6)])
        self.repo.clear_all_bookings()
        bookings = self.repo.load_all_bookings("PlanA")
        self.assertEqual(bookings, {})

    def test_load_all_bookings_empty(self):
        bookings = self.repo.load_all_bookings("PlanA")
        self.assertEqual(bookings, {})

if __name__ == "__main__":
    unittest.main()