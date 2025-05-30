# test_seating_planner.py

import unittest
import sqlite3
from typing import List, Tuple
from seating_planner import SeatingPlanner
from booking_repository import BookingRepository
from shared_data_models import Seat, SeatingPlan
from app_configuration import AppConfiguration

class TestSeatingPlanner(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite DB for isolation
        self.connection = sqlite3.connect(":memory:")
        self.repository = BookingRepository(connection=self.connection)
        self.config = AppConfiguration()
        self.planner = SeatingPlanner(
            title="TestPlan",
            num_rows=5,
            seats_per_row=5,
            config=self.config,
            repository=self.repository
        )

    def tearDown(self):
        self.connection.close()

    def test_book_seats_success(self):
        booking_id = self.planner.book_seats(3)
        self.assertIn(booking_id, self.planner._confirmed_bookings)
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map["BOOKED"]
            for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 3)

    def test_book_seats_with_start_seat(self):
        booking_id = self.planner.book_seats(2, start_seat="A1")
        self.assertIn(booking_id, self.planner._confirmed_bookings)
        seats = self.planner._confirmed_bookings[booking_id]
        self.assertEqual(seats[0], (0, 0))

    def test_cancel_booking_success(self):
        booking_id = self.planner.book_seats(2)
        self.planner.cancel_booking(booking_id)
        self.assertNotIn(booking_id, self.planner._confirmed_bookings)
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map["BOOKED"]
            for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 0)

    def test_cancel_booking_invalid(self):
        with self.assertRaises(ValueError):
            self.planner.cancel_booking("nonexistent")

    def test_book_seats_not_enough(self):
        # Book all seats
        for _ in range(5):
            self.planner.book_seats(5)
        with self.assertRaises(ValueError):
            self.planner.book_seats(1)

    def test_get_seating_plan_with_proposed(self):
        booking_id = self.planner.book_seats(2)
        plan = self.planner.get_seating_plan(booking_id)
        proposed_count = sum(
            seat.status == self.planner.status_map["PROPOSED"]
            for row in plan.plan for seat in row
        )
        self.assertEqual(proposed_count, 2)

    def test_seat_label_to_indices(self):
        self.assertEqual(self.planner._seat_label_to_indices("A1"), (0, 0))
        self.assertEqual(self.planner._seat_label_to_indices("E5"), (4, 4))
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices("Z1")
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices("A0")
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices("")

    def test_repository_clear_all_bookings(self):
        booking_id = self.planner.book_seats(2)
        self.repository.clear_all_bookings()
        self.assertFalse(self.repository.booking_exists(self.planner.title, booking_id))

if __name__ == '__main__':
    unittest.main()