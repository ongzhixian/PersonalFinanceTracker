from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

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
        booking_id (Optional[str]): Booking identifier if relevant.
    """

    title: str
    plan: List[List[Seat]]
    available_seats_count: int
    booking_id: Optional[str] = None

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
