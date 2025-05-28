Given:

```shared_data_models.py
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
    """
    title: str
    plan: List[List[str]]
```

```seating_planner.py
import uuid
from typing import List, Tuple, Dict, Optional
from shared_data_models import Seat, ProposedBooking, SeatingPlan # Import SeatingPlan

class SeatingPlanner:
    """
    Manages the seating plan logic, including booking,
    proposing seats, and confirming bookings.
    Adheres to the Single Responsibility Principle.
    """

    def __init__(self, title: str, num_rows: int, seats_per_row: int):
        if not isinstance(title, str) or not title:
            raise ValueError("Title must be a non-empty string.")
        if not isinstance(num_rows, int) or num_rows <= 0:
            raise ValueError("Number of rows must be a positive integer.")
        if not isinstance(seats_per_row, int) or seats_per_row <= 0:
            raise ValueError("Seats per row must be a positive integer.")

        self.title: str = title
        self.num_rows: int = num_rows
        self.seats_per_row: int = seats_per_row
        # Initialize seating plan with 'O' for available seats using Seat objects
        self._seating_plan: List[List[Seat]] = [
            [Seat(r, c, 'O') for c in range(self.seats_per_row)] for r in range(self.num_rows)
        ]
        self._proposed_bookings: Dict[str, ProposedBooking] = {}  # Stores ProposedBooking objects by booking_id

    def get_seating_plan(self) -> SeatingPlan: # Modified return type
        """
        Returns the current state of the seating plan as a SeatingPlan dataclass.
        'O' for available, 'X' for booked.
        """
        current_plan_status = [[seat.status for seat in row] for row in self._seating_plan]
        return SeatingPlan(title=self.title, plan=current_plan_status)

    def get_proposed_seating_plan(self, number_of_seats: int, start_seat: Optional[Tuple[int, int]] = None) -> Tuple[
            str, List[List[str]]]:
        """
        Proposes a seating arrangement for the given number of seats.
        Attempts to find consecutive seats. If start_seat is provided,
        it attempts to book from there. Otherwise, it finds the first
        available block.

        Returns a tuple of (booking_id, proposed_seating_map).
        If no seats can be found, an empty string and an empty list are returned for the map.
        """
        if number_of_seats <= 0:
            raise ValueError("Number of seats must be a positive integer.")

        proposed_map = self._get_current_seating_plan_status_map() # Get a fresh status map
        booked_seat_coords: List[Tuple[int, int]] = []
        booking_id = str(uuid.uuid4())  # Generate a unique ID for the proposed booking

        if start_seat:
            # Attempt to book from a specific start seat
            start_row, start_col = start_seat
            if 0 <= start_row < self.num_rows and 0 <= start_col < self.seats_per_row:
                if self._check_and_mark_seats(proposed_map, start_row, start_col, number_of_seats, booked_seat_coords):
                    self._proposed_bookings[booking_id] = ProposedBooking(booking_id=booking_id, seats=booked_seat_coords)
                    return booking_id, proposed_map
            return "", []  # Could not book from start_seat
        else:
            # Find the first available consecutive block
            for r in range(self.num_rows):
                for c in range(self.seats_per_row - number_of_seats + 1):
                    booked_seat_coords.clear()  # Clear for new attempt
                    if self._check_and_mark_seats(proposed_map, r, c, number_of_seats, booked_seat_coords):
                        self._proposed_bookings[booking_id] = ProposedBooking(booking_id=booking_id, seats=booked_seat_coords)
                        return booking_id, proposed_map
            return "", []  # No consecutive seats found

    def _get_current_seating_plan_status_map(self) -> List[List[str]]:
        """
        Helper method to get a fresh map of seat statuses from the current seating plan.
        """
        return [[seat.status for seat in row] for row in self._seating_plan]

    def _check_and_mark_seats(self, current_map: List[List[str]], start_row: int, start_col: int,
                                  num_seats: int, booked_seats_list: List[Tuple[int, int]]) -> bool:
        """
        Helper method to check availability and mark seats in a proposed map.
        Marks seats as 'P' (Proposed).
        """
        for i in range(num_seats):
            col_to_check = start_col + i
            if not (0 <= start_row < self.num_rows and 0 <= col_to_check < self.seats_per_row) or \
                    self._seating_plan[start_row][col_to_check].status == 'X': # Check actual seating plan status
                return False  # Seat is out of bounds or already taken in the real plan
            current_map[start_row][col_to_check] = 'P'  # Mark as proposed in the proposed map
            booked_seats_list.append((start_row, col_to_check))
        return True

    def confirm_proposed_seating_map(self, booking_id: str) -> bool:
        """
        Confirms a previously proposed seating arrangement.
        If the booking_id is valid and the seats are still available,
        it marks them as booked ('X') in the actual seating plan.
        """
        if booking_id not in self._proposed_bookings:
            return False  # Invalid booking ID

        proposed_booking = self._proposed_bookings[booking_id]
        seats_to_book = proposed_booking.seats

        # Verify all proposed seats are still available ('O') in the actual plan
        for r, c in seats_to_book:
            if not (0 <= r < self.num_rows and 0 <= c < self.seats_per_row) or \
               self._seating_plan[r][c].status == 'X':
                # Some seats were taken while proposal was being considered or invalid
                del self._proposed_bookings[booking_id]
                return False

        # Mark seats as 'X' in the actual seating plan
        for r, c in seats_to_book:
            self._seating_plan[r][c].status = 'X'

        # Clean up the proposed booking
        del self._proposed_bookings[booking_id]
        return True

    def cancel_proposed_seating_map(self, booking_id: str) -> bool:
        """
        Cancels a previously proposed seating arrangement, removing it from
        the proposed bookings. This does not affect the actual seating plan.
        """
        if booking_id in self._proposed_bookings:
            del self._proposed_bookings[booking_id]
            return True
        return False
```

Modify the SeatingPlan class someway that indicates number of available seats for booking in the seating plan.

Code should have typing and follow SOLID principles.
Write unit tests for code in a separate file.
