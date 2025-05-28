import uuid
from typing import List, Tuple, Dict, Any, Optional


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
        # Initialize seating plan with 'O' for available seats
        self._seating_plan: List[List[str]] = [['O' for _ in range(self.seats_per_row)] for _ in range(self.num_rows)]
        self._proposed_bookings: Dict[str, List[Tuple[int, int]]] = {}  # Stores proposed bookings by booking_id
        self._booking_counter: int = 0  # Simple counter for booking IDs

    def get_seating_plan(self) -> List[List[str]]:
        """
        Returns the current state of the seating plan.
        """
        return [row[:] for row in self._seating_plan]  # Return a copy to prevent external modification

    def get_proposed_seating_plan(self, number_of_seats: int, start_seat: Optional[Tuple[int, int]] = None) -> Tuple[
        str, List[List[str]]]:
        """
        Proposes a seating arrangement for the given number of seats.
        Attempts to find consecutive seats. If start_seat is provided,
        it attempts to book from there. Otherwise, it finds the first
        available block.

        Returns a tuple of (booking_id, proposed_seating_map).
        If no seats can be found, an empty list is returned for the map.
        """
        if number_of_seats <= 0:
            raise ValueError("Number of seats must be a positive integer.")

        proposed_map = [row[:] for row in self._seating_plan]  # Create a copy for the proposed plan
        booked_seats: List[Tuple[int, int]] = []
        booking_id = str(uuid.uuid4())  # Generate a unique ID for the proposed booking

        if start_seat:
            # Attempt to book from a specific start seat
            start_row, start_col = start_seat
            if 0 <= start_row < self.num_rows and 0 <= start_col < self.seats_per_row:
                if self._check_and_mark_seats(proposed_map, start_row, start_col, number_of_seats, booked_seats):
                    self._proposed_bookings[booking_id] = booked_seats
                    return booking_id, proposed_map
            return "", []  # Could not book from start_seat
        else:
            # Find the first available consecutive block
            for r in range(self.num_rows):
                for c in range(self.seats_per_row - number_of_seats + 1):
                    booked_seats.clear()  # Clear for new attempt
                    if self._check_and_mark_seats(proposed_map, r, c, number_of_seats, booked_seats):
                        self._proposed_bookings[booking_id] = booked_seats
                        return booking_id, proposed_map
            return "", []  # No consecutive seats found

    def _check_and_mark_seats(self, current_map: List[List[str]], start_row: int, start_col: int,
                              num_seats: int, booked_seats_list: List[Tuple[int, int]]) -> bool:
        """
        Helper method to check availability and mark seats in a proposed map.
        """
        for i in range(num_seats):
            col_to_check = start_col + i
            if not (0 <= start_row < self.num_rows and 0 <= col_to_check < self.seats_per_row) or \
                    current_map[start_row][col_to_check] == 'X':
                return False  # Seat is out of bounds or already taken
            current_map[start_row][col_to_check] = 'P'  # Mark as proposed
            booked_seats_list.append((start_row, col_to_check))
        return True

    def confirm_proposed_seating_map(self, booking_id: str, proposed_seating_map: List[List[str]]) -> bool:
        """
        Confirms a previously proposed seating arrangement.
        If the booking_id is valid and the seats are still available,
        it marks them as booked ('X') in the actual seating plan.
        """
        if booking_id not in self._proposed_bookings:
            return False  # Invalid booking ID

        seats_to_book = self._proposed_bookings[booking_id]

        # Verify all proposed seats are still available ('O' or 'P' in current plan)
        for r, c in seats_to_book:
            if self._seating_plan[r][c] == 'X':
                # Some seats were taken while proposal was being considered
                # Revert proposed map marks back to original if any conflict
                self._revert_proposed_marks(proposed_seating_map, seats_to_book)
                del self._proposed_bookings[booking_id]
                return False

        # Mark seats as 'X' in the actual seating plan
        for r, c in seats_to_book:
            self._seating_plan[r][c] = 'X'

        # Clean up the proposed booking
        del self._proposed_bookings[booking_id]
        return True

    def _revert_proposed_marks(self, proposed_map: List[List[str]], booked_seats: List[Tuple[int, int]]) -> None:
        """
        Helper to revert 'P' marks in a proposed map to 'O' if booking fails.
        """
        for r, c in booked_seats:
            if proposed_map[r][c] == 'P':
                proposed_map[r][c] = 'O'