Given:

```test_app_configuration.py
import unittest
from unittest.mock import MagicMock

from app_configuration import AppConfiguration
from seating_planner import SeatingPlanner


class TestSeatingPlanner(unittest.TestCase):

    def setUp(self):
        """Initialize a SeatingPlanner instance for tests."""
        app_configuration = AppConfiguration('./app_configuration.json')
        self.planner = SeatingPlanner(title="Test Event", num_rows=5, seats_per_row=10, config=app_configuration, db_path=':memory:')

    def test_seating_planner_initialization_fail_when_empty_title(self):
        """Ensure the seating plan initialization fail when title is empty string."""
        with self.assertRaises(ValueError):
            self.planner = SeatingPlanner(title="", num_rows=5, seats_per_row=10,
                                          config=AppConfiguration('./app_configuration.json'),
                                          db_path=':memory:')

    def test_seating_planner_initialization_fail_when_number_of_rows_negative(self):
        """Ensure the seating plan initialization fail when number_of_rows is negative."""
        with self.assertRaises(ValueError):
            self.planner = SeatingPlanner(title="Test Event", num_rows=-5, seats_per_row=10,
                                          config=AppConfiguration('./app_configuration.json'),
                                          db_path=':memory:')

    def test_seating_planner_initialization_fail_when_seats_per_row_negative(self):
        """Ensure the seating plan initialization fail when seats_per_row is negative."""
        with self.assertRaises(ValueError):
            self.planner = SeatingPlanner(title="Test Event", num_rows=5, seats_per_row=-10,
                                          config=AppConfiguration('./app_configuration.json'),
                                          db_path=':memory:')

    def test_initialize_seating_plan(self):
        """Ensure the seating plan is correctly initialized with all seats available."""
        plan = self.planner.get_seating_plan()
        available_count = sum(
            seat.status == self.planner.status_map.AVAILABLE for row in plan.plan for seat in row
        )
        self.assertEqual(available_count, self.planner.num_rows * self.planner.seats_per_row)

    def test_get_seating_plan_when_booking_id_exists(self):
        booking_id = self.planner.book_seats(4)
        plan = self.planner.get_seating_plan(booking_id)
        self.assertIsNotNone(plan)

    def test_get_seating_plan_when_booking_id_not_exists(self):
        plan = self.planner.get_seating_plan("DUMMY")
        self.assertIsNone(plan)

    def test_book_seats_successfully(self):
        """Test successful seat booking."""
        booking_id = self.planner.book_seats(3)
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 3)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

    def test_book_seats_with_negative_seats_to_book(self):
        with self.assertRaises(ValueError):
            _ = self.planner.book_seats(-3)

    def test_book_seats_with_no_seat_changes(self):
        """Test successful seat booking for 3 tickets.
        B .  .  .  .  .  .  .  .  .  .
        A .  .  .  .  o  o  o  .  .  .
          1  2  3  4  5  6  7  8  9  10
        """
        booking_id = self.planner.book_seats(3)
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 3)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

        last_row_seats = plan.plan[-1]
        last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in last_row_seats)
        last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in last_row_seats)
        self.assertEqual(last_row_seats_booked_count, 3)
        self.assertEqual(last_row_seats_available_count, 7)
        self.assertEqual(last_row_seats[4].status, self.planner.status_map.BOOKED)
        self.assertEqual(last_row_seats[5].status, self.planner.status_map.BOOKED)
        self.assertEqual(last_row_seats[6].status, self.planner.status_map.BOOKED)

    def test_book_seats_with_seat_changes(self):
        """Test successful seat booking for 3 tickets.
        B .  .  o  o  o  .  .  .  .  .
        A .  .  .  .  .  .  .  .  .  .
          1  2  3  4  5  6  7  8  9  10
        """
        booking_id = self.planner.book_seats(3, start_seat='B03')
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 3)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

        last_row_seats = plan.plan[-1]
        second_last_row_seats = plan.plan[-2]
        last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in last_row_seats)
        self.assertEqual(last_row_seats_available_count, 10)
        second_last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in second_last_row_seats)
        second_last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in second_last_row_seats)
        self.assertEqual(second_last_row_seats_available_count, 7)
        self.assertEqual(second_last_row_seats_booked_count, 3)
        self.assertEqual(second_last_row_seats[2].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[3].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[4].status, self.planner.status_map.BOOKED)

    def test_book_seats_with_no_seat_changes_overflow(self):
        """Test seat booking with overflow.
        B .  .  .  .  o  o  o  .  .  .
        A o  o  o  o  o  o  o  o  o  o
          1  2  3  4  5  6  7  8  9  10
        """
        booking_id = self.planner.book_seats(13)
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 13)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

        last_row_seats = plan.plan[-1]
        second_last_row_seats = plan.plan[-2]
        last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in last_row_seats)
        self.assertEqual(last_row_seats_booked_count, 10)
        second_last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in second_last_row_seats)
        second_last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in second_last_row_seats)
        self.assertEqual(second_last_row_seats_booked_count, 3)
        self.assertEqual(second_last_row_seats_available_count, 7)
        self.assertEqual(second_last_row_seats[4].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[5].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[6].status, self.planner.status_map.BOOKED)

    def test_book_seats_with_seat_changes_overflow(self):
        """Test successful seat booking for 13 tickets.
        C .  .  .  o  o  o  o  o  .  .
        B .  .  o  o  o  o  o  o  o  o
        A .  .  .  .  .  .  .  .  .  .
          1  2  3  4  5  6  7  8  9  10
        """
        booking_id = self.planner.book_seats(13, start_seat='B03')
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 13)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

        last_row_seats = plan.plan[-1]
        second_last_row_seats = plan.plan[-2]
        third_last_row_seats = plan.plan[-3]

        last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in last_row_seats)
        self.assertEqual(last_row_seats_available_count, 10)

        second_last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in second_last_row_seats)
        second_last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in second_last_row_seats)
        self.assertEqual(second_last_row_seats_available_count, 2)
        self.assertEqual(second_last_row_seats_booked_count, 8)
        self.assertEqual(second_last_row_seats[0].status, self.planner.status_map.AVAILABLE)
        self.assertEqual(second_last_row_seats[1].status, self.planner.status_map.AVAILABLE)
        self.assertEqual(second_last_row_seats[2].status, self.planner.status_map.BOOKED)

        third_last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in third_last_row_seats)
        third_last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in third_last_row_seats)
        self.assertEqual(third_last_row_seats_available_count, 5)
        self.assertEqual(third_last_row_seats_booked_count, 5)
        self.assertEqual(second_last_row_seats[3].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[4].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[5].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[6].status, self.planner.status_map.BOOKED)
        self.assertEqual(second_last_row_seats[7].status, self.planner.status_map.BOOKED)

    def test_book_seats_with_seat_changes_overlapping_existing_booking(self):
        """Test successful seat booking for 13 tickets.
        C .  o  o  o  o  o  o  o  o  .
        B .  .  #  #  #  #  o  o  o  o
        A .  .  .  .  .  .  .  .  .  .
          1  2  3  4  5  6  7  8  9  10
        """
        _ = self.planner.book_seats(4, start_seat='B03')
        booking_id = self.planner.book_seats(12, start_seat='B05')
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 16)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

        last_row_seats = plan.plan[-1]
        second_last_row_seats = plan.plan[-2]
        third_last_row_seats = plan.plan[-3]

        last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in last_row_seats)
        self.assertEqual(last_row_seats_available_count, 10)

        second_last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in second_last_row_seats)
        second_last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in second_last_row_seats)
        self.assertEqual(second_last_row_seats_available_count, 2)
        self.assertEqual(second_last_row_seats_booked_count, 8)
        self.assertEqual(second_last_row_seats[0].status, self.planner.status_map.AVAILABLE)
        self.assertEqual(second_last_row_seats[1].status, self.planner.status_map.AVAILABLE)
        self.assertEqual(second_last_row_seats[2].status, self.planner.status_map.BOOKED)

        third_last_row_seats_available_count = sum(seat.status == self.planner.status_map.AVAILABLE for seat in third_last_row_seats)
        third_last_row_seats_booked_count = sum(seat.status == self.planner.status_map.BOOKED for seat in third_last_row_seats)
        self.assertEqual(third_last_row_seats_available_count, 2)
        self.assertEqual(third_last_row_seats_booked_count, 8)
        self.assertEqual(third_last_row_seats[0].status, self.planner.status_map.AVAILABLE)
        self.assertEqual(third_last_row_seats[9].status, self.planner.status_map.AVAILABLE)
        self.assertEqual(third_last_row_seats[1].status, self.planner.status_map.BOOKED)
        self.assertEqual(third_last_row_seats[8].status, self.planner.status_map.BOOKED)

    def test_book_seats_with_seat_changes_fill_all(self):
        """Test successful seat booking for 30 tickets.
        E o  o  o  o  o  o  o  o  o  o
        D #  #  #  #  o  o  o  o  o  o
        C o  #  #  #  #  #  #  #  #  o
        B o  o  #  #  #  #  #  #  #  #
        A o  o  o  o  o  o  o  o  o  o
          1  2  3  4  5  6  7  8  9  10
        """
        _ = self.planner.book_seats(4, start_seat='B03')
        _ = self.planner.book_seats(12, start_seat='B05')
        booking_id = self.planner.book_seats(4, start_seat='D1')
        booking_id = self.planner.book_seats(30, start_seat='D1')
        plan = self.planner.get_seating_plan()
        booked_count = sum(
            seat.status == self.planner.status_map.BOOKED for row in plan.plan for seat in row
        )
        self.assertEqual(booked_count, 50)
        self.assertIn(booking_id, self.planner._confirmed_bookings)

    def test_book_seats_starting_at_specific_seat(self):
        """Ensure booking starts at a requested seat."""
        booking_id = self.planner.book_seats(2, start_seat="A1")
        booked_positions = self.planner._confirmed_bookings[booking_id]
        self.assertIn((4, 0), booked_positions)  # 'A1' corresponds to (4, 0) due to reversed row indexing
        self.assertIn((4, 1), booked_positions)  # 'A2' corresponds to (4, 1) due to reversed row indexing
        self.assertNotIn((4, 2), booked_positions)

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

    def test_apply_bookings_to_plan(self):
        app_configuration = AppConfiguration('./app_configuration.json')
        repository = MagicMock()
        repository.load_all_bookings.return_value = {
            "booking1": [(0, 1), (0, 2)],
            "booking2": [(1, 0)]
        }
        self.planner = SeatingPlanner(title="Test Event", num_rows=5, seats_per_row=10, config=app_configuration,
                                      db_path=':memory:', repository=repository)
        plan = self.planner.get_seating_plan("booking1")
        self.assertIsNotNone(plan)

    def test_seat_label_conversion(self):
        """Ensure seat label conversion works correctly."""
        row, col = self.planner._seat_label_to_indices("C5")
        self.assertEqual((row, col), (2, 4))  # 'C5' corresponds to (2, 4)

    def test_seat_label_to_indices_invalid_seat_label(self):
        """Ensure an error is raised when seat row is not A-Z."""
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices('!')  #  ! does not exist

    def test_seat_label_to_indices_invalid_row_character(self):
        """Ensure an error is raised when seat row is not A-Z."""
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices('!1')  #  !1 does not exist

    def test_seat_label_to_indices_invalid_column_number(self):
        """Ensure an error is raised when seat column is invalid."""
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices('F!')  #  F! does not exist

    def test_seat_label_out_of_range(self):
        """Ensure an error is raised when seat label is out of range."""
        with self.assertRaises(ValueError):
            self.planner._seat_label_to_indices("Z99")


if __name__ == "__main__":
    unittest.main()

```

Summarise and generate a design specification as a markdown document.

Give a succinct and concise summary of what code does.

Give a one-liner description of each class and method.