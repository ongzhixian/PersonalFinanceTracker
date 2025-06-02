import unittest
from shared_data_models import SeatStatus, Seat, SeatingPlan
from app_configuration import AppConfiguration


class TestSeatStatus(unittest.TestCase):
    """Tests for SeatStatus behavior."""

    def test_factory_method_from_config(self):
        """Validates SeatStatus factory method with config data."""
        mock_config = AppConfiguration(raw_config={"seat_statuses": {
            "available": "A",
            "booked": "X",
            "proposed": "Y"
        }})
        seat_status = SeatStatus.from_config(mock_config)
        self.assertEqual(seat_status.AVAILABLE, "A")
        self.assertEqual(seat_status.BOOKED, "X")
        self.assertEqual(seat_status.PROPOSED, "Y")

    def test_factory_method_with_defaults(self):
        """Validates SeatStatus default values when config is missing."""
        mock_config = AppConfiguration(raw_config={})
        seat_status = SeatStatus.from_config(mock_config)
        self.assertEqual(seat_status.AVAILABLE, "O")
        self.assertEqual(seat_status.BOOKED, "B")
        self.assertEqual(seat_status.PROPOSED, "P")


class TestSeat(unittest.TestCase):
    """Tests for Seat behavior."""

    def setUp(self):
        """Set up common test objects."""
        self.seat_status = SeatStatus("O", "B", "P")

    def test_seat_availability(self):
        """Checks if Seat correctly reports availability."""
        available_seat = Seat(row=1, col=1, status=self.seat_status.AVAILABLE)
        booked_seat = Seat(row=1, col=2, status=self.seat_status.BOOKED)

        self.assertTrue(available_seat.is_available(self.seat_status))
        self.assertFalse(booked_seat.is_available(self.seat_status))


class TestSeatingPlan(unittest.TestCase):
    """Tests for SeatingPlan behavior and validation."""

    def setUp(self):
        """Setup common objects for tests."""
        self.seat_status = SeatStatus("O", "B", "P")
        self.valid_plan = [
            [Seat(0, 0, "O"), Seat(0, 1, "B")],
            [Seat(1, 0, "O"), Seat(1, 1, "P")]
        ]

    def test_seating_plan_validation(self):
        """Ensures seating plan enforces consistency."""
        with self.assertRaises(ValueError):
            SeatingPlan(title="Invalid Plan", plan=[], available_seats_count=0)

        with self.assertRaises(ValueError):
            SeatingPlan(title="Mismatched Rows", plan=[
                [Seat(0, 0, "O")],
                [Seat(1, 0, "O"), Seat(1, 1, "B")]
            ], available_seats_count=0)

    def test_available_seats(self):
        """Checks available seat retrieval logic."""
        seating_plan = SeatingPlan(title="Test Plan", plan=self.valid_plan, available_seats_count=2)
        available_seats = seating_plan.get_available_seats(self.seat_status)

        self.assertEqual(len(available_seats), 2)
        self.assertEqual(available_seats[0].status, "O")
        self.assertEqual(available_seats[1].status, "O")


if __name__ == "__main__":
    unittest.main()
