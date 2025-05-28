from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class Seat:
    """
    Represents a single seat in the seating plan.
    'O' for available, 'X' for booked, 'P' for proposed.
    """
    row: int
    col: int
    status: str = 'O'

@dataclass
class ProposedBooking:
    """
    Represents a temporary proposed booking with a unique ID and the seats involved.
    """
    booking_id: str
    seats: List[Tuple[int, int]] = field(default_factory=list)

@dataclass
class SeatingPlan:
    """
    Represents the complete seating plan with a title and the seat statuses.
    Includes the number of available seats.
    """
    title: str
    plan: List[List[str]]
    available_seats_count: int