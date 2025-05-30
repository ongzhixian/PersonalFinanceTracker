# shared_data_models.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Any

from app_configuration import AppConfiguration


class MenuOption(Enum):
    BOOK_SEATS = auto()
    VIEW_BOOKING = auto()
    EXIT = auto()


class SeatStatus:
    """
    Encapsulates seat status codes, loaded from configuration.
    """
    AVAILABLE: str = "O"
    BOOKED: str = "B"
    PROPOSED: str = "P"

    @staticmethod
    def from_config(config: AppConfiguration) -> "SeatStatus":
        statuses: Dict[str, Any] = config.get("seat_statuses", {})
        status = SeatStatus()
        status.AVAILABLE = statuses.get("available", "O")
        status.BOOKED = statuses.get("booked", "B")
        status.PROPOSED = statuses.get("proposed", "P")
        return status


@dataclass(frozen=True)
class Seat:
    """
    Represents a single seat in the seating plan.
    """
    row: int
    col: int
    status: str


@dataclass(frozen=True)
class SeatingPlan:
    """
    Represents the complete seating plan with a title and the seat statuses.
    Includes the number of available seats.
    """
    title: str
    plan: List[List[Seat]]
    available_seats_count: int