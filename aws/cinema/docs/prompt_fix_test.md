Given Python code:

```shared_data_models.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict

from app_configuration import AppConfiguration


class MenuOption(Enum):
    """Enumeration for menu actions."""
    BOOK_SEATS = auto()
    VIEW_BOOKING = auto()
    EXIT = auto()


@dataclass(frozen=True)
class SeatStatus:
    """
    Represents seat status codes.
    Loaded dynamically from configuration.
    """
    AVAILABLE: str
    BOOKED: str
    PROPOSED: str

    @classmethod
    def from_config(cls, config: AppConfiguration) -> "SeatStatus":
        """
        Factory method to initialize seat statuses from configuration.

        Args:
            config (AppConfiguration): Configuration instance.

        Returns:
            SeatStatus: Configured seat status object.
        """
        statuses = config.get("seat_statuses") or {}  # Ensuring it's always a dictionary
        return cls(
            AVAILABLE=statuses.get("available", "O"),
            BOOKED=statuses.get("booked", "B"),
            PROPOSED=statuses.get("proposed", "P")
        )


@dataclass(frozen=True)
class Seat:
    """
    Represents a single seat in the seating plan.

    Attributes:
        row (int): Row index.
        col (int): Column index.
        status (str): Seat availability status.
    """
    row: int
    col: int
    status: str

    def is_available(self, seat_status: SeatStatus) -> bool:
        """Check if the seat is available."""
        return self.status == seat_status.AVAILABLE


@dataclass(frozen=True)
class SeatingPlan:
    """
    Represents a structured seating plan.

    Attributes:
        title (str): Name of the seating arrangement.
        plan (List[List[Seat]]): 2D list representing the seats.
        available_seats_count (int): Number of available seats.
    """

    title: str
    plan: List[List[Seat]]
    available_seats_count: int

    def __post_init__(self) -> None:
        """
        Validates data integrity after initialization.
        Ensures seat matrix consistency.
        """
        if not self.plan:
            raise ValueError("Seating plan cannot be empty.")

        row_lengths = {len(row) for row in self.plan}
        if len(row_lengths) > 1:
            raise ValueError("All rows in the seating plan must have the same number of seats.")

    def get_available_seats(self, seat_status: SeatStatus) -> List[Seat]:
        """
        Retrieve a list of all available seats.

        Args:
            seat_status (SeatStatus): The seat status object.

        Returns:
            List[Seat]: List of seats marked as available.
        """
        return [seat for row in self.plan for seat in row if seat.is_available(seat_status)]

```

```test_shared_data_models.py
import unittest
from shared_data_models import SeatStatus, Seat, SeatingPlan, MenuOption
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


class TestMenuOption(unittest.TestCase):
    """Tests for MenuOption enumeration."""

    def test_enum_values(self):
        """Verifies MenuOption members are correctly assigned."""
        self.assertEqual(MenuOption.BOOK_SEATS.name, "BOOK_SEATS")
        self.assertEqual(MenuOption.VIEW_BOOKING.name, "VIEW_BOOKING")
        self.assertEqual(MenuOption.EXIT.name, "EXIT")


if __name__ == "__main__":
    unittest.main()

```

Review and fix unit test code.
All unit tests must be runnable.
All unit tests must pass.