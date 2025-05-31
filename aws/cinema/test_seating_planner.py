import unittest

from app_configuration import AppConfiguration
from seating_planner import SeatingPlanner


class TestSeatingPlanner(unittest.TestCase):

    def setUp(self):
        """Initialize a SeatingPlanner instance for tests."""
        app_configuration = AppConfiguration('./app_configuration.json')
        self.planner = SeatingPlanner(title="Test Event", num_rows=5, seats_per_row=10, config=app_configuration, db_path=':memory:')

    def test_initialize_seating_plan(self):
        """Ensure the seating plan is correctly initialized with all seats available."""
        plan = self.planner.get_seating_plan()
        available_count = sum(
            seat.status == self.planner.status_map.AVAILABLE for row in plan.plan for seat in row
        )
        self.assertEqual(available_count, self.planner.num_rows * self.planner.seats_per_row)

    def test_book_seats_successfully(self):
        """Test successful seat booking."""
        booking_id = self.planner.book_seats(3)
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 3)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

    def test_book_seats_starting_at_specific_seat(self):
        """Ensure booking starts at a requested seat."""
        booking_id = self.planner.book_seats(2, start_seat="A1")
        booked_positions = self.planner._confirmed_bookings[booking_id]
        self.assertIn((0, 0), booked_positions)  # 'A1' corresponds to (0, 0)

    def test_not_enough_seats_available(self):
        """Ensure an error is raised when attempting to overbook."""
        with self.assertRaises(ValueError):
            self.planner.book_seats(1000)  # More than available seats

    def test_cancel_booking_successfully(self):
        """Ensure booked seats can be successfully canceled."""
        booking_id = self.planner.book_seats(4)
        self.planner.cancel_booking(booking_id)
        plan = self.planner.get_seating_plan()
        available_count = sum(
            seat.status == self.planner.status_map.AVAILABLE for row in plan.plan for seat in row
        )
        self.assertEqual(available_count, self.planner.num_rows * self.planner.seats_per_row)
        self.assertNotIn(booking_id, self.planner._confirmed_bookings)

    def test_cancel_nonexistent_booking(self):
        """Ensure canceling an invalid booking raises an error."""
        with self.assertRaises(ValueError):
            self.planner.cancel_booking("invalid_booking_id")

    def test_seat_label_conversion(self):
        """Ensure seat label conversion works correctly."""
        row, col = self.planner._seat_label_to_indices("C5")
        self.assertEqual((row, col), (2, 4))  # 'C5' corresponds to (2, 4)

    def test_seat_label_out_of_range(self):
        """Ensure an error is raised when seat label is out of range."""
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices("Z99")


if __name__ == "__main__":
    unittest.main()
